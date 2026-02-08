// ============================================================
// Los Ratios — Mock Data Layer
// Cross-asset ratios DENTRO de cada asset class
// + BTC vs Todo como sección especial
// + Dominancia por market cap (macro + top 50 acciones)
// + Semáforo de asset classes
// + Performance histórica (CAGR)
// + Proyecciones multi-factor
// + Crypto dominance expandido
// Structure ready for real APIs (CoinGecko, FRED, Yahoo Finance)
// ============================================================

export interface AssetDataPoint {
  date: string;
  // Commodities
  gold: number;
  silver: number;
  oil: number;       // WTI crude
  copper: number;    // USD/lb
  // Equities
  sp500: number;
  nasdaq: number;
  msciWorld: number;
  tesla: number;
  // Real Estate
  caseShiller: number;  // Case-Shiller US index
  // Crypto
  btc: number;
  eth: number;
  sol: number;
  // Market caps (trillions USD)
  btcMcap: number;
  ethMcap: number;
  solMcap: number;
  goldMcap: number;
  silverMcap: number;
  equitiesMcap: number;
  realEstateMcap: number;
  bondsMcap: number;
  cryptoMcap: number;  // total crypto
  m2Global: number;    // M2 Global proxy (trillions USD)
}

// Ratio within a class
export interface ClassRatioDataPoint {
  date: string;
  // Commodities ratios
  goldSilver: number;
  goldOil: number;
  goldCopper: number;
  silverOil: number;
  copperGold: number;
  // Equities ratios
  sp500Nasdaq: number;
  teslaSp500: number;
  sp500Msci: number;
  nasdaqMsci: number;
  // Crypto ratios
  btcEth: number;
  ethSol: number;
  btcSol: number;
  // BTC vs other classes (special section)
  btcGold: number;
  btcSp500: number;
  btcRealEstate: number;
}

export interface DominanceDataPoint {
  date: string;
  goldDom: number;
  silverDom: number;
  equitiesDom: number;
  realEstateDom: number;
  bondsDom: number;
  cryptoDom: number;
  total: number;
}

// ============================================================
// SEMÁFORO DE ASSET CLASSES
// ============================================================
export type SignalLevel = "adelantado" | "alineado" | "rezagado" | "divergente";

export interface AssetClassMetric {
  label: string;
  value: number;
  zScore: number;
  interpretation: string;
}

export interface AssetMomentum {
  pctChange12M: number;
  aboveSma50: boolean;
}

export interface AssetClassSignal {
  assetClass: string;
  icon: string;
  signal: SignalLevel;
  compositeZScore: number;
  nominalZScore: number;
  debasementDelta: number;
  momentum: AssetMomentum;
  metrics: AssetClassMetric[];
  narrative: string;
  actionSignal: string;
}

// ============================================================
// CRYPTO DOMINANCE EXPANDED
// ============================================================
export interface CryptoDominancePoint {
  date: string;
  btcDom: number;
  ethDom: number;
  solDom: number;
  othersDom: number;
}

export interface CryptoRotationSignal {
  phase: "risk_off" | "alt_season" | "neutral";
  btcDomTrend: "rising" | "falling" | "flat";
  narrative: string;
  halvingCyclePosition: string;
}

// ============================================================
// STOCK MOMENTUM
// ============================================================
export interface StockMomentumPoint {
  ticker: string;
  name: string;
  sector: string;
  color: string;
  currentDom: number;
  domChange6M: number;
  domChange3M: number;
  acceleration: number;
  quadrant: "momentum" | "catch_up" | "value_trap" | "declining";
}

export interface ConcentrationMetrics {
  top5Pct: number;
  top10Pct: number;
  hhi: number;
  hhiChange: number;
}

// ============================================================
// BOLLINGER BANDS
// ============================================================
export interface BollingerBandPoint {
  date: string;
  value: number;
  sma: number | null;
  upper1: number | null;
  lower1: number | null;
  upper2: number | null;
  lower2: number | null;
}

// ============================================================
// PERFORMANCE HISTÓRICA (CAGR)
// ============================================================
export interface AssetPerformance {
  ticker: string;
  name: string;
  sector: string;
  marketCap: number;       // billions USD
  ipoYear: number;
  priceStart: number;
  priceCurrent: number;
  years: number;
  cagrHistorical: number;  // % anual
  cagr5Y: number;          // % anual últimos 5 años
}

// ============================================================
// PROYECCIONES MULTI-FACTOR
// ============================================================
export interface AssetProjection {
  ticker: string;
  name: string;
  sector: string;
  priceCurrent: number;
  cagrHistorical: number;
  cagr5Y: number;
  confidence: "low" | "medium" | "high";
  scenarios: {
    conservative: { cagr: number; price5Y: number; price10Y: number };
    base: { cagr: number; price5Y: number; price10Y: number };
    optimistic: { cagr: number; price5Y: number; price10Y: number };
  };
  excessVsBenchmark: number;
}

// ============================================================
// TOP 50 STOCKS DOMINANCE
// ============================================================
export interface StockInfo {
  ticker: string;
  name: string;
  sector: string;
  color: string;
}

export interface StockDominanceDataPoint {
  date: string;
  [ticker: string]: number | string; // ticker -> % dominance
}

export const TOP_STOCKS: StockInfo[] = [
  { ticker: "AAPL", name: "Apple", sector: "Tech", color: "#A2AAAD" },
  { ticker: "MSFT", name: "Microsoft", sector: "Tech", color: "#00A4EF" },
  { ticker: "NVDA", name: "NVIDIA", sector: "Tech", color: "#76B900" },
  { ticker: "AMZN", name: "Amazon", sector: "Consumer", color: "#FF9900" },
  { ticker: "GOOGL", name: "Alphabet", sector: "Tech", color: "#4285F4" },
  { ticker: "META", name: "Meta", sector: "Tech", color: "#0668E1" },
  { ticker: "BRK.B", name: "Berkshire", sector: "Finance", color: "#7B2D8E" },
  { ticker: "TSLA", name: "Tesla", sector: "Auto", color: "#CC0000" },
  { ticker: "LLY", name: "Eli Lilly", sector: "Health", color: "#D52B1E" },
  { ticker: "AVGO", name: "Broadcom", sector: "Tech", color: "#CC092F" },
  { ticker: "WMT", name: "Walmart", sector: "Consumer", color: "#0071CE" },
  { ticker: "JPM", name: "JPMorgan", sector: "Finance", color: "#003B70" },
  { ticker: "V", name: "Visa", sector: "Finance", color: "#1A1F71" },
  { ticker: "UNH", name: "UnitedHealth", sector: "Health", color: "#002855" },
  { ticker: "XOM", name: "Exxon", sector: "Energy", color: "#E01F26" },
  { ticker: "MA", name: "Mastercard", sector: "Finance", color: "#FF5F00" },
  { ticker: "ORCL", name: "Oracle", sector: "Tech", color: "#F80000" },
  { ticker: "COST", name: "Costco", sector: "Consumer", color: "#005DAA" },
  { ticker: "HD", name: "Home Depot", sector: "Consumer", color: "#F96302" },
  { ticker: "PG", name: "Procter & Gamble", sector: "Consumer", color: "#003DA5" },
  { ticker: "JNJ", name: "Johnson & J.", sector: "Health", color: "#D51900" },
  { ticker: "NFLX", name: "Netflix", sector: "Tech", color: "#E50914" },
  { ticker: "ABBV", name: "AbbVie", sector: "Health", color: "#071D49" },
  { ticker: "BAC", name: "Bank of America", sector: "Finance", color: "#012169" },
  { ticker: "CRM", name: "Salesforce", sector: "Tech", color: "#00A1E0" },
  { ticker: "CVX", name: "Chevron", sector: "Energy", color: "#0066B2" },
  { ticker: "MRK", name: "Merck", sector: "Health", color: "#009B8D" },
  { ticker: "KO", name: "Coca-Cola", sector: "Consumer", color: "#F40009" },
  { ticker: "AMD", name: "AMD", sector: "Tech", color: "#ED1C24" },
  { ticker: "PEP", name: "PepsiCo", sector: "Consumer", color: "#004B93" },
  { ticker: "TMO", name: "Thermo Fisher", sector: "Health", color: "#003399" },
  { ticker: "ACN", name: "Accenture", sector: "Tech", color: "#A100FF" },
  { ticker: "LIN", name: "Linde", sector: "Materials", color: "#004990" },
  { ticker: "CSCO", name: "Cisco", sector: "Tech", color: "#049FD9" },
  { ticker: "MCD", name: "McDonald's", sector: "Consumer", color: "#FFC72C" },
  { ticker: "ABT", name: "Abbott Labs", sector: "Health", color: "#003366" },
  { ticker: "WFC", name: "Wells Fargo", sector: "Finance", color: "#D71E28" },
  { ticker: "ADBE", name: "Adobe", sector: "Tech", color: "#FF0000" },
  { ticker: "IBM", name: "IBM", sector: "Tech", color: "#054ADA" },
  { ticker: "PM", name: "Philip Morris", sector: "Consumer", color: "#6C5CE7" },
  { ticker: "GE", name: "GE Aerospace", sector: "Industrial", color: "#3C3D97" },
  { ticker: "NOW", name: "ServiceNow", sector: "Tech", color: "#62D84E" },
  { ticker: "DHR", name: "Danaher", sector: "Health", color: "#005DAA" },
  { ticker: "CAT", name: "Caterpillar", sector: "Industrial", color: "#FFCD11" },
  { ticker: "TXN", name: "Texas Instruments", sector: "Tech", color: "#CC0000" },
  { ticker: "QCOM", name: "Qualcomm", sector: "Tech", color: "#3253DC" },
  { ticker: "INTU", name: "Intuit", sector: "Tech", color: "#365EBF" },
  { ticker: "GS", name: "Goldman Sachs", sector: "Finance", color: "#7399C6" },
  { ticker: "AXP", name: "Amex", sector: "Finance", color: "#016FD0" },
  { ticker: "ISRG", name: "Intuitive Surgical", sector: "Health", color: "#0033A0" },
];

