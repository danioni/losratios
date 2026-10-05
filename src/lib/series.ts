// ============================================================
// Los Ratios — Series publicadas por senales/
// El sitio lee los CSV de senales/data/series/ cuando se construye: las páginas
// son estáticas y no se ejecuta Python. Si un archivo falta o está mal formado,
// cargarSeries() lanza y el build falla. No hay respaldo.
// Solo servidor (usa node:fs): los componentes cliente importan solo los tipos.
// ============================================================
import { readFileSync } from "node:fs";
import path from "node:path";

export const DIR_SERIES = path.join(process.cwd(), "senales", "data", "series");

const ARCHIVO_RATIOS = "ratios.csv";
const ARCHIVO_PARES = "pares.csv";
const ARCHIVO_SERIES = "series.csv";
const ARCHIVO_PRECIOS = "precios_mensuales.csv";
const ARCHIVO_DESCARGAS = "descargas_ratios.csv";

// A-R0-17: una métrica solo usa los meses con error por redondeo de hasta este
// umbral. Es el UMBRAL_ERROR_REDONDEO_PCT de senales/senales/configuracion.py.
// Aquí no decide nada: qué meses son aptos lo dice la columna apto_metricas. Solo
// sirve para nombrar el motivo de un mes que ratios.csv ya marca como no apto.
const UMBRAL_ERROR_REDONDEO_PCT = 0.5;
// A-R0-17: hasta marzo de 1968 el oro de Londres no era un precio libre. Abril
// de 1968 es el primer mes completo sin el London Gold Pool.
const SERIE_ORO = "oro";
const PRIMER_MES_ORO_LIBRE = "1968-04";
// A-R0-20: lo que precios_mensuales.csv dice del control mensual de cada metal.
const SUFIJO_CONTRASTE = "_contraste_fmi";
const CONTRASTE_DENTRO = "dentro del umbral";
const CONTRASTE_SIN_COMPARAR = "sin comparar";
const CONTRASTE_DISPUTA = "valor en disputa: ";

const MOTIVO_REDONDEO = "precisión insuficiente por redondeo";
const MOTIVO_DISPUTA = "valor en disputa";
const MOTIVO_ANTES_ORO_LIBRE = "antes del mercado libre del oro (marzo de 1968)";
const DETALLE_ANTES_ORO_LIBRE =
  "Hasta marzo de 1968 el precio del oro en Londres estaba condicionado por el sistema de Bretton Woods y, desde 1961, por el London Gold Pool (A-R0-17).";
const NOTA_SIN_SEGUNDA_FUENTE = "sin segunda fuente";

// ── Tipos ──────────────────────────────────────────────────

/** Una fila de series.csv. Los textos van tal cual: son los que exigen las licencias. */
export interface Serie {
  serie: string;
  nombre: string;
  publicada: boolean;
  estado: string;
  unidad: string;
  fuente: string;
  licencia: string;
  atribucion: string;
  validacion: string;
  supuestos: string[];
  primerMes: string;
  ultimoMes: string;
  meses: number;
}

/** Por qué un mes queda fuera de las métricas: la etiqueta y lo que la explica. */
export interface Motivo {
  etiqueta: string;
  detalle: string;
}

/** Un mes de un par publicado (una fila de ratios.csv). */
export interface PuntoRatio {
  mes: string;
  valor: number;
  errorRedondeoPct: number;
  /** apto_metricas de ratios.csv */
  apto: boolean;
  enDisputa: boolean;
  /** Por qué el mes queda fuera de las métricas. Vacío si es apto. */
  motivos: Motivo[];
  /** Reservas que no lo sacan de las métricas. */
  notas: string[];
}

export interface ErrorMaximo {
  pct: number;
  mes: string;
}

export interface ParPublicado {
  publicado: true;
  par: string;
  nombre: string;
  estado: string;
  primerMes: string;
  ultimoMes: string;
  meses: number;
  aptoDesde: string;
  mesesAptos: number;
  mesesEnDisputa: number;
  /** Mayor error_redondeo_pct de todos los meses publicados; null si no hay redondeo. */
  errorMaximo: ErrorMaximo | null;
  /** Lo mismo, solo sobre los meses aptos para métricas. */
  errorMaximoAptos: ErrorMaximo | null;
  /** Meses aptos sin control mensual contra una segunda fuente, por tramos. */
  aptosSinSegundaFuente: { meses: number; tramos: string[] };
  /** Numerador y denominador, en ese orden. */
  fuentes: Serie[];
  puntos: PuntoRatio[];
}

