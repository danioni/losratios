"use client";

import { useState, useEffect, useRef } from "react";
import { useCurrencyBase } from "./CurrencyContext";
import { CURRENCIES, type CurrencyCode, getLevelLabel } from "@/lib/currency";

export default function CurrencySelector() {
  const { base, setBase, levelMessage } = useCurrencyBase();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Hydrate from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("losratios_currency_base") as CurrencyCode | null;
      if (saved && CURRENCIES.some(c => c.code === saved)) {
        setBase(saved);
      }
    } catch { /* ignore */ }
  }, [setBase]);

  // Close dropdown on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  // Close on escape
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open]);

  const current = CURRENCIES.find(c => c.code === base)!;

  // Group currencies by level
  const grouped = [4, 3, 2, 1] as const;

  return (
    <div className="flex items-center gap-3 min-w-0 flex-wrap">
          <span
            className="text-[8px] sm:text-[9px] tracking-wider uppercase shrink-0"
            style={{ color: "var(--text-muted)" }}
          >
            Medir en:
          </span>

          {/* Selector button */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setOpen(!open)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[9px] sm:text-[10px] tracking-wider transition-all"
              style={{
                background: "var(--accent-green-bg-active)",
                border: "1px solid var(--accent-green-border-active)",
                color: "var(--accent-green)",
                boxShadow: "var(--accent-green-glow)",
              }}
            >
              <span>{current.flag}</span>
              <span className="font-medium">{current.code}</span>
              <svg
                width="10"
                height="10"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="transition-transform"
                style={{ transform: open ? "rotate(180deg)" : "rotate(0)" }}
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>

            {/* Dropdown */}
            {open && (
              <div
                className="absolute top-full left-0 mt-1 w-[280px] sm:w-[320px] rounded-lg overflow-hidden z-50"
                style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  boxShadow: "0 16px 48px rgba(0,0,0,0.4)",
                  backdropFilter: "blur(16px)",
                }}
              >
                <div className="max-h-[70vh] overflow-y-auto">
                  {grouped.map(level => {
                    const items = CURRENCIES.filter(c => c.level === level);
                    return (
                      <div key={level}>
                        {/* Level header */}
                        <div
                          className="sticky top-0 px-3 py-1.5 text-[8px] tracking-[0.15em] uppercase font-medium"
                          style={{
                            background: "var(--bg-secondary)",
                            color: level === 4
                              ? "var(--accent-gold)"
                              : level === 3
                              ? "var(--accent-amber)"
                              : level === 2
                              ? "var(--accent-cyan)"
                              : "var(--text-muted)",
                            borderBottom: "1px solid var(--border-subtle)",
                          }}
                        >
                          Nivel {level} — {getLevelLabel(level)}
                        </div>
                        {items.map(curr => (
                          <button
                            key={curr.code}
                            onClick={() => { setBase(curr.code); setOpen(false); }}
                            className="w-full flex items-center gap-2.5 px-3 py-2 text-left transition-colors"
                            style={{
                              background: base === curr.code ? "var(--accent-green-bg)" : "transparent",
                              borderBottom: "1px solid var(--border-subtle)",
                            }}
                            onMouseEnter={e => {
                              if (base !== curr.code) (e.currentTarget.style.background = "var(--accent-green-bg)");
                            }}
                            onMouseLeave={e => {
                              if (base !== curr.code) (e.currentTarget.style.background = "transparent");
                            }}
                          >
                            <span className="text-sm shrink-0">{curr.flag}</span>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span
                                  className="text-[10px] font-medium tracking-wider"
                                  style={{
                                    color: base === curr.code ? "var(--accent-green)" : "var(--text-primary)",
                                  }}
                                >
                                  {curr.code}
                                </span>
                                <span className="text-[9px] truncate" style={{ color: "var(--text-muted)" }}>
                                  {curr.name}
                                </span>
                              </div>
                              <span className="text-[8px]" style={{ color: "var(--text-muted)" }}>
                                {curr.country}
                              </span>
                            </div>
                            <span className="text-[9px] tabular-nums shrink-0" style={{ color: "var(--text-muted)" }}>
                              {curr.code === "USD"
                                ? "1.00"
                                : curr.code === "BTC"
                                ? `${(1 / curr.rateVsUSD).toLocaleString("en-US", { maximumFractionDigits: 0 })} USD`
                                : curr.code === "XAU"
                                ? `${(1 / curr.rateVsUSD).toLocaleString("en-US", { maximumFractionDigits: 0 })} USD`
                                : `${curr.rateVsUSD.toLocaleString("en-US", { maximumFractionDigits: curr.rateVsUSD >= 100 ? 0 : 2 })}/${curr.symbol}`
                              }
                            </span>
                            {base === curr.code && (
                              <span style={{ color: "var(--accent-green)" }} className="text-[10px] shrink-0">
                                ✓
                              </span>
                            )}
                          </button>
                        ))}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Level message */}
          {levelMessage && (
            <span
              className="text-[8px] sm:text-[9px] leading-tight truncate hidden sm:block"
              style={{
                color: current.level === 4
                  ? "var(--accent-gold)"
                  : current.level === 3
                  ? "var(--accent-amber)"
                  : "var(--text-muted)",
              }}
            >
              {levelMessage}
            </span>
          )}
    </div>
  );
}
