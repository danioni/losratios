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
  { code: "BTC", name: "Bitcoin", flag: "₿", symbol: "₿", level: 4, rateVsUSD: 1 / 67650, country: "Descentralizado" },
  // ── Nivel 3: Dinero duro ──
  { code: "XAU", name: "Oro (oz)", flag: "🥇", symbol: "XAU", level: 3, rateVsUSD: 1 / 5162, country: "Global" },
  // ── Nivel 2: Fiat global ──
  { code: "USD", name: "Dólar USA", flag: "🇺🇸", symbol: "$", level: 2, rateVsUSD: 1, country: "Estados Unidos" },
  { code: "EUR", name: "Euro", flag: "🇪🇺", symbol: "€", level: 2, rateVsUSD: 0.848, country: "Eurozona" },
  { code: "BRL", name: "Real", flag: "🇧🇷", symbol: "R$", level: 2, rateVsUSD: 5.15, country: "Brasil" },
  // ── Nivel 1: Fiat hispano — la masacre ──
  { code: "MXN", name: "Peso MX", flag: "🇲🇽", symbol: "MX$", level: 1, rateVsUSD: 17.24, country: "México" },
  { code: "CLP", name: "Peso CL", flag: "🇨🇱", symbol: "CL$", level: 1, rateVsUSD: 857, country: "Chile" },
  { code: "COP", name: "Peso CO", flag: "🇨🇴", symbol: "CO$", level: 1, rateVsUSD: 3749, country: "Colombia" },
  { code: "ARS", name: "Peso AR", flag: "🇦🇷", symbol: "AR$", level: 1, rateVsUSD: 1408, country: "Argentina" },
  { code: "PEN", name: "Sol", flag: "🇵🇪", symbol: "S/", level: 1, rateVsUSD: 3.36, country: "Perú" },
  { code: "UYU", name: "Peso UY", flag: "🇺🇾", symbol: "UY$", level: 1, rateVsUSD: 38.4, country: "Uruguay" },
  { code: "PYG", name: "Guaraní", flag: "🇵🇾", symbol: "₲", level: 1, rateVsUSD: 6441, country: "Paraguay" },
  { code: "BOB", name: "Boliviano", flag: "🇧🇴", symbol: "Bs", level: 1, rateVsUSD: 6.91, country: "Bolivia" },
  { code: "CRC", name: "Colón CR", flag: "🇨🇷", symbol: "₡", level: 1, rateVsUSD: 473, country: "Costa Rica" },
  { code: "GTQ", name: "Quetzal", flag: "🇬🇹", symbol: "Q", level: 1, rateVsUSD: 7.67, country: "Guatemala" },
  { code: "HNL", name: "Lempira", flag: "🇭🇳", symbol: "L", level: 1, rateVsUSD: 26.5, country: "Honduras" },
  { code: "NIO", name: "Córdoba", flag: "🇳🇮", symbol: "C$", level: 1, rateVsUSD: 36.8, country: "Nicaragua" },
  { code: "DOP", name: "Peso RD", flag: "🇩🇴", symbol: "RD$", level: 1, rateVsUSD: 60.2, country: "Rep. Dominicana" },
  { code: "PAB", name: "Balboa", flag: "🇵🇦", symbol: "B/.", level: 1, rateVsUSD: 1, country: "Panamá" },
  { code: "CUP", name: "Peso CU", flag: "🇨🇺", symbol: "CU$", level: 1, rateVsUSD: 24, country: "Cuba" },
  { code: "VES", name: "Bolívar", flag: "🇻🇪", symbol: "Bs.S", level: 1, rateVsUSD: 411, country: "Venezuela" },
  { code: "SVC", name: "ex-Colón SV", flag: "🇸🇻", symbol: "₡SV", level: 1, rateVsUSD: 1, country: "El Salvador (USD/BTC)" },
];

