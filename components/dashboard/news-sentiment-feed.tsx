"use client";

import { Newspaper, TrendingUp, TrendingDown, Minus, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useEffect, useState } from "react";

type Sentiment = "positive" | "negative" | "neutral";

interface NewsItem {
  id: string;
  title: string;
  url: string;
  keywords: string[];
  published_at: string;
  sentiment: Sentiment;
}

const POSITIVE_KEYWORDS = ["완화", "상승", "회복", "활기", "상승세", "호재", "인하", "재개발", "재건축 허용"];
const NEGATIVE_KEYWORDS = ["하락", "규제", "위기", "침체", "폭락", "강화", "제한", "세금", "부담"];

function getSentiment(keywords: string[], title: string): Sentiment {
  const text = [...keywords, title].join(" ");
  const posScore = POSITIVE_KEYWORDS.filter((k) => text.includes(k)).length;
  const negScore = NEGATIVE_KEYWORDS.filter((k) => text.includes(k)).length;
  if (posScore > negScore) return "positive";
  if (negScore > posScore) return "negative";
  return "neutral";
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(hours / 24);
  if (hours < 1) return "방금 전";
  if (hours < 24) return `${hours}시간 전`;
  if (days < 7) return `${days}일 전`;
  return new Date(dateStr).toLocaleDateString("ko-KR");
}

function SentimentBadge({ sentiment }: { sentiment: Sentiment }) {
  if (sentiment === "positive") {
    return (
      <Badge className="bg-primary/20 text-primary border-0 gap-1">
        <TrendingUp className="h-3 w-3" />
        긍정 시그널
      </Badge>
    );
  }
  if (sentiment === "negative") {
    return (
      <Badge className="bg-destructive/20 text-destructive border-0 gap-1">
        <TrendingDown className="h-3 w-3" />
        부정 시그널
      </Badge>
    );
  }
  return (
    <Badge className="bg-muted text-muted-foreground border-0 gap-1">
      <Minus className="h-3 w-3" />
      중립
    </Badge>
  );
}

export function NewsSentimentFeed() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/news")
      .then((r) => r.json())
      .then((data: { id: string; title: string; url: string; keywords: string[]; published_at: string }[]) => {
        const items = data.map((d) => ({
          ...d,
          sentiment: getSentiment(d.keywords ?? [], d.title),
        }));
        setNews(items);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card className="bg-card border-border h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Newspaper className="h-5 w-5 text-primary" />
          <CardTitle className="text-lg text-foreground">뉴스 센티먼트</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="px-0">
        <ScrollArea className="h-[320px] px-6">
          {loading ? (
            <p className="text-sm text-muted-foreground text-center py-8">로딩 중...</p>
          ) : news.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">뉴스 데이터 없음</p>
          ) : (
            <div className="space-y-4">
              {news.map((item) => (
                <div
                  key={item.id}
                  className="p-3 rounded-lg bg-secondary/50 border border-border hover:border-primary/30 transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-start gap-1 group"
                      >
                        <h4 className="text-sm font-medium text-foreground line-clamp-2 mb-2 group-hover:text-primary transition-colors">
                          {item.title}
                        </h4>
                        <ExternalLink className="h-3 w-3 text-muted-foreground mt-0.5 shrink-0" />
                      </a>
                      <div className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground mb-2">
                        <span>{timeAgo(item.published_at)}</span>
                        {(item.keywords ?? []).slice(0, 3).map((k) => (
                          <span key={k} className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                            {k}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <SentimentBadge sentiment={item.sentiment} />
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
