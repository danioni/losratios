"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  ComposedChart,
  Line,
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import {
  summaries,
  rotationSignals,
  getFilteredData,
  formatRatio,
  PAIR_DEFS,
  ASSET_CLASSES,
  getSummariesByClass,
  computeRatioSMAs,
  computeBollingerBands,
  computeStockMomentum,
  generateNarrative,
  assetClassSignals,
  cryptoDominanceData,
  cryptoRotation,
  assetPerformance,
  assetProjections,
  SMA_LONG,
  SMA_SHORT,
  type ClassRatioDataPoint,
} from "@/lib/data";
import MetricCard from "./MetricCard";
import ChartSection from "./ChartSection";
import Semaforo from "./Semaforo";
import PerformanceTable from "./PerformanceTable";
import Projections from "./Projections";
import StockMomentum from "./StockMomentum";
import CryptoDominance from "./CryptoDominance";

type TimeRange = "1Y" | "3Y" | "5Y" | "MAX";

const MONTH_NAMES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

function formatDateLabel(dateStr: string): string {
  if (!dateStr || dateStr.length < 7) return dateStr;
  const [year, month] = dateStr.split("-");
  const m = parseInt(month, 10);
  return `${MONTH_NAMES[m - 1]} ${year}`;
}

function formatDateRange(startDate: string, endDate: string): string {
  return `${formatDateLabel(startDate)} → ${formatDateLabel(endDate)}`;
}

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
  const COLORS = useThemeColors();

  const classPairs = useMemo(() => PAIR_DEFS.filter((p) => p.assetClass === activeClass), [activeClass]);

  useEffect(() => {
    const first = PAIR_DEFS.find((p) => p.assetClass === activeClass);
    if (first) setActivePairKey(first.key);
  }, [activeClass]);

  const currentPairDef = useMemo(() => PAIR_DEFS.find((p) => p.key === activePairKey), [activePairKey]);

  const { filteredRatios, filteredDominance, filteredStockDom, filteredCryptoDom, xTicks, ratioDateRange, stockDateRange } = useMemo(() => {
    const { ratios: r, dominance: d, stockDom: sd, cryptoDom: cd } = getFilteredData(range);
    const dates = r.map((x) => x.date);
    const ticks = dates.length <= 24 ? dates.filter((_, i) => i % 3 === 0) : dates.filter((_, i) => i % 12 === 0);
    const ratioRange = r.length > 0 ? formatDateRange(r[0].date, r[r.length - 1].date) : "";
    const stockRange = sd.length > 0 ? formatDateRange(sd[0].date, sd[sd.length - 1].date) : "";
    return { filteredRatios: r, filteredDominance: d, filteredStockDom: sd, filteredCryptoDom: cd, xTicks: ticks, ratioDateRange: ratioRange, stockDateRange: stockRange };
  }, [range]);

  const stockXTicks = useMemo(() => {
    if (!filteredStockDom.length) return [];
    const dates = filteredStockDom.map((x) => x.date);
    return dates.length <= 24 ? dates.filter((_, i) => i % 3 === 0) : dates.filter((_, i) => i % 12 === 0);
  }, [filteredStockDom]);

  const cryptoXTicks = useMemo(() => {
    if (!filteredCryptoDom.length) return [];
    const dates = filteredCryptoDom.map((x) => x.date);
    return dates.length <= 24 ? dates.filter((_, i) => i % 3 === 0) : dates.filter((_, i) => i % 12 === 0);
  }, [filteredCryptoDom]);

  // Pair stats + Bollinger bands
  const { pairStats, bollingerChartData } = useMemo(() => {
    const key = activePairKey as keyof ClassRatioDataPoint;
    const values = filteredRatios.map((d) => d[key] as number);
    const dates = filteredRatios.map((d) => d.date);

    const windowSize = Math.min(SMA_LONG, values.length);
    const windowValues = values.slice(-windowSize);
    const mean = windowValues.reduce((s, v) => s + v, 0) / windowValues.length;
    const variance = windowValues.reduce((s, v) => s + (v - mean) ** 2, 0) / windowValues.length;
    const stdDev = Math.sqrt(variance);
    const current = values[values.length - 1];
    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;

    // SMAs
    const { sma50, sma200 } = computeRatioSMAs(filteredRatios, key);
    // Bollinger bands (20-period)
    const bb = computeBollingerBands(values, dates, Math.min(20, values.length));

    const chartData = filteredRatios.map((d, i) => ({
      date: d.date,
      [activePairKey]: d[key],
      sma50: sma50[i],
      sma200: sma200[i],
      bbUpper2: bb[i]?.upper2 ?? null,
      bbLower2: bb[i]?.lower2 ?? null,
      bbUpper1: bb[i]?.upper1 ?? null,
      bbLower1: bb[i]?.lower1 ?? null,
      bbSma: bb[i]?.sma ?? null,
    }));

    return {
      pairStats: { mean, stdDev, current, zScore },
      bollingerChartData: chartData,
    };
  }, [filteredRatios, activePairKey]);

  const formatDate = (d: string) => d.length <= 4 ? d : d.split("-")[0];

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

  // Stock momentum
  const stockMomentum = useMemo(() => computeStockMomentum(filteredStockDom), [filteredStockDom]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-6 sm:space-y-8 relative z-10">
      {/* 1. Thesis banner */}
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

      {/* 2. Rotation Signals */}
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

      {/* 3. Semáforo */}
      <Semaforo signals={assetClassSignals} colors={COLORS} />

      {/* 4. Controls */}
      <div className="flex flex-wrap items-center gap-3 fade-in-up fade-in-up-2">
        <TimeRangeSelector range={range} onChange={setRange} />
        <span className="text-[10px] tabular-nums tracking-wider" style={{ color: "var(--text-muted)" }}>
          {ratioDateRange}
        </span>
      </div>

      {/* 5. Key metrics */}
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

      {/* 6. Performance Histórica */}
      <PerformanceTable data={assetPerformance} colors={COLORS} />

      {/* 7. Proyecciones Multi-Factor */}
      <Projections projections={assetProjections} colors={COLORS} />

      {/* 8. Stock Momentum (replaces old stock dominance) */}
      <StockMomentum
        momentum={stockMomentum}
        stockDom={filteredStockDom}
        stockDateRange={stockDateRange}
        stockXTicks={stockXTicks}
        colors={COLORS}
      />

      {/* 9. Crypto Dominance */}
      <CryptoDominance
        data={filteredCryptoDom}
        rotation={cryptoRotation}
        xTicks={cryptoXTicks}
        colors={COLORS}
      />

      {/* 10. Asset Class Ratios with Bollinger Bands */}
      <div className="space-y-4">
        <h3 className="font-serif text-base sm:text-lg" style={{ color: "var(--text-primary)" }}>
          Ratios por Asset Class
        </h3>
        <ClassTabSelector activeClass={activeClass} onChange={setActiveClass} />
        <PairSelector pairs={classPairs} activePair={activePairKey} onChange={setActivePairKey} />

        {currentPairDef && (
          <ChartSection
            title={`${currentPairDef.name} — ${currentPairDef.description}`}
            subtitle={`${ratioDateRange} · Actual: ${formatRatio(pairStats.current)} · SMA ${SMA_LONG}: ${formatRatio(pairStats.mean)} · Desv. vs SMA: ${pairStats.zScore >= 0 ? "+" : ""}${pairStats.zScore.toFixed(1)}σ`}
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

            {/* Ratio chart with Bollinger bands */}
            <div className="h-[280px] sm:h-[360px]">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={bollingerChartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
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
                  {/* Bollinger bands ±2σ */}
                  <Line type="monotone" dataKey="bbUpper2" name="BB +2σ" stroke={COLORS.red} strokeWidth={0.8} strokeDasharray="3 4" dot={false} connectNulls strokeOpacity={0.4} />
                  <Line type="monotone" dataKey="bbLower2" name="BB -2σ" stroke={COLORS.green} strokeWidth={0.8} strokeDasharray="3 4" dot={false} connectNulls strokeOpacity={0.4} />
                  {/* Bollinger bands ±1σ */}
                  <Line type="monotone" dataKey="bbUpper1" name="BB +1σ" stroke={COLORS.red} strokeWidth={0.5} strokeDasharray="2 4" dot={false} connectNulls strokeOpacity={0.25} />
                  <Line type="monotone" dataKey="bbLower1" name="BB -1σ" stroke={COLORS.green} strokeWidth={0.5} strokeDasharray="2 4" dot={false} connectNulls strokeOpacity={0.25} />
                  {/* SMA lines */}
                  <Line
                    type="monotone"
                    dataKey="sma50"
                    name={`SMA ${SMA_SHORT}`}
                    stroke={COLORS.amber}
                    strokeWidth={1.5}
                    strokeDasharray="4 3"
                    dot={false}
                    connectNulls
                  />
                  <Line
                    type="monotone"
                    dataKey="sma200"
                    name={`SMA ${SMA_LONG}`}
                    stroke={COLORS.muted}
                    strokeWidth={1.5}
                    dot={false}
                    connectNulls
                  />
                  {/* Main ratio line on top */}
                  <Line
                    type="monotone"
                    dataKey={activePairKey}
                    name={currentPairDef.pair}
                    stroke={pairColor}
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap gap-4 mt-3 justify-center">
              <div className="flex items-center gap-1.5">
                <div className="w-4 h-0.5 rounded" style={{ background: pairColor }} />
                <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Ratio</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-4 h-0.5 rounded" style={{ background: COLORS.amber, opacity: 0.8 }} />
                <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>SMA {SMA_SHORT}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-4 h-0.5 rounded" style={{ background: COLORS.muted, opacity: 0.8 }} />
                <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>SMA {SMA_LONG}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-4 h-px rounded" style={{ background: COLORS.red, opacity: 0.4 }} />
                <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>BB ±1σ/±2σ</span>
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
                  <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>SMA {SMA_LONG}</th>
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

      {/* 11. Panorama General z-score overlay */}
      <ChartSection
        title="Panorama General — Z-Score vs SMA"
        subtitle={`${ratioDateRange} · Z-score rolling (ventana 36 meses). Si BTC/Oro está caro, Cobre/Oro debería compensar. Pares cruzados para detectar rotaciones reales.`}
        delay={3}
      >
        {(() => {
          const ZSCORE_WINDOW = 36;
          const overlayKeys: { key: keyof ClassRatioDataPoint; label: string; color: string }[] = [
            { key: "btcGold", label: "BTC / Oro", color: COLORS.amber },
            { key: "copperGold", label: "Cobre / Oro", color: COLORS.red },
            { key: "sp500Nasdaq", label: "S&P / Nasdaq", color: COLORS.blue },
            { key: "goldSilver", label: "Oro / Plata", color: COLORS.gold },
            { key: "ethSol", label: "ETH / SOL", color: COLORS.purple },
            { key: "btcSp500", label: "BTC / S&P 500", color: COLORS.cyan },
          ];

          const windowSize = Math.min(ZSCORE_WINDOW, filteredRatios.length);

          const zScoreData = filteredRatios.map((d, i) => {
            const point: Record<string, number | string | null> = { date: d.date };
            for (const { key } of overlayKeys) {
              if (i < windowSize - 1) {
                point[key] = null;
              } else {
                const w: number[] = [];
                for (let j = i - windowSize + 1; j <= i; j++) {
                  w.push(filteredRatios[j][key] as number);
                }
                const mean = w.reduce((s, v) => s + v, 0) / w.length;
                const variance = w.reduce((s, v) => s + (v - mean) ** 2, 0) / w.length;
                const sd = Math.sqrt(variance);
                const current = d[key] as number;
                point[key] = sd > 0 ? (current - mean) / sd : 0;
              }
            }
            return point;
          });

          return (
            <>
              <div className="h-[280px] sm:h-[360px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={zScoreData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" ticks={xTicks} tickFormatter={formatDate} tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis
                      domain={[-3, 3]}
                      tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v: number) => `${v > 0 ? "+" : ""}${v.toFixed(0)}σ`}
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
                                <span className="font-medium tabular-nums" style={{ color: entry.value > 1 ? "var(--accent-red)" : entry.value < -1 ? "var(--accent-green)" : entry.color }}>
                                  {entry.value != null ? `${entry.value >= 0 ? "+" : ""}${entry.value.toFixed(2)}σ` : "—"}
                                </span>
                              </div>
                            ))}
                          </div>
                        );
                      }}
                    />
                    <ReferenceLine y={0} stroke={COLORS.muted} strokeDasharray="6 4" />
                    <ReferenceLine y={2} stroke={COLORS.red} strokeDasharray="3 6" strokeOpacity={0.3} />
                    <ReferenceLine y={-2} stroke={COLORS.green} strokeDasharray="3 6" strokeOpacity={0.3} />
                    <ReferenceLine y={1} stroke={COLORS.red} strokeDasharray="3 6" strokeOpacity={0.15} />
                    <ReferenceLine y={-1} stroke={COLORS.green} strokeDasharray="3 6" strokeOpacity={0.15} />
                    {overlayKeys.map(({ key, label, color }) => (
                      <Line key={key} type="monotone" dataKey={key} name={label} stroke={color} strokeWidth={1.5} dot={false} connectNulls />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-wrap gap-4 mt-4 justify-center">
                {overlayKeys.map((item) => (
                  <div key={item.label} className="flex items-center gap-1.5">
                    <div className="w-2.5 h-0.5 rounded" style={{ background: item.color }} />
                    <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{item.label}</span>
                  </div>
                ))}
              </div>
              <div className="flex flex-wrap gap-6 mt-2 justify-center">
                <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--accent-green)", opacity: 0.7 }}>↓ bajo 0 = numerador barato vs denominador</span>
                <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--accent-red)", opacity: 0.7 }}>↑ sobre 0 = numerador caro vs denominador</span>
              </div>
            </>
          );
        })()}
      </ChartSection>

      {/* 12. Macro Dominance */}
      <ChartSection
        title="Dominancia Macro — Peso de cada asset class"
        subtitle={`${ratioDateRange} · Market cap de cada clase de activo como % del total (Oro + Plata + Equities + Real Estate + Bonos + Crypto). Muestra cómo migra el capital entre clases.`}
        delay={3}
      >
        <div className="h-[280px] sm:h-[360px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredDominance} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
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

      {/* 13. Full Summary Table with narratives */}
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
            Ratio actual vs. media móvil (SMA {SMA_LONG}). La desviación (σ) indica cuán lejos está de su tendencia reciente.
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
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>SMA {SMA_LONG}</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Desv.</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Narrativa</th>
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
                  const narrative = generateNarrative(s.pair, s.zScore);

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
                      <td className="py-2.5 px-2 text-[9px] sm:text-[10px] max-w-[200px]" style={{ color: signalColor }}>{narrative}</td>
                    </tr>
                  );
                });
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 14. Closing */}
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
