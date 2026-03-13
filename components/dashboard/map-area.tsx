"use client";

import { useState } from "react";
import { MapPin, Layers, ZoomIn, ZoomOut, Crosshair } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";

const complexMarkers = [
  { id: 1, name: "래미안 크레시티", score: 92, x: 35, y: 30, price: "15.2억" },
  { id: 2, name: "힐스테이트 강남", score: 88, x: 55, y: 45, price: "18.7억" },
  { id: 3, name: "아크로리버파크", score: 95, x: 45, y: 55, price: "32.5억" },
  { id: 4, name: "반포자이", score: 90, x: 30, y: 60, price: "28.3억" },
  { id: 5, name: "래미안 퍼스티지", score: 85, x: 65, y: 35, price: "12.8억" },
];

export function MapArea() {
  const [heatmapEnabled, setHeatmapEnabled] = useState(true);
  const [hoveredMarker, setHoveredMarker] = useState<number | null>(null);

  return (
    <Card className="relative h-[500px] bg-card border-border overflow-hidden">
      {/* Map Controls */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
        <div className="flex items-center gap-2 bg-background/90 backdrop-blur-sm rounded-lg px-3 py-2 border border-border">
          <Layers className="h-4 w-4 text-primary" />
          <span className="text-sm text-foreground">공급 히트맵</span>
          <Switch
            checked={heatmapEnabled}
            onCheckedChange={setHeatmapEnabled}
            className="data-[state=checked]:bg-primary"
          />
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-1">
        <Button size="icon" variant="outline" className="h-8 w-8 bg-background/90 backdrop-blur-sm border-border">
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button size="icon" variant="outline" className="h-8 w-8 bg-background/90 backdrop-blur-sm border-border">
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button size="icon" variant="outline" className="h-8 w-8 bg-background/90 backdrop-blur-sm border-border">
          <Crosshair className="h-4 w-4" />
        </Button>
      </div>

      {/* Map Background with Dot Grid Pattern */}
      <div className="absolute inset-0 bg-[#0D1526]">
        {/* Dot Grid Pattern */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          <defs>
            <pattern id="dotGrid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" fill="#4ADE80" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dotGrid)" />
        </svg>

        {/* Heatmap Overlay */}
        {heatmapEnabled && (
          <div className="absolute inset-0">
            <div className="absolute w-48 h-48 rounded-full bg-primary/20 blur-3xl" style={{ left: "20%", top: "30%" }} />
            <div className="absolute w-64 h-64 rounded-full bg-accent/20 blur-3xl" style={{ left: "50%", top: "40%" }} />
            <div className="absolute w-40 h-40 rounded-full bg-primary/30 blur-3xl" style={{ left: "35%", top: "55%" }} />
            <div className="absolute w-56 h-56 rounded-full bg-accent/15 blur-3xl" style={{ left: "60%", top: "25%" }} />
          </div>
        )}

        {/* Seoul Districts Simplified */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* District boundaries */}
          <path
            d="M20,20 L45,15 L70,20 L80,35 L75,55 L60,70 L40,75 L25,65 L15,45 Z"
            fill="none"
            stroke="#374151"
            strokeWidth="0.3"
            className="opacity-60"
          />
          <path
            d="M35,25 L50,22 L60,28 L58,42 L45,48 L32,42 Z"
            fill="none"
            stroke="#374151"
            strokeWidth="0.3"
            className="opacity-60"
          />
          <path
            d="M40,48 L55,45 L62,55 L55,68 L42,65 L35,55 Z"
            fill="none"
            stroke="#374151"
            strokeWidth="0.3"
            className="opacity-60"
          />
        </svg>

        {/* Complex Markers */}
        {complexMarkers.map((marker, index) => (
          <motion.div
            key={marker.id}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: index * 0.15, type: "spring" }}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-20"
            style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
            onMouseEnter={() => setHoveredMarker(marker.id)}
            onMouseLeave={() => setHoveredMarker(null)}
          >
            {/* Marker */}
            <motion.div 
              className="relative"
              whileHover={{ scale: 1.1 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <div className="w-10 h-10 rounded-full bg-primary/20 animate-ping absolute inset-0" />
              <div className="w-10 h-10 rounded-full bg-card border-2 border-primary flex items-center justify-center relative">
                <MapPin className="h-5 w-5 text-primary" />
              </div>
            </motion.div>

            {/* Popup on Hover */}
            <AnimatePresence>
              {hoveredMarker === marker.id && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.2 }}
                  className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 bg-card border border-border rounded-lg p-3 shadow-xl z-30"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm font-semibold text-foreground">{marker.name}</h4>
                    <Badge className="bg-primary/20 text-primary border-0 text-xs">
                      AI {marker.score}
                    </Badge>
                  </div>
                  <p className="text-lg font-bold text-primary">{marker.price}</p>
                  <p className="text-xs text-muted-foreground mt-1">클릭하여 상세 분석 보기</p>
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                    <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-border" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 bg-background/90 backdrop-blur-sm rounded-lg px-3 py-2 border border-border">
        <p className="text-xs text-muted-foreground mb-2">공급 밀도</p>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-primary/30" />
            <span className="text-xs text-foreground">낮음</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-primary/60" />
            <span className="text-xs text-foreground">중간</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-primary" />
            <span className="text-xs text-foreground">높음</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