/** Un par que pares.csv no publica: nombre y estado, nada más. */
export interface ParNoPublicado {
  publicado: false;
  par: string;
  nombre: string;
  estado: string;
}

export type Par = ParPublicado | ParNoPublicado;

/** Una fila de descargas_ratios.csv. */
export interface Descarga {
  fechaDescarga: string;
  fuente: string;
  licencia: string;
  url: string;
  bytes: number;
  sha256: string;
  actualizada: string;
  crudoEnRepo: boolean;
}

export interface SeriesSitio {
  pares: Par[];
  series: Serie[];
  descargas: Descarga[];
  /** Último mes con dato entre los pares publicados; null si no se publica ninguno. */
  ultimoMes: string | null;
}

// ── Lectura de CSV ─────────────────────────────────────────

type Fila = Record<string, string> & { __linea: string };

function fallo(archivo: string, mensaje: string): never {
  throw new Error(`senales/data/series/${archivo}: ${mensaje}`);
}

/** RFC 4180: campos entre comillas, comillas dobladas, saltos LF o CRLF. */
function parsearCsv(texto: string, archivo: string): { campos: string[]; linea: number }[] {
  const registros: { campos: string[]; linea: number }[] = [];
  let campos: string[] = [];
  let campo = "";
  let entreComillas = false;
  let cerroComillas = false;
  let linea = 1;
  let lineaRegistro = 1;
  const cerrarCampo = () => {
    campos.push(campo);
    campo = "";
    cerroComillas = false;
  };
  for (let i = texto.charCodeAt(0) === 0xfeff ? 1 : 0; i < texto.length; i++) {
    const c = texto[i];
    if (entreComillas) {
      if (c === '"') {
        if (texto[i + 1] === '"') {
          campo += '"';
          i++;
        } else {
          entreComillas = false;
          cerroComillas = true;
        }
      } else {
        if (c === "\n") linea++;
        campo += c;
      }
    } else if (c === ",") {
      cerrarCampo();
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && texto[i + 1] === "\n") i++;
      cerrarCampo();
      registros.push({ campos, linea: lineaRegistro });
      campos = [];
      linea++;
      lineaRegistro = linea;
    } else if (cerroComillas) {
      fallo(archivo, `línea ${linea}: hay texto después de una comilla de cierre`);
    } else if (c === '"') {
      if (campo !== "") fallo(archivo, `línea ${linea}: comilla en medio de un campo`);
      entreComillas = true;
    } else {
      campo += c;
    }
  }
  if (entreComillas) fallo(archivo, `línea ${lineaRegistro}: comillas sin cerrar`);
  if (campo !== "" || campos.length > 0 || cerroComillas) {
    cerrarCampo();
    registros.push({ campos, linea: lineaRegistro });
  }
  return registros;
}

function leerCsv(dir: string, archivo: string, columnas: readonly string[]): Fila[] {
  const ruta = path.join(dir, archivo);
  let contenido: string;
  try {
    contenido = readFileSync(ruta, "utf8");
  } catch (error) {
    fallo(archivo, `no se pudo leer (${error instanceof Error ? error.message : String(error)})`);
  }
  const registros = parsearCsv(contenido, archivo);
  if (registros.length === 0) fallo(archivo, "está vacío");
  const encabezado = registros[0].campos;
  if (new Set(encabezado).size !== encabezado.length) fallo(archivo, "tiene columnas repetidas");
  const faltan = columnas.filter((columna) => !encabezado.includes(columna));
  if (faltan.length > 0) fallo(archivo, `faltan las columnas ${faltan.join(", ")}`);
  if (registros.length === 1) fallo(archivo, "no tiene filas");
  return registros.slice(1).map(({ campos, linea }) => {
    if (campos.length !== encabezado.length) {
      fallo(archivo, `línea ${linea}: tiene ${campos.length} campos y el encabezado, ${encabezado.length}`);
    }
    const fila = { __linea: String(linea) } as Fila;
    encabezado.forEach((columna, i) => {
      fila[columna] = campos[i];
    });
    return fila;
  });
}

// ── Validación de campos ───────────────────────────────────

