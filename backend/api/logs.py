from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from models import EmailLog, get_session

router = APIRouter(tags=["logs"])


@router.get("/logs")
def list_logs(
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[dict]:
    rows = (
        session.query(EmailLog).order_by(EmailLog.created_at.desc()).limit(limit).all()
    )
    return [
        {
            "id": row.id,
            "email_id": row.email_id,
            "from_addr": row.from_addr,
            "subject": row.subject,
            "intent": row.intent,
            "urgency": row.urgency,
            "confidence": row.confidence,
            "matched_rule_id": row.matched_rule_id,
            "action_type": row.action_type,
            "action_value": row.action_value,
            "hitl_required": row.hitl_required,
            "human_decision": row.human_decision,
            "action_result": row.action_result,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@router.get("/metrics")
def get_metrics(
    days: int = Query(default=7, ge=1, le=30),
    session: Session = Depends(get_session),
) -> dict:
    """Return aggregated email processing metrics for the dashboard."""

    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        session.query(EmailLog)
        .filter(EmailLog.created_at >= since)
        .all()
    )

    total = len(rows)

    # Classification breakdown
    by_intent: dict[str, int] = defaultdict(int)
    for row in rows:
        by_intent[row.intent or "general"] += 1

    # Average confidence
    avg_confidence = (
        round(sum(r.confidence for r in rows) / total, 2) if total > 0 else 0.0
    )

    # HITL rate
    hitl_count = sum(1 for r in rows if r.hitl_required)
    hitl_rate = round(hitl_count / total, 2) if total > 0 else 0.0

    # Emails per day
    emails_per_day: dict[str, int] = defaultdict(int)
    for row in rows:
        day = row.created_at.strftime("%Y-%m-%d")
        emails_per_day[day] += 1

    # Fill missing days with 0
    all_days = {}
    for i in range(days):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        all_days[day] = emails_per_day.get(day, 0)

    # Average urgency
    avg_urgency = (
        round(sum(r.urgency for r in rows) / total, 1) if total > 0 else 0.0
    )

    # Action breakdown
    by_action: dict[str, int] = defaultdict(int)
    for row in rows:
        by_action[row.action_type or "label"] += 1

    return {
        "total_emails": total,
        "by_intent": dict(by_intent),
        "by_action": dict(by_action),
        "avg_confidence": avg_confidence,
        "avg_urgency": avg_urgency,
        "hitl_rate": hitl_rate,
        "hitl_count": hitl_count,
        "emails_per_day": dict(sorted(all_days.items())),
    }