// Mock market cap data anchors for top stocks (in billions USD)
interface StockMcapAnchors {
  [year: string]: { [ticker: string]: number };
}

const stockMcapAnchors: StockMcapAnchors = {
  "2020": {
    AAPL: 2255, MSFT: 1682, NVDA: 329, AMZN: 1634, GOOGL: 1185, META: 778, "BRK.B": 543, TSLA: 669,
    LLY: 170, AVGO: 180, WMT: 408, JPM: 379, V: 444, UNH: 338, XOM: 175, MA: 339, ORCL: 178,
    COST: 162, HD: 300, PG: 344, JNJ: 422, NFLX: 239, ABBV: 191, BAC: 268, CRM: 225,
    CVX: 163, MRK: 213, KO: 235, AMD: 110, PEP: 200, TMO: 193, ACN: 185, LIN: 153,
    CSCO: 193, MCD: 170, ABT: 200, WFC: 138, ADBE: 239, IBM: 112, PM: 130, GE: 100,
    NOW: 110, DHR: 190, CAT: 94, TXN: 157, QCOM: 167, INTU: 110, GS: 105, AXP: 106, ISRG: 98,
  },
  "2021": {
    AAPL: 2913, MSFT: 2525, NVDA: 735, AMZN: 1691, GOOGL: 1923, META: 921, "BRK.B": 669, TSLA: 1061,
    LLY: 272, AVGO: 267, WMT: 393, JPM: 468, V: 468, UNH: 469, XOM: 257, MA: 354, ORCL: 213,
    COST: 227, HD: 407, PG: 388, JNJ: 451, NFLX: 270, ABBV: 264, BAC: 362, CRM: 258,
    CVX: 241, MRK: 181, KO: 265, AMD: 184, PEP: 238, TMO: 267, ACN: 270, LIN: 182,
    CSCO: 259, MCD: 273, ABT: 225, WFC: 197, ADBE: 309, IBM: 120, PM: 155, GE: 118,
    NOW: 139, DHR: 231, CAT: 118, TXN: 177, QCOM: 201, INTU: 180, GS: 157, AXP: 156, ISRG: 124,
  },
  "2022": {
    AAPL: 2066, MSFT: 1788, NVDA: 360, AMZN: 857, GOOGL: 1145, META: 319, "BRK.B": 682, TSLA: 389,
    LLY: 362, AVGO: 236, WMT: 373, JPM: 389, V: 418, UNH: 482, XOM: 457, MA: 339, ORCL: 223,
    COST: 209, HD: 302, PG: 349, JNJ: 434, NFLX: 138, ABBV: 297, BAC: 267, CRM: 128,
    CVX: 337, MRK: 280, KO: 269, AMD: 96, PEP: 244, TMO: 198, ACN: 174, LIN: 166,
    CSCO: 195, MCD: 200, ABT: 176, WFC: 161, ADBE: 159, IBM: 128, PM: 156, GE: 100,
    NOW: 95, DHR: 181, CAT: 131, TXN: 152, QCOM: 117, INTU: 118, GS: 124, AXP: 119, ISRG: 82,
  },
  "2023": {
    AAPL: 2990, MSFT: 2794, NVDA: 1220, AMZN: 1570, GOOGL: 1750, META: 909, "BRK.B": 790, TSLA: 790,
    LLY: 592, AVGO: 547, WMT: 430, JPM: 496, V: 530, UNH: 503, XOM: 414, MA: 406, ORCL: 303,
    COST: 265, HD: 355, PG: 359, JNJ: 379, NFLX: 211, ABBV: 290, BAC: 272, CRM: 260,
    CVX: 283, MRK: 273, KO: 258, AMD: 232, PEP: 232, TMO: 213, ACN: 228, LIN: 208,
    CSCO: 210, MCD: 212, ABT: 192, WFC: 182, ADBE: 280, IBM: 170, PM: 147, GE: 138,
    NOW: 153, DHR: 176, CAT: 147, TXN: 170, QCOM: 153, INTU: 183, GS: 128, AXP: 148, ISRG: 141,
  },
  "2024": {
    AAPL: 3750, MSFT: 3130, NVDA: 3400, AMZN: 2320, GOOGL: 2330, META: 1540, "BRK.B": 1020, TSLA: 1280,
    LLY: 741, AVGO: 1090, WMT: 615, JPM: 680, V: 620, UNH: 505, XOM: 468, MA: 465, ORCL: 480,
    COST: 395, HD: 395, PG: 395, JNJ: 358, NFLX: 390, ABBV: 310, BAC: 330, CRM: 310,
    CVX: 264, MRK: 260, KO: 265, AMD: 210, PEP: 224, TMO: 206, ACN: 225, LIN: 215,
    CSCO: 237, MCD: 215, ABT: 205, WFC: 230, ADBE: 260, IBM: 210, PM: 192, GE: 200,
    NOW: 218, DHR: 175, CAT: 200, TXN: 185, QCOM: 190, INTU: 190, GS: 185, AXP: 205, ISRG: 190,
  },
  "2025": {
    AAPL: 3690, MSFT: 3100, NVDA: 3300, AMZN: 2380, GOOGL: 2300, META: 1720, "BRK.B": 1100, TSLA: 1200,
    LLY: 810, AVGO: 1050, WMT: 650, JPM: 710, V: 640, UNH: 480, XOM: 450, MA: 480, ORCL: 450,
    COST: 420, HD: 380, PG: 400, JNJ: 345, NFLX: 420, ABBV: 330, BAC: 340, CRM: 290,
    CVX: 250, MRK: 240, KO: 270, AMD: 185, PEP: 218, TMO: 200, ACN: 210, LIN: 220,
    CSCO: 245, MCD: 210, ABT: 200, WFC: 240, ADBE: 240, IBM: 220, PM: 210, GE: 210,
    NOW: 200, DHR: 170, CAT: 190, TXN: 178, QCOM: 175, INTU: 185, GS: 195, AXP: 215, ISRG: 200,
  },
  "2026": {
    AAPL: 3720, MSFT: 3150, NVDA: 3350, AMZN: 2420, GOOGL: 2320, META: 1750, "BRK.B": 1120, TSLA: 1150,
    LLY: 830, AVGO: 1070, WMT: 660, JPM: 720, V: 650, UNH: 490, XOM: 440, MA: 490, ORCL: 460,
    COST: 430, HD: 385, PG: 405, JNJ: 350, NFLX: 430, ABBV: 340, BAC: 345, CRM: 295,
    CVX: 245, MRK: 235, KO: 275, AMD: 190, PEP: 220, TMO: 205, ACN: 215, LIN: 225,
    CSCO: 250, MCD: 215, ABT: 205, WFC: 245, ADBE: 245, IBM: 225, PM: 215, GE: 215,
    NOW: 205, DHR: 175, CAT: 195, TXN: 180, QCOM: 178, INTU: 188, GS: 200, AXP: 220, ISRG: 205,
  },
};

function generateStockDominance(): StockDominanceDataPoint[] {
  const years = Object.keys(stockMcapAnchors).sort();
  const result: StockDominanceDataPoint[] = [];

  for (let yi = 0; yi < years.length - 1; yi++) {
    const yearA = years[yi];
    const yearB = years[yi + 1];
    const mcapsA = stockMcapAnchors[yearA];
    const mcapsB = stockMcapAnchors[yearB];

    for (let m = 0; m < 12; m++) {
      const t = m / 12;
      const noise = () => 1 + Math.sin(yi * 7 + m * 13) * 0.02;
      const point: StockDominanceDataPoint = { date: `${yearA}-${String(m + 1).padStart(2, "0")}` };
      let totalMcap = 0;
      const mcaps: { [t: string]: number } = {};

      for (const stock of TOP_STOCKS) {
        const a = mcapsA[stock.ticker] || 0;
        const b = mcapsB[stock.ticker] || 0;
        const val = lerp(a, b, t) * noise();
        mcaps[stock.ticker] = val;
        totalMcap += val;
      }

      for (const stock of TOP_STOCKS) {
        point[stock.ticker] = (mcaps[stock.ticker] / totalMcap) * 100;
      }
      point._total = totalMcap;

      result.push(point);
    }
  }

  // Add final year point
  const lastYear = years[years.length - 1];
  const mcapsLast = stockMcapAnchors[lastYear];
  const lastPoint: StockDominanceDataPoint = { date: `${lastYear}-01` };
  let lastTotal = 0;
  for (const stock of TOP_STOCKS) {
    const val = mcapsLast[stock.ticker] || 0;
    lastTotal += val;
  }
  for (const stock of TOP_STOCKS) {
    lastPoint[stock.ticker] = ((mcapsLast[stock.ticker] || 0) / lastTotal) * 100;
  }
  lastPoint._total = lastTotal;
  result.push(lastPoint);

  return result;
}

