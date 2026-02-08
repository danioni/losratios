"use client";

import type { AssetClassSignal, SignalLevel } from "@/lib/data";

interface SemaforoProps {
  signals: AssetClassSignal[];
  colors: Record<string, string>;
}

const SIGNAL_CONFIG: Record<SignalLevel, { label: string; badgeClass: string; colorVar: string }> = {
  rezagado: { label: "Rezagado", badgeClass: "signal-badge-rezagado", colorVar: "var(--accent-amber)" },
  alineado: { label: "Alineado", badgeClass: "signal-badge-alineado", colorVar: "var(--accent-green)" },
  adelantado: { label: "Adelantado", badgeClass: "signal-badge-adelantado", colorVar: "var(--accent-cyan)" },
  divergente: { label: "Divergente", badgeClass: "signal-badge-divergente", colorVar: "var(--accent-red)" },
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
        Señal compuesta ajustada por expansión monetaria (M2 Global). Mide si cada clase de activo
        ha priceado el debasement o va rezagada. No se trata de &quot;caro&quot; o &quot;barato&quot; en fiat.
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

              {/* Position spectrum: REZAGADO ← ALINEADO → ADELANTADO */}
              <div className="mb-3">
                <div className="flex justify-between mb-1">
                  <span className="text-[7px] tracking-widest uppercase" style={{ color: "var(--accent-amber)", opacity: 0.6 }}>
                    Rezagado
                  </span>
                  <span className="text-[7px] tracking-widest uppercase" style={{ color: "var(--accent-green)", opacity: 0.6 }}>
                    Alineado
                  </span>
                  <span className="text-[7px] tracking-widest uppercase" style={{ color: "var(--accent-cyan)", opacity: 0.6 }}>
                    Adelantado
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--controls-bg)" }}>
                    <div className="relative h-full">
                      <div className="absolute inset-0 flex">
                        <div className="flex-1" style={{ background: "rgba(255, 170, 0, 0.15)" }} />
                        <div className="flex-1" style={{ background: "rgba(255, 170, 0, 0.05)" }} />
                        <div className="flex-1" style={{ background: "rgba(0, 255, 136, 0.1)" }} />
                        <div className="flex-1" style={{ background: "rgba(0, 221, 255, 0.05)" }} />
                        <div className="flex-1" style={{ background: "rgba(0, 221, 255, 0.15)" }} />
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
              </div>

              {/* Dual z-score: adjusted vs nominal + delta */}
              <div className="flex items-center gap-3 mb-3 px-1">
                <div className="flex items-baseline gap-1">
                  <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
                    Ajustado
                  </span>
                  <span className="text-[11px] tabular-nums font-medium" style={{ color: config.colorVar }}>
                    {sig.compositeZScore >= 0 ? "+" : ""}{sig.compositeZScore.toFixed(2)}σ
                  </span>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
                    Nominal
                  </span>
                  <span className="text-[10px] tabular-nums" style={{ color: "var(--text-muted)", textDecoration: "line-through", opacity: 0.5 }}>
                    {sig.nominalZScore >= 0 ? "+" : ""}{sig.nominalZScore.toFixed(2)}σ
                  </span>
                </div>
                <div
                  className="ml-auto px-1.5 py-0.5 rounded text-[8px] tabular-nums"
                  style={{
                    background: sig.debasementDelta > 0.3 ? "var(--accent-amber-bg)" : "transparent",
                    color: sig.debasementDelta > 0.3 ? "var(--accent-amber)" : "var(--text-muted)",
                  }}
                >
                  Δ {sig.debasementDelta >= 0 ? "+" : ""}{sig.debasementDelta.toFixed(2)}σ ruido
                </div>
              </div>

              {/* Metrics */}
              <div className="space-y-2 mb-3">
                {sig.metrics.map((m) => {
                  const metricColor =
                    m.zScore > 1 ? "var(--accent-cyan)" :
                    m.zScore < -1 ? "var(--accent-amber)" :
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
                            background: m.zScore > 1 ? "var(--accent-cyan-bg)" : m.zScore < -1 ? "var(--accent-amber-bg)" : "transparent",
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

              {/* Action signal */}
              <div
                className="mt-2 text-[9px] sm:text-[10px] font-medium leading-relaxed"
                style={{ color: config.colorVar, opacity: 0.85 }}
              >
                → {sig.actionSignal}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
