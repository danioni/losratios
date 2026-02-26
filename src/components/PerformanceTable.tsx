"use client";

import { useMemo, useState } from "react";
import type { AssetPerformance } from "@/lib/data";
import { useCurrencyBase } from "./CurrencyContext";

interface PerformanceTableProps {
  data: AssetPerformance[];
  colors: Record<string, string>;
}

type SortKey = "cagrHistorical" | "cagr5Y" | "vsM2" | "ticker";
type SortDir = "asc" | "desc";

export default function PerformanceTable({ data }: PerformanceTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("cagrHistorical");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const { base, formatValue, isUSD, symbol, level } = useCurrencyBase();

  const sorted = useMemo(() => {
    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortDir === "asc" ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
  }, [data, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("desc"); }
  };

  const sortIcon = (key: SortKey) => {
    if (sortKey !== key) return "↕";
    return sortDir === "desc" ? "↓" : "↑";
  };

  const winners = sorted.filter((a) => a.beatsM2);
  const losers = sorted.filter((a) => !a.beatsM2);

  // Currency label for the price column header
  const priceLabel = isUSD ? "Precio" : `Precio (${base})`;

  return (
    <div className="space-y-6 fade-in-up fade-in-up-3">
      <div className="max-w-2xl">
        <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
          ¿Qué activos realmente ganan contra el denominador?
        </h3>
        <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
          M2 Global crece ~7% por año. Si tu activo no supera eso, no estás ganando — estás perdiendo en términos reales. Solo los activos que superan esta línea entran al análisis. La mayoría de los &ldquo;activos seguros&rdquo; no le ganan a la impresora.
        </p>
      </div>

      {/* Currency context note */}
      {!isUSD && (
        <div
          className="rounded-lg px-4 py-2.5 text-[10px] sm:text-[11px] leading-relaxed"
          style={{
            background: level === 4 ? "var(--accent-gold-bg)" : level === 3 ? "var(--accent-amber-bg)" : "var(--accent-green-bg)",
            border: `1px solid ${level === 4 ? "var(--accent-gold-border)" : level === 3 ? "var(--accent-amber-border)" : "var(--accent-green-border)"}`,
            color: level === 4 ? "var(--accent-gold)" : level === 3 ? "var(--accent-amber)" : "var(--text-secondary)",
          }}
        >
          Precios convertidos a {base} ({symbol}) al tipo de cambio actual. CAGR en USD — la conversión cambia los nominales, no el rendimiento porcentual (asumiendo FX constante).
        </div>
      )}

      {/* Full table */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-[10px] sm:text-[11px]">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>#</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("ticker")}>
                  Activo {sortIcon("ticker")}
                </th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Sector</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden lg:table-cell" style={{ color: "var(--text-muted)" }}>{priceLabel}</th>
                <th className="text-center py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Desde</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("cagrHistorical")}>
                  CAGR Hist {sortIcon("cagrHistorical")}
                </th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("cagr5Y")}>
                  CAGR 5Y {sortIcon("cagr5Y")}
                </th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer" style={{ color: "var(--text-muted)" }} onClick={() => toggleSort("vsM2")}>
                  vs M2 (7%) {sortIcon("vsM2")}
                </th>
                <th className="text-center py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Universo</th>
              </tr>
            </thead>
            <tbody>
              {/* Winners first */}
              {winners.map((a, i) => (
                <tr key={a.ticker} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                  <td className="py-2.5 px-2 tabular-nums" style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                  <td className="py-2.5 px-2">
                    <div>
                      <span className="font-medium" style={{ color: "var(--text-primary)" }}>{a.ticker}</span>
                      <span className="text-[9px] ml-1.5 hidden sm:inline" style={{ color: "var(--text-muted)" }}>{a.name}</span>
                    </div>
                  </td>
                  <td className="py-2.5 px-2 hidden sm:table-cell">
                    <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ color: "var(--text-muted)" }}>
                      {a.sector}
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-right tabular-nums hidden lg:table-cell" style={{ color: "var(--text-primary)" }}>
                    {formatValue(a.priceCurrent)}
                  </td>
                  <td className="py-2.5 px-2 text-center tabular-nums hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>
                    {a.ipoYear}
                  </td>
                  <td className="py-2.5 px-2 text-right">
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
                  <td className="py-2.5 px-2 text-right">
                    <span
                      className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                      style={{
                        color: a.cagr5Y > 30 ? "var(--accent-green)" : a.cagr5Y > 15 ? "var(--accent-cyan)" : a.cagr5Y < 0 ? "var(--accent-red)" : "var(--text-primary)",
                      }}
                    >
                      {a.cagr5Y.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-right">
                    <span
                      className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                      style={{
                        color: a.vsM2 > 0 ? "var(--accent-green)" : "var(--accent-red)",
                        background: a.vsM2 > 10 ? "var(--accent-green-bg)" : a.vsM2 < 0 ? "var(--accent-red-bg)" : "transparent",
                      }}
                    >
                      {a.vsM2 >= 0 ? "+" : ""}{a.vsM2.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-center">
                    <span className="text-[10px]" style={{ color: "var(--accent-green)" }}>
                      ✓
                    </span>
                  </td>
                </tr>
              ))}
              {/* Separator */}
              {losers.length > 0 && (
                <tr>
                  <td colSpan={9} className="py-3 px-2">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
                      <span className="text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
                        No superan M2 (7% anual) — contexto, no universo ganador
                      </span>
                      <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
                    </div>
                  </td>
                </tr>
              )}
              {/* Losers (context) */}
              {losers.map((a, i) => (
                <tr key={a.ticker} style={{ borderBottom: "1px solid var(--border-subtle)", opacity: 0.5 }}>
                  <td className="py-2.5 px-2 tabular-nums" style={{ color: "var(--text-muted)" }}>{winners.length + i + 1}</td>
                  <td className="py-2.5 px-2">
                    <div>
                      <span className="font-medium" style={{ color: "var(--text-muted)" }}>{a.ticker}</span>
                      <span className="text-[9px] ml-1.5 hidden sm:inline" style={{ color: "var(--text-muted)" }}>{a.name}</span>
                    </div>
                  </td>
                  <td className="py-2.5 px-2 hidden sm:table-cell">
                    <span className="text-[9px] px-1.5 py-0.5 rounded" style={{ color: "var(--text-muted)" }}>
                      {a.sector}
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-right tabular-nums hidden lg:table-cell" style={{ color: "var(--text-muted)" }}>
                    {formatValue(a.priceCurrent)}
                  </td>
                  <td className="py-2.5 px-2 text-center tabular-nums hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>
                    {a.ipoYear}
                  </td>
                  <td className="py-2.5 px-2 text-right tabular-nums" style={{ color: "var(--text-muted)" }}>
                    {a.cagrHistorical.toFixed(1)}%
                  </td>
                  <td className="py-2.5 px-2 text-right tabular-nums" style={{ color: "var(--text-muted)" }}>
                    {a.cagr5Y.toFixed(1)}%
                  </td>
                  <td className="py-2.5 px-2 text-right">
                    <span className="tabular-nums px-1.5 py-0.5 rounded" style={{ color: "var(--accent-red)", background: "var(--accent-red-bg)" }}>
                      {a.vsM2.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2.5 px-2 text-center">
                    <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>
                      No supera denominador
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
