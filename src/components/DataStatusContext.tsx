"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { assetData as fallbackAssetData, formatDateLabel, type ComputedMarketData } from "@/lib/data";

export type DataOrigin = "api" | "cache" | "fallback";
export type DataSource = "loading" | "live" | "cache" | "error";

export interface DataStatus {
  /** Fecha (YYYY-MM) del último punto de la serie efectivamente mostrada */
  lastDate: string;
  /** api: respuesta fresca · cache: respuesta previa guardada en el navegador · fallback: anclajes estáticos */
  origin: DataOrigin;
  /** Momento de la consulta a la API (ms desde epoch), si la hubo */
  fetchedAt: number | null;
  /** El BTC del último punto salió de anclajes estáticos del servidor (CoinGecko no disponible) */
  btcStatic: boolean;
}

interface DataStatusContextValue {
  /** Respuesta de /api/market-data (fresca o del caché del navegador); null si no hay */
  liveData: ComputedMarketData | null;
  dataSource: DataSource;
  /** Frescura derivada: lo que ven Header, Dashboard y los gráficos */
  status: DataStatus;
}

const CACHE_KEY = "losratios_market_data_v5"; // v5: m2Global → m2Usd, meta de procedencia; sigue usando el respaldo de 55 años y actualiza solo el último punto
const CACHE_TTL_HOURS = 24;

const FALLBACK_LAST_DATE = fallbackAssetData[fallbackAssetData.length - 1]?.date ?? "";

const DataStatusContext = createContext<DataStatusContextValue | null>(null);

export function DataStatusProvider({ children }: { children: ReactNode }) {
  const [liveData, setLiveData] = useState<ComputedMarketData | null>(null);
  const [dataSource, setDataSource] = useState<DataSource>("loading");
  const [dataTimestamp, setDataTimestamp] = useState<number | null>(null);

  // Fetch live market data on mount with localStorage cache (24h TTL)
  useEffect(() => {
    let cancelled = false;

    // Check localStorage cache first
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        const ageHours = (Date.now() - timestamp) / (1000 * 60 * 60);
        if (ageHours < CACHE_TTL_HOURS && data?.assetData?.length > 0) {
          setLiveData(data);
          setDataSource("cache");
          setDataTimestamp(timestamp);
        }
      }
    } catch { /* ignore corrupt cache */ }

    // Always try to fetch fresh data
    fetch("/api/market-data")
      .then((res) => {
        if (!res.ok) throw new Error(`API ${res.status}`);
        const ct = res.headers.get("content-type") ?? "";
        if (!ct.includes("application/json")) throw new Error("Not JSON");
        return res.json();
      })
      .then((data: ComputedMarketData & { error?: string }) => {
        if (!cancelled && data?.assetData?.length > 0 && !data.error) {
          // Sanity check: reject data where critical fields are mostly zero or missing
          const last = data.assetData[data.assetData.length - 1];
          const hasReasonableData = last && last.btc > 1000 && last.gold > 500 && last.sp500 > 1000;
          if (!hasReasonableData) {
            console.warn("Live API data looks incomplete, falling back to static data");
            if (!cancelled) setDataSource("error");
            return;
          }
          const now = Date.now();
          setLiveData(data);
          setDataSource("live");
          setDataTimestamp(now);
          // Save to cache
          try {
            localStorage.setItem(CACHE_KEY, JSON.stringify({ data, timestamp: now }));
          } catch { /* localStorage full */ }
        }
      })
      .catch(() => {
        if (!cancelled) {
          // If we already loaded from cache, keep that
          setDataSource((prev) => prev === "cache" ? "cache" : "error");
        }
      });
    return () => { cancelled = true; };
  }, []);

  const status = useMemo<DataStatus>(() => {
    const liveLast = liveData?.assetData?.[liveData.assetData.length - 1];
    // El último punto mostrado lleva la fecha del dato de la API cuando es posterior
    // a la del respaldo estático; si no hay API, la fecha del respaldo.
    const lastDate = liveLast && liveLast.date > FALLBACK_LAST_DATE ? liveLast.date : FALLBACK_LAST_DATE;
    return {
      lastDate,
      origin: dataSource === "live" ? "api" : dataSource === "cache" ? "cache" : "fallback",
      fetchedAt: dataTimestamp,
      btcStatic: liveData?.meta?.btcSource === "static-fallback",
    };
  }, [liveData, dataSource, dataTimestamp]);

  const value = useMemo<DataStatusContextValue>(
    () => ({ liveData, dataSource, status }),
    [liveData, dataSource, status],
  );

  return (
    <DataStatusContext.Provider value={value}>
      {children}
    </DataStatusContext.Provider>
  );
}

export function useDataStatus(): DataStatusContextValue {
  const ctx = useContext(DataStatusContext);
  if (!ctx) throw new Error("useDataStatus must be used inside DataStatusProvider");
  return ctx;
}

/** Etiqueta corta: "Datos al Oct 2026" o "Datos de respaldo al Ene 2026". */
export function shortDataLabel(s: DataStatus): string {
  const date = formatDateLabel(s.lastDate);
  return s.origin === "fallback" ? `Datos de respaldo al ${date}` : `Datos al ${date}`;
}

function formatTimestamp(ts: number): string {
  const d = new Date(ts);
  const dd = String(d.getDate()).padStart(2, "0");
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const yyyy = d.getFullYear();
  const hh = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
}

/** Etiqueta larga con origen y hora de consulta. */
export function longDataLabel(s: DataStatus): string {
  const parts = [shortDataLabel(s)];
  if (s.origin === "api") parts.push(`API consultada ${s.fetchedAt ? formatTimestamp(s.fetchedAt) : "ahora"}`);
  else if (s.origin === "cache") parts.push(`caché del navegador${s.fetchedAt ? ` (${formatTimestamp(s.fetchedAt)})` : ""}`);
  else parts.push("sin respuesta de la API");
  if (s.btcStatic) parts.push("BTC: respaldo estático del servidor");
  return parts.join(" · ");
}
