// ============================================================
// Los Ratios — Data Layer
// 5 ratios that matter + universe of winners
// Structure ready for real APIs (CoinGecko, FRED, Yahoo Finance)
// ============================================================

export interface AssetDataPoint {
  date: string;
  gold: number;
  silver: number;
  sp500: number;
  nasdaq: number;
  btc: number;
  m2Global: number;    // M2 Global proxy (trillions USD)
}

// The 5 ratios that matter
export interface ClassRatioDataPoint {
  date: string;
  btcGold: number;       // BTC / Oro — EL RATIO CENTRAL
  goldSp500: number;     // Oro / S&P 500
  btcSp500: number;      // BTC / S&P 500
  nasdaqSp500: number;   // Nasdaq / S&P 500
  goldSilver: number;    // Oro / Plata
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
  context: string;
}

export interface RotationSignal {
  message: string;
  type: "rotate_from" | "rotate_to";
  pair: string;
  zScore: number;
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
// PERFORMANCE HISTÓRICA (CAGR) — Universe of Winners
// ============================================================
export interface AssetPerformance {
  ticker: string;
  name: string;
  sector: string;
  marketCap: number;       // billions USD
  ipoYear: number;
  priceStart: number;
  price5YAgo: number;
  priceCurrent: number;
  years: number;
  cagrHistorical: number;  // % anual
  cagr5Y: number;          // % anual últimos 5 años
  vsM2: number;            // CAGR - 7 (M2 benchmark)
  beatsM2: boolean;
}

// ============================================================
// PAIR DEFINITIONS — only the 5 that matter
// ============================================================
export const PAIR_DEFS: { name: string; pair: string; key: keyof ClassRatioDataPoint; description: string; color: string; startYear: number }[] = [
  { name: "BTC ÷ Oro", pair: "BTC / Oro", key: "btcGold", description: "Market share del digital gold — ¿está ganando el argumento?", color: "gold", startYear: 2010 },
  { name: "Oro ÷ S&P 500", pair: "Oro / S&P 500", key: "goldSp500", description: "Fear vs greed — protección vs crecimiento", color: "amber", startYear: 1971 },
  { name: "BTC ÷ S&P 500", pair: "BTC / S&P 500", key: "btcSp500", description: "Hard money vs capital productivo", color: "cyan", startYear: 2010 },
  { name: "Nasdaq ÷ S&P 500", pair: "Nasdaq / S&P 500", key: "nasdaqSp500", description: "Growth vs quality — el ciclo dentro del ciclo", color: "blue", startYear: 1971 },
  { name: "Oro ÷ Plata", pair: "Oro / Plata", key: "goldSilver", description: "Escasez pura vs escasez con utilidad — >80 = plata barata", color: "red", startYear: 1971 },
];

const SMA_LONG = 200;  // meses — ventana para media y z-score
const SMA_SHORT = 50;  // meses — media corta para cruces

// ============================================================
// HISTORICAL ANCHORS (1971-2026)
// Starts at 1971: Nixon shock (fiat standard) + Nasdaq launch
// Sources: FRED M2SL, Yahoo Finance, WGC, CoinGecko,
//          elnumerador.com, eldenominador.com
// BTC = 0 before 2009 (didn't exist); BTC ratios skip those rows
// ============================================================
const anchors: AssetDataPoint[] = [
  // ── Fiat standard era (1971-1994) ────────────────────────
  { date: "1971", gold: 41, silver: 1.4, sp500: 102, nasdaq: 114, btc: 0, m2Global: 4 },
  { date: "1973", gold: 106, silver: 3.3, sp500: 97, nasdaq: 92, btc: 0, m2Global: 5 },
  { date: "1975", gold: 140, silver: 4.4, sp500: 90, nasdaq: 78, btc: 0, m2Global: 6 },
  { date: "1977", gold: 165, silver: 4.7, sp500: 95, nasdaq: 105, btc: 0, m2Global: 7 },
  { date: "1979", gold: 512, silver: 21.8, sp500: 108, nasdaq: 152, btc: 0, m2Global: 9 },
  { date: "1980", gold: 615, silver: 16.4, sp500: 136, nasdaq: 202, btc: 0, m2Global: 10 },
  { date: "1982", gold: 456, silver: 10.8, sp500: 141, nasdaq: 232, btc: 0, m2Global: 12 },
  { date: "1984", gold: 309, silver: 6.1, sp500: 167, nasdaq: 247, btc: 0, m2Global: 13 },
  { date: "1986", gold: 391, silver: 5.5, sp500: 242, nasdaq: 349, btc: 0, m2Global: 15 },
  { date: "1988", gold: 410, silver: 6.1, sp500: 278, nasdaq: 381, btc: 0, m2Global: 18 },
  { date: "1990", gold: 383, silver: 4.1, sp500: 330, nasdaq: 374, btc: 0, m2Global: 20 },
  { date: "1992", gold: 333, silver: 3.7, sp500: 435, nasdaq: 677, btc: 0, m2Global: 21 },
  { date: "1994", gold: 384, silver: 5.3, sp500: 459, nasdaq: 752, btc: 0, m2Global: 22 },
  // ── Dot-com era (1995-2008) ──────────────────────────────
  { date: "1995", gold: 387, silver: 5.2, sp500: 616, nasdaq: 1052, btc: 0, m2Global: 23 },
  { date: "1996", gold: 369, silver: 4.9, sp500: 741, nasdaq: 1291, btc: 0, m2Global: 24 },
  { date: "1997", gold: 290, silver: 4.7, sp500: 970, nasdaq: 1570, btc: 0, m2Global: 25 },
  { date: "1998", gold: 288, silver: 5.1, sp500: 1229, nasdaq: 2193, btc: 0, m2Global: 27 },
  { date: "1999", gold: 290, silver: 5.3, sp500: 1469, nasdaq: 4069, btc: 0, m2Global: 28 },
  { date: "2000", gold: 273, silver: 4.6, sp500: 1320, nasdaq: 2471, btc: 0, m2Global: 30 },
  { date: "2001", gold: 276, silver: 4.4, sp500: 1148, nasdaq: 1950, btc: 0, m2Global: 32 },
  { date: "2002", gold: 347, silver: 4.8, sp500: 880, nasdaq: 1336, btc: 0, m2Global: 34 },
  { date: "2003", gold: 416, silver: 5.9, sp500: 1112, nasdaq: 2003, btc: 0, m2Global: 36 },
  { date: "2004", gold: 436, silver: 6.8, sp500: 1212, nasdaq: 2178, btc: 0, m2Global: 38 },
  { date: "2005", gold: 518, silver: 8.8, sp500: 1248, nasdaq: 2205, btc: 0, m2Global: 39 },
  { date: "2006", gold: 636, silver: 12.9, sp500: 1418, nasdaq: 2415, btc: 0, m2Global: 41 },
  { date: "2007", gold: 836, silver: 14.8, sp500: 1468, nasdaq: 2652, btc: 0, m2Global: 44 },
  { date: "2008", gold: 865, silver: 11.0, sp500: 903, nasdaq: 1577, btc: 0, m2Global: 49 },
  // ── BTC era (2009-2026) ──────────────────────────────────
  { date: "2009", gold: 1096, silver: 17.5, sp500: 1115, nasdaq: 2269, btc: 0.001, m2Global: 51 },
  { date: "2010", gold: 1421, silver: 30.9, sp500: 1258, nasdaq: 2653, btc: 0.30, m2Global: 53 },
  { date: "2011", gold: 1566, silver: 28.2, sp500: 1258, nasdaq: 2605, btc: 4.70, m2Global: 57 },
  { date: "2012", gold: 1675, silver: 30.4, sp500: 1426, nasdaq: 3020, btc: 13.5, m2Global: 63 },
  { date: "2013", gold: 1205, silver: 19.5, sp500: 1848, nasdaq: 4177, btc: 751, m2Global: 66 },
  { date: "2014", gold: 1266, silver: 19.1, sp500: 2059, nasdaq: 4736, btc: 320, m2Global: 60 },
  { date: "2015", gold: 1060, silver: 13.9, sp500: 2044, nasdaq: 5007, btc: 430, m2Global: 63 },
  { date: "2016", gold: 1151, silver: 16.1, sp500: 2239, nasdaq: 5383, btc: 960, m2Global: 67 },
  { date: "2017", gold: 1296, silver: 17.1, sp500: 2674, nasdaq: 6903, btc: 14000, m2Global: 73 },
  { date: "2018", gold: 1282, silver: 15.5, sp500: 2507, nasdaq: 6635, btc: 3800, m2Global: 76 },
  { date: "2019", gold: 1517, silver: 17.9, sp500: 3231, nasdaq: 8973, btc: 7200, m2Global: 80 },
  { date: "2020", gold: 1898, silver: 26.5, sp500: 3756, nasdaq: 12888, btc: 28900, m2Global: 95 },
  { date: "2021", gold: 1829, silver: 23.4, sp500: 4766, nasdaq: 15645, btc: 47000, m2Global: 105 },
  { date: "2022", gold: 1824, silver: 24.0, sp500: 3840, nasdaq: 10466, btc: 16500, m2Global: 100 },
  { date: "2023", gold: 2063, silver: 24.1, sp500: 4770, nasdaq: 15011, btc: 42200, m2Global: 104 },
  { date: "2024", gold: 2625, silver: 30.5, sp500: 5881, nasdaq: 19310, btc: 93000, m2Global: 110 },
  { date: "2025", gold: 4315, silver: 72, sp500: 6845, nasdaq: 23242, btc: 87500, m2Global: 114 },
  { date: "2026", gold: 4983, silver: 77, sp500: 6881, nasdaq: 22705, btc: 66676, m2Global: 118 },
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
      result.push({
        date: `${a.date}-${String(m + 1).padStart(2, "0")}`,
        gold: lerp(a.gold, b.gold, t) * n2(),
        silver: lerp(a.silver, b.silver, t) * n2(),
        sp500: lerp(a.sp500, b.sp500, t) * n2(),
        nasdaq: lerp(a.nasdaq, b.nasdaq, t) * n2(),
        btc: lerp(a.btc, b.btc, t) * n1(),
        m2Global: lerp(a.m2Global, b.m2Global, t) * n2(),
      });
    }
  }
  const last = anchors[anchors.length - 1];
  result.push({ ...last, date: `${last.date}-01` });
  return result;
}