// ============================================================
// Historical FX anchors (units of local currency per 1 USD)
// All normalized to CURRENT currency unit (post all redenominations)
// Sources: FRED/Penn World Table (1971-2010), XE.com (2015-2026)
// ============================================================
const FX_ANCHORS: Partial<Record<CurrencyCode, { year: number; rate: number }[]>> = {
  EUR: [
    { year: 1971, rate: 1.759 }, { year: 1980, rate: 0.931 }, { year: 1990, rate: 0.828 },
    { year: 2000, rate: 1.085 }, { year: 2010, rate: 0.755 }, { year: 2015, rate: 0.920 },
    { year: 2020, rate: 0.818 }, { year: 2021, rate: 0.879 }, { year: 2024, rate: 0.966 },
    { year: 2025, rate: 0.852 }, { year: 2026, rate: 0.848 },
  ],
  BRL: [
    // Normalized to current BRL (1 BRL = 2.75e12 cruzeiros novos)
    { year: 1971, rate: 1.80e-12 }, // 4.95 Cr$/USD
    { year: 1980, rate: 1.60e-11 }, // 43.89 Cr$/USD
    { year: 1985, rate: 1.21e-9 },  // 3,318 Cr$/USD (pre-cruzado, hyperinflation)
    { year: 1990, rate: 4.99e-6 },  // 13.7 Cr$(1990)/USD
    { year: 1995, rate: 0.847 },    // first full year of BRL
    { year: 2000, rate: 1.829 },
    { year: 2010, rate: 1.759 },
    { year: 2015, rate: 3.961 },
    { year: 2020, rate: 5.194 },
    { year: 2021, rate: 5.571 },
    { year: 2024, rate: 6.185 },
    { year: 2025, rate: 5.504 },
    { year: 2026, rate: 5.152 },
  ],
  MXN: [
    { year: 1971, rate: 0.0125 }, { year: 1980, rate: 0.023 }, { year: 1990, rate: 2.813 },
    { year: 2000, rate: 9.456 }, { year: 2010, rate: 12.636 }, { year: 2015, rate: 17.250 },
    { year: 2020, rate: 19.894 }, { year: 2021, rate: 20.495 }, { year: 2024, rate: 20.863 },
    { year: 2025, rate: 18.007 }, { year: 2026, rate: 17.242 },
  ],
  ARS: [
    // Normalized to current ARS (1 ARS = 10^11 pesos ley = 10^13 pesos moneda nacional)
    { year: 1971, rate: 4.52e-11 }, // ~5 pesos ley/USD (FRED normalized)
    { year: 1980, rate: 1.8e-8 },   // ~1,800 pesos ley/USD (pre-Malvinas)
    { year: 1990, rate: 0.488 },     // ~4,876 australes/USD
    { year: 2000, rate: 1.0 },       // convertibilidad 1:1
    { year: 2010, rate: 3.896 },
    { year: 2015, rate: 12.943 },
    { year: 2020, rate: 84.068 },
    { year: 2021, rate: 102.682 },
    { year: 2024, rate: 1031 },
    { year: 2025, rate: 1370 },      // ~dic 2025 (crawling peg Milei)
    { year: 2026, rate: 1406 },
  ],
  CLP: [
    { year: 1971, rate: 0.012 }, { year: 1980, rate: 39 }, { year: 1990, rate: 305 },
    { year: 2000, rate: 540 }, { year: 2010, rate: 510 }, { year: 2015, rate: 709 },
    { year: 2020, rate: 750 },  // corrected (710 was intra-year low)
    { year: 2021, rate: 851 }, { year: 2024, rate: 994 },
    { year: 2025, rate: 900 }, { year: 2026, rate: 857 }, // updated to current
  ],
  COP: [
    { year: 1971, rate: 19.9 }, { year: 1980, rate: 47.3 }, { year: 1990, rate: 502 },
    { year: 2000, rate: 2088 }, { year: 2010, rate: 1899 }, { year: 2015, rate: 3174 },
    { year: 2020, rate: 3420 }, { year: 2021, rate: 4070 }, { year: 2024, rate: 4406 },
    { year: 2025, rate: 3770 }, { year: 2026, rate: 3749 },
  ],
  PEN: [
    { year: 2000, rate: 3.49 }, { year: 2010, rate: 2.825 }, { year: 2015, rate: 3.409 },
    { year: 2020, rate: 3.617 }, { year: 2021, rate: 3.987 }, { year: 2024, rate: 3.760 },
    { year: 2025, rate: 3.365 }, { year: 2026, rate: 3.355 },
  ],
  UYU: [
    { year: 2000, rate: 12.1 }, { year: 2010, rate: 20.06 }, { year: 2015, rate: 29.9 },
    { year: 2020, rate: 42.35 }, { year: 2021, rate: 44.72 }, { year: 2024, rate: 43.7 },
    { year: 2025, rate: 39.06 }, { year: 2026, rate: 38.42 },
  ],
  PYG: [
    { year: 1971, rate: 126 }, { year: 1980, rate: 126 }, { year: 1990, rate: 1230 },
    { year: 2000, rate: 3486 }, { year: 2010, rate: 4743 }, { year: 2015, rate: 5782 },
    { year: 2020, rate: 6913 }, { year: 2021, rate: 6798 }, { year: 2024, rate: 7814 },
    { year: 2025, rate: 6671 }, { year: 2026, rate: 6441 },
  ],
  BOB: [
    { year: 1990, rate: 3.17 }, { year: 2000, rate: 6.18 }, { year: 2010, rate: 7.02 },
    { year: 2015, rate: 6.90 }, { year: 2020, rate: 6.89 }, { year: 2021, rate: 6.90 },
    { year: 2024, rate: 6.92 }, { year: 2025, rate: 6.93 }, { year: 2026, rate: 6.91 },
  ],
  CRC: [
    { year: 1971, rate: 6.63 }, { year: 1980, rate: 8.57 }, { year: 1990, rate: 91.6 },
    { year: 2000, rate: 308 }, { year: 2010, rate: 524 }, { year: 2015, rate: 537 },
    { year: 2020, rate: 609 }, { year: 2021, rate: 642 }, { year: 2024, rate: 508 },
    { year: 2025, rate: 497 }, { year: 2026, rate: 473 },
  ],
  GTQ: [
    { year: 1971, rate: 1.0 }, { year: 1980, rate: 1.0 }, { year: 1990, rate: 4.49 },
    { year: 2000, rate: 7.76 }, { year: 2010, rate: 8.06 }, { year: 2015, rate: 7.63 },
    { year: 2020, rate: 7.79 }, { year: 2021, rate: 7.72 }, { year: 2024, rate: 7.71 },
    { year: 2025, rate: 7.67 }, { year: 2026, rate: 7.67 },
  ],
  HNL: [
    { year: 1971, rate: 2.0 }, { year: 1980, rate: 2.0 }, { year: 1990, rate: 4.11 },
    { year: 2000, rate: 14.84 }, { year: 2010, rate: 18.9 }, { year: 2015, rate: 22.25 },
    { year: 2020, rate: 24.09 }, { year: 2021, rate: 24.4 }, { year: 2024, rate: 25.42 },
    { year: 2025, rate: 26.4 }, { year: 2026, rate: 26.49 },
  ],
  NIO: [
    { year: 2000, rate: 12.68 }, { year: 2010, rate: 21.36 }, { year: 2015, rate: 27.65 },
    { year: 2020, rate: 34.92 }, { year: 2021, rate: 35.4 }, { year: 2024, rate: 36.81 },
    { year: 2025, rate: 36.81 }, { year: 2026, rate: 36.76 },
  ],
  DOP: [
    { year: 1971, rate: 1.0 }, { year: 1980, rate: 1.0 }, { year: 1990, rate: 8.53 },
    { year: 2000, rate: 16.42 }, { year: 2010, rate: 36.88 }, { year: 2015, rate: 45.53 },
    { year: 2020, rate: 58.16 }, { year: 2021, rate: 57.29 }, { year: 2024, rate: 61.11 },
    { year: 2025, rate: 63.09 }, { year: 2026, rate: 60.19 },
  ],
  VES: [
    { year: 2010, rate: 2.59e-11 }, { year: 2015, rate: 6.3e-11 },
    { year: 2021, rate: 4.588 }, { year: 2024, rate: 51.96 },
    { year: 2025, rate: 298 }, { year: 2026, rate: 411 },
  ],
  SVC: [
    { year: 1971, rate: 2.5 }, { year: 1990, rate: 8.03 }, { year: 2000, rate: 8.75 },
    { year: 2026, rate: 8.75 }, // dollarized since 2001
  ],
  CUP: [
    { year: 1971, rate: 1.0 }, { year: 2000, rate: 21.0 }, { year: 2010, rate: 24.0 },
    { year: 2021, rate: 24.0 }, { year: 2026, rate: 24.0 },
  ],
};

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

