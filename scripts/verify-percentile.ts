// ============================================================
// Verificación del percentil empírico (sin supuesto de normalidad).
// Ejecutar: npm run verify
// Requiere Node ≥ 22.18 (type stripping nativo). Sale con código 1 si falla.
// ============================================================
import { computeEmpiricalPercentile } from "../src/lib/data.ts";

let failures = 0;

function check(name: string, got: number, want: number, tol = 1e-12): void {
  const ok = Math.abs(got - want) <= tol;
  if (!ok) failures++;
  console.log(`${ok ? "OK  " : "FAIL"} ${name}: got ${got}, want ${want}`);
}

// Percentil bajo supuesto de normalidad (CDF normal, Abramowitz & Stegun),
// solo para mostrar la diferencia con el empírico. No se usa en la UI.
function normalPercentile(z: number): number {
  const absZ = Math.min(Math.abs(z), 6);
  const t = 1 / (1 + 0.2316419 * absZ);
  const d = 0.3989423 * Math.exp(-0.5 * absZ * absZ);
  const tail = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return z >= 0 ? 1 - tail : tail;
}

console.log("── Casos conocidos ──");
const oneToHundred = Array.from({ length: 100 }, (_, i) => i + 1);

let r = computeEmpiricalPercentile(oneToHundred, 50.5);
check("1..100, actual 50.5 → below", r.below, 0.5);
check("1..100, actual 50.5 → above", r.above, 0.5);
check("1..100, n", r.n, 100);

r = computeEmpiricalPercentile(oneToHundred, 100);
check("1..100, actual = máximo → below", r.below, 0.99);
check("1..100, actual = máximo → above", r.above, 0);

r = computeEmpiricalPercentile(oneToHundred, 1);
check("1..100, actual = mínimo → below", r.below, 0);
check("1..100, actual = mínimo → above", r.above, 0.99);

r = computeEmpiricalPercentile(oneToHundred, 1000);
check("1..100, actual fuera de rango (alto) → below", r.below, 1);

r = computeEmpiricalPercentile([1, 2, 2, 3], 2);
check("empates [1,2,2,3], actual 2 → below", r.below, 0.25);
check("empates [1,2,2,3], actual 2 → above", r.above, 0.25);

r = computeEmpiricalPercentile([], 5);
check("ventana vacía → n", r.n, 0);
check("ventana vacía → below", r.below, 0);

// Serie exponencial (asimétrica en escala lineal): el percentil normal
// subestima cuánto del tiempo el valor actual supera a la historia.
console.log("\n── Serie asimétrica: normal vs empírico ──");
const expo = Array.from({ length: 200 }, (_, k) => Math.exp(k / 40));
const last = expo[expo.length - 1];
const meanLin = expo.reduce((s, v) => s + v, 0) / expo.length;
const sdLin = Math.sqrt(expo.reduce((s, v) => s + (v - meanLin) ** 2, 0) / expo.length);
const zLin = (last - meanLin) / sdLin;
r = computeEmpiricalPercentile(expo, last);
check("exp(k/40), k=0..199, actual = último → below", r.below, 199 / 200);
console.log(
  `     z lineal = ${zLin.toFixed(2)} → percentil normal ${(normalPercentile(zLin) * 100).toFixed(1)}% ` +
  `vs empírico ${(r.below * 100).toFixed(1)}%`,
);

console.log(failures === 0 ? "\nTodo OK" : `\n${failures} verificación(es) fallida(s)`);
process.exit(failures === 0 ? 0 : 1);
