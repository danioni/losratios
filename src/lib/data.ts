// ============================================================
// Los Ratios — Mock Data Layer
// Cross-asset ratios & pair detection
// Structure ready for real API integration (CoinGecko, FRED, Yahoo Finance)
// ============================================================

export interface AssetDataPoint {
  date: string;
  // Raw prices / values
  btc: number;
  gold: number;
  silver: number;
  sp500: number;
  realEstate: number; // Case-Shiller index
  tesla: number;
  msciWorld: number;
  // Global liquidity (denominator)
  m2Global: number; // in trillions USD
  // Stock-to-flow
  btcS2F: number;
  goldS2F: number;
  silverS2F: number;
}

export interface RatioDataPoint {
  date: string;
  // Activo ÷ Denominador (M2-adjusted)
  btcM2: number;
  goldM2: number;
  silverM2: number;
  sp500M2: number;
  realEstateM2: number;
  teslaM2: number;
  msciWorldM2: number;
  // Cross-asset ratios
  btcGold: number;
  goldSilver: number;
  btcSp500: number;
  realEstateGold: number;
  // S2F-adjusted
  btcGoldS2F: number;
}

export interface RatioSummary {
  name: string;
  pair: string;
  current: number;
  mean: number;
  stdDev: number;
  zScore: number;
  signal: string;
  signalType: "overbought" | "oversold" | "neutral";
}

// Historical anchor data points (annual from 2014-2025)
// Based on approximate historical values
const anchors: AssetDataPoint[] = [
  { date: "2014", btc: 320, gold: 1266, silver: 19.1, sp500: 2059, realEstate: 171, tesla: 44, msciWorld: 1710, m2Global: 66, btcS2F: 25, goldS2F: 62, silverS2F: 22 },
  { date: "2015", btc: 430, gold: 1160, silver: 15.7, sp500: 2044, realEstate: 179, tesla: 43, msciWorld: 1663, m2Global: 68, btcS2F: 25, goldS2F: 62, silverS2F: 22 },
  { date: "2016", btc: 960, gold: 1251, silver: 17.1, sp500: 2239, realEstate: 189, tesla: 42, msciWorld: 1751, m2Global: 72, btcS2F: 25, goldS2F: 62, silverS2F: 22 },
  { date: "2017", btc: 14000, gold: 1303, silver: 17.1, sp500: 2674, realEstate: 200, tesla: 62, msciWorld: 2103, m2Global: 78, btcS2F: 25, goldS2F: 62, silverS2F: 22 },
  { date: "2018", btc: 3800, gold: 1282, silver: 15.5, sp500: 2507, realEstate: 211, tesla: 60, msciWorld: 1884, m2Global: 81, btcS2F: 25, goldS2F: 62, silverS2F: 22 },
  { date: "2019", btc: 7200, gold: 1517, silver: 17.9, sp500: 3231, realEstate: 220, tesla: 84, msciWorld: 2358, m2Global: 84, btcS2F: 25, goldS2F: 62, silverS2F: 22 },
  { date: "2020", btc: 28900, gold: 1898, silver: 26.5, sp500: 3756, realEstate: 239, tesla: 705, msciWorld: 2690, m2Global: 94, btcS2F: 56, goldS2F: 62, silverS2F: 22 },
  { date: "2021", btc: 47000, gold: 1829, silver: 23.4, sp500: 4766, realEstate: 276, tesla: 1056, msciWorld: 3230, m2Global: 102, btcS2F: 56, goldS2F: 62, silverS2F: 22 },
  { date: "2022", btc: 16500, gold: 1824, silver: 24.0, sp500: 3840, realEstate: 308, tesla: 123, msciWorld: 2602, m2Global: 98, btcS2F: 56, goldS2F: 62, silverS2F: 22 },
  { date: "2023", btc: 42200, gold: 2063, silver: 24.1, sp500: 4770, realEstate: 312, tesla: 248, msciWorld: 3169, m2Global: 100, btcS2F: 56, goldS2F: 62, silverS2F: 22 },
  { date: "2024", btc: 93000, gold: 2625, silver: 30.5, sp500: 5881, realEstate: 324, tesla: 421, msciWorld: 3700, m2Global: 105, btcS2F: 120, goldS2F: 62, silverS2F: 22 },
  { date: "2025", btc: 97000, gold: 2850, silver: 31.8, sp500: 6020, realEstate: 330, tesla: 390, msciWorld: 3750, m2Global: 108, btcS2F: 120, goldS2F: 62, silverS2F: 22 },
];

