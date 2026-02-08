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
import { ratios, summaries, rotationSignals, getFilteredData, formatRatio, type RatioDataPoint } from "@/lib/data";
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

// Custom tooltip
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
          <div
            className="w-2 h-2 rounded-full"
            style={{ background: entry.color }}
          />
          <span style={{ color: "var(--text-muted)" }}>{entry.name}:</span>
          <span className="font-medium tabular-nums" style={{ color: entry.color }}>
            {formatRatio(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

function TimeRangeSelector({
  range,
  onChange,
}: {
  range: TimeRange;
  onChange: (r: TimeRange) => void;
}) {
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

// Pair selector for cross-asset
type CrossPair = "btcGold" | "goldSilver" | "btcSp500" | "realEstateGold";

const CROSS_PAIR_CONFIG: Record<CrossPair, { label: string; description: string }> = {
  btcGold: { label: "BTC / Oro", description: "Reserva digital vs. reserva física" },
  goldSilver: { label: "Oro / Plata", description: "Ratio histórico. >80 = plata barata, <50 = plata cara" },
  btcSp500: { label: "BTC / S&P 500", description: "Escasez vs. equity tradicional" },
  realEstateGold: { label: "Real Estate / Oro", description: "Activo productivo vs. reserva pura" },
};

function PairSelector({ pair, onChange }: { pair: CrossPair; onChange: (p: CrossPair) => void }) {
  const pairs: CrossPair[] = ["btcGold", "goldSilver", "btcSp500", "realEstateGold"];
  return (
    <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {pairs.map((p) => (
        <button
          key={p}
          onClick={() => onChange(p)}
          className="px-2 sm:px-3 py-1.5 rounded-md text-[8px] sm:text-[10px] tracking-wider uppercase transition-all"
          style={{
            background: pair === p ? "var(--accent-green-bg-active)" : "transparent",
            color: pair === p ? "var(--accent-green)" : "var(--text-muted)",
            border: pair === p ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
          }}
        >
          {CROSS_PAIR_CONFIG[p].label}
        </button>
      ))}
    </div>
  );
}

// Denominator ratio selector
type DenomRatio = "btcM2" | "goldM2" | "silverM2" | "sp500M2" | "realEstateM2" | "teslaM2" | "msciWorldM2";

const DENOM_RATIO_CONFIG: Record<DenomRatio, { label: string; color: string }> = {
  btcM2: { label: "BTC", color: "amber" },
  goldM2: { label: "Oro", color: "gold" },
  silverM2: { label: "Plata", color: "muted" },
  sp500M2: { label: "S&P 500", color: "blue" },
  realEstateM2: { label: "Real Estate", color: "purple" },
  teslaM2: { label: "Tesla", color: "red" },
  msciWorldM2: { label: "MSCI World", color: "cyan" },
};

function DenomRatioSelector({ selected, onChange }: { selected: DenomRatio; onChange: (r: DenomRatio) => void }) {
  const options: DenomRatio[] = ["btcM2", "goldM2", "silverM2", "sp500M2", "realEstateM2", "teslaM2", "msciWorldM2"];
  return (
    <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className="px-2 sm:px-3 py-1.5 rounded-md text-[8px] sm:text-[10px] tracking-wider uppercase transition-all"
          style={{
            background: selected === opt ? "var(--accent-green-bg-active)" : "transparent",
            color: selected === opt ? "var(--accent-green)" : "var(--text-muted)",
            border: selected === opt ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
          }}
        >
          {DENOM_RATIO_CONFIG[opt].label}
        </button>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [range, setRange] = useState<TimeRange>("MAX");
  const [crossPair, setCrossPair] = useState<CrossPair>("btcGold");
  const [denomRatio, setDenomRatio] = useState<DenomRatio>("btcM2");
  const COLORS = useThemeColors();

  const filteredData = useMemo(() => {
    const { ratios: r } = getFilteredData(range);
    return r;
  }, [range]);

  // Compute mean line for current cross pair
  const crossMean = useMemo(() => {
    const values = filteredData.map((d) => d[crossPair] as number);
    return values.reduce((s, v) => s + v, 0) / values.length;
  }, [filteredData, crossPair]);

  // Compute mean for denominator ratio
  const denomMean = useMemo(() => {
    const values = filteredData.map((d) => d[denomRatio] as number);
    return values.reduce((s, v) => s + v, 0) / values.length;
  }, [filteredData, denomRatio]);

  // X-axis ticks
  const xTicks = useMemo(() => {
    const dates = filteredData.map((d) => d.date);
    if (dates.length <= 24) {
      return dates.filter((_, i) => i % 3 === 0);
    }
    return dates.filter((_, i) => i % 12 === 0);
  }, [filteredData]);

  // Format date for display
  const formatDate = (d: string) => {
    if (d.length <= 4) return d;
    const parts = d.split("-");
    return `${parts[0]}`;
  };

  // Key ratios for MetricCards
  const keyMetrics = useMemo(() => {
    return [
      summaries.find((s) => s.pair === "BTC / Oro")!,
      summaries.find((s) => s.pair === "Oro / Plata")!,
      summaries.find((s) => s.pair === "BTC / Denominador")!,
    ];
  }, []);

  const getColorValue = (colorKey: string): string => {
    return COLORS[colorKey as keyof typeof COLORS] || COLORS.green;
  };

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
          Cruzamos el numerador (oferta/escasez de activos) con el denominador (liquidez global)
          para encontrar activos sobrevendidos o sobrevalorados en términos reales,
          y detectar pares desalineados para rotación de capital.
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
          {rotationSignals.slice(0, 3).map((sig, i) => (
            <div
              key={i}
              className="signal-badge-gold"
            >
              <span
                className="text-[10px] sm:text-[11px] font-medium"
                style={{ color: sig.type === "rotate_from" ? "var(--accent-red)" : "var(--accent-green)" }}
              >
                {sig.type === "rotate_from" ? "↗" : "↙"} {sig.message}
              </span>
              <span
                className="text-[9px] tabular-nums ml-auto"
                style={{ color: "var(--text-muted)" }}
              >
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

      {/* ========== SECTION 1: Activo ÷ Denominador ========== */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <h3
            className="font-serif text-base sm:text-lg"
            style={{ color: "var(--text-primary)" }}
          >
            Activo ÷ Denominador
          </h3>
          <DenomRatioSelector selected={denomRatio} onChange={setDenomRatio} />
        </div>

        <ChartSection
          title={`${DENOM_RATIO_CONFIG[denomRatio].label} ÷ M2 Global — Precio real descontando expansión monetaria`}
          subtitle={`Si el activo sube 20% pero el denominador creció 25%, perdió valor en términos reales. La línea punteada es la media histórica.`}
          delay={3}
        >
          <div className="h-[250px] sm:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="denomGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={getColorValue(DENOM_RATIO_CONFIG[denomRatio].color)} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={getColorValue(DENOM_RATIO_CONFIG[denomRatio].color)} stopOpacity={0} />
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
                  y={denomMean}
                  stroke={COLORS.muted}
                  strokeDasharray="6 4"
                  label={{
                    value: `Media: ${formatRatio(denomMean)}`,
                    position: "insideTopRight",
                    fill: "var(--text-muted)",
                    fontSize: 9,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey={denomRatio}
                  name={`${DENOM_RATIO_CONFIG[denomRatio].label} ÷ M2`}
                  stroke={getColorValue(DENOM_RATIO_CONFIG[denomRatio].color)}
                  fill="url(#denomGrad)"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartSection>
      </div>

      {/* ========== SECTION 2: Cross-Asset Ratios ========== */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <h3
            className="font-serif text-base sm:text-lg"
            style={{ color: "var(--text-primary)" }}
          >
            Activo A ÷ Activo B
          </h3>
          <PairSelector pair={crossPair} onChange={setCrossPair} />
        </div>

        <ChartSection
          title={`${CROSS_PAIR_CONFIG[crossPair].label} — ${CROSS_PAIR_CONFIG[crossPair].description}`}
          subtitle="Ratios entre activos que eliminan el efecto del denominador. La línea punteada muestra la media histórica como ancla."
          delay={4}
        >
          <div className="h-[250px] sm:h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="crossGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.cyan} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={COLORS.cyan} stopOpacity={0} />
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
                  y={crossMean}
                  stroke={COLORS.muted}
                  strokeDasharray="6 4"
                  label={{
                    value: `Media: ${formatRatio(crossMean)}`,
                    position: "insideTopRight",
                    fill: "var(--text-muted)",
                    fontSize: 9,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey={crossPair}
                  name={CROSS_PAIR_CONFIG[crossPair].label}
                  stroke={COLORS.cyan}
                  fill="url(#crossGrad)"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartSection>
      </div>

      {/* ========== SECTION 3: S2F-Adjusted ========== */}
      <ChartSection
        title="BTC ÷ Oro (S2F-Adjusted) — Comparación en igualdad de condiciones de emisión"
        subtitle="Ratio ponderado por stock-to-flow relativo entre activos. Normaliza la comparación para activos con diferentes perfiles de escasez."
        delay={5}
      >
        <div className="h-[250px] sm:h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
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
                y={(() => {
                  const vals = filteredData.map((d) => d.btcGoldS2F);
                  return vals.reduce((s, v) => s + v, 0) / vals.length;
                })()}
                stroke={COLORS.muted}
                strokeDasharray="6 4"
              />
              <Line
                type="monotone"
                dataKey="btcGoldS2F"
                name="BTC/Oro (S2F-adj)"
                stroke={COLORS.gold}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartSection>

      {/* ========== SECTION 4: Multi-ratio overlay ========== */}
      <ChartSection
        title="Panorama General — Todos los activos ÷ Denominador"
        subtitle="Vista comparativa de todos los activos normalizados por liquidez global. Base 100 = inicio del período seleccionado."
        delay={3}
      >
        <div className="h-[280px] sm:h-[360px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
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
              <Line type="monotone" dataKey="btcM2" name="BTC ÷ M2" stroke={COLORS.amber} strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="goldM2" name="Oro ÷ M2" stroke={COLORS.gold} strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="sp500M2" name="S&P 500 ÷ M2" stroke={COLORS.blue} strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="silverM2" name="Plata ÷ M2" stroke={COLORS.muted} strokeWidth={1} dot={false} strokeDasharray="4 2" />
              <Line type="monotone" dataKey="realEstateM2" name="Real Estate ÷ M2" stroke={COLORS.purple} strokeWidth={1} dot={false} strokeDasharray="4 2" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {/* Legend */}
        <div className="flex flex-wrap gap-4 mt-4 justify-center">
          {[
            { label: "BTC", color: COLORS.amber },
            { label: "Oro", color: COLORS.gold },
            { label: "S&P 500", color: COLORS.blue },
            { label: "Plata", color: COLORS.muted },
            { label: "Real Estate", color: COLORS.purple },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <div className="w-2.5 h-0.5 rounded" style={{ background: item.color }} />
              <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{item.label}</span>
            </div>
          ))}
        </div>
      </ChartSection>

      {/* ========== SUMMARY TABLE ========== */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6 md:p-8 fade-in-up fade-in-up-4">
        <div className="mb-4 sm:mb-5">
          <h2 className="mb-2">
            <span className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
              Tabla de Pares
            </span>
            <span className="font-serif italic text-sm sm:text-base sm:ml-2" style={{ color: "var(--text-secondary)", opacity: 0.7 }}>
              — Resumen de todos los ratios
            </span>
          </h2>
          <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Ratio actual vs. media histórica. La desviación estándar (σ) indica cuán lejos está el ratio de su promedio.
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
                    <td className="py-2.5 px-2" style={{ color: signalColor }}>
                      {s.signal}
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
