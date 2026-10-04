"use client";

import { formatRatio, METRICAS_VERIFICADAS, NO_MEDIDO } from "@/lib/data";

interface MetricCardProps {
  label: string;
  value: number;
  zScore: number;
  signal: string;
  signalType: "overbought" | "oversold" | "neutral";
  delay?: number;
}

export default function MetricCard({ label, value, zScore, signal, signalType, delay = 0 }: MetricCardProps) {
  const colorMap = {
    overbought: { color: "var(--accent-red)", bg: "var(--accent-red-bg)" },
    oversold: { color: "var(--accent-green)", bg: "var(--accent-green-bg)" },
    neutral: { color: "var(--text-muted)", bg: "var(--controls-bg)" },
  };
  // Sin métricas verificadas: ni z-score ni etiqueta; solo el valor del ratio.
  const { color, bg } = METRICAS_VERIFICADAS ? colorMap[signalType] : colorMap.neutral;

  return (
    <div
      className={`card-glass card-accent-top rounded-xl p-5 md:p-6 fade-in-up fade-in-up-${delay}`}
    >
      <p
        className="text-[10px] tracking-[0.2em] uppercase mb-4 flex items-center gap-2"
        style={{ color: "var(--text-muted)" }}
      >
        <span
          className="w-1 h-1 rounded-full inline-block"
          style={{ background: color }}
        />
        {label}
      </p>
      <div className="flex items-baseline gap-2">
        <span
          className="text-[28px] font-light tabular-nums tracking-tight"
          style={{ color: "var(--text-primary)" }}
        >
          {formatRatio(value)}
        </span>
      </div>
      <div
        className="flex items-center gap-2 mt-3 pt-3"
        style={{ borderTop: "1px solid var(--border-subtle)" }}
      >
        {METRICAS_VERIFICADAS ? (
          <>
            <span
              className="text-xs font-medium tabular-nums px-1.5 py-0.5 rounded"
              style={{ color, background: bg }}
            >
              {zScore >= 0 ? "+" : ""}{zScore.toFixed(1)}σ
            </span>
            <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              {signal}
            </span>
          </>
        ) : (
          <span className="text-[10px] leading-snug" style={{ color: "var(--accent-amber)" }}>
            {NO_MEDIDO}
          </span>
        )}
      </div>
    </div>
  );
}
