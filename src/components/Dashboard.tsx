"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { summaries, rotationSignals, getFilteredData, formatRatio, type DominanceDataPoint } from "@/lib/data";
import MetricCard from "./MetricCard";
import ChartSection from "./ChartSection";

type TimeRange = "1Y" | "3Y" | "5Y" | "10Y" | "MAX";

const DEFAULT_COLORS = {
  green: "#00ff88", greenDim: "#00cc6a", blue: "#3388ff",
  purple: "#aa55ff", amber: "#ffaa00", red: "#ff3355",
  cyan: "#00ddff", gold: "#ffd700", muted: "#55556a",
};

function useThemeColors() {
  const getColors = useCallback(() => {
    if (typeof window === "undefined") return DEFAULT_COLORS;
    const s = getComputedStyle(document.documentElement);
    const g = (v: string, fb: string) => s.getPropertyValue(v).trim() || fb;
    return {
      green: g("--accent-green", "#00ff88"),
      greenDim: g("--accent-green-dim", "#00cc6a"),
      blue: g("--accent-blue", "#3388ff"),
      purple: g("--accent-purple", "#aa55ff"),
      amber: g("--accent-amber", "#ffaa00"),
      red: g("--accent-red", "#ff3355"),
      cyan: g("--accent-cyan", "#00ddff"),
      gold: g("--accent-gold", "#ffd700"),
      muted: g("--text-muted", "#55556a"),
    };
  }, []);

  const [colors, setColors] = useState(DEFAULT_COLORS);

  useEffect(() => {
    setColors(getColors());
    const observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.attributeName === "data-theme") {
          requestAnimationFrame(() => setColors(getColors()));
        }
      }
    });
    observer.observe(document.documentElement, { attributes: true });
    return () => observer.disconnect();
  }, [getColors]);

  return colors;
}