// Compute gainers/losers: who gained/lost the most dominance over a period
export interface StockDominanceChange {
  ticker: string;
  name: string;
  sector: string;
  color: string;
  currentDom: number;
  startDom: number;
  changePp: number;   // change in percentage points
  changeRel: number;   // relative % change
}

export function getStockDominanceChanges(data: StockDominanceDataPoint[]): StockDominanceChange[] {
  if (data.length < 2) return [];
  const first = data[0];
  const last = data[data.length - 1];

  return TOP_STOCKS.map((stock) => {
    const startDom = (first[stock.ticker] as number) || 0;
    const currentDom = (last[stock.ticker] as number) || 0;
    const changePp = currentDom - startDom;
    const changeRel = startDom > 0 ? ((currentDom - startDom) / startDom) * 100 : 0;
    return { ticker: stock.ticker, name: stock.name, sector: stock.sector, color: stock.color, currentDom, startDom, changePp, changeRel };
  }).sort((a, b) => b.changePp - a.changePp);
}

// Sector aggregation for stock dominance
export interface SectorDominance {
  sector: string;
  currentDom: number;
  startDom: number;
  changePp: number;
}

export function getSectorDominance(data: StockDominanceDataPoint[]): SectorDominance[] {
  if (data.length < 2) return [];
  const first = data[0];
  const last = data[data.length - 1];
  const sectors: { [s: string]: { current: number; start: number } } = {};

  for (const stock of TOP_STOCKS) {
    const s = stock.sector;
    if (!sectors[s]) sectors[s] = { current: 0, start: 0 };
    sectors[s].current += (last[stock.ticker] as number) || 0;
    sectors[s].start += (first[stock.ticker] as number) || 0;
  }

  return Object.entries(sectors)
    .map(([sector, d]) => ({
      sector,
      currentDom: d.current,
      startDom: d.start,
      changePp: d.current - d.start,
    }))
    .sort((a, b) => b.currentDom - a.currentDom);
}

export interface RatioSummary {
  name: string;
  pair: string;
  assetClass: string;
  current: number;
  mean: number;
  stdDev: number;
  zScore: number;
  signal: string;
  signalType: "overbought" | "oversold" | "neutral";
  context: string;
}

export interface RotationSignal {
  message: string;
  type: "rotate_from" | "rotate_to";
  pair: string;
  assetClass: string;
  zScore: number;
}

// ============================================================
// HISTORICAL ANCHORS (2014-2026)
// ============================================================
const anchors: AssetDataPoint[] = [
  { date: "2014", gold: 1266, silver: 19.1, oil: 53, copper: 2.88, sp500: 2059, nasdaq: 4736, msciWorld: 1710, tesla: 44, caseShiller: 171, btc: 320, eth: 0.3, sol: 0, btcMcap: 0.005, ethMcap: 0, solMcap: 0, goldMcap: 7.5, silverMcap: 0.5, equitiesMcap: 65, realEstateMcap: 220, bondsMcap: 100, cryptoMcap: 0.006, m2Global: 60 },
  { date: "2015", gold: 1160, silver: 15.7, oil: 37, copper: 2.13, sp500: 2044, nasdaq: 5007, msciWorld: 1663, tesla: 43, caseShiller: 179, btc: 430, eth: 0.9, sol: 0, btcMcap: 0.007, ethMcap: 0.0001, solMcap: 0, goldMcap: 7.0, silverMcap: 0.4, equitiesMcap: 67, realEstateMcap: 230, bondsMcap: 105, cryptoMcap: 0.008, m2Global: 63 },
  { date: "2016", gold: 1251, silver: 17.1, oil: 54, copper: 2.50, sp500: 2239, nasdaq: 5383, msciWorld: 1751, tesla: 42, caseShiller: 189, btc: 960, eth: 8, sol: 0, btcMcap: 0.015, ethMcap: 0.001, solMcap: 0, goldMcap: 7.6, silverMcap: 0.5, equitiesMcap: 70, realEstateMcap: 240, bondsMcap: 110, cryptoMcap: 0.018, m2Global: 67 },
  { date: "2017", gold: 1303, silver: 17.1, oil: 60, copper: 3.26, sp500: 2674, nasdaq: 6903, msciWorld: 2103, tesla: 62, caseShiller: 200, btc: 14000, eth: 725, sol: 0, btcMcap: 0.23, ethMcap: 0.07, solMcap: 0, goldMcap: 7.8, silverMcap: 0.5, equitiesMcap: 80, realEstateMcap: 260, bondsMcap: 115, cryptoMcap: 0.6, m2Global: 73 },
  { date: "2018", gold: 1282, silver: 15.5, oil: 45, copper: 2.63, sp500: 2507, nasdaq: 6635, msciWorld: 1884, tesla: 60, caseShiller: 211, btc: 3800, eth: 133, sol: 0, btcMcap: 0.066, ethMcap: 0.014, solMcap: 0, goldMcap: 7.7, silverMcap: 0.4, equitiesMcap: 75, realEstateMcap: 270, bondsMcap: 115, cryptoMcap: 0.13, m2Global: 76 },
  { date: "2019", gold: 1517, silver: 17.9, oil: 61, copper: 2.80, sp500: 3231, nasdaq: 8973, msciWorld: 2358, tesla: 84, caseShiller: 220, btc: 7200, eth: 130, sol: 0.2, btcMcap: 0.13, ethMcap: 0.014, solMcap: 0.00005, goldMcap: 9.0, silverMcap: 0.5, equitiesMcap: 88, realEstateMcap: 280, bondsMcap: 120, cryptoMcap: 0.19, m2Global: 80 },
  { date: "2020", gold: 1898, silver: 26.5, oil: 49, copper: 3.52, sp500: 3756, nasdaq: 12888, msciWorld: 2690, tesla: 705, caseShiller: 239, btc: 28900, eth: 737, sol: 1.5, btcMcap: 0.54, ethMcap: 0.086, solMcap: 0.0005, goldMcap: 11.5, silverMcap: 0.7, equitiesMcap: 95, realEstateMcap: 290, bondsMcap: 130, cryptoMcap: 0.77, m2Global: 95 },
  { date: "2021", gold: 1829, silver: 23.4, oil: 75, copper: 4.46, sp500: 4766, nasdaq: 15645, msciWorld: 3230, tesla: 1056, caseShiller: 276, btc: 47000, eth: 3680, sol: 170, btcMcap: 0.9, ethMcap: 0.45, solMcap: 0.055, goldMcap: 11.0, silverMcap: 0.6, equitiesMcap: 120, realEstateMcap: 330, bondsMcap: 130, cryptoMcap: 2.2, m2Global: 105 },
  { date: "2022", gold: 1824, silver: 24.0, oil: 80, copper: 3.81, sp500: 3840, nasdaq: 10466, msciWorld: 2602, tesla: 123, caseShiller: 308, btc: 16500, eth: 1200, sol: 10, btcMcap: 0.32, ethMcap: 0.145, solMcap: 0.004, goldMcap: 11.0, silverMcap: 0.6, equitiesMcap: 98, realEstateMcap: 340, bondsMcap: 125, cryptoMcap: 0.8, m2Global: 100 },
  { date: "2023", gold: 2063, silver: 24.1, oil: 72, copper: 3.85, sp500: 4770, nasdaq: 15011, msciWorld: 3169, tesla: 248, caseShiller: 312, btc: 42200, eth: 2350, sol: 100, btcMcap: 0.82, ethMcap: 0.28, solMcap: 0.04, goldMcap: 12.5, silverMcap: 0.6, equitiesMcap: 110, realEstateMcap: 350, bondsMcap: 133, cryptoMcap: 1.6, m2Global: 104 },
  { date: "2024", gold: 2625, silver: 30.5, oil: 71, copper: 4.20, sp500: 5881, nasdaq: 19310, msciWorld: 3700, tesla: 421, caseShiller: 324, btc: 108000, eth: 3900, sol: 220, btcMcap: 2.13, ethMcap: 0.47, solMcap: 0.10, goldMcap: 16.0, silverMcap: 0.8, equitiesMcap: 120, realEstateMcap: 360, bondsMcap: 140, cryptoMcap: 3.6, m2Global: 110 },
  { date: "2025", gold: 2780, silver: 31.0, oil: 72, copper: 4.30, sp500: 6050, nasdaq: 19800, msciWorld: 3780, tesla: 350, caseShiller: 330, btc: 85000, eth: 2800, sol: 160, btcMcap: 1.68, ethMcap: 0.34, solMcap: 0.075, goldMcap: 17.5, silverMcap: 0.85, equitiesMcap: 122, realEstateMcap: 365, bondsMcap: 138, cryptoMcap: 2.8, m2Global: 114 },
  { date: "2026", gold: 2870, silver: 32.2, oil: 71, copper: 4.40, sp500: 6100, nasdaq: 19900, msciWorld: 3800, tesla: 370, caseShiller: 335, btc: 82000, eth: 2500, sol: 140, btcMcap: 1.62, ethMcap: 0.30, solMcap: 0.065, goldMcap: 18.2, silverMcap: 0.9, equitiesMcap: 124, realEstateMcap: 370, bondsMcap: 135, cryptoMcap: 2.6, m2Global: 118 },
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
      const n1 = () => 1 + Math.sin(i * 7 + m * 13) * 0.03;
      const n2 = () => 1 + Math.sin(i * 11 + m * 7) * 0.015;
      const n3 = () => 1 + Math.sin(i * 5 + m * 17) * 0.04;
      result.push({
        date: `${a.date}-${String(m + 1).padStart(2, "0")}`,
        gold: lerp(a.gold, b.gold, t) * n2(),
        silver: lerp(a.silver, b.silver, t) * n2(),
        oil: lerp(a.oil, b.oil, t) * n3(),
        copper: lerp(a.copper, b.copper, t) * n2(),
        sp500: lerp(a.sp500, b.sp500, t) * n2(),
        nasdaq: lerp(a.nasdaq, b.nasdaq, t) * n2(),
        msciWorld: lerp(a.msciWorld, b.msciWorld, t) * n2(),
        tesla: lerp(a.tesla, b.tesla, t) * n1(),
        caseShiller: lerp(a.caseShiller, b.caseShiller, t),
        btc: lerp(a.btc, b.btc, t) * n1(),
        eth: lerp(a.eth, b.eth, t) * n1(),
        sol: lerp(a.sol, b.sol, t) * n3(),
        btcMcap: lerp(a.btcMcap, b.btcMcap, t),
        ethMcap: lerp(a.ethMcap, b.ethMcap, t),
        solMcap: lerp(a.solMcap, b.solMcap, t),
        goldMcap: lerp(a.goldMcap, b.goldMcap, t),
        silverMcap: lerp(a.silverMcap, b.silverMcap, t),
        equitiesMcap: lerp(a.equitiesMcap, b.equitiesMcap, t),
        realEstateMcap: lerp(a.realEstateMcap, b.realEstateMcap, t),
        bondsMcap: lerp(a.bondsMcap, b.bondsMcap, t),
        cryptoMcap: lerp(a.cryptoMcap, b.cryptoMcap, t),
        m2Global: lerp(a.m2Global, b.m2Global, t) * n2(),
      });
    }
  }
  const last = anchors[anchors.length - 1];
  result.push({ ...last, date: `${last.date}-01` });
  return result;
}

