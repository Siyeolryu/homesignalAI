"use client";

import { TrendingUp, TrendingDown, BarChart3, Percent, Activity, Home } from "lucide-react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { useEffect, useState } from "react";

type Prediction = {
  dong: string;
  current_price_10k: number;
  pred_1m_10k: number;
  change_1m_pct: number;
  change_3m_pct: number;
};

function fmt억(val: number): string {
  const 억 = val / 10000;
  return `${억.toFixed(1)}억`;
}

export function KPITicker() {
  const [preds, setPreds] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/predictions")
      .then((r) => r.json())
      .then(setPreds)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const avgCurrent =
    preds.length > 0
      ? preds.reduce((s, p) => s + (p.current_price_10k ?? 0), 0) / preds.length
      : null;

  const avgChange1m =
    preds.length > 0
      ? preds.reduce((s, p) => s + (p.change_1m_pct ?? 0), 0) / preds.length
      : null;

  const avgChange3m =
    preds.length > 0
      ? preds.reduce((s, p) => s + (p.change_3m_pct ?? 0), 0) / preds.length
      : null;

  const risingDongs = preds.filter((p) => (p.change_1m_pct ?? 0) > 0).length;

  const kpiData = [
    {
      label: "분석 지역 평균가",
      value: loading ? "..." : avgCurrent ? fmt억(avgCurrent) : "-",
      change: avgChange1m != null ? `${avgChange1m > 0 ? "+" : ""}${avgChange1m.toFixed(1)}%` : "-",
      trend: (avgChange1m ?? 0) >= 0 ? "up" : "down",
      icon: BarChart3,
    },
    {
      label: "분석 지역",
      value: loading ? "..." : "5개 구",
      change: `${preds.length}개 동 분석`,
      trend: "up",
      icon: Home,
    },
    {
      label: "1개월 후 상승 예상",
      value: loading ? "..." : `${risingDongs}개 동`,
      change: preds.length > 0 ? `전체 ${preds.length}개 동 중` : "-",
      trend: risingDongs > preds.length / 2 ? "up" : "down",
      icon: Activity,
    },
    {
      label: "3개월 평균 변동률",
      value: loading
        ? "..."
        : avgChange3m != null
        ? `${avgChange3m > 0 ? "+" : ""}${avgChange3m.toFixed(1)}%`
        : "-",
      change: "AI 예측 기반",
      trend: (avgChange3m ?? 0) >= 0 ? "up" : "down",
      icon: Percent,
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {kpiData.map((kpi, index) => (
        <motion.div
          key={kpi.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: index * 0.1 }}
        >
          <Card className="p-4 bg-card border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-muted-foreground mb-1">{kpi.label}</p>
                <p className="text-2xl font-bold text-foreground">{kpi.value}</p>
              </div>
              <div className="p-2 rounded-lg bg-secondary">
                <kpi.icon className="h-4 w-4 text-primary" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2">
              {kpi.trend === "up" ? (
                <TrendingUp className="h-3 w-3 text-primary" />
              ) : (
                <TrendingDown className="h-3 w-3 text-destructive" />
              )}
              <span
                className={`text-xs font-medium ${
                  kpi.trend === "up" ? "text-primary" : "text-destructive"
                }`}
              >
                {kpi.change}
              </span>
            </div>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
