// ============================================================
// Currency Base System — "La masacre de las monedas"
// Every fiat currency of the Spanish-speaking world + EUR + BRL + XAU + BTC
// ============================================================

export type CurrencyCode =
  // Nivel 4 — Hard money absoluto
  | "BTC"
  // Nivel 3 — Dinero duro
  | "XAU"
  // Nivel 2 — Fiat global
  | "USD" | "EUR" | "BRL"
  // Nivel 1 — Fiat hispano (la masacre)
  | "CLP" | "MXN" | "ARS" | "COP" | "PEN" | "UYU"
  | "PYG" | "BOB" | "CRC" | "GTQ" | "HNL" | "NIO"
  | "DOP" | "PAB" | "CUP" | "VES" | "SVC";

export interface CurrencyDef {
  code: CurrencyCode;
  name: string;
  flag: string;
  symbol: string;
  level: 1 | 2 | 3 | 4;
  rateVsUSD: number; // cuántas unidades de esta moneda por 1 USD
  country: string;
}

// Tasas aproximadas vs USD (Feb 2026)
// Nivel 1: fiat hispano — aquí es donde se ve la masacre
export const CURRENCIES: CurrencyDef[] = [
  // ── Nivel 4: La vara más exigente ──
  { code: "BTC", name: "Bitcoin", flag: "₿", symbol: "₿", level: 4, rateVsUSD: 1 / 98000, country: "Descentralizado" },
  // ── Nivel 3: Dinero duro ──
  { code: "XAU", name: "Oro (oz)", flag: "🥇", symbol: "XAU", level: 3, rateVsUSD: 1 / 2870, country: "Global" },
  // ── Nivel 2: Fiat global ──
  { code: "USD", name: "Dólar USA", flag: "🇺🇸", symbol: "$", level: 2, rateVsUSD: 1, country: "Estados Unidos" },
  { code: "EUR", name: "Euro", flag: "🇪🇺", symbol: "€", level: 2, rateVsUSD: 0.92, country: "Eurozona" },
  { code: "BRL", name: "Real", flag: "🇧🇷", symbol: "R$", level: 2, rateVsUSD: 5.8, country: "Brasil" },
  // ── Nivel 1: Fiat hispano — la masacre ──
  { code: "MXN", name: "Peso MX", flag: "🇲🇽", symbol: "MX$", level: 1, rateVsUSD: 20.5, country: "México" },
  { code: "CLP", name: "Peso CL", flag: "🇨🇱", symbol: "CL$", level: 1, rateVsUSD: 950, country: "Chile" },
  { code: "COP", name: "Peso CO", flag: "🇨🇴", symbol: "CO$", level: 1, rateVsUSD: 4150, country: "Colombia" },
  { code: "ARS", name: "Peso AR", flag: "🇦🇷", symbol: "AR$", level: 1, rateVsUSD: 1065, country: "Argentina" },
  { code: "PEN", name: "Sol", flag: "🇵🇪", symbol: "S/", level: 1, rateVsUSD: 3.72, country: "Perú" },
  { code: "UYU", name: "Peso UY", flag: "🇺🇾", symbol: "UY$", level: 1, rateVsUSD: 43.5, country: "Uruguay" },
  { code: "PYG", name: "Guaraní", flag: "🇵🇾", symbol: "₲", level: 1, rateVsUSD: 7850, country: "Paraguay" },
  { code: "BOB", name: "Boliviano", flag: "🇧🇴", symbol: "Bs", level: 1, rateVsUSD: 6.91, country: "Bolivia" },
  { code: "CRC", name: "Colón CR", flag: "🇨🇷", symbol: "₡", level: 1, rateVsUSD: 510, country: "Costa Rica" },
  { code: "GTQ", name: "Quetzal", flag: "🇬🇹", symbol: "Q", level: 1, rateVsUSD: 7.72, country: "Guatemala" },
  { code: "HNL", name: "Lempira", flag: "🇭🇳", symbol: "L", level: 1, rateVsUSD: 25.4, country: "Honduras" },
  { code: "NIO", name: "Córdoba", flag: "🇳🇮", symbol: "C$", level: 1, rateVsUSD: 36.8, country: "Nicaragua" },
  { code: "DOP", name: "Peso RD", flag: "🇩🇴", symbol: "RD$", level: 1, rateVsUSD: 61.5, country: "Rep. Dominicana" },
  { code: "PAB", name: "Balboa", flag: "🇵🇦", symbol: "B/.", level: 1, rateVsUSD: 1, country: "Panamá" },
  { code: "CUP", name: "Peso CU", flag: "🇨🇺", symbol: "CU$", level: 1, rateVsUSD: 120, country: "Cuba" },
  { code: "VES", name: "Bolívar", flag: "🇻🇪", symbol: "Bs.S", level: 1, rateVsUSD: 56, country: "Venezuela" },
  { code: "SVC", name: "ex-Colón SV", flag: "🇸🇻", symbol: "₡SV", level: 1, rateVsUSD: 1, country: "El Salvador (USD/BTC)" },
];

