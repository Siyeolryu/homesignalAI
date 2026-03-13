"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from "recharts";

const priceData = [
  { month: "23.01", actual: 78000, predicted: null, upper: null, lower: null },
  { month: "23.03", actual: 79500, predicted: null, upper: null, lower: null },
  { month: "23.06", actual: 77800, predicted: null, upper: null, lower: null },
  { month: "23.09", actual: 78200, predicted: null, upper: null, lower: null },
  { month: "23.12", actual: 80100, predicted: null, upper: null, lower: null },
  { month: "24.03", actual: 82000, predicted: 82000, upper: 82000, lower: 82000 },
  { month: "24.06", actual: null, predicted: 83500, upper: 86000, lower: 81000 },
  { month: "24.09", actual: null, predicted: 85200, upper: 89000, lower: 81500 },
  { month: "24.12", actual: null, predicted: 86800, upper: 92000, lower: 82000 },
  { month: "25.03", actual: null, predicted: 88500, upper: 95000, lower: 82500 },
];

const scenarios = [
  {
    name: "낙관적",
    price: "9.5억",
    change: "+15.8%",
    probability: "25%",
    description: "금리 인하 + 정책 완화 시",
  },
  {
    name: "기본",
    price: "8.85억",
    change: "+7.9%",
    probability: "50%",
    description: "현재 추세 유지 시",
  },
  {
    name: "보수적",
    price: "8.25억",
    change: "+0.6%",
    probability: "25%",
    description: "경기 침체 + 금리 유지 시",
  },
];

const impactFactors = [
  { factor: "금리 변동", impact: 35, direction: "negative" },
  { factor: "입주 물량", impact: 25, direction: "negative" },
  { factor: "정책 영향", impact: 20, direction: "positive" },
  { factor: "경기 전망", impact: 15, direction: "positive" },
  { factor: "인구 이동", impact: 5, direction: "neutral" },
];

interface PriceTrendsProps {
  searchQuery: string;
}

export function PriceTrends({ searchQuery }: PriceTrendsProps) {
  const [timeRange, setTimeRange] = useState<"6m" | "1y" | "2y">("1y");

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">
            {searchQuery || "서울"} 가격 동향
          </h2>
          <p className="text-sm text-muted-foreground">
            AI 예측 가격 및 확률 밴드 분석
          </p>
        </div>
        <div className="flex gap-2">
          {(["6m", "1y", "2y"] as const).map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange(range)}
              className={timeRange === range ? "bg-primary text-primary-foreground" : ""}
            >
              {range === "6m" ? "6개월" : range === "1y" ? "1년" : "2년"}
            </Button>
          ))}
        </div>
      </div>

      {/* Main Price Chart */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary" />
              가격 추이 및 AI 예측
            </CardTitle>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-primary" />
                <span className="text-muted-foreground">실거래가</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-0.5 bg-accent" />
                <span className="text-muted-foreground">AI 예측</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-accent/20 border border-accent/50" />
                <span className="text-muted-foreground">95% 신뢰구간</span>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={priceData}>
              <defs>
                <linearGradient id="colorBand" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="month"
                tick={{ fill: "#9CA3AF", fontSize: 11 }}
                axisLine={{ stroke: "#374151" }}
              />
              <YAxis
                domain={[75000, 100000]}
                tick={{ fill: "#9CA3AF", fontSize: 11 }}
                axisLine={{ stroke: "#374151" }}
                tickFormatter={(value) => `${(value / 10000).toFixed(1)}억`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "1px solid #374151",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "#E5E7EB" }}
                formatter={(value: number, name: string) => {
                  if (!value) return ["-", name];
                  const label =
                    name === "actual"
                      ? "실거래가"
                      : name === "predicted"
                      ? "AI 예측"
                      : name === "upper"
                      ? "상한"
                      : "하한";
                  return [`${(value / 10000).toFixed(2)}억`, label];
                }}
              />
              <ReferenceLine
                x="24.03"
                stroke="#4ADE80"
                strokeDasharray="3 3"
                label={{ value: "현재", fill: "#4ADE80", fontSize: 10 }}
              />
              {/* Probability Band */}
              <Area
                type="monotone"
                dataKey="upper"
                stroke="transparent"
                fill="url(#colorBand)"
                stackId="band"
              />
              <Area
                type="monotone"
                dataKey="lower"
                stroke="transparent"
                fill="#0B1220"
                stackId="band"
              />
              {/* Actual Price Line */}
              <Area
                type="monotone"
                dataKey="actual"
                stroke="#4ADE80"
                strokeWidth={2}
                fill="transparent"
                dot={{ fill: "#4ADE80", strokeWidth: 2, r: 4 }}
                connectNulls={false}
              />
              {/* Predicted Line */}
              <Area
                type="monotone"
                dataKey="predicted"
                stroke="#3B82F6"
                strokeWidth={2}
                strokeDasharray="5 5"
                fill="transparent"
                dot={{ fill: "#3B82F6", strokeWidth: 2, r: 4 }}
                connectNulls={false}
              />
            </AreaChart>
          </ResponsiveContainer>
          <div className="mt-4 flex items-center justify-between p-3 bg-muted/50 rounded-lg">
            <div>
              <p className="text-sm text-foreground font-medium">
                12개월 후 예측: <span className="text-primary">8.85억</span>
              </p>
              <p className="text-xs text-muted-foreground">
                95% 신뢰구간: 8.25억 ~ 9.5억
              </p>
            </div>
            <Badge className="bg-primary/20 text-primary border-0">
              모델 정확도 82.4%
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Scenario Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {scenarios.map((scenario) => (
          <Card
            key={scenario.name}
            className={`bg-card border-border ${
              scenario.name === "기본" ? "ring-1 ring-primary/50" : ""
            }`}
          >
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <Badge
                  variant="outline"
                  className={
                    scenario.name === "낙관적"
                      ? "border-primary text-primary"
                      : scenario.name === "기본"
                      ? "border-accent text-accent"
                      : "border-chart-3 text-chart-3"
                  }
                >
                  {scenario.name} 시나리오
                </Badge>
                <span className="text-xs text-muted-foreground">
                  확률 {scenario.probability}
                </span>
              </div>
              <p className="text-2xl font-bold text-foreground mb-1">{scenario.price}</p>
              <p
                className={`text-sm font-medium ${
                  scenario.change.startsWith("+") ? "text-primary" : "text-destructive"
                }`}
              >
                {scenario.change}
              </p>
              <p className="text-xs text-muted-foreground mt-2">{scenario.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Impact Factors */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-base font-medium">예측 영향 요인</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {impactFactors.map((item) => (
              <div key={item.factor} className="flex items-center gap-4">
                <span className="text-sm text-foreground w-24">{item.factor}</span>
                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.direction === "positive"
                        ? "bg-primary"
                        : item.direction === "negative"
                        ? "bg-destructive"
                        : "bg-muted-foreground"
                    }`}
                    style={{ width: `${item.impact}%` }}
                  />
                </div>
                <span className="text-sm text-muted-foreground w-12 text-right">
                  {item.impact}%
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <p className="text-xs text-muted-foreground text-center">
        * AI 예측은 과거 데이터 기반이며, 실제 가격과 다를 수 있습니다. 투자 결정 시 전문가 상담을 권장합니다.
      </p>
    </div>
  );
}