// Generate monthly data via interpolation between annual anchors
function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function generateMonthlyData(): AssetDataPoint[] {
  const result: AssetDataPoint[] = [];

  for (let i = 0; i < anchors.length - 1; i++) {
    const a = anchors[i];
    const b = anchors[i + 1];

    for (let m = 0; m < 12; m++) {
      const t = m / 12;
      // Add some realistic noise
      const noise = () => 1 + (Math.sin(i * 7 + m * 13) * 0.03);
      const noiseSmall = () => 1 + (Math.sin(i * 11 + m * 7) * 0.015);

      result.push({
        date: `${a.date}-${String(m + 1).padStart(2, "0")}`,
        btc: lerp(a.btc, b.btc, t) * noise(),
        gold: lerp(a.gold, b.gold, t) * noiseSmall(),
        silver: lerp(a.silver, b.silver, t) * noiseSmall(),
        sp500: lerp(a.sp500, b.sp500, t) * noiseSmall(),
        realEstate: lerp(a.realEstate, b.realEstate, t),
        tesla: lerp(a.tesla, b.tesla, t) * noise(),
        msciWorld: lerp(a.msciWorld, b.msciWorld, t) * noiseSmall(),
        m2Global: lerp(a.m2Global, b.m2Global, t),
        btcS2F: lerp(a.btcS2F, b.btcS2F, t),
        goldS2F: lerp(a.goldS2F, b.goldS2F, t),
        silverS2F: lerp(a.silverS2F, b.silverS2F, t),
      });
    }
  }

  // Add final anchor
  const last = anchors[anchors.length - 1];
  result.push({ ...last, date: `${last.date}-01` });

  return result;
}

// Compute ratio data from raw asset data
function computeRatios(assets: AssetDataPoint[]): RatioDataPoint[] {
  // Normalize M2 to base = first point for ratio calculation
  const baseM2 = assets[0].m2Global;

  return assets.map((d) => {
    const m2Norm = d.m2Global / baseM2;
    return {
      date: d.date,
      // Activo ÷ Denominador
      btcM2: d.btc / m2Norm,
      goldM2: d.gold / m2Norm,
      silverM2: d.silver / m2Norm,
      sp500M2: d.sp500 / m2Norm,
      realEstateM2: d.realEstate / m2Norm,
      teslaM2: d.tesla / m2Norm,
      msciWorldM2: d.msciWorld / m2Norm,
      // Cross-asset
      btcGold: d.btc / d.gold,
      goldSilver: d.gold / d.silver,
      btcSp500: d.btc / d.sp500,
      realEstateGold: (d.realEstate * 1000) / d.gold, // Case-Shiller * 1000 for scale
      // S2F-adjusted: ratio weighted by relative S2F
      btcGoldS2F: (d.btc / d.gold) / (d.btcS2F / d.goldS2F),
    };
  });
}

// Calculate statistics for ratio summary
function computeStats(values: number[]): { mean: number; stdDev: number } {
  const n = values.length;
  const mean = values.reduce((s, v) => s + v, 0) / n;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / n;
  return { mean, stdDev: Math.sqrt(variance) };
}

function getSignal(zScore: number): { signal: string; signalType: "overbought" | "oversold" | "neutral" } {
  if (zScore > 2) return { signal: "Fuertemente sobrecomprado", signalType: "overbought" };
  if (zScore > 1) return { signal: "Sobrecomprado", signalType: "overbought" };
  if (zScore < -2) return { signal: "Fuertemente sobrevendido", signalType: "oversold" };
  if (zScore < -1) return { signal: "Sobrevendido", signalType: "oversold" };
  return { signal: "Neutral", signalType: "neutral" };
}