function RatioTooltip({ active, payload, label }: any) {
  if (!active || !payload) return null;
  return (
    <div
      className="rounded-lg px-4 py-3 text-xs"
      style={{
        background: "var(--bg-tooltip)",
        border: "1px solid var(--border)",
        backdropFilter: "blur(10px)",
      }}
    >
      <p className="mb-2 font-medium" style={{ color: "var(--text-secondary)" }}>
        {label}
      </p>
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center gap-2 py-0.5">
          <div className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
          <span style={{ color: "var(--text-muted)" }}>{entry.name}:</span>
          <span className="font-medium tabular-nums" style={{ color: entry.color }}>
            {formatRatio(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

function TimeRangeSelector({ range, onChange }: { range: TimeRange; onChange: (r: TimeRange) => void }) {
  const options: TimeRange[] = ["1Y", "3Y", "5Y", "10Y", "MAX"];
  return (
    <div className="flex gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className="px-2.5 sm:px-3.5 py-1.5 rounded-md text-[9px] sm:text-[10px] tracking-wider uppercase transition-all"
          style={{
            background: range === opt ? "var(--accent-green-bg-active)" : "transparent",
            color: range === opt ? "var(--accent-green)" : "var(--text-muted)",
            border: range === opt ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
            boxShadow: range === opt ? "var(--accent-green-glow)" : "none",
          }}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

// All available cross-asset pairs
type CrossPair = "btcGold" | "goldSilver" | "btcSp500" | "realEstateGold" | "sp500Gold" | "btcRealEstate" | "teslaGold" | "teslaBtc";

const PAIR_CONFIG: Record<CrossPair, { label: string; description: string; color: string }> = {
  btcGold: { label: "BTC / Oro", description: "Reserva digital vs. reserva física", color: "amber" },
  goldSilver: { label: "Oro / Plata", description: "Ratio histórico · >80 = plata barata · <50 = plata cara", color: "gold" },
  btcSp500: { label: "BTC / S&P 500", description: "Escasez absoluta vs. equity tradicional", color: "cyan" },
  sp500Gold: { label: "S&P 500 / Oro", description: "Productividad corporativa vs. reserva de valor", color: "blue" },
  realEstateGold: { label: "Real Estate / Oro", description: "Activo productivo vs. reserva pura", color: "purple" },
  btcRealEstate: { label: "BTC / Real Estate", description: "Escasez digital vs. activo tangible", color: "green" },
  teslaGold: { label: "Tesla / Oro", description: "Crecimiento especulativo vs. reserva milenaria", color: "red" },
  teslaBtc: { label: "Tesla / BTC", description: "Tech equity vs. escasez programática", color: "red" },
};

function PairSelector({ pair, onChange }: { pair: CrossPair; onChange: (p: CrossPair) => void }) {
  const presets: CrossPair[] = ["btcGold", "goldSilver", "btcSp500", "sp500Gold", "realEstateGold", "btcRealEstate", "teslaGold", "teslaBtc"];
  return (
    <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {presets.map((p) => (
        <button
          key={p}
          onClick={() => onChange(p)}
          className="px-2 sm:px-2.5 py-1.5 rounded-md text-[8px] sm:text-[9px] tracking-wider uppercase transition-all"
          style={{
            background: pair === p ? "var(--accent-green-bg-active)" : "transparent",
            color: pair === p ? "var(--accent-green)" : "var(--text-muted)",
            border: pair === p ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
          }}
        >
          {PAIR_CONFIG[p].label}
        </button>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [range, setRange] = useState<TimeRange>("MAX");
  const [crossPair, setCrossPair] = useState<CrossPair>("btcGold");
  const COLORS = useThemeColors();

  const { filteredData, filteredDominance } = useMemo(() => {
    const { ratios: r, dominance: d } = getFilteredData(range);
    return { filteredData: r, filteredDominance: d };
  }, [range]);

  // Mean & std for current pair
  const pairStats = useMemo(() => {
    const values = filteredData.map((d) => d[crossPair] as number);
    const mean = values.reduce((s, v) => s + v, 0) / values.length;
    const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length;
    const stdDev = Math.sqrt(variance);
    const current = values[values.length - 1];
    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;
    return { mean, stdDev, current, zScore, plus1: mean + stdDev, minus1: mean - stdDev, plus2: mean + 2 * stdDev, minus2: mean - 2 * stdDev };
  }, [filteredData, crossPair]);

  // S2F mean
  const s2fMean = useMemo(() => {
    const vals = filteredData.map((d) => d.btcGoldS2F);
    return vals.reduce((s, v) => s + v, 0) / vals.length;
  }, [filteredData]);

  // X-axis ticks
  const xTicks = useMemo(() => {
    const dates = filteredData.map((d) => d.date);
    if (dates.length <= 24) return dates.filter((_, i) => i % 3 === 0);
    return dates.filter((_, i) => i % 12 === 0);
  }, [filteredData]);

  const formatDate = (d: string) => {
    if (d.length <= 4) return d;
    return d.split("-")[0];
  };

  // Top 3 key metrics for cards
  const keyMetrics = useMemo(() => {
    return [
      summaries.find((s) => s.pair === "BTC / Oro")!,
      summaries.find((s) => s.pair === "Oro / Plata")!,
      summaries.find((s) => s.pair === "BTC / S&P 500")!,
    ];
  }, []);

  const getColorValue = (colorKey: string): string => {
    return COLORS[colorKey as keyof typeof COLORS] || COLORS.cyan;
  };

  const pairColor = getColorValue(PAIR_CONFIG[crossPair].color);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-6 sm:space-y-8 relative z-10">
      {/* Thesis banner */}
      <div className="text-center space-y-4 py-6 sm:py-10 fade-in-up fade-in-up-1">
        <h2 className="font-serif text-2xl sm:text-4xl md:text-5xl tracking-wide" style={{ color: "var(--text-primary)" }}>
          Los precios en fiat son ruido.
        </h2>
        <p className="font-serif italic text-lg sm:text-2xl md:text-3xl" style={{ color: "var(--accent-green)" }}>
          Los ratios son señal.
        </p>
        <p className="text-[11px] sm:text-xs leading-relaxed max-w-2xl mx-auto" style={{ color: "var(--text-muted)" }}>
          Si medís un activo en dólares, estás midiendo con una vara que se encoge.
          Acá medimos activos contra activos — eliminando el ruido monetario.
          ¿BTC está caro? Depende contra qué lo compares.
        </p>
      </div>

      {/* Rotation Signals */}
      {rotationSignals.length > 0 && (
        <div className="space-y-2 fade-in-up fade-in-up-2">
          <h3
            className="text-[10px] tracking-[0.2em] uppercase mb-3 flex items-center gap-2"
            style={{ color: "var(--accent-gold)" }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Señales de Rotación
          </h3>
          {rotationSignals.slice(0, 4).map((sig, i) => (
            <div key={i} className="signal-badge-gold">
              <span
                className="text-[10px] sm:text-[11px] font-medium"
                style={{ color: sig.type === "rotate_from" ? "var(--accent-red)" : "var(--accent-green)" }}
              >
                {sig.type === "rotate_from" ? "↗" : "↙"} {sig.message}
              </span>
              <span className="text-[9px] tabular-nums ml-auto" style={{ color: "var(--text-muted)" }}>
                {sig.zScore >= 0 ? "+" : ""}{sig.zScore.toFixed(1)}σ
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 fade-in-up fade-in-up-2">
        <TimeRangeSelector range={range} onChange={setRange} />
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        {keyMetrics.map((m, i) => (
          <MetricCard
            key={m.pair}
            label={m.pair}
            value={m.current}
            zScore={m.zScore}
            signal={m.signal}
            signalType={m.signalType}
            delay={i + 1}
          />
        ))}
      </div>

      {/* ========== MAIN CHART: Cross-Asset Ratio ========== */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="font-serif text-base sm:text-lg" style={{ color: "var(--text-primary)" }}>
            Cross-Asset Ratios
          </h3>
        </div>
        <PairSelector pair={crossPair} onChange={setCrossPair} />

        <ChartSection
          title={`${PAIR_CONFIG[crossPair].label} — ${PAIR_CONFIG[crossPair].description}`}
          subtitle={`Ratio actual: ${formatRatio(pairStats.current)} · Media: ${formatRatio(pairStats.mean)} · Desviación: ${pairStats.zScore >= 0 ? "+" : ""}${pairStats.zScore.toFixed(1)}σ`}
          delay={3}
        >
          {/* Z-score indicator bar */}
          <div className="mb-4 flex items-center gap-3">
            <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "var(--controls-bg)" }}>
              <div className="relative h-full">
                {/* Zones */}
                <div className="absolute inset-0 flex">
                  <div className="flex-1" style={{ background: "rgba(0, 255, 136, 0.15)" }} />
                  <div className="flex-1" style={{ background: "rgba(0, 255, 136, 0.05)" }} />
                  <div className="flex-1" style={{ background: "transparent" }} />
                  <div className="flex-1" style={{ background: "rgba(255, 51, 85, 0.05)" }} />
                  <div className="flex-1" style={{ background: "rgba(255, 51, 85, 0.15)" }} />
                </div>
                {/* Marker */}
                <div
                  className="absolute top-0 bottom-0 w-1 rounded-full"
                  style={{
                    background: pairStats.zScore > 1 ? "var(--accent-red)" : pairStats.zScore < -1 ? "var(--accent-green)" : "var(--accent-cyan)",
                    left: `${Math.min(Math.max((pairStats.zScore + 3) / 6 * 100, 2), 98)}%`,
                    boxShadow: `0 0 6px ${pairStats.zScore > 1 ? "var(--accent-red)" : pairStats.zScore < -1 ? "var(--accent-green)" : "var(--accent-cyan)"}`,
                  }}
                />
              </div>
            </div>
            <span className="text-[9px] tracking-wider uppercase whitespace-nowrap" style={{ color: "var(--text-muted)" }}>
              -3σ → +3σ
            </span>
          </div>

          <div className="h-[280px] sm:h-[360px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="mainGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={pairColor} stopOpacity={0.25} />
                    <stop offset="95%" stopColor={pairColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  ticks={xTicks}
                  tickFormatter={formatDate}
                  tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: number) => formatRatio(v)}
                />
                <Tooltip content={<RatioTooltip />} />
                {/* +2σ / -2σ bands */}
                {pairStats.minus2 > 0 && (
                  <ReferenceLine y={pairStats.plus2} stroke={COLORS.red} strokeDasharray="3 6" strokeOpacity={0.3} />
                )}
                {pairStats.minus2 > 0 && (
                  <ReferenceLine y={pairStats.minus2} stroke={COLORS.green} strokeDasharray="3 6" strokeOpacity={0.3} />
                )}
                {/* +1σ / -1σ */}
                <ReferenceLine y={pairStats.plus1} stroke={COLORS.red} strokeDasharray="4 4" strokeOpacity={0.2} />
                {pairStats.minus1 > 0 && (
                  <ReferenceLine y={pairStats.minus1} stroke={COLORS.green} strokeDasharray="4 4" strokeOpacity={0.2} />
                )}
                {/* Mean */}
                <ReferenceLine
                  y={pairStats.mean}
                  stroke={COLORS.muted}
                  strokeDasharray="6 4"
                  label={{
                    value: `Media: ${formatRatio(pairStats.mean)}`,
                    position: "insideTopRight",
                    fill: "var(--text-muted)",
                    fontSize: 9,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey={crossPair}
                  name={PAIR_CONFIG[crossPair].label}
                  stroke={pairColor}
                  fill="url(#mainGrad)"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          {/* Band legend */}
          <div className="flex flex-wrap gap-4 mt-3 justify-center">
            <div className="flex items-center gap-1.5">
              <div className="w-4 h-0.5" style={{ background: COLORS.muted, opacity: 0.6 }} />
              <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Media</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-4 h-0.5" style={{ background: COLORS.red, opacity: 0.3 }} />
              <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>+1σ / +2σ</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-4 h-0.5" style={{ background: COLORS.green, opacity: 0.3 }} />
              <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>-1σ / -2σ</span>
            </div>
          </div>
        </ChartSection>
      </div>

      {/* ========== S2F-Adjusted ========== */}
      <ChartSection
        title="BTC ÷ Oro (S2F-Adjusted) — Ajustado por perfil de emisión"
        subtitle="Divide el ratio BTC/Oro por el ratio de sus stock-to-flows. Si BTC tiene S2F de 120 y Oro de 62, BTC es ~2x más escaso — el ratio se ajusta por eso."
        delay={4}
      >
        <div className="h-[250px] sm:h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
              <defs>
                <linearGradient id="s2fGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.gold} stopOpacity={0.25} />
                  <stop offset="95%" stopColor={COLORS.gold} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                ticks={xTicks}
                tickFormatter={formatDate}
                tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => formatRatio(v)}
              />
              <Tooltip content={<RatioTooltip />} />
              <ReferenceLine
                y={s2fMean}
                stroke={COLORS.muted}
                strokeDasharray="6 4"
                label={{
                  value: `Media: ${formatRatio(s2fMean)}`,
                  position: "insideTopRight",
                  fill: "var(--text-muted)",
                  fontSize: 9,
                }}
              />
              <Area
                type="monotone"
                dataKey="btcGoldS2F"
                name="BTC/Oro (S2F-adj)"
                stroke={COLORS.gold}
                fill="url(#s2fGrad)"
                strokeWidth={2}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </ChartSection>

      {/* ========== DOMINANCE: Market Cap Share ========== */}
      <ChartSection
        title="Dominancia — Peso de cada activo sobre el total"
        subtitle="Market cap de cada activo como % del total (BTC + Oro + Plata + Equities + Real Estate + Bonos). Muestra cómo migra el capital entre clases de activos."
        delay={3}
      >
        <div className="h-[280px] sm:h-[360px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredDominance} margin={{ top: 5, right: 10, left: 10, bottom: 5 }} stackOffset="expand">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                ticks={xTicks}
                tickFormatter={formatDate}
                tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
              />
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
                            {(entry.value as number).toFixed(2)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                }}
              />
              <Area type="monotone" dataKey="realEstateDom" name="Real Estate" stackId="1" stroke="none" fill={COLORS.purple} fillOpacity={0.7} />
              <Area type="monotone" dataKey="bondsDom" name="Bonos" stackId="1" stroke="none" fill={COLORS.blue} fillOpacity={0.5} />
              <Area type="monotone" dataKey="equitiesDom" name="Equities" stackId="1" stroke="none" fill={COLORS.cyan} fillOpacity={0.6} />
              <Area type="monotone" dataKey="goldDom" name="Oro" stackId="1" stroke="none" fill={COLORS.gold} fillOpacity={0.7} />
              <Area type="monotone" dataKey="silverDom" name="Plata" stackId="1" stroke="none" fill={COLORS.muted} fillOpacity={0.5} />
              <Area type="monotone" dataKey="btcDom" name="Bitcoin" stackId="1" stroke="none" fill={COLORS.amber} fillOpacity={0.8} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        {/* Legend */}
        <div className="flex flex-wrap gap-4 mt-4 justify-center">
          {[
            { label: "Bitcoin", color: COLORS.amber },
            { label: "Oro", color: COLORS.gold },
            { label: "Plata", color: COLORS.muted },
            { label: "Equities", color: COLORS.cyan },
            { label: "Bonos", color: COLORS.blue },
            { label: "Real Estate", color: COLORS.purple },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ background: item.color, opacity: 0.7 }} />
              <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{item.label}</span>
            </div>
          ))}
        </div>
        {/* Current dominance stats */}
        {filteredDominance.length > 0 && (() => {
          const latest = filteredDominance[filteredDominance.length - 1];
          const items = [
            { label: "Real Estate", value: latest.realEstateDom },
            { label: "Bonos", value: latest.bondsDom },
            { label: "Equities", value: latest.equitiesDom },
            { label: "Oro", value: latest.goldDom },
            { label: "BTC", value: latest.btcDom },
            { label: "Plata", value: latest.silverDom },
          ].sort((a, b) => b.value - a.value);
          return (
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
              {items.map((item) => (
                <div key={item.label} className="text-center py-2 px-1 rounded-lg" style={{ background: "var(--controls-bg)" }}>
                  <p className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{item.label}</p>
                  <p className="text-sm font-medium tabular-nums" style={{ color: "var(--text-primary)" }}>{item.value.toFixed(1)}%</p>
                </div>
              ))}
            </div>
          );
        })()}
      </ChartSection>

      {/* ========== MULTI-PAIR OVERLAY ========== */}
      <ChartSection
        title="Overlay — Ratios clave normalizados"
        subtitle="Todos los pares principales indexados a Base 100 desde el inicio del período. Muestra cuál ganó o perdió terreno relativo."
        delay={3}
      >
        {(() => {
          // Index all cross-asset ratios to base 100
          const base = filteredData[0];
          const indexed = filteredData.map((d) => ({
            date: d.date,
            btcGold: base.btcGold > 0 ? (d.btcGold / base.btcGold) * 100 : 100,
            goldSilver: base.goldSilver > 0 ? (d.goldSilver / base.goldSilver) * 100 : 100,
            btcSp500: base.btcSp500 > 0 ? (d.btcSp500 / base.btcSp500) * 100 : 100,
            sp500Gold: base.sp500Gold > 0 ? (d.sp500Gold / base.sp500Gold) * 100 : 100,
          }));
          return (
            <>
              <div className="h-[280px] sm:h-[360px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={indexed} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      ticks={xTicks}
                      tickFormatter={formatDate}
                      tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v: number) => `${v.toFixed(0)}`}
                    />
                    <Tooltip content={<RatioTooltip />} />
                    <ReferenceLine
                      y={100}
                      stroke={COLORS.muted}
                      strokeDasharray="6 4"
                      label={{ value: "Base 100", position: "insideTopRight", fill: "var(--text-muted)", fontSize: 9 }}
                    />
                    <Line type="monotone" dataKey="btcGold" name="BTC / Oro" stroke={COLORS.amber} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="goldSilver" name="Oro / Plata" stroke={COLORS.gold} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="btcSp500" name="BTC / S&P 500" stroke={COLORS.cyan} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="sp500Gold" name="S&P 500 / Oro" stroke={COLORS.blue} strokeWidth={1.5} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-4 mt-4 justify-center">
                {[
                  { label: "BTC / Oro", color: COLORS.amber },
                  { label: "Oro / Plata", color: COLORS.gold },
                  { label: "BTC / S&P 500", color: COLORS.cyan },
                  { label: "S&P 500 / Oro", color: COLORS.blue },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-1.5">
                    <div className="w-2.5 h-0.5 rounded" style={{ background: item.color }} />
                    <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{item.label}</span>
                  </div>
                ))}
              </div>
            </>
          );
        })()}
      </ChartSection>

      {/* ========== SUMMARY TABLE ========== */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6 md:p-8 fade-in-up fade-in-up-4">
        <div className="mb-4 sm:mb-5">
          <h2 className="mb-2">
            <span className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
              Tabla de Pares
            </span>
            <span className="font-serif italic text-sm sm:text-base sm:ml-2" style={{ color: "var(--text-secondary)", opacity: 0.7 }}>
              — Todos los ratios cross-asset
            </span>
          </h2>
          <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Ratio actual vs. media histórica. La desviación (σ) indica cuán lejos está de su promedio. Sobrecomprado = el numerador está caro vs. el denominador.
          </p>
        </div>
        <div className="divider-gradient mb-5" />

        <div className="overflow-x-auto">
          <table className="w-full text-[10px] sm:text-[11px]">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Par</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Actual</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Media</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Desv.</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Señal</th>
              </tr>
            </thead>
            <tbody>
              {summaries.map((s) => {
                const signalColor =
                  s.signalType === "overbought" ? "var(--accent-red)" :
                  s.signalType === "oversold" ? "var(--accent-green)" :
                  "var(--text-muted)";
                const signalBg =
                  s.signalType === "overbought" ? "var(--accent-red-bg)" :
                  s.signalType === "oversold" ? "var(--accent-green-bg)" :
                  "transparent";

                return (
                  <tr key={s.pair} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="py-2.5 px-2 font-medium" style={{ color: "var(--text-primary)" }}>
                      {s.pair}
                    </td>
                    <td className="py-2.5 px-2 text-right tabular-nums" style={{ color: "var(--text-primary)" }}>
                      {formatRatio(s.current)}
                    </td>
                    <td className="py-2.5 px-2 text-right tabular-nums hidden sm:table-cell" style={{ color: "var(--text-secondary)" }}>
                      {formatRatio(s.mean)}
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <span
                        className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                        style={{ color: signalColor, background: signalBg }}
                      >
                        {s.zScore >= 0 ? "+" : ""}{s.zScore.toFixed(1)}σ
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-[9px] sm:text-[10px]" style={{ color: signalColor }}>
                      {s.context}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Closing */}
      <div className="text-center py-8 space-y-4 fade-in-up fade-in-up-5">
        <p className="font-serif italic text-sm sm:text-base" style={{ color: "var(--text-secondary)" }}>
          &ldquo;No preguntes si un activo está caro o barato. Preguntá contra qué lo estás midiendo.&rdquo;
        </p>
        <div className="divider-gradient max-w-xs mx-auto" />
        <div className="space-y-1">
          <p className="text-[10px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
            Datos simulados · Estructura lista para APIs reales
          </p>
          <p className="text-[9px]" style={{ color: "var(--text-muted)" }}>
            CoinGecko · FRED · Yahoo Finance · World Gold Council
          </p>
        </div>
      </div>
    </div>
  );
}
