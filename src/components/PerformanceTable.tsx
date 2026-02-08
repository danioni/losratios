"use client";

import { useMemo, useState } from "react";
import type { AssetPerformance } from "@/lib/data";

interface PerformanceTableProps {
  data: AssetPerformance[];
  colors: Record<string, string>;
}

type SortKey = "cagrHistorical" | "cagr5Y" | "marketCap" | "years" | "ticker";
type SortDir = "asc" | "desc";

const SECTOR_COLORS: Record<string, string> = {
  Tech: "var(--accent-blue)",
  Consumer: "var(--accent-amber)",
  Finance: "var(--accent-purple)",
  Health: "var(--accent-cyan)",
  Energy: "var(--accent-red)",
  Industrial: "var(--accent-gold)",
  Auto: "var(--accent-red)",
  Crypto: "var(--accent-amber)",
  Commodities: "var(--accent-gold)",
  Materials: "var(--accent-cyan)",
  Index: "var(--text-muted)",
};

function formatPrice(p: number): string {
  if (p >= 10000) return `$${(p / 1000).toFixed(0)}K`;
  if (p >= 100) return `$${p.toFixed(0)}`;
  if (p >= 1) return `$${p.toFixed(2)}`;
  if (p >= 0.01) return `$${p.toFixed(3)}`;
  return `$${p.toExponential(1)}`;
}

function formatMcap(b: number): string {
  if (b >= 1000) return `$${(b / 1000).toFixed(1)}T`;
  return `$${b.toFixed(0)}B`;
}

