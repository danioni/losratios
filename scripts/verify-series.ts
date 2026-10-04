// ============================================================
// Verificación del lector de las series de senales/ (src/lib/series.ts).
// Ejecutar: npm run verify
// Requiere Node ≥ 22.18 (type stripping nativo). Sale con código 1 si falla.
// - los CSV publicados cargan y dicen lo mismo entre sí
// - un archivo que falta o está mal formado hace que cargarSeries() lance,
//   que es lo que detiene el build
// ============================================================
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { cargarSeries, DIR_SERIES } from "../src/lib/series.ts";

let failures = 0;
function check(name: string, ok: boolean, detail = ""): void {
  if (!ok) failures++;
  console.log(`${ok ? "OK  " : "FAIL"} ${name}${detail ? `: ${detail}` : ""}`);
}

console.log("── Series publicadas ──");
const { pares, series, descargas, ultimoMes } = cargarSeries();
check("los CSV cargan", true, `${pares.length} pares, ${series.length} series, ${descargas.length} descargas, último mes ${ultimoMes}`);
for (const par of pares) {
  if (!par.publicado) {
    console.log(`     ${par.nombre.padEnd(18)} ${par.estado}`);
    continue;
  }
  const noAptos = par.puntos.filter((punto) => !punto.apto);
  console.log(
    `     ${par.nombre.padEnd(18)} ${par.estado}, ${par.primerMes} a ${par.ultimoMes}, ${par.meses} meses, ` +
    `${par.mesesAptos} aptos, ${par.mesesEnDisputa} en disputa`,
  );
  check(`${par.nombre}: todo mes no apto dice por qué`, noAptos.every((punto) => punto.motivos.length > 0));
  check(`${par.nombre}: ningún mes apto trae motivos`, par.puntos.every((punto) => !punto.apto || punto.motivos.length === 0));
  check(`${par.nombre}: todo mes en disputa trae los dos valores`,
    par.puntos.filter((punto) => punto.enDisputa).every((punto) => punto.motivos.some((motivo) => motivo.includes("FMI"))));
  const motivos = new Map<string, number>();
  for (const punto of noAptos) {
    for (const motivo of punto.motivos) {
      const clave = motivo.split(/ — | \(error/)[0];
      motivos.set(clave, (motivos.get(clave) ?? 0) + 1);
    }
  }
  for (const [motivo, meses] of motivos) console.log(`       ${String(meses).padStart(3)} meses: ${motivo}`);
  if (par.aptosSinSegundaFuente.meses > 0) {
    console.log(`       ${String(par.aptosSinSegundaFuente.meses).padStart(3)} meses aptos sin segunda fuente: ${par.aptosSinSegundaFuente.tramos.join(", ")}`);
  }
}

// Cada caso rompe una copia de los CSV y espera que cargarSeries() lance.
console.log("\n── Un archivo que falta o está mal formado detiene la carga ──");
function debeFallar(name: string, romper: (dir: string) => void): void {
  const dir = mkdtempSync(path.join(tmpdir(), "losratios-series-"));
  try {
    cpSync(DIR_SERIES, dir, { recursive: true });
    romper(dir);
    let mensaje = "";
    try {
      cargarSeries(dir);
    } catch (error) {
      mensaje = error instanceof Error ? error.message : String(error);
    }
    check(name, mensaje !== "", mensaje || "cargó sin error");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}
function editar(dir: string, archivo: string, cambio: (texto: string) => string): void {
  const ruta = path.join(dir, archivo);
  const antes = readFileSync(ruta, "utf8");
  const despues = cambio(antes);
  if (despues === antes) throw new Error(`el caso no cambió ${archivo}`);
  writeFileSync(ruta, despues);
}

for (const archivo of ["ratios.csv", "pares.csv", "series.csv", "precios_mensuales.csv", "descargas_ratios.csv"]) {
  debeFallar(`falta ${archivo}`, (dir) => rmSync(path.join(dir, archivo)));
}
debeFallar("ratios.csv vacío", (dir) => writeFileSync(path.join(dir, "ratios.csv"), ""));
debeFallar("ratios.csv sin la columna valor", (dir) => editar(dir, "ratios.csv", (t) => t.replace("mes,par,valor,", "mes,par,nivel,")));
debeFallar("ratios.csv con un valor que no es un número", (dir) => editar(dir, "ratios.csv", (t) => t.replace("38.60129145", "n/d")));
debeFallar("ratios.csv con una fila a la que le falta un campo", (dir) => editar(dir, "ratios.csv", (t) => t.replace(",0.0196,,no,estimación", ",0.0196,no,estimación")));
debeFallar("ratios.csv con un mes repetido", (dir) => editar(dir, "ratios.csv", (t) => t.replace("1960-02,oro_plata", "1960-01,oro_plata")));
debeFallar("ratios.csv al que le falta un mes que pares.csv cuenta", (dir) => editar(dir, "ratios.csv", (t) => t.replace(/^1975-06,oro_plata.*\r?\n/m, "")));
debeFallar("ratios.csv con filas de un par que no se publica", (dir) => editar(dir, "ratios.csv", (t) => `${t.trimEnd()}\n2026-08,oro_sp500,0.5,0,,sí,dato\n`));
debeFallar("pares.csv con un par publicado en estado NO MEDIDO", (dir) => editar(dir, "pares.csv", (t) => t.replace("BTC / Oro,sí,dato", "BTC / Oro,sí,NO MEDIDO: sin validación externa")));
debeFallar("pares.csv con comillas sin cerrar", (dir) => editar(dir, "pares.csv", (t) => t.replace("Oro / Plata", '"Oro / Plata')));
debeFallar("series.csv sin la serie de un par", (dir) => editar(dir, "series.csv", (t) => t.replace(/^plata,.*\r?\n/m, "")));
debeFallar("precios_mensuales.csv sin los dos valores de un mes en disputa", (dir) => editar(dir, "precios_mensuales.csv", (t) => t.replace('"valor en disputa: Pink Sheet 313.5, FMI 303.94, diferencia 3.145 %"', "dentro del umbral")));
debeFallar("descargas_ratios.csv con un SHA-256 que no lo es", (dir) => editar(dir, "descargas_ratios.csv", (t) => t.replace("5f40c787", "5f40")));

console.log(failures === 0 ? "\nTodo OK" : `\n${failures} verificación(es) fallida(s)`);
process.exit(failures === 0 ? 0 : 1);