function safeDiv(a: number, b: number): number {
  if (!b || !isFinite(b)) return 0;
  const r = a / b;
  return isFinite(r) ? r : 0;
}

function computeRatios(assets: AssetDataPoint[]): ClassRatioDataPoint[] {
  return assets.map((d) => ({
    date: d.date,
    btcGold: safeDiv(d.btc, d.gold),
    goldSp500: safeDiv(d.gold, d.sp500),
    btcSp500: safeDiv(d.btc, d.sp500),
    nasdaqSp500: safeDiv(d.nasdaq, d.sp500),
    goldSilver: safeDiv(d.gold, d.silver),
  }));
}

// ============================================================
// LOG-SCALE DETECTION
// Ratios that span >10x range need log-scale statistics
// ============================================================
export function needsLogScale(values: number[]): boolean {
  const positives = values.filter(v => v > 0);
  if (positives.length < 2) return false;
  const min = Math.min(...positives);
  const max = Math.max(...positives);
  return max / min > 10;
}

// ============================================================
// BOLLINGER BANDS (supports linear or log scale)
// ============================================================
export function computeBollingerBands(
  values: number[],
  dates: string[],
  period: number,
  useLogScale?: boolean,
): BollingerBandPoint[] {
  // Auto-detect log scale if not specified
  const logScale = useLogScale ?? needsLogScale(values);

  return values.map((v, i) => {
    if (i < period - 1 || v <= 0) {
      return { date: dates[i], value: v, sma: null, upper1: null, lower1: null, upper2: null, lower2: null };
    }
    const w = values.slice(i - period + 1, i + 1).filter(x => x > 0);
    if (w.length === 0) {
      return { date: dates[i], value: v, sma: null, upper1: null, lower1: null, upper2: null, lower2: null };
    }

    if (logScale) {
      // Log-scale: compute mean & stddev in log space, then transform back
      const logW = w.map(x => Math.log(x));
      const logMean = logW.reduce((s, x) => s + x, 0) / logW.length;
      const logVariance = logW.reduce((s, x) => s + (x - logMean) ** 2, 0) / logW.length;
      const logSd = Math.sqrt(logVariance);
      return {
        date: dates[i],
        value: v,
        sma: Math.exp(logMean),
        upper1: Math.exp(logMean + logSd),
        lower1: Math.exp(logMean - logSd),
        upper2: Math.exp(logMean + 2 * logSd),
        lower2: Math.exp(logMean - 2 * logSd),
      };
    } else {
      // Linear scale (original behavior)
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
    }
  });
}

