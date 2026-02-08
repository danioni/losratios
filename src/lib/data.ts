// ============================================================
// Los Ratios — Mock Data Layer
// Cross-asset ratios DENTRO de cada asset class
// + BTC vs Todo como sección especial
// + Dominancia por market cap (macro + top 50 acciones)
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
  goldMcap: number;
  silverMcap: number;
  equitiesMcap: number;
  realEstateMcap: number;
  bondsMcap: number;
  cryptoMcap: number;  // total crypto
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
// These represent approximate year-end market caps
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
    .map(([sector, data]) => ({
      sector,
      currentDom: data.current,
      startDom: data.start,
      changePp: data.current - data.start,
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
// HISTORICAL ANCHORS (2014-2025)
// ============================================================
const anchors: AssetDataPoint[] = [
  { date: "2014", gold: 1266, silver: 19.1, oil: 53, copper: 2.88, sp500: 2059, nasdaq: 4736, msciWorld: 1710, tesla: 44, caseShiller: 171, btc: 320, eth: 0.3, sol: 0, btcMcap: 0.005, goldMcap: 7.5, silverMcap: 0.5, equitiesMcap: 65, realEstateMcap: 220, bondsMcap: 100, cryptoMcap: 0.006 },
  { date: "2015", gold: 1160, silver: 15.7, oil: 37, copper: 2.13, sp500: 2044, nasdaq: 5007, msciWorld: 1663, tesla: 43, caseShiller: 179, btc: 430, eth: 0.9, sol: 0, btcMcap: 0.007, goldMcap: 7.0, silverMcap: 0.4, equitiesMcap: 67, realEstateMcap: 230, bondsMcap: 105, cryptoMcap: 0.008 },
  { date: "2016", gold: 1251, silver: 17.1, oil: 54, copper: 2.50, sp500: 2239, nasdaq: 5383, msciWorld: 1751, tesla: 42, caseShiller: 189, btc: 960, eth: 8, sol: 0, btcMcap: 0.015, goldMcap: 7.6, silverMcap: 0.5, equitiesMcap: 70, realEstateMcap: 240, bondsMcap: 110, cryptoMcap: 0.018 },
  { date: "2017", gold: 1303, silver: 17.1, oil: 60, copper: 3.26, sp500: 2674, nasdaq: 6903, msciWorld: 2103, tesla: 62, caseShiller: 200, btc: 14000, eth: 725, sol: 0, btcMcap: 0.23, goldMcap: 7.8, silverMcap: 0.5, equitiesMcap: 80, realEstateMcap: 260, bondsMcap: 115, cryptoMcap: 0.6 },
  { date: "2018", gold: 1282, silver: 15.5, oil: 45, copper: 2.63, sp500: 2507, nasdaq: 6635, msciWorld: 1884, tesla: 60, caseShiller: 211, btc: 3800, eth: 133, sol: 0, btcMcap: 0.066, goldMcap: 7.7, silverMcap: 0.4, equitiesMcap: 75, realEstateMcap: 270, bondsMcap: 115, cryptoMcap: 0.13 },
  { date: "2019", gold: 1517, silver: 17.9, oil: 61, copper: 2.80, sp500: 3231, nasdaq: 8973, msciWorld: 2358, tesla: 84, caseShiller: 220, btc: 7200, eth: 130, sol: 0.2, btcMcap: 0.13, goldMcap: 9.0, silverMcap: 0.5, equitiesMcap: 88, realEstateMcap: 280, bondsMcap: 120, cryptoMcap: 0.19 },
  { date: "2020", gold: 1898, silver: 26.5, oil: 49, copper: 3.52, sp500: 3756, nasdaq: 12888, msciWorld: 2690, tesla: 705, caseShiller: 239, btc: 28900, eth: 737, sol: 1.5, btcMcap: 0.54, goldMcap: 11.5, silverMcap: 0.7, equitiesMcap: 95, realEstateMcap: 290, bondsMcap: 130, cryptoMcap: 0.77 },
  { date: "2021", gold: 1829, silver: 23.4, oil: 75, copper: 4.46, sp500: 4766, nasdaq: 15645, msciWorld: 3230, tesla: 1056, caseShiller: 276, btc: 47000, eth: 3680, sol: 170, btcMcap: 0.9, goldMcap: 11.0, silverMcap: 0.6, equitiesMcap: 120, realEstateMcap: 330, bondsMcap: 130, cryptoMcap: 2.2 },
  { date: "2022", gold: 1824, silver: 24.0, oil: 80, copper: 3.81, sp500: 3840, nasdaq: 10466, msciWorld: 2602, tesla: 123, caseShiller: 308, btc: 16500, eth: 1200, sol: 10, btcMcap: 0.32, goldMcap: 11.0, silverMcap: 0.6, equitiesMcap: 98, realEstateMcap: 340, bondsMcap: 125, cryptoMcap: 0.8 },
  { date: "2023", gold: 2063, silver: 24.1, oil: 72, copper: 3.85, sp500: 4770, nasdaq: 15011, msciWorld: 3169, tesla: 248, caseShiller: 312, btc: 42200, eth: 2350, sol: 100, btcMcap: 0.82, goldMcap: 12.5, silverMcap: 0.6, equitiesMcap: 110, realEstateMcap: 350, bondsMcap: 133, cryptoMcap: 1.6 },
  { date: "2024", gold: 2625, silver: 30.5, oil: 71, copper: 4.20, sp500: 5881, nasdaq: 19310, msciWorld: 3700, tesla: 421, caseShiller: 324, btc: 93000, eth: 3400, sol: 190, btcMcap: 1.84, goldMcap: 16.0, silverMcap: 0.8, equitiesMcap: 120, realEstateMcap: 360, bondsMcap: 140, cryptoMcap: 3.3 },
  { date: "2025", gold: 2850, silver: 31.8, oil: 73, copper: 4.35, sp500: 6020, nasdaq: 19650, msciWorld: 3750, tesla: 390, caseShiller: 330, btc: 97000, eth: 2700, sol: 200, btcMcap: 1.92, goldMcap: 18.0, silverMcap: 0.9, equitiesMcap: 122, realEstateMcap: 365, bondsMcap: 140, cryptoMcap: 3.1 },
  { date: "2026", gold: 2870, silver: 32.2, oil: 71, copper: 4.40, sp500: 6050, nasdaq: 19800, msciWorld: 3780, tesla: 370, caseShiller: 335, btc: 98000, eth: 2750, sol: 210, btcMcap: 1.94, goldMcap: 18.2, silverMcap: 0.9, equitiesMcap: 124, realEstateMcap: 370, bondsMcap: 142, cryptoMcap: 3.2 },
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
        goldMcap: lerp(a.goldMcap, b.goldMcap, t),
        silverMcap: lerp(a.silverMcap, b.silverMcap, t),
        equitiesMcap: lerp(a.equitiesMcap, b.equitiesMcap, t),
        realEstateMcap: lerp(a.realEstateMcap, b.realEstateMcap, t),
        bondsMcap: lerp(a.bondsMcap, b.bondsMcap, t),
        cryptoMcap: lerp(a.cryptoMcap, b.cryptoMcap, t),
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

// EXPORTS
export const assetData = rawAssets;
export const ratios = ratioData;
export const dominance = computeDominance(rawAssets);
export const stockDominance = stockDomData;
export const summaries = buildSummaries();
export const rotationSignals = buildRotationSignals(summaries);

export const ASSET_CLASSES = ["Commodities", "Equities", "Crypto", "BTC vs Todo"] as const;

export function getFilteredData(timeframe: string): {
  assets: AssetDataPoint[];
  ratios: ClassRatioDataPoint[];
  dominance: DominanceDataPoint[];
  stockDom: StockDominanceDataPoint[];
} {
  const months = timeframe === "1Y" ? 12 : timeframe === "3Y" ? 36 : timeframe === "5Y" ? 60 : timeframe === "10Y" ? 120 : rawAssets.length;
  const sliced = rawAssets.slice(-months);
  const slicedStockDom = stockDomData.slice(-Math.min(months, stockDomData.length));
  return {
    assets: sliced,
    ratios: computeRatios(sliced),
    dominance: computeDominance(sliced),
    stockDom: slicedStockDom,
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
