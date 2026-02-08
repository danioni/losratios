// ============================================================
// Market Data API — Real data from CoinGecko, Yahoo Finance, FRED
// Server-only: used by /api/market-data route
// ============================================================

import type { AssetDataPoint } from "./data";

// ── Yahoo Finance ──────────────────────────────────────────

interface YahooChartResult {
  dates: string[];
  closes: number[];
}

export async function fetchYahooChart(
  symbol: string,
  range = "10y",
  interval = "1mo",
): Promise<YahooChartResult> {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=${range}&interval=${interval}&includePrePost=false`;
  const res = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0" },
    next: { revalidate: 3600 },
  });

  if (!res.ok) throw new Error(`Yahoo Finance ${symbol}: ${res.status}`);
  const json = await res.json();

  const result = json.chart?.result?.[0];
  if (!result) throw new Error(`Yahoo Finance ${symbol}: no data`);

  const timestamps: number[] = result.timestamp ?? [];
  const closes: number[] = result.indicators?.quote?.[0]?.close ?? [];

  const dates: string[] = [];
  const validCloses: number[] = [];

  for (let i = 0; i < timestamps.length; i++) {
    const close = closes[i];
    if (close == null || isNaN(close)) continue;
    const d = new Date(timestamps[i] * 1000);
    dates.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`);
    validCloses.push(close);
  }

  return { dates, closes: validCloses };
}

// ── CoinGecko ──────────────────────────────────────────────

interface CoinGeckoMarketItem {
  id: string;
  current_price: number;
  market_cap: number;
}

interface CoinGeckoGlobal {
  total_market_cap: { usd: number };
  market_cap_percentage: { btc: number; eth: number };
}

export async function fetchCoinGeckoMarkets(): Promise<CoinGeckoMarketItem[]> {
  const url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum,solana&order=market_cap_desc&sparkline=false";
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`CoinGecko markets: ${res.status}`);
  return res.json();
}

export async function fetchCoinGeckoGlobal(): Promise<CoinGeckoGlobal> {
  const url = "https://api.coingecko.com/api/v3/global";
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`CoinGecko global: ${res.status}`);
  const json = await res.json();
  return json.data;
}

interface CoinGeckoHistoryPoint {
  prices: [number, number][]; // [timestamp_ms, price]
  market_caps: [number, number][];
}

export async function fetchCoinGeckoHistory(
  coinId: string,
  days = 3650,
): Promise<{ dates: string[]; prices: number[]; mcaps: number[] }> {
  const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}&interval=daily`;
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`CoinGecko history ${coinId}: ${res.status}`);
  const json: CoinGeckoHistoryPoint = await res.json();

  // Downsample to monthly (take first entry per month)
  const monthlyPrices: Map<string, { price: number; mcap: number }> = new Map();
  for (let i = 0; i < json.prices.length; i++) {
    const d = new Date(json.prices[i][0]);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    if (!monthlyPrices.has(key)) {
      monthlyPrices.set(key, {
        price: json.prices[i][1],
        mcap: json.market_caps[i]?.[1] ?? 0,
      });
    }
  }

  const dates: string[] = [];
  const prices: number[] = [];
  const mcaps: number[] = [];
  for (const [date, data] of monthlyPrices) {
    dates.push(date);
    prices.push(data.price);
    mcaps.push(data.mcap / 1e12); // convert to trillions
  }

  return { dates, prices, mcaps };
}

// ── FRED ───────────────────────────────────────────────────

interface FredObservation {
  date: string;
  value: string;
}

export async function fetchFredSeries(
  seriesId: string,
): Promise<{ dates: string[]; values: number[] }> {
  const apiKey = process.env.FRED_API_KEY;
  if (!apiKey) {
    console.warn(`FRED_API_KEY not set, skipping ${seriesId}`);
    return { dates: [], values: [] };
  }

  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${apiKey}&file_type=json&frequency=m&sort_order=asc`;
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`FRED ${seriesId}: ${res.status}`);
  const json = await res.json();

  const observations: FredObservation[] = json.observations ?? [];
  const dates: string[] = [];
  const values: number[] = [];

  for (const obs of observations) {
    const val = parseFloat(obs.value);
    if (isNaN(val)) continue;
    // FRED dates are "YYYY-MM-DD", we want "YYYY-MM"
    dates.push(obs.date.slice(0, 7));
    values.push(val);
  }

  return { dates, values };
}