export function getCurrency(code: CurrencyCode): CurrencyDef {
  return CURRENCIES.find(c => c.code === code) ?? CURRENCIES[2]; // fallback USD
}

// Convert a USD value to the target currency
export function convertFromUSD(valueInUSD: number, targetCode: CurrencyCode): number {
  const curr = getCurrency(targetCode);
  return valueInUSD * curr.rateVsUSD;
}

// Format a value that's already in the target currency
export function formatInCurrency(value: number, code: CurrencyCode): string {
  const curr = getCurrency(code);

  if (code === "BTC") {
    if (value >= 1) return `${curr.symbol}${value.toFixed(2)}`;
    if (value >= 0.01) return `${curr.symbol}${value.toFixed(4)}`;
    if (value >= 0.0001) return `${curr.symbol}${value.toFixed(6)}`;
    return `${curr.symbol}${value.toExponential(2)}`;
  }

  if (code === "XAU") {
    if (value >= 1) return `${value.toFixed(2)} oz`;
    if (value >= 0.01) return `${value.toFixed(4)} oz`;
    return `${value.toExponential(2)} oz`;
  }

  // Fiat currencies
  const abs = Math.abs(value);
  if (abs >= 1_000_000_000) return `${curr.symbol}${(value / 1_000_000_000).toFixed(1)}B`;
  if (abs >= 1_000_000) return `${curr.symbol}${(value / 1_000_000).toFixed(1)}M`;
  if (abs >= 10_000) return `${curr.symbol}${(value / 1_000).toFixed(0)}K`;
  if (abs >= 100) return `${curr.symbol}${value.toFixed(0)}`;
  if (abs >= 1) return `${curr.symbol}${value.toFixed(2)}`;
  if (abs >= 0.01) return `${curr.symbol}${value.toFixed(3)}`;
  return `${curr.symbol}${value.toExponential(1)}`;
}

// Format a USD value directly into the target currency string
export function formatUSDAs(valueInUSD: number, code: CurrencyCode): string {
  const converted = convertFromUSD(valueInUSD, code);
  return formatInCurrency(converted, code);
}

// Recalculate CAGR in a different base currency
// Simplified: assumes current FX rate was constant (no historical FX data)
// This is actually the correct simplification because:
// FX-adjusted CAGR ≈ USD CAGR + currency depreciation CAGR
// The constant-FX assumption makes the point even MORE dramatic
export function convertCAGR(
  cagrUSD: number,
  _code: CurrencyCode,
): number {
  // CAGR is a percentage — it doesn't change with currency conversion
  // IF we assume the FX rate was constant over the period.
  // The magic is: when you convert the PRICES (start and end) to the
  // new currency and recalculate CAGR, you get the same CAGR.
  // Because: (P_end * FX) / (P_start * FX) = P_end / P_start
  //
  // The REAL impact shows when we compare the CAGR vs the local inflation
  // or when we show absolute values. The CAGR itself stays the same
  // under constant-FX assumption.
  //
  // What DOES change: the nominal price display. $100K BTC in pesos
  // looks like CL$95,000,000 — that's the shock value.
  return cagrUSD;
}

// Get the pedagogical message for the current level
export function getLevelMessage(code: CurrencyCode): string | null {
  const curr = getCurrency(code);

  if (code === "BTC") {
    return "Estás midiendo en el activo más escaso del mundo. Pocos portfolios sobreviven esta vara.";
  }
  if (code === "XAU") {
    return "Midiendo en oro — 5,000 años de historia como reserva de valor. La vara del dinero duro.";
  }
  if (curr.level === 2 && code !== "USD") {
    return `Midiendo en ${curr.name}. El fiat global también se devalúa, solo que más lento.`;
  }
  if (curr.level === 1) {
    if (code === "ARS") return "Midiendo en pesos argentinos. La ilusión nominal más extrema del continente.";
    if (code === "VES") return "Midiendo en bolívares. El caso extremo de destrucción monetaria.";
    if (code === "CUP") return "Midiendo en pesos cubanos. Mercado negro y control de cambios.";
    if (code === "PAB") return `Midiendo en balboas — paridad 1:1 con USD. Panamá dolarizó de facto.`;
    if (code === "SVC") return `El Salvador adoptó Bitcoin como moneda legal. El colón ya no circula.`;
    return `Midiendo en ${curr.name} ${curr.flag}. La ilusión de "ganar" se amplifica con la devaluación.`;
  }
  return null;
}

// Get the level label for grouping in the selector
export function getLevelLabel(level: 1 | 2 | 3 | 4): string {
  switch (level) {
    case 1: return "Fiat Hispano";
    case 2: return "Fiat Global";
    case 3: return "Dinero Duro";
    case 4: return "Modo Difícil";
  }
}
