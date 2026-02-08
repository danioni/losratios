// ============================================================
// Los Ratios — Mock Data Layer
// Puramente cross-asset: Activo A ÷ Activo B
// Detectar qué está relativamente caro o barato entre activos
// Structure ready for real API integration (CoinGecko, FRED, Yahoo Finance)
// ============================================================

export interface AssetDataPoint {
  date: string;
  btc: number;
  gold: number;
  silver: number;
  sp500: number;
  realEstate: number; // Case-Shiller index
  tesla: number;
  msciWorld: number;
  // Stock-to-flow
  btcS2F: number;
  goldS2F: number;
  silverS2F: number;
  // Market caps (trillions USD)
  btcMcap: number;
  goldMcap: number;
  silverMcap: number;
  equitiesMcap: number;
  realEstateMcap: number;
  bondsMcap: number;
}

export interface DominanceDataPoint {
  date: string;
  btcDom: number;
  goldDom: number;
  silverDom: number;
  equitiesDom: number;
  realEstateDom: number;
  bondsDom: number;
  total: number;
}

export interface RatioDataPoint {
  date: string;
  // Cross-asset ratios
  btcGold: number;
  goldSilver: number;
  btcSp500: number;
  realEstateGold: number;
  sp500Gold: number;
  btcRealEstate: number;
  teslaGold: number;
  teslaBtc: number;
  // S2F-adjusted
  btcGoldS2F: number;
  btcSilverS2F: number;
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
  context: string; // short interpretation
}

// Historical anchor data points (annual from 2014-2025)
// Market caps in trillions USD (approximate)
const anchors: AssetDataPoint[] = [
  { date: "2014", btc: 320, gold: 1266, silver: 19.1, sp500: 2059, realEstate: 171, tesla: 44, msciWorld: 1710, btcS2F: 25, goldS2F: 62, silverS2F: 22, btcMcap: 0.005, goldMcap: 7.5, silverMcap: 0.5, equitiesMcap: 65, realEstateMcap: 220, bondsMcap: 100 },
  { date: "2015", btc: 430, gold: 1160, silver: 15.7, sp500: 2044, realEstate: 179, tesla: 43, msciWorld: 1663, btcS2F: 25, goldS2F: 62, silverS2F: 22, btcMcap: 0.007, goldMcap: 7.0, silverMcap: 0.4, equitiesMcap: 67, realEstateMcap: 230, bondsMcap: 105 },
  { date: "2016", btc: 960, gold: 1251, silver: 17.1, sp500: 2239, realEstate: 189, tesla: 42, msciWorld: 1751, btcS2F: 25, goldS2F: 62, silverS2F: 22, btcMcap: 0.015, goldMcap: 7.6, silverMcap: 0.5, equitiesMcap: 70, realEstateMcap: 240, bondsMcap: 110 },
  { date: "2017", btc: 14000, gold: 1303, silver: 17.1, sp500: 2674, realEstate: 200, tesla: 62, msciWorld: 2103, btcS2F: 25, goldS2F: 62, silverS2F: 22, btcMcap: 0.23, goldMcap: 7.8, silverMcap: 0.5, equitiesMcap: 80, realEstateMcap: 260, bondsMcap: 115 },
  { date: "2018", btc: 3800, gold: 1282, silver: 15.5, sp500: 2507, realEstate: 211, tesla: 60, msciWorld: 1884, btcS2F: 25, goldS2F: 62, silverS2F: 22, btcMcap: 0.066, goldMcap: 7.7, silverMcap: 0.4, equitiesMcap: 75, realEstateMcap: 270, bondsMcap: 115 },
  { date: "2019", btc: 7200, gold: 1517, silver: 17.9, sp500: 3231, realEstate: 220, tesla: 84, msciWorld: 2358, btcS2F: 25, goldS2F: 62, silverS2F: 22, btcMcap: 0.13, goldMcap: 9.0, silverMcap: 0.5, equitiesMcap: 88, realEstateMcap: 280, bondsMcap: 120 },
  { date: "2020", btc: 28900, gold: 1898, silver: 26.5, sp500: 3756, realEstate: 239, tesla: 705, msciWorld: 2690, btcS2F: 56, goldS2F: 62, silverS2F: 22, btcMcap: 0.54, goldMcap: 11.5, silverMcap: 0.7, equitiesMcap: 95, realEstateMcap: 290, bondsMcap: 130 },
  { date: "2021", btc: 47000, gold: 1829, silver: 23.4, sp500: 4766, realEstate: 276, tesla: 1056, msciWorld: 3230, btcS2F: 56, goldS2F: 62, silverS2F: 22, btcMcap: 0.9, goldMcap: 11.0, silverMcap: 0.6, equitiesMcap: 120, realEstateMcap: 330, bondsMcap: 130 },
  { date: "2022", btc: 16500, gold: 1824, silver: 24.0, sp500: 3840, realEstate: 308, tesla: 123, msciWorld: 2602, btcS2F: 56, goldS2F: 62, silverS2F: 22, btcMcap: 0.32, goldMcap: 11.0, silverMcap: 0.6, equitiesMcap: 98, realEstateMcap: 340, bondsMcap: 125 },
  { date: "2023", btc: 42200, gold: 2063, silver: 24.1, sp500: 4770, realEstate: 312, tesla: 248, msciWorld: 3169, btcS2F: 56, goldS2F: 62, silverS2F: 22, btcMcap: 0.82, goldMcap: 12.5, silverMcap: 0.6, equitiesMcap: 110, realEstateMcap: 350, bondsMcap: 133 },
  { date: "2024", btc: 93000, gold: 2625, silver: 30.5, sp500: 5881, realEstate: 324, tesla: 421, msciWorld: 3700, btcS2F: 120, goldS2F: 62, silverS2F: 22, btcMcap: 1.84, goldMcap: 16.0, silverMcap: 0.8, equitiesMcap: 120, realEstateMcap: 360, bondsMcap: 140 },
  { date: "2025", btc: 97000, gold: 2850, silver: 31.8, sp500: 6020, realEstate: 330, tesla: 390, msciWorld: 3750, btcS2F: 120, goldS2F: 62, silverS2F: 22, btcMcap: 1.92, goldMcap: 18.0, silverMcap: 0.9, equitiesMcap: 122, realEstateMcap: 365, bondsMcap: 140 },
];

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
        btcS2F: lerp(a.btcS2F, b.btcS2F, t),
        goldS2F: lerp(a.goldS2F, b.goldS2F, t),
        silverS2F: lerp(a.silverS2F, b.silverS2F, t),
        btcMcap: lerp(a.btcMcap, b.btcMcap, t),
        goldMcap: lerp(a.goldMcap, b.goldMcap, t),
        silverMcap: lerp(a.silverMcap, b.silverMcap, t),
        equitiesMcap: lerp(a.equitiesMcap, b.equitiesMcap, t),
        realEstateMcap: lerp(a.realEstateMcap, b.realEstateMcap, t),
        bondsMcap: lerp(a.bondsMcap, b.bondsMcap, t),
      });
    }
  }

  const last = anchors[anchors.length - 1];
  result.push({ ...last, date: `${last.date}-01` });
  return result;
}