// ── Merge all sources into AssetDataPoint[] ────────────────

// Known supply constants for market cap derivation
const GOLD_SUPPLY_OZ = 212_582 * 32_150.7; // ~212,582 tonnes × 32,150.7 oz/tonne
const SILVER_SUPPLY_OZ = 1_740_000_000; // ~1.74B oz above-ground

// Align multiple time series to a common monthly date range
function alignToMonthlyGrid(
  series: { dates: string[]; values: number[] }[],
): { dates: string[]; aligned: number[][] } {
  // Find the common date range
  const allDates = new Set<string>();
  for (const s of series) {
    for (const d of s.dates) allDates.add(d);
  }
  const dates = [...allDates].sort();

  // For each series, create a lookup and forward-fill missing values
  const aligned: number[][] = series.map((s) => {
    const lookup = new Map<string, number>();
    for (let i = 0; i < s.dates.length; i++) {
      lookup.set(s.dates[i], s.values[i]);
    }

    const result: number[] = [];
    let lastVal = 0;
    for (const d of dates) {
      const v = lookup.get(d);
      if (v !== undefined) {
        lastVal = v;
      }
      result.push(lastVal);
    }
    return result;
  });

  return { dates, aligned };
}

export async function fetchAllMarketData(): Promise<AssetDataPoint[]> {
  // Fetch everything in parallel
  const [
    // Equities
    sp500Data,
    nasdaqData,
    msciData,
    teslaData,
    // Commodities
    goldData,
    silverData,
    oilData,
    copperData,
    // Bonds
    tltData,
    // Crypto historical
    btcHist,
    ethHist,
    solHist,
    // Crypto current
    cryptoMarkets,
    cryptoGlobal,
    // Macro
    m2Data,
    caseShillerData,
  ] = await Promise.all([
    fetchYahooChart("^GSPC").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("^IXIC").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("URTH").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("TSLA").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("GC=F").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("SI=F").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("CL=F").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("HG=F").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("TLT").catch(() => ({ dates: [], closes: [] })),
    fetchCoinGeckoHistory("bitcoin").catch(() => ({ dates: [], prices: [], mcaps: [] })),
    fetchCoinGeckoHistory("ethereum").catch(() => ({ dates: [], prices: [], mcaps: [] })),
    fetchCoinGeckoHistory("solana", 1825).catch(() => ({ dates: [], prices: [], mcaps: [] })),
    fetchCoinGeckoMarkets().catch(() => [] as CoinGeckoMarketItem[]),
    fetchCoinGeckoGlobal().catch(() => ({ total_market_cap: { usd: 0 }, market_cap_percentage: { btc: 0, eth: 0 } })),
    fetchFredSeries("M2SL").catch(() => ({ dates: [], values: [] })),
    fetchFredSeries("CSUSHPINSA").catch(() => ({ dates: [], values: [] })),
  ]);

  // Prepare all series for alignment
  const allSeries = [
    { dates: sp500Data.dates, values: sp500Data.closes },       // 0: sp500
    { dates: nasdaqData.dates, values: nasdaqData.closes },     // 1: nasdaq
    { dates: msciData.dates, values: msciData.closes },         // 2: msci
    { dates: teslaData.dates, values: teslaData.closes },       // 3: tesla
    { dates: goldData.dates, values: goldData.closes },         // 4: gold
    { dates: silverData.dates, values: silverData.closes },     // 5: silver
    { dates: oilData.dates, values: oilData.closes },           // 6: oil
    { dates: copperData.dates, values: copperData.closes },     // 7: copper
    { dates: tltData.dates, values: tltData.closes },           // 8: tlt (bonds proxy)
    { dates: btcHist.dates, values: btcHist.prices },           // 9: btc price
    { dates: btcHist.dates, values: btcHist.mcaps },            // 10: btc mcap
    { dates: ethHist.dates, values: ethHist.prices },           // 11: eth price
    { dates: ethHist.dates, values: ethHist.mcaps },            // 12: eth mcap
    { dates: solHist.dates, values: solHist.prices },           // 13: sol price
    { dates: solHist.dates, values: solHist.mcaps },            // 14: sol mcap
    { dates: m2Data.dates, values: m2Data.values },             // 15: m2
    { dates: caseShillerData.dates, values: caseShillerData.values }, // 16: case-shiller
  ];

  // Check if we got enough data (at least sp500 or btc)
  const hasData = sp500Data.dates.length > 12 || btcHist.dates.length > 12;
  if (!hasData) {
    throw new Error("Insufficient market data from APIs");
  }

  const { dates, aligned } = alignToMonthlyGrid(allSeries);

  // Current crypto data from CoinGecko markets endpoint
  const btcCurrent = cryptoMarkets.find((c) => c.id === "bitcoin");
  const ethCurrent = cryptoMarkets.find((c) => c.id === "ethereum");
  const solCurrent = cryptoMarkets.find((c) => c.id === "solana");
  const totalCryptoMcap = cryptoGlobal.total_market_cap?.usd ?? 0;

  // Build AssetDataPoint array
  const result: AssetDataPoint[] = dates.map((date, i) => {
    const goldPrice = aligned[4][i] || 0;
    const silverPrice = aligned[5][i] || 0;
    const m2Val = aligned[15][i] || 0;
    // M2SL is in billions, convert to trillions. Multiply by ~3 as rough global proxy (US M2 ≈ 1/3 of global)
    const m2GlobalProxy = (m2Val / 1000) * 3;

    // Derive market caps from known supply
    const goldMcap = (goldPrice * GOLD_SUPPLY_OZ) / 1e12; // trillions
    const silverMcap = (silverPrice * SILVER_SUPPLY_OZ) / 1e12;

    // Bond market cap proxy from TLT price (normalized)
    const tltPrice = aligned[8][i] || 100;
    const bondsMcapProxy = (tltPrice / 100) * 130; // rough scale to ~130T

    // Equities market cap rough estimate from S&P level
    const sp500Level = aligned[0][i] || 0;
    const equitiesMcapProxy = sp500Level > 0 ? (sp500Level / 6000) * 120 : 0; // rough scale

    return {
      date,
      gold: goldPrice,
      silver: silverPrice,
      oil: aligned[6][i] || 0,
      copper: aligned[7][i] || 0,
      sp500: aligned[0][i] || 0,
      nasdaq: aligned[1][i] || 0,
      msciWorld: aligned[2][i] || 0,
      tesla: aligned[3][i] || 0,
      caseShiller: aligned[16][i] || 0,
      btc: aligned[9][i] || 0,
      eth: aligned[11][i] || 0,
      sol: aligned[13][i] || 0,
      btcMcap: aligned[10][i] || 0,
      ethMcap: aligned[12][i] || 0,
      solMcap: aligned[14][i] || 0,
      goldMcap,
      silverMcap,
      equitiesMcap: equitiesMcapProxy,
      realEstateMcap: 360, // ~360T global, slow-moving
      bondsMcap: bondsMcapProxy,
      cryptoMcap: aligned[10][i] + aligned[12][i] + aligned[14][i] || 0,
      m2Global: m2GlobalProxy || 0,
    };
  });

  // Override the last data point with live crypto prices if available
  if (result.length > 0 && btcCurrent) {
    const last = result[result.length - 1];
    last.btc = btcCurrent.current_price;
    last.btcMcap = btcCurrent.market_cap / 1e12;
    if (ethCurrent) {
      last.eth = ethCurrent.current_price;
      last.ethMcap = ethCurrent.market_cap / 1e12;
    }
    if (solCurrent) {
      last.sol = solCurrent.current_price;
      last.solMcap = solCurrent.market_cap / 1e12;
    }
    last.cryptoMcap = totalCryptoMcap / 1e12;
  }

  return result;
}
