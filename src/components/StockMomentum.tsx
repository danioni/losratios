"use client";

import { useMemo, useState } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from "recharts";
import type { StockMomentumPoint, ConcentrationMetrics, StockDominanceDataPoint } from "@/lib/data";
import {
  TOP_STOCKS,
  getStockDominanceChanges,
  getSectorDominance,
} from "@/lib/data";

interface StockMomentumProps {
  momentum: { points: StockMomentumPoint[]; concentration: ConcentrationMetrics };
  stockDom: StockDominanceDataPoint[];
  stockDateRange: string;
  stockXTicks: string[];
  colors: Record<string, string>;
}

const QUADRANT_LABELS: Record<string, { label: string; color: string }> = {
  momentum: { label: "Momentum", color: "var(--accent-green)" },
  catch_up: { label: "Catch-up", color: "var(--accent-cyan)" },
  declining: { label: "Declining", color: "var(--accent-amber)" },
  value_trap: { label: "Value Trap", color: "var(--accent-red)" },
};

export default function StockMomentum({ momentum, stockDom, stockDateRange, stockXTicks, colors }: StockMomentumProps) {
  const [view, setView] = useState<"scatter" | "top10" | "gainers" | "sectors">("scatter");

  const formatDate = (d: string) => d.length <= 4 ? d : d.split("-")[0];

  const stockChanges = useMemo(() => getStockDominanceChanges(stockDom), [stockDom]);
  const sectorDom = useMemo(() => getSectorDominance(stockDom), [stockDom]);

  // Scatter data with median for quadrant lines
  const medianDom = useMemo(() => {
    if (!momentum.points.length) return 2;
    const sorted = [...momentum.points.map(p => p.currentDom)].sort((a, b) => a - b);
    return sorted[Math.floor(sorted.length / 2)];
  }, [momentum.points]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
            Dominancia Acciones — Top 50
          </h3>
          <p className="text-[10px] sm:text-[11px] leading-relaxed mt-1" style={{ color: "var(--text-muted)" }}>
            Momentum, concentración y rotación. Período: {stockDateRange}
          </p>
        </div>
      </div>

      {/* View toggle */}
      <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
        {([
          { key: "scatter" as const, label: "Momentum Scatter" },
          { key: "top10" as const, label: "Top 10 Chart" },
          { key: "gainers" as const, label: "Gainers / Losers" },
          { key: "sectors" as const, label: "Por Sector" },
        ]).map((v) => (
          <button
            key={v.key}
            onClick={() => setView(v.key)}
            className="px-2.5 sm:px-3 py-1.5 rounded-md text-[9px] sm:text-[10px] tracking-wider uppercase transition-all"
            style={{
              background: view === v.key ? "var(--accent-green-bg-active)" : "transparent",
              color: view === v.key ? "var(--accent-green)" : "var(--text-muted)",
              border: view === v.key ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
            }}
          >
            {v.label}
          </button>
        ))}
      </div>

      {/* Concentration metrics */}
      {view === "scatter" && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div className="text-center py-2 px-2 rounded-lg" style={{ background: "var(--controls-bg)" }}>
            <p className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Top 5 %</p>
            <p className="text-sm font-medium tabular-nums" style={{ color: "var(--text-primary)" }}>{momentum.concentration.top5Pct.toFixed(1)}%</p>
          </div>
          <div className="text-center py-2 px-2 rounded-lg" style={{ background: "var(--controls-bg)" }}>
            <p className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Top 10 %</p>
            <p className="text-sm font-medium tabular-nums" style={{ color: "var(--text-primary)" }}>{momentum.concentration.top10Pct.toFixed(1)}%</p>
          </div>
          <div className="text-center py-2 px-2 rounded-lg" style={{ background: "var(--controls-bg)" }}>
            <p className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>HHI</p>
            <p className="text-sm font-medium tabular-nums" style={{ color: "var(--text-primary)" }}>{momentum.concentration.hhi.toFixed(0)}</p>
          </div>
          <div className="text-center py-2 px-2 rounded-lg" style={{ background: "var(--controls-bg)" }}>
            <p className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>HHI Δ6M</p>
            <p className="text-sm font-medium tabular-nums" style={{ color: momentum.concentration.hhiChange > 0 ? "var(--accent-red)" : "var(--accent-green)" }}>
              {momentum.concentration.hhiChange >= 0 ? "+" : ""}{momentum.concentration.hhiChange.toFixed(0)}
            </p>
          </div>
        </div>
      )}

      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6">
        {/* Scatter plot */}
        {view === "scatter" && momentum.points.length > 0 && (
          <>
            <div className="h-[320px] sm:h-[420px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, left: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="currentDom"
                    name="Dominancia %"
                    tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    label={{ value: "Dominancia %", position: "bottom", fill: "var(--text-muted)", fontSize: 10 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="domChange6M"
                    name="Cambio 6M"
                    tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v: number) => `${v >= 0 ? "+" : ""}${v.toFixed(1)}pp`}
                    label={{ value: "Cambio 6M (pp)", angle: -90, position: "insideLeft", fill: "var(--text-muted)", fontSize: 10 }}
                  />
                  <ReferenceLine x={medianDom} stroke={colors.muted} strokeDasharray="4 4" strokeOpacity={0.5} />
                  <ReferenceLine y={0} stroke={colors.muted} strokeDasharray="4 4" strokeOpacity={0.5} />
                  <Tooltip
                    content={({ active, payload }: any) => {
                      if (!active || !payload || !payload[0]) return null;
                      const d = payload[0].payload as StockMomentumPoint;
                      const qConfig = QUADRANT_LABELS[d.quadrant];
                      return (
                        <div className="rounded-lg px-4 py-3 text-xs" style={{ background: "var(--bg-tooltip)", border: "1px solid var(--border)", backdropFilter: "blur(10px)" }}>
                          <div className="flex items-center gap-2 mb-1.5">
                            <div className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                            <span className="font-medium" style={{ color: "var(--text-primary)" }}>{d.ticker}</span>
                            <span style={{ color: "var(--text-muted)" }}>{d.name}</span>
                          </div>
                          <p style={{ color: "var(--text-muted)" }}>Dom: <span className="tabular-nums" style={{ color: "var(--text-primary)" }}>{d.currentDom.toFixed(2)}%</span></p>
                          <p style={{ color: "var(--text-muted)" }}>Δ6M: <span className="tabular-nums" style={{ color: d.domChange6M >= 0 ? "var(--accent-green)" : "var(--accent-red)" }}>{d.domChange6M >= 0 ? "+" : ""}{d.domChange6M.toFixed(2)}pp</span></p>
                          <p style={{ color: "var(--text-muted)" }}>Accel: <span className="tabular-nums" style={{ color: d.acceleration >= 0 ? "var(--accent-cyan)" : "var(--accent-amber)" }}>{d.acceleration >= 0 ? "+" : ""}{d.acceleration.toFixed(3)}</span></p>
                          <p style={{ color: qConfig.color }}>{qConfig.label}</p>
                        </div>
                      );
                    }}
                  />
                  <Scatter data={momentum.points} shape="circle">
                    {momentum.points.map((point, i) => (
                      <Cell key={i} fill={point.color} fillOpacity={0.8} r={Math.max(3, Math.sqrt(point.currentDom) * 3)} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap gap-4 mt-3 justify-center">
              {Object.entries(QUADRANT_LABELS).map(([key, conf]) => (
                <div key={key} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ background: conf.color }} />
                  <span className="text-[8px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>{conf.label}</span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Top 10 chart */}
        {view === "top10" && stockDom.length > 0 && (
          <>
            <div className="h-[300px] sm:h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stockDom} margin={{ top: 5, right: 10, left: 10, bottom: 5 }} stackOffset="expand">
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
                              <span className="font-medium tabular-nums" style={{ color: entry.color }}>{(entry.value as number * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                        </div>
                      );
                    }}
                  />
                  {TOP_STOCKS.slice(0, 10).map((stock) => (
                    <Area key={stock.ticker} type="monotone" dataKey={stock.ticker} name={stock.name} stackId="1" stroke="none" fill={stock.color} fillOpacity={0.8} />
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

        {/* Gainers / Losers */}
        {view === "gainers" && stockChanges.length > 0 && (
          <div className="space-y-4">
            <p className="text-[9px] tracking-wider" style={{ color: "var(--text-muted)" }}>Cambio en dominancia: {stockDateRange}</p>
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
                      <span className="text-[11px] font-medium tabular-nums" style={{ color: "var(--accent-green)" }}>+{stock.changePp.toFixed(2)}pp</span>
                      <span className="text-[9px] tabular-nums ml-1.5" style={{ color: "var(--text-muted)" }}>{stock.currentDom.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
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
                      <span className="text-[11px] font-medium tabular-nums" style={{ color: "var(--accent-red)" }}>{stock.changePp.toFixed(2)}pp</span>
                      <span className="text-[9px] tabular-nums ml-1.5" style={{ color: "var(--text-muted)" }}>{stock.currentDom.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Sectors */}
        {view === "sectors" && sectorDom.length > 0 && (
          <div className="space-y-4">
            <p className="text-[9px] tracking-wider" style={{ color: "var(--text-muted)" }}>Cambio por sector: {stockDateRange}</p>
            <div className="h-[250px] sm:h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sectorDom} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${v.toFixed(0)}%`} />
                  <YAxis type="category" dataKey="sector" tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} width={70} />
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
                      <Cell key={i} fill={entry.changePp >= 0 ? colors.green : colors.red} fillOpacity={0.7} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
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
      </div>

      {/* Full stocks table */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6">
        <div className="mb-4">
          <h4 className="text-[10px] tracking-[0.2em] uppercase" style={{ color: "var(--text-muted)" }}>
            Top 50 Acciones — Dominancia por Market Cap
          </h4>
          <p className="text-[9px] mt-1" style={{ color: "var(--text-muted)" }}>
            % del market cap total de las top 50. Período: {stockDateRange}
          </p>
        </div>
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
  );
}
