"use client";

import { useMemo, useState } from "react";
import type { AssetProjection } from "@/lib/data";

interface ProjectionsProps {
  projections: AssetProjection[];
  colors: Record<string, string>;
}

function formatPrice(p: number): string {
  if (p >= 1_000_000) return `$${(p / 1_000_000).toFixed(1)}M`;
  if (p >= 10000) return `$${(p / 1000).toFixed(0)}K`;
  if (p >= 100) return `$${p.toFixed(0)}`;
  if (p >= 1) return `$${p.toFixed(2)}`;
  return `$${p.toFixed(4)}`;
}

function formatReturn(amount: number, cagr: number, years: number): string {
  const futureVal = amount * Math.pow(1 + cagr / 100, years);
  if (futureVal >= 1_000_000) return `$${(futureVal / 1_000_000).toFixed(1)}M`;
  if (futureVal >= 1000) return `$${(futureVal / 1000).toFixed(0)}K`;
  return `$${futureVal.toFixed(0)}`;
}

export default function Projections({ projections, colors }: ProjectionsProps) {
  const [selectedTicker, setSelectedTicker] = useState("BTC");
  const [amount, setAmount] = useState(10000);
  const [horizon, setHorizon] = useState<5 | 10>(5);
  const [sortKey, setSortKey] = useState<"excessVsBenchmark" | "baseCagr">("excessVsBenchmark");

  const selected = useMemo(() => projections.find((p) => p.ticker === selectedTicker), [projections, selectedTicker]);

  const sortedProjections = useMemo(() => {
    return [...projections].sort((a, b) => {
      if (sortKey === "excessVsBenchmark") return b.excessVsBenchmark - a.excessVsBenchmark;
      return b.scenarios.base.cagr - a.scenarios.base.cagr;
    });
  }, [projections, sortKey]);

  const confidenceColors: Record<string, string> = {
    high: "var(--accent-green)",
    medium: "var(--accent-amber)",
    low: "var(--accent-red)",
  };

  return (
    <div className="space-y-6 fade-in-up fade-in-up-3">
      <div>
        <h3 className="font-serif text-base sm:text-lg tracking-wide" style={{ color: "var(--text-primary)" }}>
          Proyecciones Multi-Factor
        </h3>
        <p className="text-[10px] sm:text-[11px] leading-relaxed mt-1" style={{ color: "var(--text-muted)" }}>
          Simulador de inversión basado en CAGR histórico y reciente. 3 escenarios: conservador (70% × min CAGR), base (40% hist + 60% 5Y), optimista (110% × max CAGR).
        </p>
      </div>

      {/* Simulator */}
      <div className="card-glass card-accent-gold rounded-xl p-4 sm:p-5">
        <h4 className="text-[10px] tracking-[0.2em] uppercase mb-4 flex items-center gap-2" style={{ color: "var(--accent-gold)" }}>
          💰 Simulador de Inversión
        </h4>

        <div className="flex flex-wrap items-center gap-3 mb-4">
          {/* Asset selector */}
          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="px-3 py-1.5 rounded-lg text-[10px] sm:text-[11px] outline-none cursor-pointer"
            style={{ background: "var(--controls-bg)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
          >
            {projections.map((p) => (
              <option key={p.ticker} value={p.ticker}>
                {p.ticker} — {p.name}
              </option>
            ))}
          </select>

          {/* Amount */}
          <div className="flex items-center gap-1">
            <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>$</span>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Math.max(1, parseInt(e.target.value) || 0))}
              className="w-24 px-2 py-1.5 rounded-lg text-[10px] sm:text-[11px] tabular-nums outline-none"
              style={{ background: "var(--controls-bg)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
            />
          </div>

          {/* Horizon */}
          <div className="flex gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
            {([5, 10] as const).map((y) => (
              <button
                key={y}
                onClick={() => setHorizon(y)}
                className="px-2.5 py-1 rounded-md text-[9px] sm:text-[10px] tracking-wider uppercase transition-all"
                style={{
                  background: horizon === y ? "var(--accent-green-bg-active)" : "transparent",
                  color: horizon === y ? "var(--accent-green)" : "var(--text-muted)",
                  border: horizon === y ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
                }}
              >
                {y}Y
              </button>
            ))}
          </div>
        </div>

        {selected && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Conservative */}
            <div className="rounded-lg p-3" style={{ background: "var(--controls-bg)" }}>
              <p className="text-[9px] tracking-wider uppercase mb-2" style={{ color: "var(--accent-red)" }}>Conservador</p>
              <p className="text-lg font-light tabular-nums" style={{ color: "var(--text-primary)" }}>
                {formatReturn(amount, selected.scenarios.conservative.cagr, horizon)}
              </p>
              <p className="text-[9px] tabular-nums" style={{ color: "var(--text-muted)" }}>
                CAGR: {selected.scenarios.conservative.cagr.toFixed(1)}% · Precio: {formatPrice(horizon === 5 ? selected.scenarios.conservative.price5Y : selected.scenarios.conservative.price10Y)}
              </p>
            </div>
            {/* Base */}
            <div className="rounded-lg p-3" style={{ background: "var(--accent-green-bg)", border: "1px solid var(--accent-green-border)" }}>
              <p className="text-[9px] tracking-wider uppercase mb-2" style={{ color: "var(--accent-green)" }}>Base</p>
              <p className="text-lg font-light tabular-nums" style={{ color: "var(--text-primary)" }}>
                {formatReturn(amount, selected.scenarios.base.cagr, horizon)}
              </p>
              <p className="text-[9px] tabular-nums" style={{ color: "var(--text-muted)" }}>
                CAGR: {selected.scenarios.base.cagr.toFixed(1)}% · Precio: {formatPrice(horizon === 5 ? selected.scenarios.base.price5Y : selected.scenarios.base.price10Y)}
              </p>
            </div>
            {/* Optimistic */}
            <div className="rounded-lg p-3" style={{ background: "var(--controls-bg)" }}>
              <p className="text-[9px] tracking-wider uppercase mb-2" style={{ color: "var(--accent-cyan)" }}>Optimista</p>
              <p className="text-lg font-light tabular-nums" style={{ color: "var(--text-primary)" }}>
                {formatReturn(amount, selected.scenarios.optimistic.cagr, horizon)}
              </p>
              <p className="text-[9px] tabular-nums" style={{ color: "var(--text-muted)" }}>
                CAGR: {selected.scenarios.optimistic.cagr.toFixed(1)}% · Precio: {formatPrice(horizon === 5 ? selected.scenarios.optimistic.price5Y : selected.scenarios.optimistic.price10Y)}
              </p>
            </div>
          </div>
        )}

        {selected && (
          <div className="flex items-center gap-3 mt-3 pt-3" style={{ borderTop: "1px solid var(--border-subtle)" }}>
            <span className="text-[9px] tracking-wider" style={{ color: "var(--text-muted)" }}>Confianza:</span>
            <span
              className="text-[9px] font-medium tracking-wider uppercase px-1.5 py-0.5 rounded"
              style={{ color: confidenceColors[selected.confidence] }}
            >
              {selected.confidence}
            </span>
            <span className="text-[9px]" style={{ color: "var(--text-muted)" }}>·</span>
            <span className="text-[9px] tracking-wider" style={{ color: "var(--text-muted)" }}>
              vs S&P 500:
            </span>
            <span
              className="text-[9px] font-medium tabular-nums"
              style={{ color: selected.excessVsBenchmark > 0 ? "var(--accent-green)" : selected.excessVsBenchmark < 0 ? "var(--accent-red)" : "var(--text-muted)" }}
            >
              {selected.excessVsBenchmark >= 0 ? "+" : ""}{selected.excessVsBenchmark.toFixed(1)}% anual
            </span>
          </div>
        )}
      </div>

      {/* Full projections table */}
      <div className="card-glass card-accent-left rounded-xl p-4 sm:p-5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h4 className="text-[10px] tracking-[0.2em] uppercase" style={{ color: "var(--text-muted)" }}>
            Tabla de Proyecciones
          </h4>
          <div className="flex gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
            {([
              { key: "excessVsBenchmark" as const, label: "vs S&P" },
              { key: "baseCagr" as const, label: "CAGR Base" },
            ]).map((opt) => (
              <button
                key={opt.key}
                onClick={() => setSortKey(opt.key)}
                className="px-2.5 py-1 rounded-md text-[8px] sm:text-[9px] tracking-wider uppercase transition-all"
                style={{
                  background: sortKey === opt.key ? "var(--accent-green-bg-active)" : "transparent",
                  color: sortKey === opt.key ? "var(--accent-green)" : "var(--text-muted)",
                  border: sortKey === opt.key ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
          <table className="w-full text-[10px] sm:text-[11px]">
            <thead className="sticky top-0" style={{ background: "var(--bg-card)" }}>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>#</th>
                <th className="text-left py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Activo</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Actual</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Consv.</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Base</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>Optim.</th>
                <th className="text-right py-2 px-2 tracking-wider uppercase font-medium" style={{ color: "var(--text-muted)" }}>vs S&P</th>
                <th className="text-center py-2 px-2 tracking-wider uppercase font-medium hidden sm:table-cell" style={{ color: "var(--text-muted)" }}>Conf.</th>
              </tr>
            </thead>
            <tbody>
              {sortedProjections.map((p, i) => (
                <tr
                  key={p.ticker}
                  style={{ borderBottom: "1px solid var(--border-subtle)", cursor: "pointer" }}
                  onClick={() => setSelectedTicker(p.ticker)}
                  className={selectedTicker === p.ticker ? "opacity-100" : "opacity-80 hover:opacity-100"}
                >
                  <td className="py-2 px-2 tabular-nums" style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                  <td className="py-2 px-2">
                    <span className="font-medium" style={{ color: selectedTicker === p.ticker ? "var(--accent-green)" : "var(--text-primary)" }}>{p.ticker}</span>
                    <span className="text-[9px] ml-1.5 hidden sm:inline" style={{ color: "var(--text-muted)" }}>{p.name}</span>
                  </td>
                  <td className="py-2 px-2 text-right tabular-nums hidden sm:table-cell" style={{ color: "var(--text-secondary)" }}>
                    {formatPrice(p.priceCurrent)}
                  </td>
                  <td className="py-2 px-2 text-right tabular-nums" style={{ color: "var(--text-muted)" }}>
                    {p.scenarios.conservative.cagr.toFixed(1)}%
                  </td>
                  <td className="py-2 px-2 text-right">
                    <span className="tabular-nums font-medium" style={{ color: "var(--accent-green)" }}>
                      {p.scenarios.base.cagr.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2 px-2 text-right tabular-nums" style={{ color: "var(--accent-cyan)" }}>
                    {p.scenarios.optimistic.cagr.toFixed(1)}%
                  </td>
                  <td className="py-2 px-2 text-right">
                    <span
                      className="tabular-nums px-1.5 py-0.5 rounded font-medium"
                      style={{
                        color: p.excessVsBenchmark > 0 ? "var(--accent-green)" : p.excessVsBenchmark < -5 ? "var(--accent-red)" : "var(--text-muted)",
                        background: p.excessVsBenchmark > 5 ? "var(--accent-green-bg)" : p.excessVsBenchmark < -5 ? "var(--accent-red-bg)" : "transparent",
                      }}
                    >
                      {p.excessVsBenchmark >= 0 ? "+" : ""}{p.excessVsBenchmark.toFixed(1)}%
                    </span>
                  </td>
                  <td className="py-2 px-2 text-center hidden sm:table-cell">
                    <span className="text-[8px] px-1.5 py-0.5 rounded uppercase tracking-wider" style={{ color: confidenceColors[p.confidence] }}>
                      {p.confidence}
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