function computeRatios(assets: AssetDataPoint[]): ClassRatioDataPoint[] {
  return assets.map((d) => ({
    date: d.date,
    // Commodities
    goldSilver: d.gold / d.silver,
    goldOil: d.gold / d.oil,
    goldCopper: d.gold / (d.copper * 1000), // scale copper to $/ton
    silverOil: d.silver / d.oil,
    copperGold: (d.copper * 1000) / d.gold,
    // Equities
    sp500Nasdaq: d.sp500 / d.nasdaq,
    teslaSp500: d.tesla / d.sp500,
    sp500Msci: d.sp500 / d.msciWorld,
    nasdaqMsci: d.nasdaq / d.msciWorld,
    // Crypto
    btcEth: d.btc / (d.eth || 0.01),
    ethSol: (d.eth || 0.01) / (d.sol || 0.01),
    btcSol: d.btc / (d.sol || 0.01),
    // BTC vs classes
    btcGold: d.btc / d.gold,
    btcSp500: d.btc / d.sp500,
    btcRealEstate: d.btc / (d.caseShiller * 1000),
  }));
}

function computeDominance(assets: AssetDataPoint[]): DominanceDataPoint[] {
  return assets.map((d) => {
    const total = d.goldMcap + d.silverMcap + d.equitiesMcap + d.realEstateMcap + d.bondsMcap + d.cryptoMcap;
    return {
      date: d.date,
      goldDom: (d.goldMcap / total) * 100,
      silverDom: (d.silverMcap / total) * 100,
      equitiesDom: (d.equitiesMcap / total) * 100,
      realEstateDom: (d.realEstateMcap / total) * 100,
      bondsDom: (d.bondsMcap / total) * 100,
      cryptoDom: (d.cryptoMcap / total) * 100,
      total,
    };
  });
}

// ============================================================
// CRYPTO DOMINANCE COMPUTATION
// ============================================================
function computeCryptoDominance(assets: AssetDataPoint[]): CryptoDominancePoint[] {
  return assets.map((d) => {
    const total = d.cryptoMcap || 0.001;
    const btcDom = (d.btcMcap / total) * 100;
    const ethDom = (d.ethMcap / total) * 100;
    const solDom = (d.solMcap / total) * 100;
    return {
      date: d.date,
      btcDom: Math.min(btcDom, 100),
      ethDom: Math.min(ethDom, 100),
      solDom: Math.min(solDom, 100),
      othersDom: Math.max(100 - btcDom - ethDom - solDom, 0),
    };
  });
}

function getCryptoRotationSignal(cryptoDom: CryptoDominancePoint[]): CryptoRotationSignal {
  if (cryptoDom.length < 7) {
    return { phase: "neutral", btcDomTrend: "flat", narrative: "Datos insuficientes para evaluar rotación crypto.", halvingCyclePosition: "N/A" };
  }
  const latest = cryptoDom[cryptoDom.length - 1];
  const sixMAgo = cryptoDom[Math.max(0, cryptoDom.length - 7)];
  const btcDomChange = latest.btcDom - sixMAgo.btcDom;

  const btcDomTrend: CryptoRotationSignal["btcDomTrend"] =
    btcDomChange > 2 ? "rising" : btcDomChange < -2 ? "falling" : "flat";

  // BTC halving: April 2024
  const latestDate = new Date(latest.date + "-01");
  const halvingDate = new Date("2024-04-01");
  const monthsSinceHalving = Math.round(
    (latestDate.getTime() - halvingDate.getTime()) / (30 * 24 * 3600 * 1000)
  );
  const halvingCyclePosition = monthsSinceHalving >= 0
    ? `${monthsSinceHalving} meses post-halving`
    : `${Math.abs(monthsSinceHalving)} meses pre-halving`;

  let phase: CryptoRotationSignal["phase"];
  let narrative: string;
  if (btcDomTrend === "rising") {
    phase = "risk_off";
    narrative = `BTC dominancia subiendo (${btcDomChange > 0 ? "+" : ""}${btcDomChange.toFixed(1)}pp en 6M). Capital se refugia en BTC. Fase conservadora.`;
  } else if (btcDomTrend === "falling" && latest.othersDom > sixMAgo.othersDom) {
    phase = "alt_season";
    narrative = `BTC dominancia cayendo (${btcDomChange.toFixed(1)}pp en 6M). Alts ganando terreno. Posible alt season.`;
  } else {
    phase = "neutral";
    narrative = `Dominancia BTC estable (${btcDomChange > 0 ? "+" : ""}${btcDomChange.toFixed(1)}pp en 6M). Sin rotación clara entre BTC y alts.`;
  }

  return { phase, btcDomTrend, narrative, halvingCyclePosition };
}

// ============================================================
// STOCK MOMENTUM COMPUTATION
// ============================================================
export function computeStockMomentum(data: StockDominanceDataPoint[]): {
  points: StockMomentumPoint[];
  concentration: ConcentrationMetrics;
} {
  if (data.length < 7) return { points: [], concentration: { top5Pct: 0, top10Pct: 0, hhi: 0, hhiChange: 0 } };

  const latest = data[data.length - 1];
  const sixMAgo = data[Math.max(0, data.length - 7)];
  const threeMAgo = data[Math.max(0, data.length - 4)];

  const currentDoms = TOP_STOCKS.map(s => (latest[s.ticker] as number) || 0);
  const sorted = [...currentDoms].sort((a, b) => a - b);
  const medianDom = sorted[Math.floor(sorted.length / 2)];

  const points: StockMomentumPoint[] = TOP_STOCKS.map(stock => {
    const currentDom = (latest[stock.ticker] as number) || 0;
    const dom6MAgo = (sixMAgo[stock.ticker] as number) || 0;
    const dom3MAgo = (threeMAgo[stock.ticker] as number) || 0;
    const domChange6M = currentDom - dom6MAgo;
    const domChange3M = currentDom - dom3MAgo;
    const priorChange3M = dom3MAgo - dom6MAgo;
    const acceleration = domChange3M - priorChange3M;

    let quadrant: StockMomentumPoint["quadrant"];
    if (currentDom > medianDom && domChange6M > 0) quadrant = "momentum";
    else if (currentDom <= medianDom && domChange6M > 0) quadrant = "catch_up";
    else if (currentDom > medianDom && domChange6M <= 0) quadrant = "declining";
    else quadrant = "value_trap";

    return { ticker: stock.ticker, name: stock.name, sector: stock.sector, color: stock.color, currentDom, domChange6M, domChange3M, acceleration, quadrant };
  });

  // Concentration
  const sortedDesc = [...currentDoms].sort((a, b) => b - a);
  const top5Pct = sortedDesc.slice(0, 5).reduce((s, v) => s + v, 0);
  const top10Pct = sortedDesc.slice(0, 10).reduce((s, v) => s + v, 0);
  const hhi = currentDoms.reduce((s, v) => s + v * v, 0);

  const oldDoms = TOP_STOCKS.map(s => (sixMAgo[s.ticker] as number) || 0);
  const oldHhi = oldDoms.reduce((s, v) => s + v * v, 0);

  return {
    points,
    concentration: { top5Pct, top10Pct, hhi, hhiChange: hhi - oldHhi },
  };
}

