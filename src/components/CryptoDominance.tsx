"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { CryptoDominancePoint, CryptoRotationSignal } from "@/lib/data";

interface CryptoDominanceProps {
  data: CryptoDominancePoint[];
  rotation: CryptoRotationSignal;
  xTicks: string[];
  colors: Record<string, string>;
}

const PHASE_CONFIG: Record<string, { label: string; color: string; badge: string }> = {
  risk_off: { label: "Risk-Off (BTC)", color: "var(--accent-amber)", badge: "signal-badge-extendido" },
  alt_season: { label: "Alt Season", color: "var(--accent-green)", badge: "signal-badge-acumular" },
  neutral: { label: "Neutral", color: "var(--text-muted)", badge: "signal-badge-neutral" },
};

export default function CryptoDominance({ data, rotation, xTicks, colors }: CryptoDominanceProps) {
  const formatDate = (d: string) => d.length <= 4 ? d : d.split("-")[0];
  const latest = data.length > 0 ? data[data.length - 1] : null;
  const phaseConfig = PHASE_CONFIG[rotation.phase] || PHASE_CONFIG.neutral;

  return (
    <div className="space-y-4 fade-in-up fade-in-up-4">
      <div>
        <h3 className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
          Crypto Dominancia
        </h3>
        <p className="text-[10px] sm:text-[11px] leading-relaxed mt-1" style={{ color: "var(--text-muted)" }}>
          BTC / ETH / SOL / Others como % del market cap crypto total. Señal de rotación y posición del ciclo halving.
        </p>
      </div>

      {/* Rotation signal */}
      <div className={phaseConfig.badge}>
        <span className="w-1.5 h-1.5 rounded-full pulse-dot" style={{ background: phaseConfig.color }} />
        <span className="text-[10px] sm:text-[11px] font-medium tracking-wider uppercase" style={{ color: phaseConfig.color }}>
          {phaseConfig.label}
        </span>
        <span className="text-[9px] sm:text-[10px] ml-2" style={{ color: "var(--text-secondary)" }}>
          {rotation.narrative}
        </span>
      </div>

      {/* Halving cycle */}
      <div className="flex items-center gap-2">
        <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Ciclo Halving:</span>
        <span className="text-[9px] font-medium" style={{ color: "var(--accent-amber)" }}>{rotation.halvingCyclePosition}</span>
        <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>·</span>
        <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>BTC Dom Trend:</span>
        <span className="text-[9px] font-medium" style={{
          color: rotation.btcDomTrend === "rising" ? "var(--accent-amber)" : rotation.btcDomTrend === "falling" ? "var(--accent-green)" : "var(--text-muted)",
        }}>
          {rotation.btcDomTrend === "rising" ? "↗ Subiendo" : rotation.btcDomTrend === "falling" ? "↘ Cayendo" : "→ Estable"}
        </span>
      </div>

      {/* Stacked area chart */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6">
        <div className="h-[280px] sm:h-[360px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" ticks={xTicks} tickFormatter={formatDate} tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${v.toFixed(0)}%`} />
              <Tooltip
                content={({ active, payload, label }: any) => {
                  if (!active || !payload) return null;
                  return (
                    <div className="rounded-lg px-4 py-3 text-xs" style={{ background: "var(--bg-tooltip)", border: "1px solid var(--border)", backdropFilter: "blur(10px)" }}>
                      <p className="mb-2 font-medium" style={{ color: "var(--text-secondary)" }}>{label}</p>
                      {payload.map((entry: any, i: number) => (
                        <div key={i} className="flex items-center gap-2 py-0.5">
                          <div className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
                          <span style={{ color: "var(--text-muted)" }}>{entry.name}:</span>
                          <span className="font-medium tabular-nums" style={{ color: entry.color }}>
                            {(entry.value as number).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                }}
              />
              <Area type="monotone" dataKey="btcDom" name="BTC" stackId="1" stroke="none" fill={colors.amber} fillOpacity={0.8} />
              <Area type="monotone" dataKey="ethDom" name="ETH" stackId="1" stroke="none" fill={colors.blue} fillOpacity={0.7} />
              <Area type="monotone" dataKey="solDom" name="SOL" stackId="1" stroke="none" fill={colors.purple} fillOpacity={0.7} />
              <Area type="monotone" dataKey="othersDom" name="Others" stackId="1" stroke="none" fill={colors.muted} fillOpacity={0.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-wrap gap-4 mt-4 justify-center">
          {[
            { label: "BTC", color: colors.amber },
            { label: "ETH", color: colors.blue },
            { label: "SOL", color: colors.purple },
            { label: "Others", color: colors.muted },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ background: item.color, opacity: 0.7 }} />
              <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Current dominance mini-cards */}
      {latest && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {[
            { label: "BTC", value: latest.btcDom, color: colors.amber },
            { label: "ETH", value: latest.ethDom, color: colors.blue },
            { label: "SOL", value: latest.solDom, color: colors.purple },
            { label: "Others", value: latest.othersDom, color: colors.muted },
          ].map((item) => (
            <div key={item.label} className="text-center py-2 px-2 rounded-lg" style={{ background: "var(--controls-bg)" }}>
              <p className="text-[9px] tracking-wider uppercase" style={{ color: item.color }}>{item.label}</p>
              <p className="text-sm font-medium tabular-nums" style={{ color: "var(--text-primary)" }}>{item.value.toFixed(1)}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
