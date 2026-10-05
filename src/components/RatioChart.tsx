"use client";

import { useMemo } from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatDateLabel, formatRatio, needsLogScale, METRICAS_VERIFICADAS, NO_MEDIDO } from "@/lib/data";
import type { ParPublicado, PuntoRatio } from "@/lib/series";
import ChartSection from "./ChartSection";

export type TimeRange = "1Y" | "3Y" | "5Y" | "MAX";

const MESES_POR_RANGO: Record<TimeRange, number | null> = { "1Y": 12, "3Y": 36, "5Y": 60, MAX: null };

interface FilaGrafico {
  mes: string;
  /** Todos los meses publicados: la línea punteada, que queda a la vista donde el mes no es apto */
  todos: number | null;
  /** Solo los meses aptos para métricas: la línea llena */
  aptos: number | null;
  /** Solo los meses con un valor en disputa: el círculo */
  disputa: number | null;
  punto: PuntoRatio | null;
}

function mesSiguiente(mes: string): string {
  const [anio, numero] = mes.split("-").map(Number);
  return numero === 12 ? `${anio + 1}-01` : `${anio}-${String(numero + 1).padStart(2, "0")}`;
}

/** Hasta dos años, una marca por trimestre; después, eneros cada tantos años como haga falta. */
function marcasDelEje(meses: string[]): string[] {
  if (meses.length <= 24) return meses.filter((mes) => (Number(mes.slice(5)) - 1) % 3 === 0);
  const paso = Math.ceil(meses.length / 12 / 12);
  return meses.filter((mes) => mes.endsWith("-01") && Number(mes.slice(0, 4)) % paso === 0);
}

function formatoDecada(exponente: number): string {
  return exponente >= 0 ? String(10 ** exponente) : (10 ** exponente).toFixed(-exponente);
}

function TooltipMes({ fila, nombre }: { fila: FilaGrafico; nombre: string }) {
  const punto = fila.punto;
  return (
    <div
      className="rounded-lg px-4 py-3 text-[10px] sm:text-[11px] leading-relaxed max-w-[300px] sm:max-w-[360px]"
      style={{
        background: "var(--bg-tooltip)",
        border: "1px solid var(--border)",
        backdropFilter: "blur(10px)",
      }}
    >
      <p className="mb-1.5 font-medium" style={{ color: "var(--text-secondary)" }}>
        {formatDateLabel(fila.mes)}
      </p>
      {punto === null ? (
        <p style={{ color: "var(--text-muted)" }}>Sin dato publicado para este mes.</p>
      ) : (
        <>
          <p className="tabular-nums" style={{ color: "var(--text-primary)" }}>
            {nombre}: <span className="font-medium">{formatRatio(punto.valor)}</span>
          </p>
          <p className="tabular-nums" style={{ color: "var(--text-muted)" }}>
            Error máximo por redondeo: {punto.errorRedondeoPct} %
          </p>
          {punto.apto ? (
            <p className="mt-1.5" style={{ color: "var(--text-muted)" }}>Apto para métricas.</p>
          ) : (
            <div className="mt-1.5" style={{ color: "var(--accent-amber)" }}>
              <p className="font-medium">Fuera de las métricas:</p>
              {punto.motivos.map((motivo) => (
                <p key={motivo.etiqueta + motivo.detalle}>
                  · {motivo.etiqueta}
                  {motivo.detalle && (
                    <span className="block pl-2.5" style={{ color: "var(--text-secondary)" }}>{motivo.detalle}</span>
                  )}
                </p>
              ))}
            </div>
          )}
          {punto.notas.map((nota) => (
            <p key={nota} className="mt-1" style={{ color: "var(--text-secondary)" }}>· {nota}</p>
          ))}
        </>
      )}
    </div>
  );
}

function Dato({ etiqueta, children }: { etiqueta: string; children: React.ReactNode }) {
  return (
    <div className="grid sm:grid-cols-[190px_1fr] gap-x-4 gap-y-0.5">
      <dt className="text-[9px] tracking-wider uppercase pt-0.5" style={{ color: "var(--text-muted)" }}>{etiqueta}</dt>
      <dd className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>{children}</dd>
    </div>
  );
}

