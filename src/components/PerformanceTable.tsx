"use client";

import { useMemo, useState } from "react";
import type { AssetPerformance } from "@/lib/data";
import { computeCAGR, getAnchorPrice } from "@/lib/data";
import { convertCAGR } from "@/lib/currency";
import { useCurrencyBase } from "./CurrencyContext";

interface PerformanceTableProps {
  data: AssetPerformance[];
  colors: Record<string, string>;
}

type SortKey = "cagrHistorical" | "cagr5Y" | "vsM2" | "ticker";
type SortDir = "asc" | "desc";

const BTC_START_YEAR = 2010;
const M2_BENCHMARK = 7;

export default function PerformanceTable({ data }: PerformanceTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("cagrHistorical");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const { base, formatValue, isUSD, symbol, level } = useCurrencyBase();

  const isHardBase = base === "BTC" || base === "XAU";
  const benchmark = isHardBase ? 0 : M2_BENCHMARK;

  // For hard bases, use the live price of the base asset for conversions
  // instead of the static FX rate in currency.ts (avoids mismatch)
  const baseAssetTicker = base === "BTC" ? "BTC" : base === "XAU" ? "GOLD" : null;
  const baseCurrentUSD = isHardBase
    ? (data.find(a => a.ticker === baseAssetTicker)?.priceCurrent ?? 0)
    : 0;

  const formatPrice = (asset: typeof data[0]) => {
    if (isHardBase && baseCurrentUSD > 0) {
      // Base asset always shows exactly 1.0000
      if (asset.ticker === baseAssetTicker) {
        return base === "BTC" ? "₿1.0000" : "1.0000 oz";
      }
      // Other assets: divide by live base price
      const valueInBase = asset.priceCurrent / baseCurrentUSD;
      if (base === "BTC") {
        if (valueInBase >= 1) return `₿${valueInBase.toFixed(2)}`;
        if (valueInBase >= 0.01) return `₿${valueInBase.toFixed(4)}`;
        if (valueInBase >= 0.0001) return `₿${valueInBase.toFixed(6)}`;
        return `₿${valueInBase.toExponential(2)}`;
      }
      // XAU
      if (valueInBase >= 1) return `${valueInBase.toFixed(2)} oz`;
      if (valueInBase >= 0.01) return `${valueInBase.toFixed(4)} oz`;
      return `${valueInBase.toExponential(2)} oz`;
    }
    return formatValue(asset.priceCurrent);
  };

  // Adjust CAGR for non-USD bases
  const adjustedData = useMemo(() => {
    // Fiat currencies: adjust CAGR using historical FX depreciation
    if (!isHardBase && !isUSD) {
      return data.map(a => {
        const cagrHist = convertCAGR(a.cagrHistorical, base, a.ipoYear, 2026);
        const cagr5Y = convertCAGR(a.cagr5Y, base, 2021, 2026);
        const vsM2 = cagrHist - benchmark;
        return { ...a, cagrHistorical: cagrHist, cagr5Y, vsM2, beatsM2: cagrHist > benchmark };
      });
    }

    if (!isHardBase) return data;

    // BTC/XAU base: recalculate CAGR using historical asset anchor prices
    const baseTicker = base === "BTC" ? "btc" as const : "gold" as const;
    const baseUSD = baseCurrentUSD > 0 ? baseCurrentUSD : getAnchorPrice(baseTicker, 2026);

    return data.map(a => {
      let effectiveIpoYear = a.ipoYear;
      let effectivePriceStart = a.priceStart;
      let effectiveYears = a.years;

      // For BTC base, assets before 2010 get truncated start
      if (base === "BTC" && a.ipoYear < BTC_START_YEAR) {
        effectiveIpoYear = BTC_START_YEAR;
        const totalYears = 2026 - a.ipoYear;
        const yearsToTarget = BTC_START_YEAR - a.ipoYear;
        effectivePriceStart = a.priceStart * Math.pow(a.priceCurrent / a.priceStart, yearsToTarget / totalYears);
        effectiveYears = 2026 - BTC_START_YEAR;
      }

      const baseAtStart = getAnchorPrice(baseTicker, effectiveIpoYear);
      if (baseAtStart <= 0 || baseUSD <= 0) return a;

      const startInBase = effectivePriceStart / baseAtStart;
      const currentInBase = a.priceCurrent / baseUSD;
      const cagrHist = computeCAGR(startInBase, currentInBase, effectiveYears);

      // 5Y CAGR in base currency
      const base5YUSD = getAnchorPrice(baseTicker, 2021);
      let cagr5Y = a.cagr5Y;
      if (base5YUSD > 0 && a.price5YAgo > 0) {
        cagr5Y = computeCAGR(a.price5YAgo / base5YUSD, a.priceCurrent / baseUSD, 5);
      }

      const vsM2 = cagrHist - benchmark;

      return {
        ...a,
        ipoYear: effectiveIpoYear,
        years: effectiveYears,
        cagrHistorical: cagrHist,
        cagr5Y,
        vsM2,
        beatsM2: cagrHist > benchmark,
      };
    });
  }, [data, base, isHardBase, isUSD, benchmark, baseCurrentUSD]);

  const sorted = useMemo(() => {
    return [...adjustedData].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortDir === "asc" ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
  }, [adjustedData, sortKey, sortDir]);

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

  // Dynamic labels based on base currency
  const vsLabel = base === "BTC" ? "vs BTC" : base === "XAU" ? "vs Oro" : "vs M2 (7%)";
  const separatorText = base === "BTC"
    ? "No superan BTC — pierden contra el activo m\u00e1s escaso"
    : base === "XAU"
    ? "No superan Oro — pierden contra dinero duro"
    : "No superan M2 (7% anual) — contexto, no universo ganador";
  const loserLabel = base === "BTC"
    ? "No supera BTC"
    : base === "XAU"
    ? "No supera Oro"
    : "No supera denominador";

  return (
    <div className="space-y-6 fade-in-up fade-in-up-3">
      <div className="max-w-2xl">
        <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
          {base === "BTC"
            ? "\u00bfQu\u00e9 activos realmente ganan contra Bitcoin?"
            : base === "XAU"
            ? "\u00bfQu\u00e9 activos realmente ganan contra el oro?"
            : "\u00bfQu\u00e9 activos realmente ganan contra el denominador?"}
        </h3>
        <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
          {base === "BTC"
            ? "Midiendo en BTC. Si tu activo no supera al activo m\u00e1s escaso, est\u00e1s perdiendo en los t\u00e9rminos m\u00e1s exigentes. Pocos sobreviven esta vara."
            : base === "XAU"
            ? "Midiendo en oro. Si tu activo no supera 5,000 a\u00f1os de dinero duro, est\u00e1s perdiendo en t\u00e9rminos reales."
            : "M2 Global crece ~7% por a\u00f1o. Si tu activo no supera eso, no est\u00e1s ganando \u2014 est\u00e1s perdiendo en t\u00e9rminos reales. Solo los activos que superan esta l\u00ednea entran al an\u00e1lisis. La mayor\u00eda de los \u201cactivos seguros\u201d no le ganan a la impresora."}
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
          {base === "BTC" ? (
            <>CAGR recalculado en BTC. Mide el rendimiento real contra el activo m&aacute;s escaso. Pocos portfolios sobreviven esta vara.</>
          ) : base === "XAU" ? (
            <>CAGR recalculado en onzas de oro. Mide el rendimiento real contra 5,000 a&ntilde;os de dinero duro.</>
          ) : (
            <>Precios convertidos a {base} ({symbol}) al tipo de cambio actual. CAGR en USD &mdash; la conversi&oacute;n cambia los nominales, no el rendimiento porcentual (asumiendo FX constante).</>
          )}
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
                  {vsLabel} {sortIcon("vsM2")}
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
                    {formatPrice(a)}
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
                        {separatorText}
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
                    {formatPrice(a)}
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
                      {loserLabel}
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
