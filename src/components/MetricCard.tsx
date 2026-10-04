"use client";

import { formatRatio, METRICAS_VERIFICADAS, NO_MEDIDO } from "@/lib/data";

interface MetricCardProps {
  label: string;
  value: number;
  /** De dónde sale el valor: mes del dato y estado del par */
  detail: string;
  delay?: number;
}

export default function MetricCard({ label, value, detail, delay = 0 }: MetricCardProps) {
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
          style={{ background: "var(--text-muted)" }}
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
      <p className="text-[10px] mt-1" style={{ color: "var(--text-muted)" }}>
        {detail}
      </p>
      {/* Sin métricas verificadas: ni z-score ni etiqueta; solo el valor del ratio. */}
      {!METRICAS_VERIFICADAS && (
        <div
          className="flex items-center gap-2 mt-3 pt-3"
          style={{ borderTop: "1px solid var(--border-subtle)" }}
        >
          <span className="text-[10px] leading-snug" style={{ color: "var(--accent-amber)" }}>
            z-score y señal — {NO_MEDIDO}
          </span>
        </div>
      )}
    </div>
  );
}