export default function PerformanceTable({ data, colors }: PerformanceTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("cagrHistorical");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [sectorFilter, setSectorFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  const sectors = useMemo(() => {
    const s = new Set(data.map((d) => d.sector));
    return ["all", ...Array.from(s).sort()];
  }, [data]);

  const top5Historical = useMemo(() => [...data].sort((a, b) => b.cagrHistorical - a.cagrHistorical).slice(0, 5), [data]);
  const top5Recent = useMemo(() => [...data].sort((a, b) => b.cagr5Y - a.cagr5Y).slice(0, 5), [data]);

  const filtered = useMemo(() => {
    let result = [...data];
    if (sectorFilter !== "all") result = result.filter((d) => d.sector === sectorFilter);
    if (search) {
      const q = search.toLowerCase();
      result = result.filter((d) => d.ticker.toLowerCase().includes(q) || d.name.toLowerCase().includes(q));
    }
    result.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortDir === "asc" ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
    return result;
  }, [data, sortKey, sortDir, sectorFilter, search]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("desc"); }
  };

  const sortIcon = (key: SortKey) => {
    if (sortKey !== key) return "↕";
    return sortDir === "desc" ? "↓" : "↑";
  };

  return (
    <div className="space-y-6 fade-in-up fade-in-up-3">
      <div>
        <h3 className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
          Performance Histórica
        </h3>
        <p className="text-[10px] sm:text-[11px] leading-relaxed mt-1" style={{ color: "var(--text-muted)" }}>
          CAGR (Compound Annual Growth Rate) desde IPO y últimos 5 años. Datos simulados de ~45 activos.
        </p>
      </div>

      {/* Top 5 cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Historical Top 5 */}
        <div className="card-glass card-accent-gold rounded-xl p-4 sm:p-5">
          <h4 className="text-[10px] tracking-[0.2em] uppercase mb-3 flex items-center gap-2" style={{ color: "var(--accent-gold)" }}>
            🏆 Top 5 CAGR Histórico
          </h4>
          <div className="space-y-2">
            {top5Historical.map((a, i) => (
              <div key={a.ticker} className="flex items-center gap-3 py-1.5 px-2 rounded-lg" style={{ background: i === 0 ? "var(--accent-gold-bg)" : "transparent" }}>
                <span className="text-[10px] tabular-nums w-4" style={{ color: "var(--text-muted)" }}>#{i + 1}</span>
                <span className="text-[11px] font-medium w-12" style={{ color: "var(--text-primary)" }}>{a.ticker}</span>
                <span className="text-[9px] flex-1" style={{ color: "var(--text-muted)" }}>
                  {formatPrice(a.priceStart)} → {formatPrice(a.priceCurrent)} · {a.years}Y
                </span>
                <span className="text-[11px] font-medium tabular-nums" style={{ color: "var(--accent-green)" }}>
                  {a.cagrHistorical.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* 5Y Top 5 */}
        <div className="card-glass card-accent-top rounded-xl p-4 sm:p-5">
          <h4 className="text-[10px] tracking-[0.2em] uppercase mb-3 flex items-center gap-2" style={{ color: "var(--accent-green)" }}>
            🚀 Top 5 CAGR 5 Años
          </h4>
          <div className="space-y-2">
            {top5Recent.map((a, i) => (
              <div key={a.ticker} className="flex items-center gap-3 py-1.5 px-2 rounded-lg" style={{ background: i === 0 ? "var(--accent-green-bg)" : "transparent" }}>
                <span className="text-[10px] tabular-nums w-4" style={{ color: "var(--text-muted)" }}>#{i + 1}</span>
                <span className="text-[11px] font-medium w-12" style={{ color: "var(--text-primary)" }}>{a.ticker}</span>
                <span className="text-[9px] flex-1" style={{ color: "var(--text-muted)" }}>
                  {formatPrice(a.priceCurrent)} · {a.sector}
                </span>
                <span className="text-[11px] font-medium tabular-nums" style={{ color: "var(--accent-green)" }}>
                  {a.cagr5Y.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Buscar ticker o nombre..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 rounded-lg text-[10px] sm:text-[11px] outline-none"
          style={{
            background: "var(--controls-bg)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)",
          }}
        />
        <div className="flex flex-wrap gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
          {sectors.map((s) => (
            <button
              key={s}
              onClick={() => setSectorFilter(s)}
              className="px-2 py-1 rounded-md text-[8px] sm:text-[9px] tracking-wider uppercase transition-all"
              style={{
                background: sectorFilter === s ? "var(--accent-green-bg-active)" : "transparent",
                color: sectorFilter === s ? "var(--accent-green)" : "var(--text-muted)",
                border: sectorFilter === s ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
              }}
            >
              {s === "all" ? "Todos" : s}
            </button>
          ))}
        </div>
      </div>

      {/* Full table */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-5">
        <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
          <table className="w-full text-[10px] sm:text-[11px]">
            <thead className="sticky top-0" style={{ background: "var(--bg-card)" }}>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>#</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("ticker")}>
                  Activo {sortIcon("ticker")}
                </th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Sector</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden md:table-cell cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("marketCap")}>
                  Mcap {sortIcon("marketCap")}
                </th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden lg:table-cell" style={{ color: "var(--text-muted)" }}>Inicio</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden lg:table-cell" style={{ color: "var(--text-muted)" }}>Actual</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("years")}>
                  Años {sortIcon("years")}
                </th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("cagrHistorical")}>
                  CAGR Hist {sortIcon("cagrHistorical")}
                </th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("cagr5Y")}>
                  CAGR 5Y {sortIcon("cagr5Y")}
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a, i) => {
                const sectorColor = SECTOR_COLORS[a.sector] || "var(--text-muted)";
                return (
                  <tr key={a.ticker} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="py-2 px-2 tabular-nums" style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                    <td className="py-2 px-2">
                      <div>
                        <span className="font-medium" style={{ color: "var(--text-primary)" }}>{a.ticker}</span>
                        <span className="text-[9px] ml-1.5 hidden sm:inline" style={{ color: "var(--text-muted)" }}>{a.name}</span>
                      </div>
                    </td>
                    <td className="py-2 px-2 hidden sm:table-cell">
                      <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ color: sectorColor, background: `color-mix(in srgb, ${sectorColor} 10%, transparent)` }}>
                        {a.sector}
                      </span>
                    </td>
                    <td className="py-2 px-2 text-right tabular-nums hidden md:table-cell" style={{ color: "var(--text-secondary)" }}>
                      {formatMcap(a.marketCap)}
                    </td>
                    <td className="py-2 px-2 text-right tabular-nums hidden lg:table-cell" style={{ color: "var(--text-muted)" }}>
                      {formatPrice(a.priceStart)}
                    </td>
                    <td className="py-2 px-2 text-right tabular-nums hidden lg:table-cell" style={{ color: "var(--text-primary)" }}>
                      {formatPrice(a.priceCurrent)}
                    </td>
                    <td className="py-2 px-2 text-right tabular-nums" style={{ color: "var(--text-secondary)" }}>
                      {a.years}
                    </td>
                    <td className="py-2 px-2 text-right">
                      <span
                        className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                        style={{
                          color: a.cagrHistorical > 20 ? "var(--accent-green)" : a.cagrHistorical > 10 ? "var(--accent-cyan)" : "var(--text-primary)",
                          background: a.cagrHistorical > 20 ? "var(--accent-green-bg)" : "transparent",
                        }}
                      >
                        {a.cagrHistorical.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-2 px-2 text-right">
                      <span
                        className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                        style={{
                          color: a.cagr5Y > 30 ? "var(--accent-green)" : a.cagr5Y > 15 ? "var(--accent-cyan)" : a.cagr5Y < 0 ? "var(--accent-red)" : "var(--text-primary)",
                          background: a.cagr5Y > 30 ? "var(--accent-green-bg)" : a.cagr5Y < 0 ? "var(--accent-red-bg)" : "transparent",
                        }}
                      >
                        {a.cagr5Y.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