const PATRON_MES = /^\d{4}-(0[1-9]|1[0-2])$/;
const PATRON_NUMERO = /^-?\d+(\.\d+)?([eE][-+]?\d+)?$/;
const PATRON_ENTERO = /^\d+$/;
const PATRON_FECHA = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
const PATRON_SHA256 = /^[0-9a-f]{64}$/;

function lugar(fila: Fila, columna: string): string {
  return `línea ${fila.__linea}, columna ${columna}`;
}

function texto(archivo: string, fila: Fila, columna: string): string {
  const valor = fila[columna];
  if (valor.trim() === "") fallo(archivo, `${lugar(fila, columna)}: está vacía`);
  return valor;
}

function mes(archivo: string, fila: Fila, columna: string): string {
  const valor = fila[columna];
  if (!PATRON_MES.test(valor)) fallo(archivo, `${lugar(fila, columna)}: "${valor}" no es un mes AAAA-MM`);
  return valor;
}

function numero(archivo: string, fila: Fila, columna: string): number {
  const valor = fila[columna];
  if (!PATRON_NUMERO.test(valor) || !Number.isFinite(Number(valor))) {
    fallo(archivo, `${lugar(fila, columna)}: "${valor}" no es un número`);
  }
  return Number(valor);
}

function entero(archivo: string, fila: Fila, columna: string): number {
  const valor = fila[columna];
  if (!PATRON_ENTERO.test(valor)) fallo(archivo, `${lugar(fila, columna)}: "${valor}" no es un entero`);
  return Number(valor);
}

function siNo(archivo: string, fila: Fila, columna: string): boolean {
  const valor = fila[columna];
  if (valor !== "sí" && valor !== "no") fallo(archivo, `${lugar(fila, columna)}: "${valor}" no es "sí" ni "no"`);
  return valor === "sí";
}

// ── Meses ──────────────────────────────────────────────────

function indiceMes(valor: string): number {
  const [anio, numeroMes] = valor.split("-").map(Number);
  return anio * 12 + (numeroMes - 1);
}

/** Tramos de meses consecutivos: ["1968-04 a 1979-12", "2026-09"]. */
function tramos(meses: string[]): string[] {
  const salida: string[] = [];
  let inicio = "";
  let anterior = "";
  for (const actual of meses) {
    if (inicio === "") {
      inicio = actual;
    } else if (indiceMes(actual) !== indiceMes(anterior) + 1) {
      salida.push(inicio === anterior ? inicio : `${inicio} a ${anterior}`);
      inicio = actual;
    }
    anterior = actual;
  }
  if (inicio !== "") salida.push(inicio === anterior ? inicio : `${inicio} a ${anterior}`);
  return salida;
}

// ── Las tablas ─────────────────────────────────────────────

function leerSeries(dir: string): Serie[] {
  const filas = leerCsv(dir, ARCHIVO_SERIES, [
    "serie", "nombre", "publicada", "estado", "unidad", "fuente", "licencia",
    "atribucion", "validacion", "supuestos", "primer_mes", "ultimo_mes", "meses",
  ]);
  const series = filas.map((fila) => ({
    serie: texto(ARCHIVO_SERIES, fila, "serie"),
    nombre: texto(ARCHIVO_SERIES, fila, "nombre"),
    publicada: siNo(ARCHIVO_SERIES, fila, "publicada"),
    estado: texto(ARCHIVO_SERIES, fila, "estado"),
    unidad: texto(ARCHIVO_SERIES, fila, "unidad"),
    fuente: texto(ARCHIVO_SERIES, fila, "fuente"),
    licencia: texto(ARCHIVO_SERIES, fila, "licencia"),
    atribucion: texto(ARCHIVO_SERIES, fila, "atribucion"),
    validacion: fila.validacion,
    supuestos: fila.supuestos.split(" ").filter(Boolean),
    primerMes: mes(ARCHIVO_SERIES, fila, "primer_mes"),
    ultimoMes: mes(ARCHIVO_SERIES, fila, "ultimo_mes"),
    meses: entero(ARCHIVO_SERIES, fila, "meses"),
  }));
  if (new Set(series.map((serie) => serie.serie)).size !== series.length) {
    fallo(ARCHIVO_SERIES, "hay series repetidas");
  }
  return series;
}