// Get interpolated FX rate for a given currency and year
export function getFXRate(code: CurrencyCode, year: number): number | null {
  if (code === "USD" || code === "PAB") return 1; // always 1:1
  if (code === "BTC" || code === "XAU") return null; // handled separately

  const anchors = FX_ANCHORS[code];
  if (!anchors || anchors.length === 0) return null;

  // Before first anchor
  if (year <= anchors[0].year) return anchors[0].rate;
  // After last anchor
  if (year >= anchors[anchors.length - 1].year) return anchors[anchors.length - 1].rate;

  // Find surrounding anchors and interpolate geometrically
  for (let i = 0; i < anchors.length - 1; i++) {
    if (year >= anchors[i].year && year <= anchors[i + 1].year) {
      const a = anchors[i];
      const b = anchors[i + 1];
      const t = (year - a.year) / (b.year - a.year);
      // Geometric interpolation for FX rates (exponential depreciation)
      if (a.rate > 0 && b.rate > 0) {
        return a.rate * Math.pow(b.rate / a.rate, t);
      }
      return a.rate + (b.rate - a.rate) * t; // linear fallback
    }
  }
  return anchors[anchors.length - 1].rate;
}

// Get the first year with reliable FX data for a currency
export function getFirstFXYear(code: CurrencyCode): number | null {
  if (code === "USD" || code === "PAB") return 1900; // always available
  if (code === "BTC" || code === "XAU") return null;
  const anchors = FX_ANCHORS[code];
  if (!anchors || anchors.length === 0) return null;
  return anchors[0].year;
}