// ============================================================
// SMA COMPUTATION (supports geometric mean for log-scale ratios)
// ============================================================
export function computeSMA(values: number[], period: number, useLogScale?: boolean): (number | null)[] {
  const logScale = useLogScale ?? false;
  const result: (number | null)[] = [];
  for (let i = 0; i < values.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      if (logScale) {
        // Geometric mean SMA
        let logSum = 0;
        let count = 0;
        for (let j = i - period + 1; j <= i; j++) {
          if (values[j] > 0) { logSum += Math.log(values[j]); count++; }
        }
        result.push(count > 0 ? Math.exp(logSum / count) : null);
      } else {
        let sum = 0;
        for (let j = i - period + 1; j <= i; j++) sum += values[j];
        result.push(sum / period);
      }
    }
  }
  return result;
}

// ============================================================
// STATISTICS & SIGNALS
// ============================================================
function computeStats(values: number[]): { mean: number; stdDev: number } {
  const n = values.length;
  if (n === 0) return { mean: 0, stdDev: 0 };
  const mean = values.reduce((s, v) => s + v, 0) / n;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / n;
  return { mean, stdDev: Math.sqrt(variance) };
}

/**
 * Compute z-score in log space for ratios that span orders of magnitude.
 * Returns the z-score of log(current) relative to the distribution of log(values).
 * This gives meaningful z-scores for exponential assets like BTC.
 */
