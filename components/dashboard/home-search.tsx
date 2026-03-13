"use client";

import { useState } from "react";
import { Search, TrendingUp, MapPin, Building2, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { HomeSignalLogo } from "./logo";

const popularSearches = [
  "강남구",
  "서초구",
  "송파구",
  "마포구",
  "용산구",
  "동대문구",
  "성동구",
  "영등포구",
];

const recentNews = [
  { title: "서울 아파트 매매가 3개월 연속 상승", sentiment: "positive" },
  { title: "금리 인하 기대감에 거래량 회복세", sentiment: "positive" },
  { title: "전세가율 하락세 지속...68% 기록", sentiment: "negative" },
];

interface HomeSearchProps {
  onSearch: (query: string) => void;
}

export function HomeSearch({ onSearch }: HomeSearchProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
    }
  };

  const handleQuickSearch = (query: string) => {
    setSearchQuery(query);
    onSearch(query);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Dot Grid Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <svg className="w-full h-full opacity-[0.03]">
          <defs>
            <pattern
              id="homeDotGrid"
              x="0"
              y="0"
              width="24"
              height="24"
              patternUnits="userSpaceOnUse"
            >
              <circle cx="2" cy="2" r="1" fill="#4ADE80" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#homeDotGrid)" />
        </svg>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-2xl text-center"
        >
          {/* Logo */}
          <div className="flex items-center justify-center mb-6">
            <HomeSignalLogo className="scale-125" />
          </div>

          {/* Tagline */}
          <p className="text-lg text-muted-foreground mb-8">
            AI 기반 부동산 시장 분석 및 가격 예측 플랫폼
          </p>

          {/* Search Box */}
          <form onSubmit={handleSubmit} className="relative mb-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="지역명, 단지명, 주소를 입력하세요 (예: 동대문구, 래미안)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-14 pl-12 pr-32 text-base bg-card border-border rounded-xl focus:border-primary focus:ring-primary"
              />
              <Button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-6 bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                AI 분석
              </Button>
            </div>
          </form>

          {/* Popular Searches */}
          <div className="mb-12">
            <p className="text-sm text-muted-foreground mb-3">인기 검색 지역</p>
            <div className="flex flex-wrap justify-center gap-2">
              {popularSearches.map((term) => (
                <Badge
                  key={term}
                  variant="outline"
                  className="cursor-pointer hover:bg-primary/10 hover:border-primary transition-colors py-1.5 px-3"
                  onClick={() => handleQuickSearch(term)}
                >
                  <MapPin className="h-3 w-3 mr-1" />
                  {term}
                </Badge>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-4 mb-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="p-4 bg-card border-border">
                <TrendingUp className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">12.4억</p>
                <p className="text-xs text-muted-foreground">서울 평균 매매가</p>
              </Card>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="p-4 bg-card border-border">
                <Building2 className="h-6 w-6 text-accent mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">8,420</p>
                <p className="text-xs text-muted-foreground">이번 달 거래량</p>
              </Card>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card className="p-4 bg-card border-border">
                <Sparkles className="h-6 w-6 text-chart-3 mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">78%</p>
                <p className="text-xs text-muted-foreground">AI 예측 신뢰도</p>
              </Card>
            </motion.div>
          </div>

          {/* Recent News */}
          <div className="text-left">
            <p className="text-sm text-muted-foreground mb-3">실시간 부동산 뉴스</p>
            <div className="space-y-2">
              {recentNews.map((news, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className="flex items-center gap-2 p-3 rounded-lg bg-card/50 border border-border/50"
                >
                  <div
                    className={`w-2 h-2 rounded-full ${
                      news.sentiment === "positive" ? "bg-primary" : "bg-destructive"
                    }`}
                  />
                  <span className="text-sm text-foreground">{news.title}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-xs text-muted-foreground border-t border-border">
        <p>본 서비스의 AI 예측은 참고용이며, 투자 결정은 전문가 상담 후 신중하게 판단하시기 바랍니다.</p>
      </footer>
    </div>
  );
}
