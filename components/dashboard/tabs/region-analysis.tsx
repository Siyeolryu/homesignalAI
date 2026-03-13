"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

const riskData = [
  { factor: "공급 리스크", value: 72, fullMark: 100 },
  { factor: "금리 민감도", value: 85, fullMark: 100 },
  { factor: "거래 활동성", value: 58, fullMark: 100 },
  { factor: "정책 영향", value: 65, fullMark: 100 },
  { factor: "가격 변동성", value: 45, fullMark: 100 },
];

const supplyData = [
  { district: "강남구", supply: 2400, color: "#4ADE80" },
  { district: "서초구", supply: 1800, color: "#3B82F6" },
  { district: "송파구", supply: 3200, color: "#4ADE80" },
  { district: "동대문구", supply: 1200, color: "#F59E0B" },
  { district: "마포구", supply: 950, color: "#3B82F6" },
  { district: "용산구", supply: 680, color: "#4ADE80" },
];

const districtStats = [
  { name: "동대문구", avgPrice: "8.2억", change: "+3.2%", risk: "보통", aiScore: 76 },
  { name: "중랑구", avgPrice: "6.8억", change: "+2.1%", risk: "낮음", aiScore: 82 },
  { name: "성북구", avgPrice: "7.5억", change: "+1.8%", risk: "낮음", aiScore: 79 },
  { name: "광진구", avgPrice: "9.4억", change: "+4.5%", risk: "보통", aiScore: 74 },
];

interface RegionAnalysisProps {
  searchQuery: string;
}

export function RegionAnalysis({ searchQuery }: RegionAnalysisProps) {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">
            {searchQuery || "서울"} 지역 분석
          </h2>
          <p className="text-sm text-muted-foreground">
            AI 기반 지역별 투자 리스크 및 공급 분석
          </p>
        </div>
        <Badge variant="outline" className="text-primary border-primary">
          분석 기준일: 2024.03.07
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Radar Chart */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary" />
              리스크 분석 레이더
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={riskData} cx="50%" cy="50%" outerRadius="70%">
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis
                  dataKey="factor"
                  tick={{ fill: "#9CA3AF", fontSize: 11 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  tick={{ fill: "#6B7280", fontSize: 10 }}
                />
                <Radar
                  name="리스크 지수"
                  dataKey="value"
                  stroke="#4ADE80"
                  fill="#4ADE80"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
            <div className="mt-4 p-3 bg-muted/50 rounded-lg">
              <p className="text-xs text-muted-foreground">
                <span className="text-foreground font-medium">종합 리스크: 중간 (65/100)</span>
                <br />
                금리 민감도가 높아 금리 변동 시 가격 영향 가능성 있음
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Supply Bar Chart */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-accent" />
              향후 2년 공급 물량 (세대수)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={supplyData} layout="vertical">
                <XAxis type="number" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="district"
                  tick={{ fill: "#9CA3AF", fontSize: 11 }}
                  width={60}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1F2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "#E5E7EB" }}
                  itemStyle={{ color: "#4ADE80" }}
                  formatter={(value: number) => [`${value.toLocaleString()} 세대`, "공급 물량"]}
                />
                <Bar dataKey="supply" radius={[0, 4, 4, 0]}>
                  {supplyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 p-3 bg-muted/50 rounded-lg">
              <p className="text-xs text-muted-foreground">
                <span className="text-foreground font-medium">송파구 공급 과잉 주의</span>
                <br />
                2025-2026년 대규모 입주 예정으로 전세가 하락 리스크 존재
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* District Comparison Table */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-base font-medium">주변 지역 비교</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-muted-foreground font-medium">지역</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">평균가</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">전월 대비</th>
                  <th className="text-center py-3 px-4 text-muted-foreground font-medium">리스크</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">AI 점수</th>
                </tr>
              </thead>
              <tbody>
                {districtStats.map((district) => (
                  <tr key={district.name} className="border-b border-border/50 hover:bg-muted/30">
                    <td className="py-3 px-4 font-medium text-foreground">{district.name}</td>
                    <td className="py-3 px-4 text-right text-foreground">{district.avgPrice}</td>
                    <td className={`py-3 px-4 text-right ${
                      district.change.startsWith("+") ? "text-primary" : "text-destructive"
                    }`}>
                      {district.change}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Badge
                        variant="outline"
                        className={
                          district.risk === "낮음"
                            ? "border-primary text-primary"
                            : district.risk === "보통"
                            ? "border-chart-3 text-chart-3"
                            : "border-destructive text-destructive"
                        }
                      >
                        {district.risk}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-primary font-medium">{district.aiScore}</span>
                      <span className="text-muted-foreground">/100</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <p className="text-xs text-muted-foreground text-center">
        * 리스크 분석은 과거 데이터 기반 AI 모델의 예측이며, 실제 시장 상황과 다를 수 있습니다.
      </p>
    </div>
  );
}