export default function RatioChart({ par, range, color }: { par: ParPublicado; range: TimeRange; color: string }) {
  const { filas, marcas, escalaLog, dominio, marcasY, primerVisible, ultimoVisible } = useMemo(() => {
    const cantidad = MESES_POR_RANGO[range];
    const visibles = cantidad === null ? par.puntos : par.puntos.slice(-cantidad);
    const escalaLog = needsLogScale(visibles.map((punto) => punto.valor));
    // En escala logarítmica se grafica log10 del ratio y el eje se rotula con el valor real.
    const aGrafico = (valor: number) => (escalaLog ? Math.log10(valor) : valor);

    // Una fila por mes del calendario entre el primero y el último visibles: si
    // falta un mes en ratios.csv, queda vacío y la línea se corta. No se interpola.
    const porMes = new Map(visibles.map((punto) => [punto.mes, punto]));
    const filas: FilaGrafico[] = [];
    const ultimo = visibles[visibles.length - 1].mes;
    for (let mes = visibles[0].mes; mes <= ultimo; mes = mesSiguiente(mes)) {
      const punto = porMes.get(mes) ?? null;
      const valor = punto === null ? null : aGrafico(punto.valor);
      filas.push({
        mes,
        todos: valor,
        aptos: punto?.apto ? valor : null,
        disputa: punto?.enDisputa ? valor : null,
        punto,
      });
    }

    let dominio: [number, number] | undefined;
    let marcasY: number[] | undefined;
    if (escalaLog) {
      // El eje va del mínimo al máximo visibles, con un margen, y se rotula en
      // las décadas enteras que caen adentro: 0.01, 0.1, 1, 10…
      const valores = visibles.map((punto) => Math.log10(punto.valor));
      const minimo = Math.min(...valores);
      const maximo = Math.max(...valores);
      const margen = (maximo - minimo) * 0.05;
      dominio = [minimo - margen, maximo + margen];
      const primera = Math.ceil(dominio[0]);
      marcasY = Array.from({ length: Math.floor(dominio[1]) - primera + 1 }, (_, i) => primera + i);
    }

    return {
      filas,
      marcas: marcasDelEje(filas.map((fila) => fila.mes)),
      escalaLog,
      dominio,
      marcasY,
      primerVisible: visibles[0].mes,
      ultimoVisible: ultimo,
    };
  }, [par.puntos, range]);

  const ultimoPunto = par.puntos[par.puntos.length - 1];
  const hayNoAptos = par.mesesAptos < par.meses;
  const formatoMes = (mes: string) => (filas.length <= 24 ? formatDateLabel(mes) : mes.slice(0, 4));

  return (
    <ChartSection
      title={par.nombre}
      subtitle={`${formatDateLabel(primerVisible)} → ${formatDateLabel(ultimoVisible)} · Último dato (${formatDateLabel(ultimoPunto.mes)}): ${formatRatio(ultimoPunto.valor)}`}
      delay={3}
    >
      {/* Las métricas siguen ocultas: se publicarán sobre estas mismas series */}
      {!METRICAS_VERIFICADAS && (
        <p className="text-[10px] sm:text-[11px] mb-4 leading-relaxed font-medium" style={{ color: "var(--accent-amber)" }}>
          z-score · percentil · bandas · señales — {NO_MEDIDO}
        </p>
      )}

      {/* Nivel mensual del ratio */}
      <div className="h-[280px] sm:h-[360px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={filas} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="mes"
              ticks={marcas}
              tickFormatter={formatoMes}
              tick={{ fill: "var(--text-muted)", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={dominio}
              ticks={marcasY}
              tick={{ fill: "var(--text-muted)", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => (escalaLog ? formatoDecada(v) : v > 0 ? formatRatio(v) : "0")}
            />
            <Tooltip
              content={({ active, payload }) => {
                const fila: FilaGrafico | undefined = payload?.[0]?.payload;
                return active && fila ? <TooltipMes fila={fila} nombre={par.nombre} /> : null;
              }}
            />
            {/* Todos los meses, punteada y atenuada: queda a la vista donde el mes no es apto */}
            <Line type="linear" dataKey="todos" name={par.nombre} stroke={color} strokeWidth={1.5} strokeDasharray="2 3" strokeOpacity={0.55} dot={false} activeDot={{ r: 4 }} connectNulls={false} isAnimationActive={false} />
            {/* Meses aptos para métricas, llena: une solo meses aptos consecutivos */}
            <Line type="linear" dataKey="aptos" stroke={color} strokeWidth={2} dot={false} activeDot={false} connectNulls={false} isAnimationActive={false} />
            {/* Meses con un valor en disputa: solo el círculo */}
            <Line type="linear" dataKey="disputa" stroke="none" strokeWidth={0} dot={{ r: 3, fill: "var(--bg-card)", stroke: color, strokeWidth: 1.5 }} activeDot={false} connectNulls={false} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Leyenda de los estilos */}
      <div className="flex flex-wrap gap-x-5 gap-y-2 mt-3 justify-center">
        <div className="flex items-center gap-1.5">
          <svg width="22" height="6" aria-hidden="true"><line x1="0" y1="3" x2="22" y2="3" stroke={color} strokeWidth="2" /></svg>
          <span className="text-[8px] sm:text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Mes apto para métricas</span>
        </div>
        {hayNoAptos && (
          <div className="flex items-center gap-1.5">
            <svg width="22" height="6" aria-hidden="true"><line x1="0" y1="3" x2="22" y2="3" stroke={color} strokeWidth="1.5" strokeDasharray="2 3" strokeOpacity="0.55" /></svg>
            <span className="text-[8px] sm:text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Publicado, fuera de las métricas</span>
          </div>
        )}
        {par.mesesEnDisputa > 0 && (
          <div className="flex items-center gap-1.5">
            <svg width="10" height="10" aria-hidden="true"><circle cx="5" cy="5" r="3" fill="var(--bg-card)" stroke={color} strokeWidth="1.5" /></svg>
            <span className="text-[8px] sm:text-[9px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>Valor en disputa</span>
          </div>
        )}
      </div>
      <p className="text-[9px] mt-3 leading-relaxed italic" style={{ color: "var(--text-muted)", opacity: 0.8 }}>
        Nivel mensual del ratio, un punto por mes publicado, sin interpolar.
        {hayNoAptos && " Los meses fuera de las métricas se muestran igual; el motivo aparece al pasar el cursor."}
        {par.aptosSinSegundaFuente.meses > 0 && " Un mes apto puede no tener control mensual contra una segunda fuente: también lo dice al pasar el cursor."}
        {escalaLog && " Eje vertical en escala logarítmica."}
      </p>

      {/* Ficha de la serie: todo sale de pares.csv, ratios.csv y series.csv */}
      <div className="divider-gradient my-5" />
      <dl className="space-y-2.5">
        <Dato etiqueta="Estado">{par.estado}</Dato>
        <Dato etiqueta="Meses">{par.primerMes} a {par.ultimoMes} · {par.meses} meses</Dato>
        <Dato etiqueta="Último dato">{formatDateLabel(par.ultimoMes)}</Dato>
        {par.errorMaximo && (
          <Dato etiqueta="Error máximo por redondeo">
            {par.errorMaximo.pct} % ({par.errorMaximo.mes})
            {par.errorMaximoAptos && par.errorMaximoAptos.mes !== par.errorMaximo.mes &&
              `; en los meses aptos para métricas, ${par.errorMaximoAptos.pct} % (${par.errorMaximoAptos.mes})`}
          </Dato>
        )}
        <Dato etiqueta="Aptos para métricas">
          {par.mesesAptos} de {par.meses} meses{par.aptoDesde && `, desde ${par.aptoDesde}`}
          {par.mesesEnDisputa > 0 && ` · ${par.mesesEnDisputa} con un valor en disputa`}
          {par.aptosSinSegundaFuente.meses > 0 &&
            ` · ${par.aptosSinSegundaFuente.meses} de los aptos, sin segunda fuente (${par.aptosSinSegundaFuente.tramos.join(", ")})`}
        </Dato>
        {par.fuentes.map((serie) => (
          <Dato key={serie.serie} etiqueta={`Fuente · ${serie.nombre}`}>
            <span style={{ color: "var(--text-primary)" }}>{serie.fuente}</span> · {serie.unidad} · estado: {serie.estado}
            <br />
            <span style={{ color: "var(--text-muted)" }}>Atribución:</span> {serie.atribucion}
            <br />
            <span style={{ color: "var(--text-muted)" }}>Licencia:</span> {serie.licencia}
            {serie.validacion && (
              <>
                <br />
                <span style={{ color: "var(--text-muted)" }}>Validación:</span> {serie.validacion}
              </>
            )}
          </Dato>
        ))}
      </dl>
    </ChartSection>
  );
}
