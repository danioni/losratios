// ============================================================
// Los Ratios — métricas y tablas que todavía no se publican
// Los ratios que muestra el sitio no salen de acá: se leen de senales/ en el
// build (src/lib/series.ts). Este archivo conserva el código de lo que está
// oculto: las funciones de las métricas y los datos de las tablas de CAGR.
// ============================================================

export interface AssetDataPoint {
  date: string;
  gold: number;
  silver: number;
  sp500: number;
  nasdaq: number;
  btc: number;
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
  vsM2: number;            // CAGR − 7 (supuesto de expansión monetaria ~7% anual, no dato medido)
  beatsM2: boolean;
}

const SMA_LONG = 200;  // meses — ventana para media y z-score
const SMA_SHORT = 50;  // meses — media corta para cruces

// ============================================================
// MÉTRICAS — FLAG
// El sitio muestra el nivel mensual de cada ratio. z-score, percentil,
// etiquetas (Neutral/Extendido/Extremo), bandas de Bollinger y señales de
// rotación no se publican todavía: se publicarán en la siguiente etapa sobre
// estas mismas series, y solo con los meses que ratios.csv marca como aptos
// (apto_metricas, A-R0-17 y A-R0-20). Las funciones de cálculo se conservan
// abajo; el flag queda en false hasta entonces.
// ============================================================
export const METRICAS_VERIFICADAS = false;
export const NO_MEDIDO = "NO MEDIDO: se publicarán en la siguiente etapa sobre estas mismas series.";

// ============================================================
// TABLAS DE CAGR Y PODER ADQUISITIVO — FLAG
// Sus cifras salen de valores de referencia escritos a mano (los anclajes de
// abajo y los de currency.ts), no de series observadas. Quedan ocultas hasta
// tenerlas; el código de las tablas se conserva.
// ============================================================
export const TABLAS_MEDIDAS = false;
export const NO_MEDIDO_TABLAS = "NO MEDIDO: se publicarán cuando haya series observadas para ellas.";
export const NOTA_VALORES_REFERENCIA =
  "Calculado sobre valores de referencia sin procedencia verificada; se reemplaza cuando haya series observadas.";

