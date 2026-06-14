"use client";

import { useEffect, useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
} from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const COLORS = ["#f59e0b", "#ef4444", "#10b981", "#3b82f6", "#8b5cf6", "#ec4899"];

interface Metrics {
  total_emails: number;
  by_intent: Record<string, number>;
  by_action: Record<string, number>;
  avg_confidence: number;
  avg_urgency: number;
  hitl_rate: number;
  hitl_count: number;
  emails_per_day: Record<string, number>;
}

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/metrics`)
      .then((r) => r.json())
      .then((data) => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <main style={{ flex: 1, padding: "2rem", color: "#d1d5db" }}>
          Loading metrics...
        </main>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <main style={{ flex: 1, padding: "2rem", color: "#d1d5db" }}>
          Failed to load metrics.
        </main>
      </div>
    );
  }

  const intentData = Object.entries(metrics.by_intent).map(([name, value]) => ({
    name,
    value,
  }));

  const dailyData = Object.entries(metrics.emails_per_day).map(([date, count]) => ({
    date: date.slice(5),
    count,
  }));

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#0f0f0f" }}>
      <Sidebar />
      <main style={{ flex: 1, padding: "2rem", color: "#d1d5db" }}>
        <h1 style={{ color: "#f59e0b", fontFamily: "monospace", fontSize: "1.8rem", marginBottom: "1.5rem" }}>
          📊 Metrics
        </h1>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
          {[
            { label: "Total Emails", value: metrics.total_emails },
            { label: "Avg Confidence", value: `${(metrics.avg_confidence * 100).toFixed(0)}%` },
            { label: "Avg Urgency", value: `${metrics.avg_urgency} / 5` },
            { label: "HITL Rate", value: `${(metrics.hitl_rate * 100).toFixed(0)}%` },
            { label: "HITL Count", value: metrics.hitl_count },
          ].map((stat) => (
            <div key={stat.label} style={{ background: "#1a1a1a", border: "0.5px solid #2a2a2a", borderRadius: "8px", padding: "1rem", textAlign: "center" }}>
              <div style={{ fontSize: "1.8rem", fontWeight: "bold", color: "#f59e0b", fontFamily: "monospace" }}>
                {stat.value}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#6b7280", marginTop: "4px" }}>{stat.label}</div>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#1a1a1a", border: "0.5px solid #2a2a2a", borderRadius: "8px", padding: "1.5rem" }}>
            <h2 style={{ fontFamily: "monospace", fontSize: "1rem", color: "#d1d5db", marginBottom: "1rem" }}>Emails Per Day</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={dailyData}>
                <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} />
                <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#1a1a1a", border: "1px solid #2a2a2a", color: "#d1d5db" }} />
                <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ background: "#1a1a1a", border: "0.5px solid #2a2a2a", borderRadius: "8px", padding: "1.5rem" }}>
            <h2 style={{ fontFamily: "monospace", fontSize: "1rem", color: "#d1d5db", marginBottom: "1rem" }}>Classification Breakdown</h2>
            {intentData.length === 0 ? (
              <p style={{ color: "#6b7280", fontSize: "0.85rem" }}>No data yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={intentData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                    {intentData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1a1a1a", border: "1px solid #2a2a2a", color: "#d1d5db" }} />
                  <Legend wrapperStyle={{ color: "#6b7280", fontSize: "12px" }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}