// ============================================================
// BOLLINGER BANDS
// ============================================================
export function computeBollingerBands(
  values: number[],
  dates: string[],
  period: number,
): BollingerBandPoint[] {
  return values.map((v, i) => {
    if (i < period - 1) {
      return { date: dates[i], value: v, sma: null, upper1: null, lower1: null, upper2: null, lower2: null };
    }
    const w = values.slice(i - period + 1, i + 1);
    const mean = w.reduce((s, x) => s + x, 0) / w.length;
    const variance = w.reduce((s, x) => s + (x - mean) ** 2, 0) / w.length;
    const sd = Math.sqrt(variance);
    return {
      date: dates[i],
      value: v,
      sma: mean,
      upper1: mean + sd,
      lower1: mean - sd,
      upper2: mean + 2 * sd,
      lower2: mean - 2 * sd,
    };
  });
}

// ============================================================
// NARRATIVE GENERATION
// ============================================================
export function generateNarrative(pair: string, zScore: number): string {
  const parts = pair.split(" / ");
  const a = parts[0], b = parts[1];
  const absZ = Math.abs(zScore).toFixed(1);

  if (Math.abs(zScore) < 0.5) {
    return `${a} y ${b} en equilibrio relativo.`;
  }
  if (zScore > 1.5) {
    return `${a} está ${absZ}\u03C3 caro vs ${b}. Históricamente esto revierte en 3-6 meses. Considerar rotar hacia ${b}.`;
  }
  if (zScore > 0.5) {
    return `${a} está ${absZ}\u03C3 caro vs ${b}. Posible reversión en 6-12 meses.`;
  }
  if (zScore < -1.5) {
    return `${a} está ${absZ}\u03C3 barato vs ${b}. Zona de acumulación histórica. Considerar sobreponderar ${a}.`;
  }
  return `${a} está ${absZ}\u03C3 barato vs ${b}. Posible oportunidad de entrada.`;
}

function computeStats(values: number[]): { mean: number; stdDev: number } {
  const n = values.length;
  const mean = values.reduce((s, v) => s + v, 0) / n;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / n;
  return { mean, stdDev: Math.sqrt(variance) };
}

// Simple Moving Average — returns null for the first (period - 1) points
export function computeSMA(values: number[], period: number): (number | null)[] {
  const result: (number | null)[] = [];
  for (let i = 0; i < values.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      let sum = 0;
      for (let j = i - period + 1; j <= i; j++) sum += values[j];
      result.push(sum / period);
    }
  }
  return result;
}

function getSignal(zScore: number, pair: string): { signal: string; signalType: "overbought" | "oversold" | "neutral"; context: string } {
  const parts = pair.split(" / ");
  const a = parts[0], b = parts[1];
  if (zScore > 2) return { signal: "Fuertemente sobrecomprado", signalType: "overbought", context: `${a} muy caro vs ${b}` };
  if (zScore > 1) return { signal: "Sobrecomprado", signalType: "overbought", context: `${a} caro relativo a ${b}` };
  if (zScore < -2) return { signal: "Fuertemente sobrevendido", signalType: "oversold", context: `${a} muy barato vs ${b}` };
  if (zScore < -1) return { signal: "Sobrevendido", signalType: "oversold", context: `${a} barato relativo a ${b}` };
  return { signal: "Neutral", signalType: "neutral", context: "En equilibrio relativo" };
}

// ============================================================
// SEMÁFORO: ASSET CLASS SIGNALS — DEBASEMENT ADJUSTED
// ============================================================

// M2-adjusted SMA: scales the nominal SMA by accumulated M2 growth over the period
function computeM2AdjustedDeviation(
  priceValues: number[],
  m2Values: number[],
  period: number,
  normDivisor: number,
): { nominalDevPct: number; adjustedDevPct: number; nominalZ: number; adjustedZ: number } {
  const n = priceValues.length;
  const effectivePeriod = Math.min(period, n);
  const latestPrice = priceValues[n - 1];

  // Nominal SMA
  const window = priceValues.slice(n - effectivePeriod);
  const nominalSMA = window.reduce((s, v) => s + v, 0) / effectivePeriod;

  // M2 growth over the SMA window
  const m2Start = m2Values[n - effectivePeriod];
  const m2End = m2Values[n - 1];
  const m2Growth = m2Start > 0 ? (m2End - m2Start) / m2Start : 0;

  // Adjusted SMA = nominal × (1 + M2 growth)
  const adjustedSMA = nominalSMA * (1 + m2Growth);

  const nominalDevPct = nominalSMA > 0 ? ((latestPrice - nominalSMA) / nominalSMA) * 100 : 0;
  const adjustedDevPct = adjustedSMA > 0 ? ((latestPrice - adjustedSMA) / adjustedSMA) * 100 : 0;

  return {
    nominalDevPct,
    adjustedDevPct,
    nominalZ: nominalDevPct / normDivisor,
    adjustedZ: adjustedDevPct / normDivisor,
  };
}

function getSignalLevel(adjustedZ: number): SignalLevel {
  if (adjustedZ > 1.5) return "adelantado";
  if (adjustedZ > 0.5) return "adelantado";
  if (adjustedZ >= -0.5) return "alineado";
  if (adjustedZ >= -1.5) return "rezagado";
  return "divergente";
}

function generateClassNarrative(cls: string, adjustedZ: number): string {
  const level = getSignalLevel(adjustedZ);

  switch (cls) {
    case "Acciones": {
      if (level === "rezagado") return `Acciones no pricearon el debasement. Acumular.`;
      if (level === "adelantado") return `Acciones se adelantaron al debasement. Rotar a rezagados.`;
      if (level === "divergente") return `Acciones divergen del debasement. Oportunidad extrema o problema estructural.`;
      return `Acciones alineadas con la expansión monetaria. Mantener.`;
    }
    case "Crypto": {
      if (level === "rezagado") return `BTC no priceó el debasement. Acumular.`;
      if (level === "adelantado") return `Crypto se adelantó al debasement. Rotar a rezagados.`;
      if (level === "divergente") return `Crypto diverge del debasement. Oportunidad extrema o cambio estructural.`;
      return `Crypto alineado con la expansión monetaria. Mantener.`;
    }
    case "Oro": {
      if (level === "rezagado") return `Oro no priceó la expansión monetaria. Acumular metales.`;
      if (level === "adelantado") return `Oro se adelantó al debasement. Rotar a plata o rezagados.`;
      if (level === "divergente") return `Oro diverge del debasement. Oportunidad extrema.`;
      return `Oro alineado con las condiciones monetarias. Mantener.`;
    }
    case "Bonos": {
      if (level === "rezagado") return `Bonos no pricearon el debasement. Oportunidad si se espera más expansión.`;
      if (level === "adelantado") return `Bonos se adelantaron. Rotar hacia activos duros.`;
      if (level === "divergente") return `Bonos divergen del debasement. Estrés monetario.`;
      return `Bonos alineados con las condiciones monetarias. Mantener.`;
    }
    default:
      return `Nivel compuesto ajustado: ${adjustedZ.toFixed(1)}\u03C3.`;
  }
}

function generateActionSignal(level: SignalLevel): string {
  switch (level) {
    case "adelantado":
      return "Considerar rotar hacia activos REZAGADOS. No vender a fiat.";
    case "alineado":
      return "Mantener. El activo refleja correctamente las condiciones monetarias.";
    case "rezagado":
      return "Oportunidad de acumulación. El mercado no ha priceado el debasement.";
    case "divergente":
      return "Investigar causa. Posible oportunidad extrema o señal de problema estructural.";
  }
}

function computeMomentum(values: number[]): AssetMomentum {
  const n = values.length;
  const current = values[n - 1];
  const ago12M = values[Math.max(0, n - 13)]; // ~12 months back
  const pctChange12M = ago12M > 0 ? ((current - ago12M) / ago12M) * 100 : 0;

  // SMA 50 check
  const sma50Len = Math.min(50, n);
  const sma50 = values.slice(n - sma50Len).reduce((s, v) => s + v, 0) / sma50Len;
  const aboveSma50 = current > sma50;

  return { pctChange12M, aboveSma50 };
}

