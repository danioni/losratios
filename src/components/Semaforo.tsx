"use client";

import type { AssetClassSignal, SignalLevel } from "@/lib/data";

interface SemaforoProps {
  signals: AssetClassSignal[];
  colors: Record<string, string>;
}

const SIGNAL_CONFIG: Record<SignalLevel, { label: string; badgeClass: string; colorVar: string }> = {
  acumular: { label: "Acumular", badgeClass: "signal-badge-acumular", colorVar: "var(--accent-green)" },
  neutral: { label: "Neutral", badgeClass: "signal-badge-neutral", colorVar: "var(--text-muted)" },
  extendido: { label: "Extendido", badgeClass: "signal-badge-extendido", colorVar: "var(--accent-amber)" },
  sobrecomprado: { label: "Sobrecomprado", badgeClass: "signal-badge-sobrecomprado", colorVar: "var(--accent-red)" },
};

export default function Semaforo({ signals }: SemaforoProps) {
  return (
    <div className="space-y-4 fade-in-up fade-in-up-2">
      <h3
        className="font-serif text-base sm:text-lg tracking-wide"
        style={{ color: "var(--text-primary)" }}
      >
        Semáforo de Asset Classes
      </h3>
      <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
        Señal compuesta por asset class. Combina desviación vs SMA y métricas internas de cada clase.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {signals.map((sig) => {
          const config = SIGNAL_CONFIG[sig.signal];
          return (
            <div
              key={sig.assetClass}
              className="card-glass card-accent-top rounded-xl p-4 sm:p-5"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{sig.icon}</span>
                  <span
                    className="text-[11px] sm:text-xs font-medium tracking-wider uppercase"
                    style={{ color: "var(--text-primary)" }}
                  >
                    {sig.assetClass}
                  </span>
                </div>
                <div className={config.badgeClass}>
                  <span
                    className="w-1.5 h-1.5 rounded-full pulse-dot"
                    style={{ background: config.colorVar }}
                  />
                  <span
                    className="text-[9px] sm:text-[10px] font-medium tracking-wider uppercase"
                    style={{ color: config.colorVar }}
                  >
                    {config.label}
                  </span>
                </div>
              </div>

              {/* Z-score bar */}
              <div className="mb-3 flex items-center gap-2">
                <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--controls-bg)" }}>
                  <div className="relative h-full">
                    <div className="absolute inset-0 flex">
                      <div className="flex-1" style={{ background: "rgba(0, 255, 136, 0.15)" }} />
                      <div className="flex-1" style={{ background: "rgba(0, 255, 136, 0.05)" }} />
                      <div className="flex-1" style={{ background: "transparent" }} />
                      <div className="flex-1" style={{ background: "rgba(255, 51, 85, 0.05)" }} />
                      <div className="flex-1" style={{ background: "rgba(255, 51, 85, 0.15)" }} />
                    </div>
                    <div
                      className="absolute top-0 bottom-0 w-1 rounded-full"
                      style={{
                        background: config.colorVar,
                        left: `${Math.min(Math.max((sig.compositeZScore + 3) / 6 * 100, 2), 98)}%`,
                        boxShadow: `0 0 4px ${config.colorVar}`,
                      }}
                    />
                  </div>
                </div>
                <span className="text-[9px] tabular-nums font-medium" style={{ color: config.colorVar }}>
                  {sig.compositeZScore >= 0 ? "+" : ""}{sig.compositeZScore.toFixed(1)}σ
                </span>
              </div>

              {/* Metrics */}
              <div className="space-y-2 mb-3">
                {sig.metrics.map((m) => {
                  const metricColor =
                    m.zScore > 1 ? "var(--accent-red)" :
                    m.zScore < -1 ? "var(--accent-green)" :
                    "var(--text-secondary)";
                  return (
                    <div key={m.label} className="flex items-center justify-between">
                      <span className="text-[9px] tracking-wider" style={{ color: "var(--text-muted)" }}>
                        {m.label}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[9px] tabular-nums" style={{ color: metricColor }}>
                          {m.interpretation}
                        </span>
                        <span
                          className="text-[8px] tabular-nums px-1 py-0.5 rounded"
                          style={{
                            color: metricColor,
                            background: m.zScore > 1 ? "var(--accent-red-bg)" : m.zScore < -1 ? "var(--accent-green-bg)" : "transparent",
                          }}
                        >
                          {m.zScore >= 0 ? "+" : ""}{m.zScore.toFixed(1)}σ
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Narrative */}
              <div
                className="pt-2 text-[9px] sm:text-[10px] leading-relaxed"
                style={{ borderTop: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}
              >
                {sig.narrative}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