function computeLogStats(values: number[]): { mean: number; stdDev: number; logMean: number; logStdDev: number } {
  const positives = values.filter(v => v > 0);
  const n = positives.length;
  if (n === 0) return { mean: 0, stdDev: 0, logMean: 0, logStdDev: 0 };
  const logValues = positives.map(v => Math.log(v));
  const logMean = logValues.reduce((s, v) => s + v, 0) / n;
  const logVariance = logValues.reduce((s, v) => s + (v - logMean) ** 2, 0) / n;
  return {
    mean: Math.exp(logMean),  // geometric mean
    stdDev: Math.exp(Math.sqrt(logVariance)),  // geometric stddev (multiplicative)
    logMean,
    logStdDev: Math.sqrt(logVariance),
  };
}

function getSignal(zScore: number, pair: string): { signal: string; signalType: "overbought" | "oversold" | "neutral"; context: string } {
  const parts = pair.split(" / ");
  const a = parts[0], b = parts[1];
  if (zScore > 2) return { signal: "Fuertemente extendido", signalType: "overbought", context: `${a} muy caro vs ${b}` };
  if (zScore > 1) return { signal: "Extendido", signalType: "overbought", context: `${a} caro relativo a ${b}` };
  if (zScore < -2) return { signal: "Fuertemente comprimido", signalType: "oversold", context: `${a} muy barato vs ${b}` };
  if (zScore < -1) return { signal: "Comprimido", signalType: "oversold", context: `${a} barato relativo a ${b}` };
  return { signal: "Neutral", signalType: "neutral", context: "En equilibrio relativo" };
}

export function generateNarrative(pair: string, zScore: number): string {
  const parts = pair.split(" / ");
  const a = parts[0], b = parts[1];
  const absZ = Math.abs(zScore).toFixed(1);

  if (Math.abs(zScore) < 0.5) {
    return `${a} y ${b} en equilibrio relativo.`;
  }
  if (zScore > 1.5) {
    return `${a} está ${absZ}\u03C3 por encima de su relación histórica con ${b}. Presión histórica de reversión.`;
  }
  if (zScore > 0.5) {
    return `${a} está ${absZ}\u03C3 caro vs ${b}. ${b} históricamente rezagado — oportunidad de acumulación gradual.`;
  }
  if (zScore < -1.5) {
    return `${a} está ${absZ}\u03C3 por debajo de su relación histórica con ${b}. Zona de acumulación histórica.`;
  }
  return `${a} está ${absZ}\u03C3 barato vs ${b}. ${a} históricamente rezagado — oportunidad de acumulación gradual.`;
}

// ============================================================
// BUILD SUMMARIES & ROTATION SIGNALS
// ============================================================
function buildSummaries(ratios: ClassRatioDataPoint[]): RatioSummary[] {
  return PAIR_DEFS.map(({ pair, key }) => {
    const values = ratios.map((d) => d[key] as number);
    const current = values[values.length - 1];

    const windowSize = Math.min(SMA_LONG, values.length);
    const windowValues = values.slice(-windowSize);

    // Use log-scale for ratios that span orders of magnitude (BTC/Gold, BTC/S&P)
    const useLog = needsLogScale(windowValues);

    let zScore: number;
    let mean: number;
    let stdDev: number;

    if (useLog && current > 0) {
      const logStats = computeLogStats(windowValues);
      zScore = logStats.logStdDev > 0 ? (Math.log(current) - logStats.logMean) / logStats.logStdDev : 0;
      mean = logStats.mean;    // geometric mean
      stdDev = logStats.logStdDev;  // in log space
    } else {
      const stats = computeStats(windowValues);
      zScore = stats.stdDev > 0 ? (current - stats.mean) / stats.stdDev : 0;
      mean = stats.mean;
      stdDev = stats.stdDev;
    }

    const { signal, signalType, context } = getSignal(zScore, pair);
    return { name: `${pair}`, pair, current, mean, stdDev, zScore, signal, signalType, context };
  });
}