function computeAssetClassSignals(): AssetClassSignal[] {
  const signals: AssetClassSignal[] = [];
  const m2Values = rawAssets.map(d => d.m2Global);

  // --- ACCIONES ---
  const sp500Values = rawAssets.map(d => d.sp500);
  const sp500Dev = computeM2AdjustedDeviation(sp500Values, m2Values, 200, 8);

  const sp500NasdaqSummary = summariesData.find(s => s.pair === "S&P 500 / Nasdaq");
  const concentrationZ = sp500NasdaqSummary ? sp500NasdaqSummary.zScore : 0;

  const nomAccionesZ = sp500Dev.nominalZ * 0.6 + concentrationZ * 0.4;
  const adjAccionesZ = sp500Dev.adjustedZ * 0.6 + concentrationZ * 0.4;
  const deltaAcciones = nomAccionesZ - adjAccionesZ;

  const accionesMom = computeMomentum(sp500Values);
  const accionesLevel = getSignalLevel(adjAccionesZ);
  const accionesMetrics: AssetClassMetric[] = [
    { label: "vs SMA 200 ajustado (M2)", value: sp500Dev.adjustedDevPct, zScore: sp500Dev.adjustedZ,
      interpretation: `${sp500Dev.adjustedDevPct > 0 ? "+" : ""}${sp500Dev.adjustedDevPct.toFixed(1)}% vs SMA ajustado` },
    { label: "S&P/Nasdaq (concentración)", value: sp500NasdaqSummary?.current ?? 0, zScore: concentrationZ,
      interpretation: concentrationZ > 1 ? "Tech rezagado" : concentrationZ < -1 ? "Tech dominante" : "Equilibrado" },
    { label: "Delta nominal vs real", value: deltaAcciones, zScore: deltaAcciones,
      interpretation: `${deltaAcciones > 0 ? "+" : ""}${deltaAcciones.toFixed(2)}\u03C3 ruido monetario` },
  ];
  signals.push({
    assetClass: "Acciones", icon: "📈", signal: accionesLevel,
    compositeZScore: adjAccionesZ, nominalZScore: nomAccionesZ, debasementDelta: deltaAcciones,
    momentum: accionesMom,
    metrics: accionesMetrics, narrative: generateClassNarrative("Acciones", adjAccionesZ),
    actionSignal: generateActionSignal(accionesLevel),
  });

  // --- CRYPTO ---
  const btcValues = rawAssets.map(d => d.btc);
  const btcDev = computeM2AdjustedDeviation(btcValues, m2Values, 200, 30);

  const latest = rawAssets[rawAssets.length - 1];
  const btcDominance = latest.cryptoMcap > 0 ? (latest.btcMcap / latest.cryptoMcap) * 100 : 50;
  const btcDomZ = (btcDominance - 55) / 10;

  const nomCryptoZ = btcDev.nominalZ * 0.6 + btcDomZ * 0.4;
  const adjCryptoZ = btcDev.adjustedZ * 0.6 + btcDomZ * 0.4;
  const deltaCrypto = nomCryptoZ - adjCryptoZ;

  const cryptoMom = computeMomentum(btcValues);
  const cryptoLevel = getSignalLevel(adjCryptoZ);
  const cryptoMetrics: AssetClassMetric[] = [
    { label: "BTC vs SMA 200 ajustado (M2)", value: btcDev.adjustedDevPct, zScore: btcDev.adjustedZ,
      interpretation: `${btcDev.adjustedDevPct > 0 ? "+" : ""}${btcDev.adjustedDevPct.toFixed(0)}% vs SMA ajustado` },
    { label: "BTC Dominancia", value: btcDominance, zScore: btcDomZ,
      interpretation: btcDominance > 60 ? "BTC dominante (risk-off)" : btcDominance < 45 ? "Alts subiendo (risk-on)" : "Equilibrado" },
    { label: "Delta nominal vs real", value: deltaCrypto, zScore: deltaCrypto,
      interpretation: `${deltaCrypto > 0 ? "+" : ""}${deltaCrypto.toFixed(2)}\u03C3 ruido monetario` },
  ];
  signals.push({
    assetClass: "Crypto", icon: "₿", signal: cryptoLevel,
    compositeZScore: adjCryptoZ, nominalZScore: nomCryptoZ, debasementDelta: deltaCrypto,
    momentum: cryptoMom,
    metrics: cryptoMetrics, narrative: generateClassNarrative("Crypto", adjCryptoZ),
    actionSignal: generateActionSignal(cryptoLevel),
  });

  // --- ORO ---
  const goldValues = rawAssets.map(d => d.gold);
  const goldDev = computeM2AdjustedDeviation(goldValues, m2Values, 200, 6);

  const goldSilverSummary = summariesData.find(s => s.pair === "Oro / Plata");
  const goldSilverZ = goldSilverSummary ? goldSilverSummary.zScore : 0;

  const nomOroZ = goldDev.nominalZ * 0.6 + goldSilverZ * 0.4;
  const adjOroZ = goldDev.adjustedZ * 0.6 + goldSilverZ * 0.4;
  const deltaOro = nomOroZ - adjOroZ;

  const oroMom = computeMomentum(goldValues);
  const oroLevel = getSignalLevel(adjOroZ);
  const oroMetrics: AssetClassMetric[] = [
    { label: "Oro vs SMA 200 ajustado (M2)", value: goldDev.adjustedDevPct, zScore: goldDev.adjustedZ,
      interpretation: `${goldDev.adjustedDevPct > 0 ? "+" : ""}${goldDev.adjustedDevPct.toFixed(1)}% vs SMA ajustado` },
    { label: "Oro/Plata ratio", value: goldSilverSummary?.current ?? 0, zScore: goldSilverZ,
      interpretation: goldSilverZ > 1 ? "Plata rezagada (oportunidad)" : goldSilverZ < -1 ? "Plata cara" : "Equilibrado" },
    { label: "Delta nominal vs real", value: deltaOro, zScore: deltaOro,
      interpretation: `${deltaOro > 0 ? "+" : ""}${deltaOro.toFixed(2)}\u03C3 ruido monetario` },
  ];
  signals.push({
    assetClass: "Oro", icon: "🥇", signal: oroLevel,
    compositeZScore: adjOroZ, nominalZScore: nomOroZ, debasementDelta: deltaOro,
    momentum: oroMom,
    metrics: oroMetrics, narrative: generateClassNarrative("Oro", adjOroZ),
    actionSignal: generateActionSignal(oroLevel),
  });

  // --- BONOS ---
  const bondValues = rawAssets.map(d => d.bondsMcap);
  const bondDev = computeM2AdjustedDeviation(bondValues, m2Values, 60, 3);

  const yieldSpreadZ = bondDev.adjustedZ * 0.5;

  const nomBonosZ = bondDev.nominalZ * 0.6 + (bondDev.nominalZ * 0.5) * 0.4;
  const adjBonosZ = bondDev.adjustedZ * 0.6 + yieldSpreadZ * 0.4;
  const deltaBonos = nomBonosZ - adjBonosZ;

  const bonosMom = computeMomentum(bondValues);
  const bonosLevel = getSignalLevel(adjBonosZ);
  const bonosMetrics: AssetClassMetric[] = [
    { label: "Bonos vs tendencia ajustada (M2)", value: bondDev.adjustedDevPct, zScore: bondDev.adjustedZ,
      interpretation: bondDev.adjustedZ > 0.5 ? "Yields comprimidos" : bondDev.adjustedZ < -0.5 ? "Yields elevados" : "Yields neutrales" },
    { label: "Spread proxy", value: yieldSpreadZ, zScore: yieldSpreadZ,
      interpretation: yieldSpreadZ > 0.5 ? "Curva aplanandose" : "Curva normal" },
    { label: "Delta nominal vs real", value: deltaBonos, zScore: deltaBonos,
      interpretation: `${deltaBonos > 0 ? "+" : ""}${deltaBonos.toFixed(2)}\u03C3 ruido monetario` },
  ];
  signals.push({
    assetClass: "Bonos", icon: "🏛️", signal: bonosLevel,
    compositeZScore: adjBonosZ, nominalZScore: nomBonosZ, debasementDelta: deltaBonos,
    momentum: bonosMom,
    metrics: bonosMetrics, narrative: generateClassNarrative("Bonos", adjBonosZ),
    actionSignal: generateActionSignal(bonosLevel),
  });

  return signals;
}

// ============================================================
// PERFORMANCE HISTÓRICA (CAGR)
// ============================================================

