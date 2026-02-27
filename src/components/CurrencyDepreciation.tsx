"use client";

import { useMemo, useState } from "react";
import { getCurrencyDepreciationData, type CurrencyDepreciationRow } from "@/lib/currency";
import { useCurrencyBase } from "./CurrencyContext";

type SortKey = "annualGlobalLoss" | "annualDepVsUSD" | "code";
type SortDir = "asc" | "desc";

export default function CurrencyDepreciation() {
  const [sortKey, setSortKey] = useState<SortKey>("annualGlobalLoss");
  const [sortDir, setSortDir] = useState<SortDir>("asc"); // worst first
  const { base } = useCurrencyBase();

  const data = useMemo(() => getCurrencyDepreciationData(), []);

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
    if (sortKey === key) setSortDir(d => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
  };

  const sortIcon = (key: SortKey) => {
    if (sortKey !== key) return "↕";
    return sortDir === "asc" ? "↑" : "↓";
  };

  // Separate into "gain" and "lose" groups
  const gainers = sorted.filter(r => r.annualGlobalLoss > 0);
  const losers = sorted.filter(r => r.annualGlobalLoss <= 0);

  const formatPct = (val: number, showSign = true) => {
    const sign = val > 0 ? "+" : "";
    return `${showSign ? sign : ""}${val.toFixed(1)}%`;
  };

  const depColor = (val: number) => {
    if (val > 5) return "var(--accent-green)";
    if (val > 0) return "var(--accent-cyan)";
    if (val > -5) return "var(--text-muted)";
    if (val > -20) return "var(--accent-amber)";
    return "var(--accent-red)";
  };

  const depBg = (val: number) => {
    if (val > 5) return "var(--accent-green-bg)";
    if (val < -20) return "var(--accent-red-bg)";
    return "transparent";
  };

  const renderRow = (r: CurrencyDepreciationRow, idx: number, isGainer: boolean) => {
    const isSelected = r.code === base;
    return (
      <tr
        key={r.code}
        style={{
          borderBottom: "1px solid var(--border-subtle)",
          opacity: isGainer ? 1 : 0.7,
          background: isSelected ? "var(--accent-green-bg)" : "transparent",
        }}
      >
        <td className="py-2 px-2 tabular-nums" style={{ color: "var(--text-muted)" }}>
          {idx + 1}
        </td>
        <td className="py-2 px-2">
          <span className="mr-1.5">{r.flag}</span>
          <span className="font-medium" style={{ color: isSelected ? "var(--accent-green)" : "var(--text-primary)" }}>
            {r.code}
          </span>
          <span className="text-[9px] ml-1.5 hidden sm:inline" style={{ color: "var(--text-muted)" }}>
            {r.name}
          </span>
        </td>
        <td className="py-2 px-2 hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>
          {r.country}
        </td>
        <td className="py-2 px-2 text-center tabular-nums hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>
          {r.firstYear ?? "—"}
        </td>
        <td className="py-2 px-2 text-right">
          <span
            className="tabular-nums px-1.5 py-0.5 rounded font-medium"
            style={{ color: depColor(r.annualDepVsUSD) }}
          >
            {formatPct(r.annualDepVsUSD)}
          </span>
        </td>
        <td className="py-2 px-2 text-right">
          <span
            className="tabular-nums px-1.5 py-0.5 rounded font-medium"
            style={{
              color: depColor(r.annualGlobalLoss),
              background: depBg(r.annualGlobalLoss),
            }}
          >
            {formatPct(r.annualGlobalLoss)}
          </span>
        </td>
      </tr>
    );
  };

  let globalIdx = 0;

  return (
    <div className="space-y-6 fade-in-up fade-in-up-4">
      <div className="max-w-2xl">
        <h3
          className="font-serif text-lg sm:text-xl tracking-wide mb-3"
          style={{ color: "var(--text-primary)" }}
        >
          Poder adquisitivo global
        </h3>
        <p
          className="text-[11px] sm:text-xs leading-relaxed"
          style={{ color: "var(--text-muted)" }}
        >
          Localmente te puedes sentir millonario. Lo que importa es tu posici&oacute;n
          relativa en el mundo. Cada moneda pierde poder adquisitivo a su propio ritmo
          &mdash; el d&oacute;lar incluido. Si tu moneda pierde X% por a&ntilde;o, tu
          inversi&oacute;n necesita rendir al menos X% solo para no retroceder.
        </p>
      </div>

      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-[10px] sm:text-[11px]">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                <th
                  className="text-left py-2 px-2 tracking-wider uppercase font-medium"
                  style={{ color: "var(--text-muted)" }}
                >
                  #
                </th>
                <th
                  className="text-left py-2 px-2 tracking-wider uppercase font-medium cursor-pointer"
                  style={{ color: "var(--text-muted)" }}
                  onClick={() => toggleSort("code")}
                >
                  Moneda {sortIcon("code")}
                </th>
                <th
                  className="text-left py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell"
                  style={{ color: "var(--text-muted)" }}
                >
                  Pa&iacute;s
                </th>
                <th
                  className="text-center py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell"
                  style={{ color: "var(--text-muted)" }}
                >
                  Desde
                </th>
                <th
                  className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer"
                  style={{ color: "var(--text-muted)" }}
                  onClick={() => toggleSort("annualDepVsUSD")}
                >
                  vs USD/a&ntilde;o {sortIcon("annualDepVsUSD")}
                </th>
                <th
                  className="text-right py-2 px-2 tracking-wider uppercase font-medium cursor-pointer"
                  style={{ color: "var(--text-muted)" }}
                  onClick={() => toggleSort("annualGlobalLoss")}
                >
                  Global/a&ntilde;o {sortIcon("annualGlobalLoss")}
                </th>
              </tr>
            </thead>
            <tbody>
              {/* Gainers first (BTC, XAU) */}
              {gainers.map(r => renderRow(r, globalIdx++, true))}

              {/* Separator */}
              {gainers.length > 0 && losers.length > 0 && (
                <tr>
                  <td colSpan={6} className="py-3 px-2">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
                      <span
                        className="text-[9px] tracking-wider uppercase"
                        style={{ color: "var(--text-muted)" }}
                      >
                        Pierden poder adquisitivo &mdash; la mayor&iacute;a de las monedas del mundo
                      </span>
                      <div className="flex-1 h-px" style={{ background: "var(--border)" }} />
                    </div>
                  </td>
                </tr>
              )}

              {/* Losers */}
              {losers.map(r => renderRow(r, globalIdx++, false))}
            </tbody>
          </table>
        </div>

        <p
          className="text-[9px] sm:text-[10px] mt-4 leading-relaxed"
          style={{ color: "var(--text-muted)" }}
        >
          <strong style={{ color: "var(--text-secondary)" }}>vs USD/a&ntilde;o</strong>: cambio anual
          de poder adquisitivo contra el d&oacute;lar.{" "}
          <strong style={{ color: "var(--text-secondary)" }}>Global/a&ntilde;o</strong>: p&eacute;rdida
          total de poder adquisitivo (incluye expansi&oacute;n M2 global ~7%/a&ntilde;o).
          Los resets monetarios en Am&eacute;rica Latina son frecuentes &mdash; &ldquo;Desde&rdquo;
          indica el a&ntilde;o m&aacute;s antiguo con datos confiables.
          EUR pre-1999: serie sint&eacute;tica derivada del Marco Alem&aacute;n (metodolog&iacute;a BCE, 1&nbsp;EUR&nbsp;=&nbsp;1.95583&nbsp;DEM).
        </p>
      </div>
    </div>
  );
}