function buildRotationSignals(sums: RatioSummary[]): RotationSignal[] {
  const signals: RotationSignal[] = [];
  for (const s of sums) {
    const parts = s.pair.split(" / ");
    if (s.zScore > 1.5) {
      signals.push({
        message: `${parts[0]} caro vs ${parts[1]} — ${parts[1]} históricamente rezagado`,
        type: "rotate_from", pair: s.pair, zScore: s.zScore,
      });
    } else if (s.zScore < -1.5) {
      signals.push({
        message: `${parts[0]} barato vs ${parts[1]} — oportunidad de acumulación gradual`,
        type: "rotate_to", pair: s.pair, zScore: s.zScore,
      });
    }
  }
  return signals.sort((a, b) => Math.abs(b.zScore) - Math.abs(a.zScore));
}

// ============================================================
// PERFORMANCE HISTÓRICA — Universe of Winners Only
// ============================================================
const M2_BENCHMARK = 7; // M2 Global CAGR ~7% anual

const PERFORMANCE_ANCHORS: { ticker: string; name: string; sector: string; marketCap: number; ipoYear: number; priceStart: number; price5YAgo: number; priceCurrent: number }[] = [
  // Universe of winners — assets that historically beat M2
  { ticker: "BTC", name: "Bitcoin", sector: "Crypto", marketCap: 1330, ipoYear: 2009, priceStart: 0.001, price5YAgo: 7200, priceCurrent: 66676 },
  { ticker: "GOLD", name: "Oro (onza)", sector: "Commodities", marketCap: 18200, ipoYear: 1971, priceStart: 35, price5YAgo: 1517, priceCurrent: 4983 },
  { ticker: "AAPL", name: "Apple", sector: "Tech", marketCap: 3900, ipoYear: 1980, priceStart: 0.10, price5YAgo: 75, priceCurrent: 265 },
  { ticker: "MSFT", name: "Microsoft", sector: "Tech", marketCap: 2970, ipoYear: 1986, priceStart: 0.10, price5YAgo: 160, priceCurrent: 400 },
  { ticker: "GOOGL", name: "Alphabet", sector: "Tech", marketCap: 3700, ipoYear: 2004, priceStart: 2.50, price5YAgo: 73, priceCurrent: 303 },
  { ticker: "NVDA", name: "NVIDIA", sector: "Tech", marketCap: 4600, ipoYear: 1999, priceStart: 1.50, price5YAgo: 59, priceCurrent: 188 },
  { ticker: "META", name: "Meta", sector: "Tech", marketCap: 1630, ipoYear: 2012, priceStart: 38, price5YAgo: 208, priceCurrent: 643 },
  { ticker: "V", name: "Visa", sector: "Finance", marketCap: 620, ipoYear: 2008, priceStart: 11, price5YAgo: 188, priceCurrent: 320 },
  { ticker: "MA", name: "Mastercard", sector: "Finance", marketCap: 480, ipoYear: 2006, priceStart: 3.90, price5YAgo: 317, priceCurrent: 522 },
  { ticker: "COST", name: "Costco", sector: "Consumer", marketCap: 450, ipoYear: 1985, priceStart: 2.50, price5YAgo: 335, priceCurrent: 1008 },
  { ticker: "BRK.B", name: "Berkshire Hathaway", sector: "Finance", marketCap: 1120, ipoYear: 1996, priceStart: 23, price5YAgo: 220, priceCurrent: 503 },
  // Context assets that DON'T beat M2 — shown for comparison
  { ticker: "SPX", name: "S&P 500", sector: "Index", marketCap: 124000, ipoYear: 1957, priceStart: 44, price5YAgo: 3231, priceCurrent: 6881 },
  { ticker: "SILVER", name: "Plata (onza)", sector: "Commodities", marketCap: 1800, ipoYear: 1971, priceStart: 1.39, price5YAgo: 17.9, priceCurrent: 77 },
];