// Compute cross-asset ratios only
function computeRatios(assets: AssetDataPoint[]): RatioDataPoint[] {
  return assets.map((d) => ({
    date: d.date,
    btcGold: d.btc / d.gold,
    goldSilver: d.gold / d.silver,
    btcSp500: d.btc / d.sp500,
    realEstateGold: (d.realEstate * 1000) / d.gold,
    sp500Gold: d.sp500 / d.gold,
    btcRealEstate: d.btc / (d.realEstate * 1000),
    teslaGold: d.tesla / d.gold,
    teslaBtc: d.tesla / d.btc,
    // S2F-adjusted
    btcGoldS2F: (d.btc / d.gold) / (d.btcS2F / d.goldS2F),
    btcSilverS2F: (d.btc / d.silver) / (d.btcS2F / d.silverS2F),
  }));
}

function computeStats(values: number[]): { mean: number; stdDev: number } {
  const n = values.length;
  const mean = values.reduce((s, v) => s + v, 0) / n;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / n;
  return { mean, stdDev: Math.sqrt(variance) };
}

function getSignal(zScore: number, pair: string): { signal: string; signalType: "overbought" | "oversold" | "neutral"; context: string } {
  const parts = pair.split(" / ");
  const a = parts[0];
  const b = parts[1];

  if (zScore > 2) return {
    signal: "Fuertemente sobrecomprado",
    signalType: "overbought",
    context: `${a} muy caro vs ${b}`,
  };
  if (zScore > 1) return {
    signal: "Sobrecomprado",
    signalType: "overbought",
    context: `${a} caro relativo a ${b}`,
  };
  if (zScore < -2) return {
    signal: "Fuertemente sobrevendido",
    signalType: "oversold",
    context: `${a} muy barato vs ${b}`,
  };
  if (zScore < -1) return {
    signal: "Sobrevendido",
    signalType: "oversold",
    context: `${a} barato relativo a ${b}`,
  };
  return { signal: "Neutral", signalType: "neutral", context: "En equilibrio relativo" };
}

