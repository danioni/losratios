import { NextResponse } from "next/server";
import { fetchAllMarketData } from "@/lib/market-api";
import { computeAllFromRawAssets } from "@/lib/data";

export const revalidate = 3600; // ISR: re-fetch every hour

export async function GET() {
  try {
    const rawAssets = await fetchAllMarketData();
    const computed = computeAllFromRawAssets(rawAssets);
    return NextResponse.json(computed);
  } catch (error) {
    console.error("Market data fetch failed:", error);
    return NextResponse.json(
      { error: "Failed to fetch market data" },
      { status: 500 },
    );
  }
}
