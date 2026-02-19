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

interface CoinGeckoHistoryPoint {
  prices: [number, number][];
  market_caps: [number, number][];
}

export async function fetchCoinGeckoMarkets(): Promise<CoinGeckoMarketItem[]> {
  const url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin&order=market_cap_desc&sparkline=false";
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`CoinGecko markets: ${res.status}`);
  return res.json();
}

export async function fetchCoinGeckoHistory(
  coinId: string,
  days = 3650,
): Promise<{ dates: string[]; prices: number[] }> {
  const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}&interval=daily`;
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`CoinGecko history ${coinId}: ${res.status}`);
  const json: CoinGeckoHistoryPoint = await res.json();

  // Downsample to monthly (take first entry per month)
  const monthlyPrices: Map<string, number> = new Map();
  for (let i = 0; i < json.prices.length; i++) {
    const d = new Date(json.prices[i][0]);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    if (!monthlyPrices.has(key)) {
      monthlyPrices.set(key, json.prices[i][1]);
    }
  }

  const dates: string[] = [];
  const prices: number[] = [];
  for (const [date, price] of monthlyPrices) {
    dates.push(date);
    prices.push(price);
  }

  return { dates, prices };
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
    dates.push(obs.date.slice(0, 7));
    values.push(val);
  }

  return { dates, values };
}

// ── BTC Static Fallback (when CoinGecko is rate-limited) ───

const BTC_STATIC_ANCHORS = [
  { date: "2013-12", price: 750 },
  { date: "2014-12", price: 320 },
  { date: "2015-12", price: 430 },
  { date: "2016-12", price: 960 },
  { date: "2017-12", price: 14000 },
  { date: "2018-12", price: 3800 },
  { date: "2019-12", price: 7200 },
  { date: "2020-12", price: 28900 },
  { date: "2021-12", price: 47000 },
  { date: "2022-12", price: 16500 },
  { date: "2023-12", price: 42200 },
  { date: "2024-12", price: 93000 },
];

function buildBtcFallback(): { dates: string[]; prices: number[] } {
  const dates: string[] = [];
  const prices: number[] = [];

  for (let i = 0; i < BTC_STATIC_ANCHORS.length - 1; i++) {
    const a = BTC_STATIC_ANCHORS[i];
    const b = BTC_STATIC_ANCHORS[i + 1];

    // Parse year/month from each anchor
    const [aY, aM] = a.date.split("-").map(Number);
    const [bY, bM] = b.date.split("-").map(Number);
    const totalMonths = (bY - aY) * 12 + (bM - aM);

    // Generate monthly points using geometric interpolation:
    // price = a.price * (b.price / a.price) ^ (t)  where t ∈ [0,1)
    for (let m = 0; m < totalMonths; m++) {
      const t = m / totalMonths;
      const year = aY + Math.floor((aM + m - 1) / 12);
      const month = ((aM + m - 1) % 12) + 1;
      dates.push(`${year}-${String(month).padStart(2, "0")}`);
      prices.push(a.price * Math.pow(b.price / a.price, t));
    }
  }

  // Append last anchor
  const last = BTC_STATIC_ANCHORS[BTC_STATIC_ANCHORS.length - 1];
  dates.push(last.date);
  prices.push(last.price);

  return { dates, prices };
}

// ── Merge all sources into AssetDataPoint[] ────────────────

function alignToMonthlyGrid(
  series: { dates: string[]; values: number[] }[],
): { dates: string[]; aligned: number[][] } {
  const allDates = new Set<string>();
  for (const s of series) {
    for (const d of s.dates) allDates.add(d);
  }
  const dates = [...allDates].sort();

  const aligned: number[][] = series.map((s) => {
    const lookup = new Map<string, number>();
    for (let i = 0; i < s.dates.length; i++) {
      lookup.set(s.dates[i], s.values[i]);
    }

    const result: number[] = [];
    let lastVal = NaN;
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
  // Fetch everything in parallel — only what we need for the 5 ratios
  const [
    sp500Data,
    nasdaqData,
    goldData,
    silverData,
    btcHist,
    btcMarkets,
    m2Data,
  ] = await Promise.all([
    fetchYahooChart("^GSPC").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("^IXIC").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("GC=F").catch(() => ({ dates: [], closes: [] })),
    fetchYahooChart("SI=F").catch(() => ({ dates: [], closes: [] })),
    fetchCoinGeckoHistory("bitcoin").catch(() => ({ dates: [], prices: [] })),
    fetchCoinGeckoMarkets().catch(() => [] as CoinGeckoMarketItem[]),
    fetchFredSeries("M2SL").catch(() => ({ dates: [], values: [] })),
  ]);

  // Check we have enough data
  const hasEquity = sp500Data.dates.length > 12;
  const hasCrypto = btcHist.dates.length > 12;
  if (!hasEquity && !hasCrypto) {
    throw new Error("Insufficient market data from APIs");
  }

  // Bug #2: Use static BTC fallback when CoinGecko is rate-limited
  const btcData = btcHist.dates.length >= 24
    ? btcHist
    : buildBtcFallback();

  console.log(
    `BTC source: ${btcHist.dates.length >= 24 ? "CoinGecko live" : "static fallback"} — ${btcData.dates.length} months`,
  );

  const allSeries = [
    { dates: sp500Data.dates, values: sp500Data.closes },     // 0: sp500
    { dates: nasdaqData.dates, values: nasdaqData.closes },   // 1: nasdaq
    { dates: goldData.dates, values: goldData.closes },       // 2: gold
    { dates: silverData.dates, values: silverData.closes },   // 3: silver
    { dates: btcData.dates, values: btcData.prices },         // 4: btc
    { dates: m2Data.dates, values: m2Data.values },           // 5: m2
  ];

  const { dates, aligned } = alignToMonthlyGrid(allSeries);

  // Build simplified AssetDataPoint array
  const result: AssetDataPoint[] = dates.map((date, i) => {
    const m2Val = aligned[5][i] || 0;
    // M2SL is in billions, convert to trillions. Multiply by ~3 as rough global proxy
    const m2GlobalProxy = (m2Val / 1000) * 3;

    return {
      date,
      gold: aligned[2][i] || 0,
      silver: aligned[3][i] || 0,
      sp500: aligned[0][i] || 0,
      nasdaq: aligned[1][i] || 0,
      btc: aligned[4][i] || 0,
      m2Global: m2GlobalProxy || 0,
    };
  });

  // Filter out data points where ANY critical field is zero/missing
  const filtered = result.filter(
    (d) => d.btc > 0 && d.gold > 0 && d.sp500 > 0,
  );
  if (filtered.length === 0) {
    throw new Error("All market data fields are zero — API data unusable");
  }

  // Override the last data point with live BTC price if available
  const btcCurrent = btcMarkets.find((c) => c.id === "bitcoin");
  if (filtered.length > 0 && btcCurrent) {
    filtered[filtered.length - 1].btc = btcCurrent.current_price;
  }

  return filtered;
}