// Recalculate CAGR in a different base currency using historical FX data
// When the asset predates available FX data, we compute the FX depreciation
// rate only over the period with reliable data and apply it to the full CAGR.
// This avoids clamping (which dilutes the real depreciation rate).
export function convertCAGR(
  cagrUSD: number,
  code: CurrencyCode,
  startYear?: number,
  endYear?: number,
): number {
  if (code === "USD" || code === "PAB" || code === "BTC" || code === "XAU") return cagrUSD;

  const start = startYear ?? 2000;
  const end = endYear ?? 2026;
  const years = end - start;
  if (years <= 0) return cagrUSD;

  const anchors = FX_ANCHORS[code];
  if (!anchors || anchors.length === 0) return cagrUSD;

  const firstFXYear = anchors[0].year;
  const fxEnd = getFXRate(code, end);
  if (!fxEnd || fxEnd <= 0) return cagrUSD;

  // Use the actual FX data period (don't clamp pre-anchor years)
  const effectiveFXStart = Math.max(start, firstFXYear);
  const fxStart = getFXRate(code, effectiveFXStart);
  if (!fxStart || fxStart <= 0) return cagrUSD;

  // FX depreciation rate computed only over the period with real data
  const fxYears = end - effectiveFXStart;
  if (fxYears <= 0) return cagrUSD;

  const usdDecimal = cagrUSD / 100;
  const fxGrowth = Math.pow(fxEnd / fxStart, 1 / fxYears);
  return ((1 + usdDecimal) * fxGrowth - 1) * 100;
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