// Static performance data for ~50 assets
// ipoYear = year of IPO or first available price, priceStart = price at start
const PERFORMANCE_ANCHORS: { ticker: string; name: string; sector: string; marketCap: number; ipoYear: number; priceStart: number; price5YAgo: number; priceCurrent: number }[] = [
  // Mega Tech
  { ticker: "AAPL", name: "Apple", sector: "Tech", marketCap: 3720, ipoYear: 1980, priceStart: 0.10, price5YAgo: 75, priceCurrent: 242 },
  { ticker: "MSFT", name: "Microsoft", sector: "Tech", marketCap: 3150, ipoYear: 1986, priceStart: 0.10, price5YAgo: 160, priceCurrent: 423 },
  { ticker: "NVDA", name: "NVIDIA", sector: "Tech", marketCap: 3350, ipoYear: 1999, priceStart: 1.50, price5YAgo: 59, priceCurrent: 136 },
  { ticker: "AMZN", name: "Amazon", sector: "Consumer", marketCap: 2420, ipoYear: 1997, priceStart: 1.50, price5YAgo: 103, priceCurrent: 228 },
  { ticker: "GOOGL", name: "Alphabet", sector: "Tech", marketCap: 2320, ipoYear: 2004, priceStart: 2.50, price5YAgo: 73, priceCurrent: 189 },
  { ticker: "META", name: "Meta", sector: "Tech", marketCap: 1750, ipoYear: 2012, priceStart: 38, price5YAgo: 208, priceCurrent: 680 },
  { ticker: "TSLA", name: "Tesla", sector: "Auto", marketCap: 1150, ipoYear: 2010, priceStart: 1.13, price5YAgo: 53, priceCurrent: 360 },
  { ticker: "AVGO", name: "Broadcom", sector: "Tech", marketCap: 1070, ipoYear: 2009, priceStart: 15, price5YAgo: 75, priceCurrent: 228 },
  { ticker: "BRK.B", name: "Berkshire", sector: "Finance", marketCap: 1120, ipoYear: 1996, priceStart: 23, price5YAgo: 220, priceCurrent: 482 },
  { ticker: "LLY", name: "Eli Lilly", sector: "Health", marketCap: 830, ipoYear: 1970, priceStart: 0.60, price5YAgo: 141, priceCurrent: 872 },
  // Large Cap
  { ticker: "WMT", name: "Walmart", sector: "Consumer", marketCap: 660, ipoYear: 1972, priceStart: 0.05, price5YAgo: 59, priceCurrent: 97 },
  { ticker: "JPM", name: "JPMorgan", sector: "Finance", marketCap: 720, ipoYear: 1969, priceStart: 1.50, price5YAgo: 135, priceCurrent: 253 },
  { ticker: "V", name: "Visa", sector: "Finance", marketCap: 650, ipoYear: 2008, priceStart: 11, price5YAgo: 188, priceCurrent: 330 },
  { ticker: "UNH", name: "UnitedHealth", sector: "Health", marketCap: 490, ipoYear: 1984, priceStart: 0.25, price5YAgo: 302, priceCurrent: 537 },
  { ticker: "XOM", name: "Exxon", sector: "Energy", marketCap: 440, ipoYear: 1920, priceStart: 0.01, price5YAgo: 55, priceCurrent: 106 },
  { ticker: "MA", name: "Mastercard", sector: "Finance", marketCap: 490, ipoYear: 2006, priceStart: 3.90, price5YAgo: 317, priceCurrent: 533 },
  { ticker: "ORCL", name: "Oracle", sector: "Tech", marketCap: 460, ipoYear: 1986, priceStart: 0.10, price5YAgo: 58, priceCurrent: 168 },
  { ticker: "COST", name: "Costco", sector: "Consumer", marketCap: 430, ipoYear: 1985, priceStart: 2.50, price5YAgo: 335, priceCurrent: 967 },
  { ticker: "HD", name: "Home Depot", sector: "Consumer", marketCap: 385, ipoYear: 1981, priceStart: 0.03, price5YAgo: 275, priceCurrent: 388 },
  { ticker: "PG", name: "Procter & Gamble", sector: "Consumer", marketCap: 405, ipoYear: 1890, priceStart: 0.001, price5YAgo: 119, priceCurrent: 171 },
  { ticker: "JNJ", name: "Johnson & J.", sector: "Health", marketCap: 350, ipoYear: 1944, priceStart: 0.02, price5YAgo: 148, priceCurrent: 148 },
  { ticker: "NFLX", name: "Netflix", sector: "Tech", marketCap: 430, ipoYear: 2002, priceStart: 1.20, price5YAgo: 352, priceCurrent: 1000 },
  { ticker: "ABBV", name: "AbbVie", sector: "Health", marketCap: 340, ipoYear: 2013, priceStart: 36, price5YAgo: 88, priceCurrent: 193 },
  { ticker: "BAC", name: "Bank of America", sector: "Finance", marketCap: 345, ipoYear: 1972, priceStart: 0.10, price5YAgo: 32, priceCurrent: 44 },
  { ticker: "CRM", name: "Salesforce", sector: "Tech", marketCap: 295, ipoYear: 2004, priceStart: 3.95, price5YAgo: 177, priceCurrent: 304 },
  { ticker: "CVX", name: "Chevron", sector: "Energy", marketCap: 245, ipoYear: 1921, priceStart: 0.01, price5YAgo: 103, priceCurrent: 141 },
  { ticker: "MRK", name: "Merck", sector: "Health", marketCap: 235, ipoYear: 1946, priceStart: 0.05, price5YAgo: 80, priceCurrent: 93 },
  { ticker: "KO", name: "Coca-Cola", sector: "Consumer", marketCap: 275, ipoYear: 1919, priceStart: 0.006, price5YAgo: 55, priceCurrent: 64 },
  { ticker: "AMD", name: "AMD", sector: "Tech", marketCap: 190, ipoYear: 1972, priceStart: 0.05, price5YAgo: 52, priceCurrent: 117 },
  { ticker: "PEP", name: "PepsiCo", sector: "Consumer", marketCap: 220, ipoYear: 1965, priceStart: 0.03, price5YAgo: 134, priceCurrent: 151 },
  // Mid-large
  { ticker: "CSCO", name: "Cisco", sector: "Tech", marketCap: 250, ipoYear: 1990, priceStart: 0.08, price5YAgo: 47, priceCurrent: 62 },
  { ticker: "ADBE", name: "Adobe", sector: "Tech", marketCap: 245, ipoYear: 1986, priceStart: 0.04, price5YAgo: 366, priceCurrent: 541 },
  { ticker: "IBM", name: "IBM", sector: "Tech", marketCap: 225, ipoYear: 1911, priceStart: 0.001, price5YAgo: 129, priceCurrent: 243 },
  { ticker: "GE", name: "GE Aerospace", sector: "Industrial", marketCap: 215, ipoYear: 1892, priceStart: 0.001, price5YAgo: 90, priceCurrent: 197 },
  { ticker: "NOW", name: "ServiceNow", sector: "Tech", marketCap: 205, ipoYear: 2012, priceStart: 24, price5YAgo: 357, priceCurrent: 990 },
  { ticker: "CAT", name: "Caterpillar", sector: "Industrial", marketCap: 195, ipoYear: 1929, priceStart: 0.05, price5YAgo: 178, priceCurrent: 400 },
  { ticker: "GS", name: "Goldman Sachs", sector: "Finance", marketCap: 200, ipoYear: 1999, priceStart: 53, price5YAgo: 252, priceCurrent: 609 },
  { ticker: "AXP", name: "Amex", sector: "Finance", marketCap: 220, ipoYear: 1977, priceStart: 1.20, price5YAgo: 120, priceCurrent: 307 },
  { ticker: "ISRG", name: "Intuitive Surgical", sector: "Health", marketCap: 205, ipoYear: 2000, priceStart: 9, price5YAgo: 285, priceCurrent: 569 },
  // Crypto (special — not stocks)
  { ticker: "BTC", name: "Bitcoin", sector: "Crypto", marketCap: 1940, ipoYear: 2009, priceStart: 0.001, price5YAgo: 7200, priceCurrent: 98000 },
  { ticker: "ETH", name: "Ethereum", sector: "Crypto", marketCap: 340, ipoYear: 2015, priceStart: 0.30, price5YAgo: 130, priceCurrent: 2750 },
  { ticker: "SOL", name: "Solana", sector: "Crypto", marketCap: 100, ipoYear: 2020, priceStart: 0.20, price5YAgo: 1.50, priceCurrent: 210 },
  // Commodities
  { ticker: "GOLD", name: "Oro (onza)", sector: "Commodities", marketCap: 18200, ipoYear: 1971, priceStart: 35, price5YAgo: 1517, priceCurrent: 2870 },
  { ticker: "SILVER", name: "Plata (onza)", sector: "Commodities", marketCap: 900, ipoYear: 1971, priceStart: 1.39, price5YAgo: 17.9, priceCurrent: 32.2 },
  // Index
  { ticker: "SPX", name: "S&P 500", sector: "Index", marketCap: 124000, ipoYear: 1957, priceStart: 44, price5YAgo: 3231, priceCurrent: 6050 },
];

function computeCAGR(priceStart: number, priceEnd: number, years: number): number {
  if (priceStart <= 0 || priceEnd <= 0 || years <= 0) return 0;
  return (Math.pow(priceEnd / priceStart, 1 / years) - 1) * 100;
}

function buildPerformanceData(): AssetPerformance[] {
  const currentYear = 2026;
  return PERFORMANCE_ANCHORS.map(a => {
    const years = currentYear - a.ipoYear;
    const cagrHistorical = computeCAGR(a.priceStart, a.priceCurrent, years);
    const cagr5Y = computeCAGR(a.price5YAgo, a.priceCurrent, 5);
    return {
      ticker: a.ticker,
      name: a.name,
      sector: a.sector,
      marketCap: a.marketCap,
      ipoYear: a.ipoYear,
      priceStart: a.priceStart,
      priceCurrent: a.priceCurrent,
      years,
      cagrHistorical,
      cagr5Y,
    };
  }).sort((a, b) => b.cagrHistorical - a.cagrHistorical);
}

