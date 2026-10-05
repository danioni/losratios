// ============================================================
// Los Ratios — métricas que todavía no se publican
// Los ratios que muestra el sitio no salen de aquí: se leen de senales/ en el
// build (src/lib/series.ts). Este archivo conserva las funciones de cálculo de
// lo que está oculto. No contiene datos: lo que se publique leerá de senales/.
// ============================================================

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
// TABLAS DE CAGR Y PODER ADQUISITIVO
// No se publican: no hay series observadas para ellas, y el sitio muestra este
// texto en su lugar. Cuando se publiquen leerán de senales/, como los ratios.
// ============================================================
export const NO_MEDIDO_TABLAS = "NO MEDIDO: se publicarán cuando haya series observadas para ellas.";

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
  return `${a}/${b} en zona extrema de su historia (${z})`;
}

// ============================================================
// CAGR
// ============================================================
export function computeCAGR(priceStart: number, priceEnd: number, years: number): number {
  if (priceStart <= 0 || priceEnd <= 0 || years <= 0) return 0;
  return (Math.pow(priceEnd / priceStart, 1 / years) - 1) * 100;
}

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