// Generate all data
const rawAssets = generateMonthlyData();
const ratioData = computeRatios(rawAssets);

// Compute summary for all tracked ratios
function buildSummaries(): RatioSummary[] {
  const pairs: { name: string; pair: string; key: keyof RatioDataPoint }[] = [
    { name: "BTC ÷ M2 Global", pair: "BTC / Denominador", key: "btcM2" },
    { name: "Oro ÷ M2 Global", pair: "Oro / Denominador", key: "goldM2" },
    { name: "Plata ÷ M2 Global", pair: "Plata / Denominador", key: "silverM2" },
    { name: "S&P 500 ÷ M2 Global", pair: "S&P 500 / Denominador", key: "sp500M2" },
    { name: "Real Estate ÷ M2 Global", pair: "Real Estate / Denominador", key: "realEstateM2" },
    { name: "BTC ÷ Oro", pair: "BTC / Oro", key: "btcGold" },
    { name: "Oro ÷ Plata", pair: "Oro / Plata", key: "goldSilver" },
    { name: "BTC ÷ S&P 500", pair: "BTC / S&P 500", key: "btcSp500" },
    { name: "Real Estate ÷ Oro", pair: "Real Estate / Oro", key: "realEstateGold" },
    { name: "BTC ÷ Oro (S2F-adj)", pair: "BTC / Oro (S2F)", key: "btcGoldS2F" },
  ];

  return pairs.map(({ name, pair, key }) => {
    const values = ratioData.map((d) => d[key] as number);
    const { mean, stdDev } = computeStats(values);
    const current = values[values.length - 1];
    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;
    const { signal, signalType } = getSignal(zScore);

    return { name, pair, current, mean, stdDev, zScore, signal, signalType };
  });
}

// Rotation signals
export interface RotationSignal {
  message: string;
  type: "rotate_from" | "rotate_to" | "watch";
  pair: string;
  zScore: number;
}

function buildRotationSignals(summaries: RatioSummary[]): RotationSignal[] {
  const signals: RotationSignal[] = [];

  for (const s of summaries) {
    if (s.zScore > 1.5) {
      const parts = s.pair.split(" / ");
      signals.push({
        message: `${parts[0]} caro relativo a ${parts[1]} — considerar rotación`,
        type: "rotate_from",
        pair: s.pair,
        zScore: s.zScore,
      });
    } else if (s.zScore < -1.5) {
      const parts = s.pair.split(" / ");
      signals.push({
        message: `${parts[0]} barato relativo a ${parts[1]} — oportunidad de acumulación`,
        type: "rotate_to",
        pair: s.pair,
        zScore: s.zScore,
      });
    }
  }

  return signals.sort((a, b) => Math.abs(b.zScore) - Math.abs(a.zScore));
}

// Exported data
export const assetData = rawAssets;
export const ratios = ratioData;
export const summaries = buildSummaries();
export const rotationSignals = buildRotationSignals(summaries);

// Helper: get data filtered by timeframe
export function getFilteredData(timeframe: string): { assets: AssetDataPoint[]; ratios: RatioDataPoint[] } {
  const months = timeframe === "1Y" ? 12 : timeframe === "3Y" ? 36 : timeframe === "5Y" ? 60 : timeframe === "10Y" ? 120 : rawAssets.length;
  const sliced = rawAssets.slice(-months);
  return {
    assets: sliced,
    ratios: computeRatios(sliced),
  };
}

// Helper for formatted ratio display
export function formatRatio(value: number): string {
  if (value >= 10000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (value >= 100) return value.toFixed(1);
  if (value >= 1) return value.toFixed(2);
  if (value >= 0.01) return value.toFixed(4);
  return value.toExponential(2);
}

export function formatPercent(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
}