/** El control mensual de cada metal, por mes: { "1985-03": { oro: "valor en disputa: …" } }. */
function leerContrastes(dir: string): Map<string, Record<string, string>> {
  const filas = leerCsv(dir, ARCHIVO_PRECIOS, ["mes"]);
  const columnas = Object.keys(filas[0]).filter((columna) => columna.endsWith(SUFIJO_CONTRASTE));
  const contrastes = new Map<string, Record<string, string>>();
  for (const fila of filas) {
    const clave = mes(ARCHIVO_PRECIOS, fila, "mes");
    if (contrastes.has(clave)) fallo(ARCHIVO_PRECIOS, `línea ${fila.__linea}: el mes ${clave} está repetido`);
    const delMes: Record<string, string> = {};
    for (const columna of columnas) {
      const valor = fila[columna];
      const conocido =
        valor === "" || valor === CONTRASTE_DENTRO || valor === CONTRASTE_SIN_COMPARAR || valor.startsWith(CONTRASTE_DISPUTA);
      if (!conocido) fallo(ARCHIVO_PRECIOS, `${lugar(fila, columna)}: "${valor}" no es un resultado conocido del control`);
      delMes[columna.slice(0, -SUFIJO_CONTRASTE.length)] = valor;
    }
    contrastes.set(clave, delMes);
  }
  return contrastes;
}

function leerDescargas(dir: string): Descarga[] {
  const filas = leerCsv(dir, ARCHIVO_DESCARGAS, [
    "fecha_descarga", "fuente", "licencia", "url", "bytes", "sha256", "actualizada", "crudo_en_repo",
  ]);
  return filas.map((fila) => {
    const { fecha_descarga: fecha, url, sha256, actualizada } = fila;
    if (!PATRON_FECHA.test(fecha)) fallo(ARCHIVO_DESCARGAS, `${lugar(fila, "fecha_descarga")}: "${fecha}" no es una fecha AAAA-MM-DD`);
    if (!url.startsWith("https://")) fallo(ARCHIVO_DESCARGAS, `${lugar(fila, "url")}: "${url}" no es una URL https`);
    if (!PATRON_SHA256.test(sha256)) fallo(ARCHIVO_DESCARGAS, `${lugar(fila, "sha256")}: "${sha256}" no es un SHA-256`);
    if (actualizada !== "" && !PATRON_FECHA.test(actualizada)) {
      fallo(ARCHIVO_DESCARGAS, `${lugar(fila, "actualizada")}: "${actualizada}" no es una fecha AAAA-MM-DD`);
    }
    return {
      fechaDescarga: fecha,
      fuente: texto(ARCHIVO_DESCARGAS, fila, "fuente"),
      licencia: texto(ARCHIVO_DESCARGAS, fila, "licencia"),
      url,
      bytes: entero(ARCHIVO_DESCARGAS, fila, "bytes"),
      sha256,
      actualizada,
      crudoEnRepo: siNo(ARCHIVO_DESCARGAS, fila, "crudo_en_repo"),
    };
  });
}

/** Numerador y denominador de un par: las dos series cuyas claves forman la suya. */
function lados(par: string, series: Serie[]): [Serie, Serie] {
  for (const numerador of series) {
    for (const denominador of series) {
      if (`${numerador.serie}_${denominador.serie}` === par) return [numerador, denominador];
    }
  }
  fallo(ARCHIVO_PARES, `el par ${par} no se corresponde con dos series de ${ARCHIVO_SERIES}`);
}

function errorMaximo(puntos: PuntoRatio[]): ErrorMaximo | null {
  let maximo: ErrorMaximo | null = null;
  for (const punto of puntos) {
    if (punto.errorRedondeoPct > (maximo?.pct ?? 0)) maximo = { pct: punto.errorRedondeoPct, mes: punto.mes };
  }
  return maximo;
}

/**
 * Lee y valida las series que publica senales/. Lanza si un archivo falta, si
 * está mal formado o si los archivos se contradicen entre sí.
 */