const rawAssets = generateMonthlyData();
const ratioData = computeRatios(rawAssets);

function buildSummaries(): RatioSummary[] {
  const pairs: { name: string; pair: string; key: keyof RatioDataPoint }[] = [
    { name: "BTC ÷ Oro", pair: "BTC / Oro", key: "btcGold" },
    { name: "Oro ÷ Plata", pair: "Oro / Plata", key: "goldSilver" },
    { name: "BTC ÷ S&P 500", pair: "BTC / S&P 500", key: "btcSp500" },
    { name: "S&P 500 ÷ Oro", pair: "S&P 500 / Oro", key: "sp500Gold" },
    { name: "Real Estate ÷ Oro", pair: "Real Estate / Oro", key: "realEstateGold" },
    { name: "BTC ÷ Real Estate", pair: "BTC / Real Estate", key: "btcRealEstate" },
    { name: "Tesla ÷ Oro", pair: "Tesla / Oro", key: "teslaGold" },
    { name: "Tesla ÷ BTC", pair: "Tesla / BTC", key: "teslaBtc" },
    { name: "BTC ÷ Oro (S2F)", pair: "BTC / Oro (S2F)", key: "btcGoldS2F" },
  ];

  return pairs.map(({ name, pair, key }) => {
    const values = ratioData.map((d) => d[key] as number);
    const { mean, stdDev } = computeStats(values);
    const current = values[values.length - 1];
    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;
    const { signal, signalType, context } = getSignal(zScore, pair);

    return { name, pair, current, mean, stdDev, zScore, signal, signalType, context };
  });
}

// Rotation signals
export interface RotationSignal {
  message: string;
  type: "rotate_from" | "rotate_to" | "watch";
  pair: string;
  zScore: number;
}

function buildRotationSignals(sums: RatioSummary[]): RotationSignal[] {
  const signals: RotationSignal[] = [];

  for (const s of sums) {
    const parts = s.pair.split(" / ");
    if (s.zScore > 1.5) {
      signals.push({
        message: `${parts[0]} caro relativo a ${parts[1]} — considerar rotación hacia ${parts[1]}`,
        type: "rotate_from",
        pair: s.pair,
        zScore: s.zScore,
      });
    } else if (s.zScore < -1.5) {
      signals.push({
        message: `${parts[0]} barato relativo a ${parts[1]} — oportunidad de acumular ${parts[0]}`,
        type: "rotate_to",
        pair: s.pair,
        zScore: s.zScore,
      });
    }
  }

  return signals.sort((a, b) => Math.abs(b.zScore) - Math.abs(a.zScore));
}

// Compute dominance (market cap share)
function computeDominance(assets: AssetDataPoint[]): DominanceDataPoint[] {
  return assets.map((d) => {
    const total = d.btcMcap + d.goldMcap + d.silverMcap + d.equitiesMcap + d.realEstateMcap + d.bondsMcap;
    return {
      date: d.date,
      btcDom: (d.btcMcap / total) * 100,
      goldDom: (d.goldMcap / total) * 100,
      silverDom: (d.silverMcap / total) * 100,
      equitiesDom: (d.equitiesMcap / total) * 100,
      realEstateDom: (d.realEstateMcap / total) * 100,
      bondsDom: (d.bondsMcap / total) * 100,
      total,
    };
  });
}

const dominanceData = computeDominance(rawAssets);

// Exports
export const assetData = rawAssets;
export const ratios = ratioData;
export const dominance = dominanceData;
export const summaries = buildSummaries();
export const rotationSignals = buildRotationSignals(summaries);

export function getFilteredData(timeframe: string): { assets: AssetDataPoint[]; ratios: RatioDataPoint[]; dominance: DominanceDataPoint[] } {
  const months = timeframe === "1Y" ? 12 : timeframe === "3Y" ? 36 : timeframe === "5Y" ? 60 : timeframe === "10Y" ? 120 : rawAssets.length;
  const sliced = rawAssets.slice(-months);
  return {
    assets: sliced,
    ratios: computeRatios(sliced),
    dominance: computeDominance(sliced),
  };
}

export function formatRatio(value: number): string {
  if (value >= 10000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (value >= 100) return value.toFixed(1);
  if (value >= 1) return value.toFixed(2);
  if (value >= 0.01) return value.toFixed(4);
  return value.toExponential(2);
}