// ============================================================
// PROYECCIONES MULTI-FACTOR
// ============================================================
function buildProjections(performances: AssetPerformance[]): AssetProjection[] {
  // S&P 500 base CAGR for benchmark comparison
  const spxPerf = performances.find(p => p.ticker === "SPX");
  const spxBaseCagr = spxPerf ? (spxPerf.cagrHistorical * 0.4 + spxPerf.cagr5Y * 0.6) : 10;

  return performances.map(p => {
    const baseCagr = p.cagrHistorical * 0.4 + p.cagr5Y * 0.6;
    const conservativeCagr = Math.min(p.cagrHistorical, p.cagr5Y) * 0.7;
    const optimisticCagr = Math.max(p.cagrHistorical, p.cagr5Y) * 1.1;

    const price5YBase = p.priceCurrent * Math.pow(1 + baseCagr / 100, 5);
    const price10YBase = p.priceCurrent * Math.pow(1 + baseCagr / 100, 10);
    const price5YCons = p.priceCurrent * Math.pow(1 + conservativeCagr / 100, 5);
    const price10YCons = p.priceCurrent * Math.pow(1 + conservativeCagr / 100, 10);
    const price5YOpt = p.priceCurrent * Math.pow(1 + optimisticCagr / 100, 5);
    const price10YOpt = p.priceCurrent * Math.pow(1 + optimisticCagr / 100, 10);

    // Confidence: higher for assets with longer history and consistent CAGR
    const cagrDiff = Math.abs(p.cagrHistorical - p.cagr5Y);
    const confidence: AssetProjection["confidence"] = p.years > 30 && cagrDiff < 10 ? "high" : p.years > 15 ? "medium" : "low";

    return {
      ticker: p.ticker,
      name: p.name,
      sector: p.sector,
      priceCurrent: p.priceCurrent,
      cagrHistorical: p.cagrHistorical,
      cagr5Y: p.cagr5Y,
      confidence,
      scenarios: {
        conservative: { cagr: conservativeCagr, price5Y: price5YCons, price10Y: price10YCons },
        base: { cagr: baseCagr, price5Y: price5YBase, price10Y: price10YBase },
        optimistic: { cagr: optimisticCagr, price5Y: price5YOpt, price10Y: price10YOpt },
      },
      excessVsBenchmark: baseCagr - spxBaseCagr,
    };
  });
}

const rawAssets = generateMonthlyData();
const ratioData = computeRatios(rawAssets);
const stockDomData = generateStockDominance();

// ============================================================
// PAIR DEFINITIONS BY CLASS
// ============================================================
export const PAIR_DEFS: { name: string; pair: string; key: keyof ClassRatioDataPoint; assetClass: string; description: string; color: string }[] = [
  // Commodities
  { name: "Oro ÷ Plata", pair: "Oro / Plata", key: "goldSilver", assetClass: "Commodities", description: ">80 = plata barata · <50 = plata cara", color: "gold" },
  { name: "Oro ÷ Petróleo", pair: "Oro / Petróleo", key: "goldOil", assetClass: "Commodities", description: "Refugio vs. energía · ratio alto = petróleo barato", color: "amber" },
  { name: "Oro ÷ Cobre", pair: "Oro / Cobre", key: "goldCopper", assetClass: "Commodities", description: "Refugio vs. ciclo industrial", color: "red" },
  { name: "Plata ÷ Petróleo", pair: "Plata / Petróleo", key: "silverOil", assetClass: "Commodities", description: "Metal monetario vs. energía", color: "muted" },
  // Equities
  { name: "S&P 500 ÷ Nasdaq", pair: "S&P 500 / Nasdaq", key: "sp500Nasdaq", assetClass: "Equities", description: "Broad market vs. tech-heavy", color: "blue" },
  { name: "Tesla ÷ S&P 500", pair: "Tesla / S&P 500", key: "teslaSp500", assetClass: "Equities", description: "Especulación pura vs. mercado", color: "red" },
  { name: "S&P 500 ÷ MSCI", pair: "S&P 500 / MSCI World", key: "sp500Msci", assetClass: "Equities", description: "USA vs. mundo", color: "cyan" },
  { name: "Nasdaq ÷ MSCI", pair: "Nasdaq / MSCI World", key: "nasdaqMsci", assetClass: "Equities", description: "Tech USA vs. mundo", color: "purple" },
  // Crypto
  { name: "BTC ÷ ETH", pair: "BTC / ETH", key: "btcEth", assetClass: "Crypto", description: "Store-of-value vs. smart contracts", color: "amber" },
  { name: "ETH ÷ SOL", pair: "ETH / SOL", key: "ethSol", assetClass: "Crypto", description: "L1 legacy vs. L1 nueva generación", color: "purple" },
  { name: "BTC ÷ SOL", pair: "BTC / SOL", key: "btcSol", assetClass: "Crypto", description: "Reserva digital vs. alt L1", color: "cyan" },
  // BTC vs classes
  { name: "BTC ÷ Oro", pair: "BTC / Oro", key: "btcGold", assetClass: "BTC vs Todo", description: "Reserva digital vs. reserva física", color: "gold" },
  { name: "BTC ÷ S&P 500", pair: "BTC / S&P 500", key: "btcSp500", assetClass: "BTC vs Todo", description: "Escasez absoluta vs. equity", color: "blue" },
  { name: "BTC ÷ Real Estate", pair: "BTC / Real Estate", key: "btcRealEstate", assetClass: "BTC vs Todo", description: "Digital vs. tangible", color: "purple" },
];

const SMA_LONG = 200;  // meses — ventana para media y z-score
const SMA_SHORT = 50;  // meses — media corta para cruces

function buildSummaries(): RatioSummary[] {
  return PAIR_DEFS.map(({ pair, key, assetClass }) => {
    const values = ratioData.map((d) => d[key] as number);
    const current = values[values.length - 1];

    // Usar ventana SMA para media y stdDev (en vez de todo el histórico)
    const windowSize = Math.min(SMA_LONG, values.length);
    const windowValues = values.slice(-windowSize);
    const { mean, stdDev } = computeStats(windowValues);

    const zScore = stdDev > 0 ? (current - mean) / stdDev : 0;
    const { signal, signalType, context } = getSignal(zScore, pair);
    return { name: `${pair}`, pair, assetClass, current, mean, stdDev, zScore, signal, signalType, context };
  });
}

function buildRotationSignals(sums: RatioSummary[]): RotationSignal[] {
  const signals: RotationSignal[] = [];
  for (const s of sums) {
    const parts = s.pair.split(" / ");
    if (s.zScore > 1.5) {
      signals.push({ message: `${parts[0]} caro vs ${parts[1]} — rotar hacia ${parts[1]}`, type: "rotate_from", pair: s.pair, assetClass: s.assetClass, zScore: s.zScore });
    } else if (s.zScore < -1.5) {
      signals.push({ message: `${parts[0]} barato vs ${parts[1]} — acumular ${parts[0]}`, type: "rotate_to", pair: s.pair, assetClass: s.assetClass, zScore: s.zScore });
    }
  }
  return signals.sort((a, b) => Math.abs(b.zScore) - Math.abs(a.zScore));
}

// Build data in correct order (summaries needed for signals computation)
const summariesData = buildSummaries();

// EXPORTS
export const assetData = rawAssets;
export const ratios = ratioData;
export const dominance = computeDominance(rawAssets);
export const stockDominance = stockDomData;
export const summaries = summariesData;
export const rotationSignals = buildRotationSignals(summaries);
export const cryptoDominanceData = computeCryptoDominance(rawAssets);
export const cryptoRotation = getCryptoRotationSignal(cryptoDominanceData);
export const assetClassSignals = computeAssetClassSignals();
export const assetPerformance = buildPerformanceData();
export const assetProjections = buildProjections(assetPerformance);

export const ASSET_CLASSES = ["Commodities", "Equities", "Crypto", "BTC vs Todo"] as const;

export function getFilteredData(timeframe: string): {
  assets: AssetDataPoint[];
  ratios: ClassRatioDataPoint[];
  dominance: DominanceDataPoint[];
  stockDom: StockDominanceDataPoint[];
  cryptoDom: CryptoDominancePoint[];
} {
  const months = timeframe === "1Y" ? 12 : timeframe === "3Y" ? 36 : timeframe === "5Y" ? 60 : timeframe === "10Y" ? 120 : rawAssets.length;
  const sliced = rawAssets.slice(-months);
  const slicedStockDom = stockDomData.slice(-Math.min(months, stockDomData.length));
  return {
    assets: sliced,
    ratios: computeRatios(sliced),
    dominance: computeDominance(sliced),
    stockDom: slicedStockDom,
    cryptoDom: computeCryptoDominance(sliced),
  };
}

export function formatRatio(value: number): string {
  if (value >= 10000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (value >= 100) return value.toFixed(1);
  if (value >= 1) return value.toFixed(2);
  if (value >= 0.01) return value.toFixed(4);
  return value.toExponential(2);
}

export function getSummariesByClass(cls: string): RatioSummary[] {
  return summaries.filter((s) => s.assetClass === cls);
}

// Compute SMA series for a given ratio key over filtered data
export function computeRatioSMAs(
  data: ClassRatioDataPoint[],
  key: keyof ClassRatioDataPoint,
): { sma50: (number | null)[]; sma200: (number | null)[] } {
  const values = data.map((d) => d[key] as number);
  return {
    sma50: computeSMA(values, Math.min(SMA_SHORT, values.length)),
    sma200: computeSMA(values, Math.min(SMA_LONG, values.length)),
  };
}

export { SMA_LONG, SMA_SHORT };