export function cargarSeries(dir: string = DIR_SERIES): SeriesSitio {
  const series = leerSeries(dir);
  const contrastes = leerContrastes(dir);
  const descargas = leerDescargas(dir);

  const filasPares = leerCsv(dir, ARCHIVO_PARES, [
    "par", "nombre", "publicado", "estado", "primer_mes", "ultimo_mes", "meses",
    "apto_desde", "meses_aptos", "meses_en_disputa",
  ]);
  const filasRatios = leerCsv(dir, ARCHIVO_RATIOS, [
    "mes", "par", "valor", "error_redondeo_pct", "valor_en_disputa", "apto_metricas", "estado",
  ]);

  const clavesPares = filasPares.map((fila) => texto(ARCHIVO_PARES, fila, "par"));
  if (new Set(clavesPares).size !== clavesPares.length) fallo(ARCHIVO_PARES, "hay pares repetidos");

  const ratiosPorPar = new Map<string, Fila[]>();
  for (const fila of filasRatios) {
    const clave = fila.par;
    if (!clavesPares.includes(clave)) {
      fallo(ARCHIVO_RATIOS, `${lugar(fila, "par")}: el par "${clave}" no está en ${ARCHIVO_PARES}`);
    }
    ratiosPorPar.set(clave, [...(ratiosPorPar.get(clave) ?? []), fila]);
  }

  const pares = filasPares.map((filaPar): Par => {
    const par = filaPar.par;
    const nombre = texto(ARCHIVO_PARES, filaPar, "nombre");
    const estado = texto(ARCHIVO_PARES, filaPar, "estado");
    const publicado = siNo(ARCHIVO_PARES, filaPar, "publicado");
    const [numerador, denominador] = lados(par, series);
    const filas = ratiosPorPar.get(par) ?? [];

    if (!publicado) {
      // Lo que no se publica no puede tener valores en el sitio.
      if (filas.length > 0) fallo(ARCHIVO_RATIOS, `trae ${filas.length} filas del par ${par}, que ${ARCHIVO_PARES} no publica`);
      return { publicado: false, par, nombre, estado };
    }

    if (estado.startsWith("NO MEDIDO")) fallo(ARCHIVO_PARES, `el par ${par} figura como publicado y su estado es "${estado}"`);
    for (const lado of [numerador, denominador]) {
      if (!lado.publicada) fallo(ARCHIVO_PARES, `el par ${par} figura como publicado y la serie ${lado.serie} no se publica`);
    }
    if (filas.length === 0) fallo(ARCHIVO_RATIOS, `no trae filas del par ${par}, que ${ARCHIVO_PARES} publica`);

    const primerMes = mes(ARCHIVO_PARES, filaPar, "primer_mes");
    const ultimoMes = mes(ARCHIVO_PARES, filaPar, "ultimo_mes");
    const aptoDesde = filaPar.apto_desde === "" ? "" : mes(ARCHIVO_PARES, filaPar, "apto_desde");
    const tieneOro = [numerador, denominador].some((lado) => lado.serie === SERIE_ORO);

    const puntos = filas
      .map((fila): PuntoRatio => {
        const delMes = mes(ARCHIVO_RATIOS, fila, "mes");
        const valor = numero(ARCHIVO_RATIOS, fila, "valor");
        if (valor <= 0) fallo(ARCHIVO_RATIOS, `${lugar(fila, "valor")}: un ratio tiene que ser mayor que cero`);
        const errorRedondeoPct = numero(ARCHIVO_RATIOS, fila, "error_redondeo_pct");
        if (errorRedondeoPct < 0) fallo(ARCHIVO_RATIOS, `${lugar(fila, "error_redondeo_pct")}: es negativo`);
        const apto = siNo(ARCHIVO_RATIOS, fila, "apto_metricas");
        if (fila.estado !== estado) {
          fallo(ARCHIVO_RATIOS, `${lugar(fila, "estado")}: dice "${fila.estado}" y ${ARCHIVO_PARES} dice "${estado}"`);
        }
        const delControl = contrastes.get(delMes) ?? {};

        // A-R0-20: el mes en disputa se publica con los dos números a la vista.
        const ladosEnDisputa = fila.valor_en_disputa === "" ? [] : fila.valor_en_disputa.split(" y ");
        const motivos = ladosEnDisputa.map((clave): Motivo => {
          const lado = [numerador, denominador].find((serie) => serie.serie === clave);
          if (!lado) fallo(ARCHIVO_RATIOS, `${lugar(fila, "valor_en_disputa")}: "${clave}" no es un lado del par ${par}`);
          const detalle = delControl[clave] ?? "";
          if (!detalle.startsWith(CONTRASTE_DISPUTA)) {
            fallo(ARCHIVO_PRECIOS, `el mes ${delMes} no trae los dos valores de ${clave}, que ${ARCHIVO_RATIOS} marca en disputa`);
          }
          return { etiqueta: MOTIVO_DISPUTA, detalle: `${lado.nombre}: ${detalle.slice(CONTRASTE_DISPUTA.length)}` };
        });
        if (errorRedondeoPct > UMBRAL_ERROR_REDONDEO_PCT) {
          motivos.push({ etiqueta: MOTIVO_REDONDEO, detalle: `error máximo ${errorRedondeoPct} %; el umbral es ${UMBRAL_ERROR_REDONDEO_PCT} %` });
        }
        // Las dos reglas de arriba son de senales/ (A-R0-17, A-R0-20): si un mes las
        // incumple y figura como apto, el sitio y el pipeline ya no dicen lo mismo.
        if (apto && motivos.length > 0) {
          fallo(ARCHIVO_RATIOS, `línea ${fila.__linea}: el mes ${delMes} de ${par} figura como apto y tiene motivos para no serlo (${motivos.map((motivo) => motivo.etiqueta).join("; ")})`);
        }
        if (!apto && tieneOro && delMes < PRIMER_MES_ORO_LIBRE) {
          motivos.push({ etiqueta: MOTIVO_ANTES_ORO_LIBRE, detalle: DETALLE_ANTES_ORO_LIBRE });
        }
        if (!apto && motivos.length === 0) {
          motivos.push(
            aptoDesde !== "" && delMes < aptoDesde
              ? { etiqueta: "anterior al tramo apto para métricas", detalle: `el tramo apto empieza en ${aptoDesde}` }
              : { etiqueta: `motivo no declarado en ${ARCHIVO_RATIOS}`, detalle: "" },
          );
        }

        const sinComparar = [numerador, denominador].filter((lado) => delControl[lado.serie] === CONTRASTE_SIN_COMPARAR);
        const notas =
          sinComparar.length > 0
            ? [`${NOTA_SIN_SEGUNDA_FUENTE} — ${sinComparar.map((lado) => lado.nombre).join(" y ")}: sin control mensual contra el FMI`]
            : [];

        return { mes: delMes, valor, errorRedondeoPct, apto, enDisputa: ladosEnDisputa.length > 0, motivos, notas };
      })
      .sort((a, b) => a.mes.localeCompare(b.mes));

    for (let i = 1; i < puntos.length; i++) {
      if (puntos[i].mes === puntos[i - 1].mes) fallo(ARCHIVO_RATIOS, `el mes ${puntos[i].mes} del par ${par} está repetido`);
    }
    const aptos = puntos.filter((punto) => punto.apto);
    const controles: [string, number | string, number | string][] = [
      ["meses", entero(ARCHIVO_PARES, filaPar, "meses"), puntos.length],
      ["primer_mes", primerMes, puntos[0].mes],
      ["ultimo_mes", ultimoMes, puntos[puntos.length - 1].mes],
      ["meses_aptos", entero(ARCHIVO_PARES, filaPar, "meses_aptos"), aptos.length],
      ["meses_en_disputa", entero(ARCHIVO_PARES, filaPar, "meses_en_disputa"), puntos.filter((punto) => punto.enDisputa).length],
    ];
    for (const [columna, declarado, contado] of controles) {
      if (declarado !== contado) {
        fallo(ARCHIVO_PARES, `el par ${par} declara ${columna} = ${declarado} y ${ARCHIVO_RATIOS} trae ${contado}`);
      }
    }

    const sinSegundaFuente = aptos.filter((punto) => punto.notas.length > 0).map((punto) => punto.mes);
    return {
      publicado: true,
      par,
      nombre,
      estado,
      primerMes,
      ultimoMes,
      meses: puntos.length,
      aptoDesde,
      mesesAptos: aptos.length,
      mesesEnDisputa: puntos.filter((punto) => punto.enDisputa).length,
      errorMaximo: errorMaximo(puntos),
      errorMaximoAptos: errorMaximo(aptos),
      aptosSinSegundaFuente: { meses: sinSegundaFuente.length, tramos: tramos(sinSegundaFuente) },
      fuentes: [numerador, denominador],
      puntos,
    };
  });

  const ultimos = pares.filter((par): par is ParPublicado => par.publicado).map((par) => par.ultimoMes);
  return {
    pares,
    series,
    descargas,
    ultimoMes: ultimos.length > 0 ? ultimos.reduce((a, b) => (a > b ? a : b)) : null,
  };
}
