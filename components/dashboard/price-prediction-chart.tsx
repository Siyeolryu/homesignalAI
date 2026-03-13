"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Calendar } from "lucide-react";
import { useEffect, useState } from "react";

type Prediction = {
  dong: string;
  base_ym: string;
  current_price_10k: number;
  pred_1m_10k: number;
  pred_2m_10k: number;
  pred_3m_10k: number;
};

type ChartPoint = {
  month: string;
  actual: number | null;
  predicted: number | null;
};

function addMonths(ym: string, n: number): string {
  const [y, m] = ym.split("-").map(Number);
  const date = new Date(y, m - 1 + n);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}`;
}

export function PricePredictionChart() {
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [baseYm, setBaseYm] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/predictions")
      .then((r) => r.json())
      .then((preds: Prediction[]) => {
        if (!preds.length) return;

        // 전체 동 평균
        const avg = (key: keyof Prediction) =>
          preds.reduce((s, p) => s + ((p[key] as number) ?? 0), 0) / preds.length;

        const bym = preds[0].base_ym; // e.g. "2025-12"
        setBaseYm(bym);

        const baseLabel = addMonths(bym, 0);
        const p1Label = addMonths(bym, 1);
        const p2Label = addMonths(bym, 2);
        const p3Label = addMonths(bym, 3);

        const current10k = avg("current_price_10k");
        const pred1 = avg("pred_1m_10k");
        const pred2 = avg("pred_2m_10k");
        const pred3 = avg("pred_3m_10k");

        const toEok = (v: number) => Math.round((v / 10000) * 10) / 10;

        setChartData([
          { month: baseLabel, actual: toEok(current10k), predicted: toEok(current10k) },
          { month: p1Label, actual: null, predicted: toEok(pred1) },
          { month: p2Label, actual: null, predicted: toEok(pred2) },
          { month: p3Label, actual: null, predicted: toEok(pred3) },
        ]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const yMin =
    chartData.length > 0
      ? Math.floor(Math.min(...chartData.map((d) => d.predicted ?? d.actual ?? 99)) - 0.5)
      : 0;
  const yMax =
    chartData.length > 0
      ? Math.ceil(Math.max(...chartData.map((d) => d.predicted ?? d.actual ?? 0)) + 0.5)
      : 20;

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg text-foreground">AI 가격 예측</CardTitle>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>{baseYm ? `기준월: ${baseYm}` : "로딩 중..."}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-[280px] flex items-center justify-center text-muted-foreground text-sm">
            데이터 로딩 중...
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-[280px] flex items-center justify-center text-muted-foreground text-sm">
            예측 데이터가 없습니다. predict_model.py를 먼저 실행해 주세요.
          </div>
        ) : (
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4ADE80" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#4ADE80" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.5} />
                <XAxis
                  dataKey="month"
                  tick={{ fill: "#9CA3AF", fontSize: 11 }}
                  tickLine={{ stroke: "#374151" }}
                  axisLine={{ stroke: "#374151" }}
                />
                <YAxis
                  domain={[yMin, yMax]}
                  tick={{ fill: "#9CA3AF", fontSize: 11 }}
                  tickLine={{ stroke: "#374151" }}
                  axisLine={{ stroke: "#374151" }}
                  tickFormatter={(v) => `${v}억`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111827",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                    color: "#E5E7EB",
                  }}
                  labelStyle={{ color: "#9CA3AF" }}
                  formatter={(value: number, name: string) => {
                    const labels: Record<string, string> = {
                      actual: "현재가",
                      predicted: "AI 예측",
                    };
                    return [`${value}억`, labels[name] || name];
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="actual"
                  stroke="#4ADE80"
                  strokeWidth={2}
                  fill="url(#colorActual)"
                  dot={{ fill: "#4ADE80", strokeWidth: 0, r: 4 }}
                  activeDot={{ r: 6, fill: "#4ADE80" }}
                />
                <Area
                  type="monotone"
                  dataKey="predicted"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  fill="url(#colorPredicted)"
                  dot={{ fill: "#3B82F6", strokeWidth: 0, r: 4 }}
                  activeDot={{ r: 6, fill: "#3B82F6" }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-primary rounded" />
            <span className="text-xs text-muted-foreground">현재가</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-blue-500 rounded" style={{ borderStyle: "dashed" }} />
            <span className="text-xs text-muted-foreground">AI 예측 (1~3개월)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