// ============================================================
// VALORES DE REFERENCIA (1971-2026)
// Escritos a mano, sin procedencia verificada. Ya no alimentan ningún ratio:
// solo los lee getAnchorPrice(), para la tabla de CAGR, que está oculta.
// ============================================================
const anchors: AssetDataPoint[] = [
  // ── Fiat standard era (1971-1994) ────────────────────────
  { date: "1971", gold: 41, silver: 1.4, sp500: 102, nasdaq: 114, btc: 0 },
  { date: "1973", gold: 106, silver: 3.3, sp500: 97, nasdaq: 92, btc: 0 },
  { date: "1975", gold: 140, silver: 4.4, sp500: 90, nasdaq: 78, btc: 0 },
  { date: "1977", gold: 165, silver: 4.7, sp500: 95, nasdaq: 105, btc: 0 },
  { date: "1979", gold: 512, silver: 21.8, sp500: 108, nasdaq: 152, btc: 0 },
  { date: "1980", gold: 615, silver: 16.4, sp500: 136, nasdaq: 202, btc: 0 },
  { date: "1982", gold: 456, silver: 10.8, sp500: 141, nasdaq: 232, btc: 0 },
  { date: "1984", gold: 309, silver: 6.1, sp500: 167, nasdaq: 247, btc: 0 },
  { date: "1986", gold: 391, silver: 5.5, sp500: 242, nasdaq: 349, btc: 0 },
  { date: "1988", gold: 410, silver: 6.1, sp500: 278, nasdaq: 381, btc: 0 },
  { date: "1990", gold: 383, silver: 4.1, sp500: 330, nasdaq: 374, btc: 0 },
  { date: "1992", gold: 333, silver: 3.7, sp500: 435, nasdaq: 677, btc: 0 },
  { date: "1994", gold: 384, silver: 5.3, sp500: 459, nasdaq: 752, btc: 0 },
  // ── Dot-com era (1995-2008) ──────────────────────────────
  { date: "1995", gold: 387, silver: 5.2, sp500: 616, nasdaq: 1052, btc: 0 },
  { date: "1996", gold: 369, silver: 4.9, sp500: 741, nasdaq: 1291, btc: 0 },
  { date: "1997", gold: 290, silver: 4.7, sp500: 970, nasdaq: 1570, btc: 0 },
  { date: "1998", gold: 288, silver: 5.1, sp500: 1229, nasdaq: 2193, btc: 0 },
  { date: "1999", gold: 290, silver: 5.3, sp500: 1469, nasdaq: 4069, btc: 0 },
  { date: "2000", gold: 273, silver: 4.6, sp500: 1320, nasdaq: 2471, btc: 0 },
  { date: "2001", gold: 276, silver: 4.4, sp500: 1148, nasdaq: 1950, btc: 0 },
  { date: "2002", gold: 347, silver: 4.8, sp500: 880, nasdaq: 1336, btc: 0 },
  { date: "2003", gold: 416, silver: 5.9, sp500: 1112, nasdaq: 2003, btc: 0 },
  { date: "2004", gold: 436, silver: 6.8, sp500: 1212, nasdaq: 2178, btc: 0 },
  { date: "2005", gold: 518, silver: 8.8, sp500: 1248, nasdaq: 2205, btc: 0 },
  { date: "2006", gold: 636, silver: 12.9, sp500: 1418, nasdaq: 2415, btc: 0 },
  { date: "2007", gold: 836, silver: 14.8, sp500: 1468, nasdaq: 2652, btc: 0 },
  { date: "2008", gold: 865, silver: 11.0, sp500: 903, nasdaq: 1577, btc: 0 },
  // ── BTC era (2009-2026) ──────────────────────────────────
  { date: "2009", gold: 1096, silver: 17.5, sp500: 1115, nasdaq: 2269, btc: 0.001 },
  { date: "2010", gold: 1421, silver: 30.9, sp500: 1258, nasdaq: 2653, btc: 0.30 },
  { date: "2011", gold: 1566, silver: 28.2, sp500: 1258, nasdaq: 2605, btc: 4.70 },
  { date: "2012", gold: 1675, silver: 30.4, sp500: 1426, nasdaq: 3020, btc: 13.5 },
  { date: "2013", gold: 1205, silver: 19.5, sp500: 1848, nasdaq: 4177, btc: 751 },
  { date: "2014", gold: 1266, silver: 19.1, sp500: 2059, nasdaq: 4736, btc: 320 },
  { date: "2015", gold: 1060, silver: 13.9, sp500: 2044, nasdaq: 5007, btc: 430 },
  { date: "2016", gold: 1151, silver: 16.1, sp500: 2239, nasdaq: 5383, btc: 960 },
  { date: "2017", gold: 1296, silver: 17.1, sp500: 2674, nasdaq: 6903, btc: 14000 },
  { date: "2018", gold: 1282, silver: 15.5, sp500: 2507, nasdaq: 6635, btc: 3800 },
  { date: "2019", gold: 1517, silver: 17.9, sp500: 3231, nasdaq: 8973, btc: 7200 },
  { date: "2020", gold: 1898, silver: 26.5, sp500: 3756, nasdaq: 12888, btc: 28900 },
  { date: "2021", gold: 1829, silver: 23.4, sp500: 4766, nasdaq: 15645, btc: 47000 },
  { date: "2022", gold: 1824, silver: 24.0, sp500: 3840, nasdaq: 10466, btc: 16500 },
  { date: "2023", gold: 2063, silver: 24.1, sp500: 4770, nasdaq: 15011, btc: 42200 },
  { date: "2024", gold: 2625, silver: 30.5, sp500: 5881, nasdaq: 19310, btc: 93000 },
  { date: "2025", gold: 4315, silver: 72, sp500: 6845, nasdaq: 23242, btc: 87500 },
  { date: "2026", gold: 5162, silver: 87, sp500: 6901, nasdaq: 22878, btc: 67650 },
];

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
export function computeStats(values: number[]): { mean: number; stdDev: number } {
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
export function computeLogStats(values: number[]): { mean: number; stdDev: number; logMean: number; logStdDev: number } {
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

/**
 * Percentil empírico: fracción de observaciones de `values` estrictamente por
 * debajo del valor actual (y, por separado, estrictamente por encima).
 * No supone normalidad. Debe recibir exactamente la misma ventana que se usó
 * para el z-score (en escala log: solo los valores positivos de la ventana).
 */
export function computeEmpiricalPercentile(
  values: number[],
  current: number,
): { below: number; above: number; n: number } {
  const n = values.length;
  if (n === 0 || !isFinite(current)) return { below: 0, above: 0, n: 0 };
  let below = 0;
  let above = 0;
  for (const v of values) {
    if (v < current) below++;
    else if (v > current) above++;
  }
  return { below: below / n, above: above / n, n };
}

// ============================================================
// CORTES DE SEÑAL — únicos para etiqueta, narrativa y rotación
//   |z| < 1        → Neutral
//   1 ≤ |z| < 2    → Extendido (z > 0) / Comprimido (z < 0)
//   |z| ≥ 2        → Extremo
// ============================================================
export const Z_EXTENDED = 1;
export const Z_EXTREME = 2;

export function formatZ(zScore: number): string {
  return `${zScore >= 0 ? "+" : ""}${zScore.toFixed(1)}σ`;
}

export function getSignal(zScore: number, pair: string): { signal: string; signalType: "overbought" | "oversold" | "neutral"; context: string } {
  const absZ = Math.abs(zScore);
  const context = generateNarrative(pair, zScore);
  if (absZ >= Z_EXTREME) {
    return { signal: "Extremo", signalType: zScore > 0 ? "overbought" : "oversold", context };
  }
  if (absZ >= Z_EXTENDED) {
    return zScore > 0
      ? { signal: "Extendido", signalType: "overbought", context }
      : { signal: "Comprimido", signalType: "oversold", context };
  }
  return { signal: "Neutral", signalType: "neutral", context };
}

/**
 * Texto descriptivo del estado del ratio. Sin verbos de acción ni "oportunidad":
 * describe dónde está el ratio respecto de su historia, nada más.
 */
export function generateNarrative(pair: string, zScore: number): string {
  const parts = pair.split(" / ");
  const a = parts[0], b = parts[1];
  const absZ = Math.abs(zScore);
  const z = formatZ(zScore);

  if (absZ < Z_EXTENDED) {
    return `${a}/${b} cerca de su relación histórica`;
  }
  if (absZ < Z_EXTREME) {
    return `${a} ${zScore > 0 ? "caro" : "barato"} vs ${b} respecto de su historia (${z})`;
  }
  return `${a}/${b} en zona extrema de su historia (${z}). Históricamente los extremos tienden a revertir; el momento no es predecible.`;
}

// ============================================================
// PERFORMANCE HISTÓRICA — Universe of Winners Only
// ============================================================
const M2_BENCHMARK = 7; // Supuesto: expansión monetaria ~7% anual. No es un dato medido de M2 global ni de inflación.

const PERFORMANCE_ANCHORS: { ticker: string; name: string; sector: string; marketCap: number; ipoYear: number; priceStart: number; price5YAgo: number; priceCurrent: number }[] = [
  // Universe of winners — assets whose CAGR exceeds the ~7% annual assumption
  // price5YAgo = Feb 2021 prices, priceCurrent = Feb 2026 prices
  { ticker: "BTC", name: "Bitcoin", sector: "Crypto", marketCap: 1340, ipoYear: 2009, priceStart: 0.001, price5YAgo: 33593, priceCurrent: 67650 },
  { ticker: "GOLD", name: "Oro (onza)", sector: "Commodities", marketCap: 18200, ipoYear: 1971, priceStart: 35, price5YAgo: 1854, priceCurrent: 5162 },
  { ticker: "AAPL", name: "Apple", sector: "Tech", marketCap: 3900, ipoYear: 1980, priceStart: 0.10, price5YAgo: 130, priceCurrent: 274 },
  { ticker: "MSFT", name: "Microsoft", sector: "Tech", marketCap: 2970, ipoYear: 1986, priceStart: 0.10, price5YAgo: 229, priceCurrent: 399 },
  { ticker: "GOOGL", name: "Alphabet", sector: "Tech", marketCap: 3700, ipoYear: 2004, priceStart: 2.50, price5YAgo: 94, priceCurrent: 306 },
  { ticker: "NVDA", name: "NVIDIA", sector: "Tech", marketCap: 4600, ipoYear: 1999, priceStart: 1.50, price5YAgo: 13.2, priceCurrent: 185 },
  { ticker: "META", name: "Meta", sector: "Tech", marketCap: 1630, ipoYear: 2012, priceStart: 38, price5YAgo: 260, priceCurrent: 653 },
  { ticker: "V", name: "Visa", sector: "Finance", marketCap: 620, ipoYear: 2008, priceStart: 11, price5YAgo: 191, priceCurrent: 313 },
  { ticker: "MA", name: "Mastercard", sector: "Finance", marketCap: 480, ipoYear: 2006, priceStart: 3.90, price5YAgo: 313, priceCurrent: 496 },
  { ticker: "COST", name: "Costco", sector: "Consumer", marketCap: 450, ipoYear: 1985, priceStart: 2.50, price5YAgo: 331, priceCurrent: 987 },
  { ticker: "BRK.B", name: "Berkshire Hathaway", sector: "Finance", marketCap: 1120, ipoYear: 1996, priceStart: 23, price5YAgo: 229, priceCurrent: 494 },
  // Context assets that DON'T beat M2 — shown for comparison
  { ticker: "SPX", name: "S&P 500", sector: "Index", marketCap: 124000, ipoYear: 1957, priceStart: 44, price5YAgo: 3773, priceCurrent: 6901 },
  { ticker: "SILVER", name: "Plata (onza)", sector: "Commodities", marketCap: 1800, ipoYear: 1971, priceStart: 1.39, price5YAgo: 28.5, priceCurrent: 87 },
];

export function computeCAGR(priceStart: number, priceEnd: number, years: number): number {
  if (priceStart <= 0 || priceEnd <= 0 || years <= 0) return 0;
  return (Math.pow(priceEnd / priceStart, 1 / years) - 1) * 100;
}

export function getAnchorPrice(asset: 'gold' | 'silver' | 'sp500' | 'nasdaq' | 'btc', year: number): number {
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
    const priceCurrent = a.priceCurrent;

    const years = currentYear - a.ipoYear;
    const cagrHistorical = computeCAGR(a.priceStart, priceCurrent, years);
    const cagr5Y = computeCAGR(a.price5YAgo, priceCurrent, 5);
    const vsM2 = cagrHistorical - M2_BENCHMARK;
    return {
      ticker: a.ticker,
      name: a.name,
      sector: a.sector,
      marketCap: a.marketCap,
      ipoYear: a.ipoYear,
      priceStart: a.priceStart,
      price5YAgo: a.price5YAgo,
      priceCurrent,
      years,
      cagrHistorical,
      cagr5Y,
      vsM2,
      beatsM2: cagrHistorical > M2_BENCHMARK,
    };
  }).sort((a, b) => b.cagrHistorical - a.cagrHistorical);
}

export const assetPerformance = buildPerformanceData();

const MONTH_NAMES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

/** "2026-01" → "Ene 2026". Devuelve la entrada tal cual si no tiene formato YYYY-MM. */
export function formatDateLabel(dateStr: string): string {
  if (!dateStr || dateStr.length < 7) return dateStr;
  const [year, month] = dateStr.split("-");
  const m = parseInt(month, 10);
  if (!MONTH_NAMES[m - 1]) return dateStr;
  return `${MONTH_NAMES[m - 1]} ${year}`;
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

export { SMA_LONG, SMA_SHORT };
