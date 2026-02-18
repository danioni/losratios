"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  summaries as fallbackSummaries,
  rotationSignals as fallbackRotationSignals,
  getFilteredData,
  formatRatio,
  PAIR_DEFS,
  computeRatioSMAs,
  computeBollingerBands,
  assetPerformance as fallbackAssetPerformance,
  assetData as fallbackAssetData,
  SMA_LONG,
  SMA_SHORT,
  generateNarrative,
  type ClassRatioDataPoint,
  type ComputedMarketData,
} from "@/lib/data";
import MetricCard from "./MetricCard";
import ChartSection from "./ChartSection";
import PerformanceTable from "./PerformanceTable";

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

function RatioChart({
  pairDef,
  filteredRatios,
  xTicks,
  ratioDateRange,
  COLORS,
}: {
  pairDef: typeof PAIR_DEFS[number];
  filteredRatios: ClassRatioDataPoint[];
  xTicks: string[];
  ratioDateRange: string;
  COLORS: typeof DEFAULT_COLORS;
}) {
  const { pairStats, bollingerChartData } = useMemo(() => {
    const key = pairDef.key as keyof ClassRatioDataPoint;
    const values = filteredRatios.map((d) => d[key] as number);
    const dates = filteredRatios.map((d) => d.date);

    const windowSize = Math.min(SMA_LONG, values.length);
    const windowValues = values.slice(-windowSize);
    const mean = windowValues.reduce((s, v) => s + v, 0) / windowValues.length;
    const variance = windowValues.reduce((s, v) => s + (v - mean) ** 2, 0) / windowValues.length;
    const stdDev = Math.sqrt(variance);
    const current = values[values.length - 1];
    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;

    const { sma50, sma200 } = computeRatioSMAs(filteredRatios, key);
    const bb = computeBollingerBands(values, dates, Math.min(20, values.length));

    const chartData = filteredRatios.map((d, i) => ({
      date: d.date,
      [pairDef.key]: d[key],
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
  }, [filteredRatios, pairDef.key]);

  const formatDate = (d: string) => d.length <= 4 ? d : d.split("-")[0];
  const getColorValue = (colorKey: string): string => {
    return COLORS[colorKey as keyof typeof COLORS] || COLORS.cyan;
  };
  const pairColor = getColorValue(pairDef.color);
  const narrative = generateNarrative(pairDef.pair, pairStats.zScore);

  // Human-readable z-score explanation
  const absZ = Math.abs(pairStats.zScore);
  const percentile = Math.round((1 - 2 * (1 - 0.5 * (1 + Math.min(absZ, 3) * (0.3275911 * Math.exp(-0.5 * absZ * absZ))))) * 100);
  const zExplanation = pairStats.zScore > 0.5
    ? `${pairDef.pair.split(" / ")[0]} está más caro vs ${pairDef.pair.split(" / ")[1]} de lo que ha estado el ~${Math.min(percentile, 99)}% del tiempo`
    : pairStats.zScore < -0.5
    ? `${pairDef.pair.split(" / ")[0]} está más barato vs ${pairDef.pair.split(" / ")[1]} de lo que ha estado el ~${Math.min(percentile, 99)}% del tiempo`
    : `${pairDef.pair.split(" / ")[0]} y ${pairDef.pair.split(" / ")[1]} en equilibrio relativo`;

  return (
    <ChartSection
      title={`${pairDef.name}`}
      subtitle={`${ratioDateRange} · Actual: ${formatRatio(pairStats.current)} · SMA ${SMA_LONG}: ${formatRatio(pairStats.mean)} · Desv: ${pairStats.zScore >= 0 ? "+" : ""}${pairStats.zScore.toFixed(1)}σ`}
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

      {/* Z-score explanation in plain language */}
      <p className="text-[10px] sm:text-[11px] mb-4 leading-relaxed" style={{ color: pairStats.zScore > 1 ? "var(--accent-red)" : pairStats.zScore < -1 ? "var(--accent-green)" : "var(--text-muted)" }}>
        {pairStats.zScore >= 0 ? "+" : ""}{pairStats.zScore.toFixed(1)}σ = {zExplanation}
      </p>

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
            <Line type="monotone" dataKey="sma50" name={`SMA ${SMA_SHORT}`} stroke={COLORS.amber} strokeWidth={1.5} strokeDasharray="4 3" dot={false} connectNulls />
            <Line type="monotone" dataKey="sma200" name={`SMA ${SMA_LONG}`} stroke={COLORS.muted} strokeWidth={1.5} dot={false} connectNulls />
            {/* Main ratio line on top */}
            <Line type="monotone" dataKey={pairDef.key} name={pairDef.pair} stroke={pairColor} strokeWidth={2} dot={false} connectNulls />
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
      {/* Narrative */}
      <p className="text-[10px] sm:text-[11px] mt-4 leading-relaxed" style={{ color: "var(--text-secondary)" }}>
        {narrative}
      </p>
    </ChartSection>
  );
}

export default function Dashboard() {
  const [range, setRange] = useState<TimeRange>("MAX");
  const [liveData, setLiveData] = useState<ComputedMarketData | null>(null);
  const [dataSource, setDataSource] = useState<"mock" | "live">("mock");
  const COLORS = useThemeColors();

  // Fetch live market data on mount
  useEffect(() => {
    let cancelled = false;
    fetch("/api/market-data")
      .then((res) => {
        if (!res.ok) throw new Error(`API ${res.status}`);
        const ct = res.headers.get("content-type") ?? "";
        if (!ct.includes("application/json")) throw new Error("Not JSON");
        return res.json();
      })
      .then((data: ComputedMarketData) => {
        if (!cancelled && data?.assetData?.length > 0 && !(data as any).error) {
          setLiveData(data);
          setDataSource("live");
        }
      })
      .catch(() => {
        // Silently fall back to mock data
      });
    return () => { cancelled = true; };
  }, []);

  // Resolve data sources: live if available, else fallback
  const summaries = liveData?.summaries ?? fallbackSummaries;
  const currentAssetPerformance = liveData?.assetPerformance ?? fallbackAssetPerformance;
  const sourceAssets = liveData?.assetData ?? fallbackAssetData;

  const { filteredRatios, xTicks, ratioDateRange } = useMemo(() => {
    const { ratios: r } = getFilteredData(range, sourceAssets);
    const dates = r.map((x) => x.date);
    const ticks = dates.length <= 24 ? dates.filter((_, i) => i % 3 === 0) : dates.filter((_, i) => i % 12 === 0);
    const ratioRange = r.length > 0 ? formatDateRange(r[0].date, r[r.length - 1].date) : "";
    return { filteredRatios: r, xTicks: ticks, ratioDateRange: ratioRange };
  }, [range, sourceAssets]);

  const keyMetrics = useMemo(() => {
    return [
      summaries.find((s) => s.pair === "BTC / Oro"),
      summaries.find((s) => s.pair === "Oro / S&P 500"),
      summaries.find((s) => s.pair === "BTC / S&P 500"),
      summaries.find((s) => s.pair === "Nasdaq / S&P 500"),
    ].filter(Boolean) as typeof summaries;
  }, [summaries]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-8 sm:space-y-12 relative z-10">
      {/* ═══════════════════════════════════════════════════════ */}
      {/* HERO — Approved copy from CLAUDE.md                    */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="text-center space-y-5 py-8 sm:py-12 fade-in-up fade-in-up-1">
        <h2 className="font-serif text-2xl sm:text-4xl md:text-5xl tracking-wide leading-tight" style={{ color: "var(--text-primary)" }}>
          Deja de medir en dólares.
        </h2>
        <p className="font-serif italic text-base sm:text-xl md:text-2xl" style={{ color: "var(--accent-green)" }}>
          El dólar es la vara que se encoge.
        </p>
        <div className="max-w-2xl mx-auto space-y-3">
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            La única forma de saber si un activo está caro o barato es compararlo con otro activo. No con dinero fiat. Aquí medimos activos contra activos.
          </p>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Imagina que quieres saber si una persona es alta. Pero tu metro se encoge 7% por año.
            Mañana medirías a la misma persona y dirías que creció. No creció. Tu metro se encogió.
            Así funciona medir activos en dólares. El precio &ldquo;sube&rdquo; — pero ¿el activo vale más, o el dólar vale menos?
          </p>
          <p className="text-[11px] sm:text-xs font-medium" style={{ color: "var(--accent-green)" }}>
            La respuesta está en los ratios.
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3 fade-in-up fade-in-up-2">
        <TimeRangeSelector range={range} onChange={setRange} />
        <span className="text-[10px] tabular-nums tracking-wider" style={{ color: "var(--text-muted)" }}>
          {ratioDateRange}
        </span>
        <span className="text-[10px] tabular-nums tracking-wider ml-auto" style={{ color: "var(--text-muted)" }}>
          {dataSource === "live" ? "Datos en vivo" : "Datos simulados"}
        </span>
      </div>

      {/* Key metrics — 4 cards */}
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

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 1 — BTC/Oro: EL RATIO CENTRAL                 */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            BTC ÷ Oro — El ratio central
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            ¿Cuánto market share le está sacando Bitcoin al oro como reserva de valor? Este es el ratio más importante del sitio. Cuando está bajo históricamente, el mercado duda del argumento del &ldquo;digital gold&rdquo;. Cuando está alto, el argumento está ganando.
          </p>
        </div>
        <RatioChart pairDef={PAIR_DEFS[0]} filteredRatios={filteredRatios} xTicks={xTicks} ratioDateRange={ratioDateRange} COLORS={COLORS} />
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 2 — El espectro monetario                      */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            Dentro de los ganadores: ¿hard money o capital productivo?
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Oro/S&P 500 y BTC/S&P 500 juntos cuentan una historia: cuánto está apostando el mercado a la narrativa de escasez pura (oro y Bitcoin) vs la narrativa de crecimiento productivo (acciones). No es &ldquo;comprá BTC&rdquo; o &ldquo;comprá acciones&rdquo;. Es cuánto de cada uno, y cuándo cambia el peso.
          </p>
        </div>
        <RatioChart pairDef={PAIR_DEFS[1]} filteredRatios={filteredRatios} xTicks={xTicks} ratioDateRange={ratioDateRange} COLORS={COLORS} />
        <RatioChart pairDef={PAIR_DEFS[2]} filteredRatios={filteredRatios} xTicks={xTicks} ratioDateRange={ratioDateRange} COLORS={COLORS} />
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 3 — Growth vs Quality                          */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            Growth vs Quality: el ciclo dentro del ciclo
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Dentro del capital productivo, el Nasdaq (growth/tech) vs el S&P 500 (quality/broad market) marca otro ciclo. Cuando el Nasdaq está muy caro relativo al S&P, los quality compounders como Visa, Mastercard, Costco y Berkshire están relativamente baratos.
          </p>
        </div>
        <RatioChart pairDef={PAIR_DEFS[3]} filteredRatios={filteredRatios} xTicks={xTicks} ratioDateRange={ratioDateRange} COLORS={COLORS} />
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 4 — La escasez medida                          */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            ¿Cuánto paga el mercado por escasez?
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Oro/Plata mide el apetito por escasez pura (oro) vs escasez con utilidad industrial (plata). Cuando está por encima de 80, la plata históricamente está barata relativa al oro. Conecta con el argumento del Numerador: cuanto más inelástica la oferta, más captura el activo del debasement.
          </p>
        </div>
        <RatioChart pairDef={PAIR_DEFS[4]} filteredRatios={filteredRatios} xTicks={xTicks} ratioDateRange={ratioDateRange} COLORS={COLORS} />
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 5 — Performance Table (Universe of Winners)    */}
      {/* ═══════════════════════════════════════════════════════ */}
      <PerformanceTable data={currentAssetPerformance} colors={COLORS} />

      {/* ═══════════════════════════════════════════════════════ */}
      {/* DISCLAIMER NARRATIVO                                   */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="py-8 space-y-4 fade-in-up fade-in-up-5">
        <div className="divider-gradient max-w-xs mx-auto" />
        <div className="max-w-2xl mx-auto text-center space-y-3">
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Los ratios no predicen. Documentan desequilibrios históricos que tienden a revertir. Cuándo revierten — eso nadie lo sabe. Esto no es asesoría financiera. Es un marco analítico.
          </p>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CTA FINAL                                              */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="text-center py-8 space-y-6 fade-in-up fade-in-up-5">
        <div className="space-y-2">
          <p className="font-serif text-sm sm:text-base" style={{ color: "var(--text-primary)" }}>
            Los precios en fiat son ruido. Los ratios son señal.
          </p>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Ya tenés el marco completo:
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-4 text-[10px] sm:text-[11px] tracking-wider">
          <a href="https://eldenominador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--accent-amber)" }}>
            El Denominador →
          </a>
          <span style={{ color: "var(--text-muted)" }}>por qué el dinero se encoge</span>
        </div>
        <div className="flex flex-wrap justify-center gap-4 text-[10px] sm:text-[11px] tracking-wider">
          <a href="https://elnumerador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--accent-cyan)" }}>
            El Numerador →
          </a>
          <span style={{ color: "var(--text-muted)" }}>por qué los activos se multiplican</span>
        </div>
        <div className="flex flex-wrap justify-center gap-4 text-[10px] sm:text-[11px] tracking-wider">
          <a href="https://losratios.com" className="font-medium" style={{ color: "var(--accent-green)" }}>
            Los Ratios
          </a>
          <span style={{ color: "var(--text-muted)" }}>cómo comparar sin la vara que se encoge</span>
        </div>
        <div className="pt-4">
          <a
            href="https://elfaro.capital"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-[11px] sm:text-xs tracking-wider uppercase font-medium transition-all hover:opacity-90"
            style={{
              background: "var(--accent-green-bg-active)",
              color: "var(--accent-green)",
              border: "1px solid var(--accent-green-border-active)",
              boxShadow: "var(--accent-green-glow)",
            }}
          >
            ¿Qué hacer con eso? → El Faro Capital
          </a>
        </div>
        <div className="space-y-1 pt-2">
          <p className="text-[10px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
            {dataSource === "live" ? "Datos en vivo · Actualización cada hora" : "Datos simulados · Cargando datos reales..."}
          </p>
          <p className="text-[9px]" style={{ color: "var(--text-muted)" }}>
            CoinGecko · FRED · Yahoo Finance
          </p>
        </div>
      </div>
    </div>
  );
}
