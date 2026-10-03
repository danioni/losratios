// ============================================================
// Verificación de la serie mensual de respaldo (generateMonthlyData).
// Ejecutar: npm run verify
// - meses consecutivos sin huecos desde 1971-01 hasta el último ancla
// - cada ancla se reproduce exactamente en su mes (sin ruido sintético)
// - los meses intermedios son interpolación pura (punto medio verificable)
// ============================================================
import { assetData, ANCHORS } from "../src/lib/data.ts";

let failures = 0;
function check(name: string, ok: boolean, detail = ""): void {
  if (!ok) failures++;
  console.log(`${ok ? "OK  " : "FAIL"} ${name}${detail ? `: ${detail}` : ""}`);
}
function nextMonth(date: string): string {
  const [y, m] = date.split("-").map(Number);
  return m === 12 ? `${y + 1}-01` : `${y}-${String(m + 1).padStart(2, "0")}`;
}

const dates = assetData.map((d) => d.date);
const firstAnchor = ANCHORS[0].date;
const lastAnchor = ANCHORS[ANCHORS.length - 1].date;
const expectedMonths = (parseInt(lastAnchor, 10) - parseInt(firstAnchor, 10)) * 12 + 1;

console.log("── Continuidad mensual ──");
check("primer mes", dates[0] === `${firstAnchor}-01`, `${dates[0]} (esperado ${firstAnchor}-01)`);
check("último mes", dates[dates.length - 1] === `${lastAnchor}-01`, `${dates[dates.length - 1]} (esperado ${lastAnchor}-01)`);
check("cantidad de meses", dates.length === expectedMonths, `${dates.length} (esperado ${expectedMonths})`);

const gaps: string[] = [];
for (let i = 1; i < dates.length; i++) {
  if (dates[i] !== nextMonth(dates[i - 1])) gaps.push(`${dates[i - 1]} → ${dates[i]}`);
}
check("sin huecos ni duplicados entre meses consecutivos", gaps.length === 0, gaps.length ? gaps.slice(0, 5).join(", ") : "ninguno");

const years = new Set(dates.map((d) => d.slice(0, 4)));
const missingYears: number[] = [];
for (let y = parseInt(firstAnchor, 10); y <= parseInt(lastAnchor, 10); y++) {
  if (!years.has(String(y))) missingYears.push(y);
}
check("todos los años presentes", missingYears.length === 0, missingYears.length ? missingYears.join(", ") : "ninguno falta");

console.log("\n── Anclas reproducidas exactamente (sin ruido) ──");
const byDate = new Map(assetData.map((d) => [d.date, d]));
let anchorMismatch = 0;
for (const a of ANCHORS) {
  const p = byDate.get(`${a.date}-01`);
  const same = !!p && p.gold === a.gold && p.silver === a.silver && p.sp500 === a.sp500 && p.nasdaq === a.nasdaq && p.btc === a.btc;
  if (!same) anchorMismatch++;
}
check(`${ANCHORS.length} anclas coinciden con su mes de enero`, anchorMismatch === 0, anchorMismatch ? `${anchorMismatch} difieren` : "todas");

console.log("\n── Interpolación pura entre anclas bianuales ──");
// 1971 → 1973: 24 meses; 1972-01 es el punto medio exacto (t = 0,5)
const a71 = ANCHORS.find((a) => a.date === "1971")!;
const a73 = ANCHORS.find((a) => a.date === "1973")!;
const mid = byDate.get("1972-01");
check("1972-01 existe", !!mid);
if (mid) {
  const want = (a71.gold + a73.gold) / 2;
  check("1972-01 oro = punto medio lineal 1971/1973", Math.abs(mid.gold - want) < 1e-9, `${mid.gold} vs ${want}`);
}
const noNaN = assetData.every((d) => [d.gold, d.silver, d.sp500, d.nasdaq, d.btc].every((v) => Number.isFinite(v)));
check("sin NaN/Infinity en la serie", noNaN);

console.log(failures === 0 ? "\nTodo OK" : `\n${failures} verificación(es) fallida(s)`);
process.exit(failures === 0 ? 0 : 1);
