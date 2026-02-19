"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import {
  type CurrencyCode,
  getCurrency,
  convertFromUSD,
  formatUSDAs,
  formatInCurrency,
  getLevelMessage,
} from "@/lib/currency";

interface CurrencyBaseContextValue {
  base: CurrencyCode;
  setBase: (code: CurrencyCode) => void;
  /** Convert a USD value to the current base currency */
  convert: (valueInUSD: number) => number;
  /** Format a USD value in the current base currency */
  formatValue: (valueInUSD: number) => string;
  /** Format a value that's already converted */
  formatConverted: (value: number) => string;
  /** Current FX rate (units of base per 1 USD) */
  fxRate: number;
  /** Symbol for the current base */
  symbol: string;
  /** Pedagogical message for the current level */
  levelMessage: string | null;
  /** Current level (1-4) */
  level: 1 | 2 | 3 | 4;
  /** Whether base is USD (no conversion needed) */
  isUSD: boolean;
}

const CurrencyBaseContext = createContext<CurrencyBaseContextValue | null>(null);

export function CurrencyBaseProvider({ children }: { children: ReactNode }) {
  const [base, setBaseState] = useState<CurrencyCode>("USD");

  const setBase = useCallback((code: CurrencyCode) => {
    setBaseState(code);
    try {
      localStorage.setItem("losratios_currency_base", code);
    } catch { /* ignore */ }
  }, []);

  // Hydrate from localStorage on mount — handled in useEffect in parent
  // to avoid SSR mismatch (useState default is USD, safe for SSR)

  const curr = getCurrency(base);

  const convert = useCallback(
    (valueInUSD: number) => convertFromUSD(valueInUSD, base),
    [base],
  );

  const formatValue = useCallback(
    (valueInUSD: number) => formatUSDAs(valueInUSD, base),
    [base],
  );

  const formatConverted = useCallback(
    (value: number) => formatInCurrency(value, base),
    [base],
  );

  const value: CurrencyBaseContextValue = {
    base,
    setBase,
    convert,
    formatValue,
    formatConverted,
    fxRate: curr.rateVsUSD,
    symbol: curr.symbol,
    levelMessage: getLevelMessage(base),
    level: curr.level,
    isUSD: base === "USD",
  };

  return (
    <CurrencyBaseContext.Provider value={value}>
      {children}
    </CurrencyBaseContext.Provider>
  );
}

export function useCurrencyBase(): CurrencyBaseContextValue {
  const ctx = useContext(CurrencyBaseContext);
  if (!ctx) throw new Error("useCurrencyBase must be used inside CurrencyBaseProvider");
  return ctx;
}
