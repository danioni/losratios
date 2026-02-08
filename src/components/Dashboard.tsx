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
  BarChart,
  Bar,
  Cell,
} from "recharts";
import {
  summaries,
  rotationSignals,
  getFilteredData,
  formatRatio,
  PAIR_DEFS,
  ASSET_CLASSES,
  getSummariesByClass,
  TOP_STOCKS,
  getStockDominanceChanges,
  getSectorDominance,
  type ClassRatioDataPoint,
  type StockDominanceDataPoint,
} from "@/lib/data";
import MetricCard from "./MetricCard";
import ChartSection from "./ChartSection";

type TimeRange = "1Y" | "3Y" | "5Y" | "MAX";

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
            {typeof entry.value === "number" ? (entry.value < 1 ? entry.value.toFixed(4) : entry.value >= 100 ? entry.value.toFixed(1) : entry.value.toFixed(2)) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

function TimeRangeSelector({ range, onChange }: { range: TimeRange; onChange: (r: TimeRange) => void }) {
  const options: TimeRange[] = ["1Y", "3Y", "5Y", "MAX"];
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

// Asset class tab selector
function ClassTabSelector({ activeClass, onChange }: { activeClass: string; onChange: (c: string) => void }) {
  const classIcons: Record<string, string> = {
    "Commodities": "🏆",
    "Equities": "📈",
    "Crypto": "₿",
    "BTC vs Todo": "⚡",
  };
  return (
    <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {ASSET_CLASSES.map((cls) => (
        <button
          key={cls}
          onClick={() => onChange(cls)}
          className="px-2.5 sm:px-3 py-1.5 rounded-md text-[9px] sm:text-[10px] tracking-wider uppercase transition-all"
          style={{
            background: activeClass === cls ? "var(--accent-green-bg-active)" : "transparent",
            color: activeClass === cls ? "var(--accent-green)" : "var(--text-muted)",
            border: activeClass === cls ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
          }}
        >
          {classIcons[cls]} {cls}
        </button>
      ))}
    </div>
  );
}

// Pair selector within a class
function PairSelector({ pairs, activePair, onChange }: {
  pairs: typeof PAIR_DEFS;
  activePair: string;
  onChange: (key: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {pairs.map((p) => (
        <button
          key={p.key}
          onClick={() => onChange(p.key)}
          className="px-2 sm:px-2.5 py-1.5 rounded-md text-[8px] sm:text-[9px] tracking-wider uppercase transition-all"
          style={{
            background: activePair === p.key ? "var(--accent-green-bg-active)" : "transparent",
            color: activePair === p.key ? "var(--accent-green)" : "var(--text-muted)",
            border: activePair === p.key ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
          }}
        >
          {p.name}
        </button>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [range, setRange] = useState<TimeRange>("MAX");
  const [activeClass, setActiveClass] = useState<string>("Commodities");
  const [activePairKey, setActivePairKey] = useState<string>("goldSilver");
  const [stockView, setStockView] = useState<"top10" | "gainers" | "sectors">("top10");
  const COLORS = useThemeColors();

  // Get pairs for current class
  const classPairs = useMemo(() => PAIR_DEFS.filter((p) => p.assetClass === activeClass), [activeClass]);

  // Switch to first pair of new class
  useEffect(() => {
    const first = PAIR_DEFS.find((p) => p.assetClass === activeClass);
    if (first) setActivePairKey(first.key);
  }, [activeClass]);

  const currentPairDef = useMemo(() => PAIR_DEFS.find((p) => p.key === activePairKey), [activePairKey]);

  const { filteredRatios, filteredDominance, filteredStockDom, xTicks } = useMemo(() => {
    const { ratios: r, dominance: d, stockDom: sd } = getFilteredData(range);
    const dates = r.map((x) => x.date);
    const ticks = dates.length <= 24 ? dates.filter((_, i) => i % 3 === 0) : dates.filter((_, i) => i % 12 === 0);
    return { filteredRatios: r, filteredDominance: d, filteredStockDom: sd, xTicks: ticks };
  }, [range]);

  // Stock dom x-axis ticks
  const stockXTicks = useMemo(() => {
    if (!filteredStockDom.length) return [];
    const dates = filteredStockDom.map((x) => x.date);
    return dates.length <= 24 ? dates.filter((_, i) => i % 3 === 0) : dates.filter((_, i) => i % 12 === 0);
  }, [filteredStockDom]);

  // Pair stats for current selection
  const pairStats = useMemo(() => {
    const values = filteredRatios.map((d) => d[activePairKey as keyof ClassRatioDataPoint] as number);
    const mean = values.reduce((s, v) => s + v, 0) / values.length;
    const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length;
    const stdDev = Math.sqrt(variance);
    const current = values[values.length - 1];
    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;
    return { mean, stdDev, current, zScore, plus1: mean + stdDev, minus1: mean - stdDev, plus2: mean + 2 * stdDev, minus2: mean - 2 * stdDev };
  }, [filteredRatios, activePairKey]);

  const formatDate = (d: string) => {
    if (d.length <= 4) return d;
    return d.split("-")[0];
  };

  // Key metrics: one per class
  const keyMetrics = useMemo(() => {
    return [
      summaries.find((s) => s.pair === "Oro / Plata"),
      summaries.find((s) => s.pair === "S&P 500 / Nasdaq"),
      summaries.find((s) => s.pair === "BTC / ETH"),
      summaries.find((s) => s.pair === "BTC / Oro"),
    ].filter(Boolean) as typeof summaries;
  }, []);

  const classSummaries = useMemo(() => getSummariesByClass(activeClass), [activeClass]);

  const getColorValue = (colorKey: string): string => {
    return COLORS[colorKey as keyof typeof COLORS] || COLORS.cyan;
  };

  const pairColor = currentPairDef ? getColorValue(currentPairDef.color) : COLORS.cyan;

  // Stock dominance data
  const stockChanges = useMemo(() => getStockDominanceChanges(filteredStockDom), [filteredStockDom]);
  const sectorDom = useMemo(() => getSectorDominance(filteredStockDom), [filteredStockDom]);

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
                z={sig.zScore >= 0 ? "+" : ""}{sig.zScore.toFixed(1)}σ
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 fade-in-up fade-in-up-2">
        <TimeRangeSelector range={range} onChange={setRange} />
      </div>

      {/* Key metrics - one per class */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
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

      {/* ========== ASSET CLASS RATIOS ========== */}
      <div className="space-y-4">
        <h3 className="font-serif text-base sm:text-lg" style={{ color: "var(--text-primary)" }}>
          Ratios por Asset Class
        </h3>
        <ClassTabSelector activeClass={activeClass} onChange={setActiveClass} />
        <PairSelector pairs={classPairs} activePair={activePairKey} onChange={setActivePairKey} />

        {currentPairDef && (
          <ChartSection
            title={`${currentPairDef.name} — ${currentPairDef.description}`}
            subtitle={`Ratio actual: ${formatRatio(pairStats.current)} · Media: ${formatRatio(pairStats.mean)} · Desviación: ${pairStats.zScore >= 0 ? "+" : ""}${pairStats.zScore.toFixed(1)}σ`}
            delay={3}
          >
            {/* Z-score indicator bar */}
            <div className="mb-4 flex items-center gap-3">
              <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "var(--controls-bg)" }}>
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
                <AreaChart data={filteredRatios} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
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
                  {pairStats.minus2 > 0 && (
                    <ReferenceLine y={pairStats.plus2} stroke={COLORS.red} strokeDasharray="3 6" strokeOpacity={0.3} />
                  )}
                  {pairStats.minus2 > 0 && (
                    <ReferenceLine y={pairStats.minus2} stroke={COLORS.green} strokeDasharray="3 6" strokeOpacity={0.3} />
                  )}
                  <ReferenceLine y={pairStats.plus1} stroke={COLORS.red} strokeDasharray="4 4" strokeOpacity={0.2} />
                  {pairStats.minus1 > 0 && (
                    <ReferenceLine y={pairStats.minus1} stroke={COLORS.green} strokeDasharray="4 4" strokeOpacity={0.2} />
                  )}
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
                    dataKey={activePairKey}
                    name={currentPairDef.pair}
                    stroke={pairColor}
                    fill="url(#mainGrad)"
                    strokeWidth={2}
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
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
        )}

        {/* Class summary table */}
        <div className="card-glass rounded-xl p-4 sm:p-5">
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
                {classSummaries.map((s) => {
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
                      <td className="py-2.5 px-2 font-medium" style={{ color: "var(--text-primary)" }}>{s.pair}</td>
                      <td className="py-2.5 px-2 text-right tabular-nums" style={{ color: "var(--text-primary)" }}>{formatRatio(s.current)}</td>
                      <td className="py-2.5 px-2 text-right tabular-nums hidden sm:table-cell" style={{ color: "var(--text-secondary)" }}>{formatRatio(s.mean)}</td>
                      <td className="py-2.5 px-2 text-right">
                        <span className="tabular-nums px-1.5 py-0.5 rounded font-medium" style={{ color: signalColor, background: signalBg }}>
                          {s.zScore >= 0 ? "+" : ""}{s.zScore.toFixed(1)}σ
                        </span>
                      </td>
                      <td className="py-2.5 px-2 text-[9px] sm:text-[10px]" style={{ color: signalColor }}>{s.context}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ========== OVERLAY: Ratios normalizados ========== */}
      <ChartSection
        title="Overlay — Ratios clave normalizados"
        subtitle="Todos los pares principales indexados a Base 100 desde el inicio del período. Muestra cuál ganó o perdió terreno relativo."
        delay={3}
      >
        {(() => {
          const base = filteredRatios[0];
          if (!base) return null;
          const indexed = filteredRatios.map((d) => ({
            date: d.date,
            btcGold: base.btcGold > 0 ? (d.btcGold / base.btcGold) * 100 : 100,
            goldSilver: base.goldSilver > 0 ? (d.goldSilver / base.goldSilver) * 100 : 100,
            btcSp500: base.btcSp500 > 0 ? (d.btcSp500 / base.btcSp500) * 100 : 100,
            sp500Msci: base.sp500Msci > 0 ? (d.sp500Msci / base.sp500Msci) * 100 : 100,
            btcEth: base.btcEth > 0 ? (d.btcEth / base.btcEth) * 100 : 100,
          }));
          return (
            <>
              <div className="h-[280px] sm:h-[360px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={indexed} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" ticks={xTicks} tickFormatter={formatDate} tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${v.toFixed(0)}`} />
                    <Tooltip content={<RatioTooltip />} />
                    <ReferenceLine y={100} stroke={COLORS.muted} strokeDasharray="6 4" label={{ value: "Base 100", position: "insideTopRight", fill: "var(--text-muted)", fontSize: 9 }} />
                    <Line type="monotone" dataKey="btcGold" name="BTC / Oro" stroke={COLORS.amber} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="goldSilver" name="Oro / Plata" stroke={COLORS.gold} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="btcSp500" name="BTC / S&P 500" stroke={COLORS.cyan} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="sp500Msci" name="S&P 500 / MSCI" stroke={COLORS.blue} strokeWidth={1.5} dot={false} />
                    <Line type="monotone" dataKey="btcEth" name="BTC / ETH" stroke={COLORS.purple} strokeWidth={1.5} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-4 mt-4 justify-center">
                {[
                  { label: "BTC / Oro", color: COLORS.amber },
                  { label: "Oro / Plata", color: COLORS.gold },
                  { label: "BTC / S&P 500", color: COLORS.cyan },
                  { label: "S&P 500 / MSCI", color: COLORS.blue },
                  { label: "BTC / ETH", color: COLORS.purple },
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

      {/* ========== DOMINANCE: Macro Market Cap Share ========== */}
      <ChartSection
        title="Dominancia Macro — Peso de cada asset class"
        subtitle="Market cap de cada clase de activo como % del total (Oro + Plata + Equities + Real Estate + Bonos + Crypto). Muestra cómo migra el capital entre clases."
        delay={3}
      >
        <div className="h-[280px] sm:h-[360px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredDominance} margin={{ top: 5, right: 10, left: 10, bottom: 5 }} stackOffset="expand">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" ticks={xTicks} tickFormatter={formatDate} tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`} />
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
                            {(entry.value as number * 100).toFixed(1)}%
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
              <Area type="monotone" dataKey="cryptoDom" name="Crypto" stackId="1" stroke="none" fill={COLORS.amber} fillOpacity={0.8} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-wrap gap-4 mt-4 justify-center">
          {[
            { label: "Crypto", color: COLORS.amber },
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
        {filteredDominance.length > 0 && (() => {
          const latest = filteredDominance[filteredDominance.length - 1];
          const items = [
            { label: "Real Estate", value: latest.realEstateDom },
            { label: "Bonos", value: latest.bondsDom },
            { label: "Equities", value: latest.equitiesDom },
            { label: "Oro", value: latest.goldDom },
            { label: "Crypto", value: latest.cryptoDom },
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

      {/* ========== STOCK DOMINANCE: Top 50 ========== */}
      <div className="space-y-4">
        <ChartSection
          title="Dominancia Acciones — Top 50 por Market Cap"
          subtitle="¿Quién gana terreno? Market cap de cada acción como % del total top-50. Detectá qué empresas están acumulando capital relativo."
          delay={4}
        >
          {/* View toggle */}
          <div className="flex flex-wrap gap-1 p-1 rounded-lg mb-4" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
            {([
              { key: "top10" as const, label: "Top 10 Chart" },
              { key: "gainers" as const, label: "Gainers / Losers" },
              { key: "sectors" as const, label: "Por Sector" },
            ]).map((v) => (
              <button
                key={v.key}
                onClick={() => setStockView(v.key)}
                className="px-2.5 sm:px-3 py-1.5 rounded-md text-[9px] sm:text-[10px] tracking-wider uppercase transition-all"
                style={{
                  background: stockView === v.key ? "var(--accent-green-bg-active)" : "transparent",
                  color: stockView === v.key ? "var(--accent-green)" : "var(--text-muted)",
                  border: stockView === v.key ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
                }}
              >
                {v.label}
              </button>
            ))}
          </div>

          {stockView === "top10" && filteredStockDom.length > 0 && (
            <>
              <div className="h-[300px] sm:h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={filteredStockDom} margin={{ top: 5, right: 10, left: 10, bottom: 5 }} stackOffset="expand">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" ticks={stockXTicks} tickFormatter={formatDate} tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`} />
                    <Tooltip
                      content={({ active, payload, label }: any) => {
                        if (!active || !payload) return null;
                        return (
                          <div className="rounded-lg px-4 py-3 text-xs max-h-[300px] overflow-y-auto" style={{ background: "var(--bg-tooltip)", border: "1px solid var(--border)", backdropFilter: "blur(10px)" }}>
                            <p className="mb-2 font-medium" style={{ color: "var(--text-secondary)" }}>{label}</p>
                            {payload.slice().reverse().map((entry: any, i: number) => (
                              <div key={i} className="flex items-center gap-2 py-0.5">
                                <div className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
                                <span style={{ color: "var(--text-muted)" }}>{entry.name}:</span>
                                <span className="font-medium tabular-nums" style={{ color: entry.color }}>
                                  {(entry.value as number * 100).toFixed(1)}%
                                </span>
                              </div>
                            ))}
                          </div>
                        );
                      }}
                    />
                    {TOP_STOCKS.slice(0, 10).map((stock) => (
                      <Area
                        key={stock.ticker}
                        type="monotone"
                        dataKey={stock.ticker}
                        name={stock.name}
                        stackId="1"
                        stroke="none"
                        fill={stock.color}
                        fillOpacity={0.8}
                      />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-3 mt-4 justify-center">
                {TOP_STOCKS.slice(0, 10).map((stock) => (
                  <div key={stock.ticker} className="flex items-center gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-sm" style={{ background: stock.color }} />
                    <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{stock.ticker}</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {stockView === "gainers" && stockChanges.length > 0 && (
            <div className="space-y-4">
              {/* Gainers */}
              <div>
                <h4 className="text-[10px] tracking-[0.2em] uppercase mb-3 flex items-center gap-2" style={{ color: "var(--accent-green)" }}>
                  <span>↗</span> Ganando Terreno
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {stockChanges.filter((s) => s.changePp > 0).slice(0, 10).map((stock) => (
                    <div key={stock.ticker} className="flex items-center gap-3 py-2 px-3 rounded-lg" style={{ background: "var(--controls-bg)" }}>
                      <div className="w-2 h-2 rounded-full shrink-0" style={{ background: stock.color }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-medium" style={{ color: "var(--text-primary)" }}>{stock.ticker}</span>
                          <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>{stock.name}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-[11px] font-medium tabular-nums" style={{ color: "var(--accent-green)" }}>
                          +{stock.changePp.toFixed(2)}pp
                        </span>
                        <span className="text-[9px] tabular-nums ml-1.5" style={{ color: "var(--text-muted)" }}>
                          {stock.currentDom.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {/* Losers */}
              <div>
                <h4 className="text-[10px] tracking-[0.2em] uppercase mb-3 flex items-center gap-2" style={{ color: "var(--accent-red)" }}>
                  <span>↘</span> Perdiendo Terreno
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {stockChanges.filter((s) => s.changePp < 0).slice(-10).reverse().map((stock) => (
                    <div key={stock.ticker} className="flex items-center gap-3 py-2 px-3 rounded-lg" style={{ background: "var(--controls-bg)" }}>
                      <div className="w-2 h-2 rounded-full shrink-0" style={{ background: stock.color }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] font-medium" style={{ color: "var(--text-primary)" }}>{stock.ticker}</span>
                          <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>{stock.name}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-[11px] font-medium tabular-nums" style={{ color: "var(--accent-red)" }}>
                          {stock.changePp.toFixed(2)}pp
                        </span>
                        <span className="text-[9px] tabular-nums ml-1.5" style={{ color: "var(--text-muted)" }}>
                          {stock.currentDom.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {stockView === "sectors" && sectorDom.length > 0 && (
            <div className="space-y-4">
              <div className="h-[250px] sm:h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={sectorDom} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis
                      type="number"
                      tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v: number) => `${v.toFixed(0)}%`}
                    />
                    <YAxis
                      type="category"
                      dataKey="sector"
                      tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      width={70}
                    />
                    <Tooltip
                      content={({ active, payload }: any) => {
                        if (!active || !payload || !payload[0]) return null;
                        const d = payload[0].payload;
                        return (
                          <div className="rounded-lg px-4 py-3 text-xs" style={{ background: "var(--bg-tooltip)", border: "1px solid var(--border)", backdropFilter: "blur(10px)" }}>
                            <p className="font-medium mb-1" style={{ color: "var(--text-primary)" }}>{d.sector}</p>
                            <p style={{ color: "var(--text-muted)" }}>Actual: <span className="tabular-nums" style={{ color: "var(--accent-cyan)" }}>{d.currentDom.toFixed(1)}%</span></p>
                            <p style={{ color: "var(--text-muted)" }}>Cambio: <span className="tabular-nums" style={{ color: d.changePp >= 0 ? "var(--accent-green)" : "var(--accent-red)" }}>{d.changePp >= 0 ? "+" : ""}{d.changePp.toFixed(2)}pp</span></p>
                          </div>
                        );
                      }}
                    />
                    <Bar dataKey="currentDom" radius={[0, 4, 4, 0]}>
                      {sectorDom.map((entry, i) => (
                        <Cell key={i} fill={entry.changePp >= 0 ? COLORS.green : COLORS.red} fillOpacity={0.7} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Sector change table */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {sectorDom.map((s) => (
                  <div key={s.sector} className="text-center py-2 px-2 rounded-lg" style={{ background: "var(--controls-bg)" }}>
                    <p className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{s.sector}</p>
                    <p className="text-sm font-medium tabular-nums" style={{ color: "var(--text-primary)" }}>{s.currentDom.toFixed(1)}%</p>
                    <p className="text-[10px] tabular-nums" style={{ color: s.changePp >= 0 ? "var(--accent-green)" : "var(--accent-red)" }}>
                      {s.changePp >= 0 ? "+" : ""}{s.changePp.toFixed(2)}pp
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </ChartSection>

        {/* Full stocks table */}
        <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6 md:p-8 fade-in-up fade-in-up-4">
          <div className="mb-4 sm:mb-5">
            <h2 className="mb-2">
              <span className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
                Top 50 Acciones
              </span>
              <span className="font-serif italic text-sm sm:text-base sm:ml-2" style={{ color: "var(--text-secondary)", opacity: 0.7 }}>
                — Dominancia por Market Cap
              </span>
            </h2>
            <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
              % del market cap total de las top 50. Cambio en puntos porcentuales vs. inicio del período seleccionado.
            </p>
          </div>
          <div className="divider-gradient mb-5" />
          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full text-[10px] sm:text-[11px]">
              <thead className="sticky top-0" style={{ background: "var(--bg-card)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>#</th>
                  <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Ticker</th>
                  <th className="text-left py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Nombre</th>
                  <th className="text-left py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Sector</th>
                  <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Dom %</th>
                  <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Cambio</th>
                </tr>
              </thead>
              <tbody>
                {stockChanges.map((stock, i) => (
                  <tr key={stock.ticker} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="py-2 px-2 tabular-nums" style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                    <td className="py-2 px-2">
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full shrink-0" style={{ background: stock.color }} />
                        <span className="font-medium" style={{ color: "var(--text-primary)" }}>{stock.ticker}</span>
                      </div>
                    </td>
                    <td className="py-2 px-2 hidden sm:table-cell" style={{ color: "var(--text-secondary)" }}>{stock.name}</td>
                    <td className="py-2 px-2 hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>{stock.sector}</td>
                    <td className="py-2 px-2 text-right tabular-nums" style={{ color: "var(--text-primary)" }}>{stock.currentDom.toFixed(2)}%</td>
                    <td className="py-2 px-2 text-right">
                      <span
                        className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                        style={{
                          color: stock.changePp > 0 ? "var(--accent-green)" : stock.changePp < 0 ? "var(--accent-red)" : "var(--text-muted)",
                          background: stock.changePp > 0 ? "var(--accent-green-bg)" : stock.changePp < 0 ? "var(--accent-red-bg)" : "transparent",
                        }}
                      >
                        {stock.changePp >= 0 ? "+" : ""}{stock.changePp.toFixed(2)}pp
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ========== FULL SUMMARY TABLE ========== */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6 md:p-8 fade-in-up fade-in-up-4">
        <div className="mb-4 sm:mb-5">
          <h2 className="mb-2">
            <span className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
              Tabla de Pares
            </span>
            <span className="font-serif italic text-sm sm:text-base sm:ml-2" style={{ color: "var(--text-secondary)", opacity: 0.7 }}>
              — Todos los ratios por asset class
            </span>
          </h2>
          <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Ratio actual vs. media histórica. La desviación (σ) indica cuán lejos está de su promedio.
          </p>
        </div>
        <div className="divider-gradient mb-5" />

        <div className="overflow-x-auto">
          <table className="w-full text-[10px] sm:text-[11px]">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Clase</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Par</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Actual</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Media</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Desv.</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Señal</th>
              </tr>
            </thead>
            <tbody>
              {ASSET_CLASSES.map((cls) => {
                const classSums = getSummariesByClass(cls);
                return classSums.map((s, idx) => {
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
                      {idx === 0 ? (
                        <td className="py-2.5 px-2 text-[9px] tracking-wider uppercase align-top" rowSpan={classSums.length} style={{ color: "var(--accent-green)", borderRight: "1px solid var(--border-subtle)" }}>
                          {cls}
                        </td>
                      ) : null}
                      <td className="py-2.5 px-2 font-medium" style={{ color: "var(--text-primary)" }}>{s.pair}</td>
                      <td className="py-2.5 px-2 text-right tabular-nums" style={{ color: "var(--text-primary)" }}>{formatRatio(s.current)}</td>
                      <td className="py-2.5 px-2 text-right tabular-nums hidden sm:table-cell" style={{ color: "var(--text-secondary)" }}>{formatRatio(s.mean)}</td>
                      <td className="py-2.5 px-2 text-right">
                        <span className="tabular-nums px-1.5 py-0.5 rounded font-medium" style={{ color: signalColor, background: signalBg }}>
                          {s.zScore >= 0 ? "+" : ""}{s.zScore.toFixed(1)}σ
                        </span>
                      </td>
                      <td className="py-2.5 px-2 text-[9px] sm:text-[10px]" style={{ color: signalColor }}>{s.context}</td>
                    </tr>
                  );
                });
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