export function computeCAGR(priceStart: number, priceEnd: number, years: number): number {
  if (priceStart <= 0 || priceEnd <= 0 || years <= 0) return 0;
  return (Math.pow(priceEnd / priceStart, 1 / years) - 1) * 100;
}

export function getAnchorPrice(asset: 'gold' | 'silver' | 'sp500' | 'nasdaq' | 'btc' | 'm2Global', year: number): number {
  let best = anchors[0];
  for (const a of anchors) {
    const aYear = parseInt(a.date);
    if (aYear <= year) best = a;
    if (aYear > year) break;
  }
  return best[asset];
}

function buildPerformanceData(): AssetPerformance[] {
  const currentYear = 2026;
  return PERFORMANCE_ANCHORS.map(a => {
    const years = currentYear - a.ipoYear;
    const cagrHistorical = computeCAGR(a.priceStart, a.priceCurrent, years);
    const cagr5Y = computeCAGR(a.price5YAgo, a.priceCurrent, 5);
    const vsM2 = cagrHistorical - M2_BENCHMARK;
    return {
      ticker: a.ticker,
      name: a.name,
      sector: a.sector,
      marketCap: a.marketCap,
      ipoYear: a.ipoYear,
      priceStart: a.priceStart,
      price5YAgo: a.price5YAgo,
      priceCurrent: a.priceCurrent,
      years,
      cagrHistorical,
      cagr5Y,
      vsM2,
      beatsM2: cagrHistorical > M2_BENCHMARK,
    };
  }).sort((a, b) => b.cagrHistorical - a.cagrHistorical);
}

// ============================================================
// BUILD ALL DATA
// ============================================================
const rawAssets = generateMonthlyData();
const ratioData = computeRatios(rawAssets);
const summariesData = buildSummaries(ratioData);

// EXPORTS (static fallback data for SSR / offline)
export const assetData = rawAssets;
export const ratios = ratioData;
export const summaries = summariesData;
export const rotationSignals = buildRotationSignals(summaries);
export const assetPerformance = buildPerformanceData();

// ============================================================
// COMPUTED MARKET DATA — used by API route
// ============================================================
export interface ComputedMarketData {
  assetData: AssetDataPoint[];
  ratios: ClassRatioDataPoint[];
  summaries: RatioSummary[];
  rotationSignals: RotationSignal[];
  assetPerformance: AssetPerformance[];
}

/**
 * Takes raw AssetDataPoint[] (from real APIs) and computes everything.
 */
export function computeAllFromRawAssets(assets: AssetDataPoint[]): ComputedMarketData {
  const ratioD = computeRatios(assets);
  const sumsD = buildSummaries(ratioD);
  const rotD = buildRotationSignals(sumsD);
  const perfD = buildPerformanceData(); // static anchors (CAGR benchmarks)

  return {
    assetData: assets,
    ratios: ratioD,
    summaries: sumsD,
    rotationSignals: rotD,
    assetPerformance: perfD,
  };
}

export function getFilteredData(
  timeframe: string,
  sourceAssets?: AssetDataPoint[],
): {
  assets: AssetDataPoint[];
  ratios: ClassRatioDataPoint[];
} {
  const assets = sourceAssets ?? rawAssets;
  const months = timeframe === "1Y" ? 12 : timeframe === "3Y" ? 36 : timeframe === "5Y" ? 60 : timeframe === "10Y" ? 120 : assets.length;
  const sliced = assets.slice(-months);
  return {
    assets: sliced,
    ratios: computeRatios(sliced),
  };
}

export function formatRatio(value: number): string {
  if (value >= 10000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (value >= 100) return value.toFixed(1);
  if (value >= 10) return value.toFixed(2);
  if (value >= 1) return value.toFixed(2);
  if (value >= 0.01) return value.toFixed(4);
  if (value >= 0.0001) return value.toFixed(6);
  return value.toExponential(2);
}

// Compute SMA series for a given ratio key over filtered data
export function computeRatioSMAs(
  data: ClassRatioDataPoint[],
  key: keyof ClassRatioDataPoint,
): { sma50: (number | null)[]; sma200: (number | null)[]; isLogScale: boolean } {
  const values = data.map((d) => d[key] as number);
  const useLog = needsLogScale(values);
  return {
    sma50: computeSMA(values, Math.min(SMA_SHORT, values.length), useLog),
    sma200: computeSMA(values, Math.min(SMA_LONG, values.length), useLog),
    isLogScale: useLog,
  };
}

export { SMA_LONG, SMA_SHORT };
