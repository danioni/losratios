"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  formatDateLabel,
  METRICAS_VERIFICADAS,
  NO_MEDIDO,
  NO_MEDIDO_TABLAS,
} from "@/lib/data";
import type { Par, ParPublicado } from "@/lib/series";
import MetricCard from "./MetricCard";
import NoMedidoCard from "./NoMedidoCard";
import RatioChart, { type TimeRange } from "./RatioChart";

// Color de cada par en su gráfico. Un par que no esté aquí usa el cian.
const COLOR_DEL_PAR: Record<string, keyof typeof DEFAULT_COLORS> = {
  btc_oro: "gold",
  oro_sp500: "amber",
  btc_sp500: "cyan",
  nasdaq_sp500: "blue",
  oro_plata: "red",
};
// Los pares que la portada presenta con texto propio, en este orden.
const PARES_DE_PORTADA = ["btc_oro", "oro_sp500", "btc_sp500", "nasdaq_sp500", "oro_plata"];

const DEFAULT_COLORS = {
  green: "#00ff88", greenDim: "#00cc6a", blue: "#3388ff",
  purple: "#aa55ff", amber: "#ffaa00", red: "#ff3355",
  cyan: "#00ddff", gold: "#ffd700", muted: "#55556a",
};

function useThemeColors() {
  const getColors = useCallback(() => {
    if (typeof window === "undefined") return DEFAULT_COLORS;
    const s = getComputedStyle(document.documentElement);
    const g = (v: string, fb: string) => s.getPropertyValue(v).trim() || fb;
    return {
      green: g("--accent-green", "#00ff88"),
      greenDim: g("--accent-green-dim", "#00cc6a"),
      blue: g("--accent-blue", "#3388ff"),
      purple: g("--accent-purple", "#aa55ff"),
      amber: g("--accent-amber", "#ffaa00"),
      red: g("--accent-red", "#ff3355"),
      cyan: g("--accent-cyan", "#00ddff"),
      gold: g("--accent-gold", "#ffd700"),
      muted: g("--text-muted", "#55556a"),
    };
  }, []);

  const [colors, setColors] = useState(DEFAULT_COLORS);

  useEffect(() => {
    setColors(getColors());
    const observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.attributeName === "data-theme") {
          requestAnimationFrame(() => setColors(getColors()));
        }
      }
    });
    observer.observe(document.documentElement, { attributes: true });
    return () => observer.disconnect();
  }, [getColors]);

  return colors;
}

function TimeRangeSelector({ range, onChange }: { range: TimeRange; onChange: (r: TimeRange) => void }) {
  const options: TimeRange[] = ["1Y", "3Y", "5Y", "MAX"];
  return (
    <div className="flex gap-1 p-1 rounded-lg" style={{ background: "var(--controls-bg)", border: "1px solid var(--border-subtle)" }}>
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className="px-2.5 sm:px-3.5 py-1.5 rounded-md text-[9px] sm:text-[10px] tracking-wider uppercase transition-all"
          style={{
            background: range === opt ? "var(--accent-green-bg-active)" : "transparent",
            color: range === opt ? "var(--accent-green)" : "var(--text-muted)",
            border: range === opt ? "1px solid var(--accent-green-border-active)" : "1px solid transparent",
            boxShadow: range === opt ? "var(--accent-green-glow)" : "none",
          }}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

export default function Dashboard({ pares, ultimoMes }: { pares: Par[]; ultimoMes: string | null }) {
  const [range, setRange] = useState<TimeRange>("MAX");
  const COLORS = useThemeColors();

  const timestampLabel = ultimoMes ? `Último dato: ${formatDateLabel(ultimoMes)}` : "Sin pares publicados";
  // En el orden de la portada; un par nuevo va al final.
  const orden = (par: Par) => (PARES_DE_PORTADA.includes(par.par) ? PARES_DE_PORTADA.indexOf(par.par) : PARES_DE_PORTADA.length);
  const publicados = pares
    .filter((par): par is ParPublicado => par.publicado)
    .sort((a, b) => orden(a) - orden(b));

  // Gráfico si pares.csv publica el par; si no, tarjeta con su nombre y su estado.
  const bloque = (clave: string) => {
    const par = pares.find((candidato) => candidato.par === clave);
    // Sin el par no hay nada que mostrar en su lugar: el build se detiene.
    if (!par) throw new Error(`senales/data/series/pares.csv: no trae el par ${clave}, que la portada presenta`);
    return par.publicado ? (
      <RatioChart key={par.par} par={par} range={range} color={COLORS[COLOR_DEL_PAR[par.par] ?? "cyan"]} />
    ) : (
      <NoMedidoCard key={par.par} title={par.nombre} estado={par.estado} />
    );
  };
  const otrosPares = pares.filter((par) => !PARES_DE_PORTADA.includes(par.par));

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-8 sm:space-y-12 relative z-10">
      {/* ═══════════════════════════════════════════════════════ */}
      {/* HERO — Approved copy from CLAUDE.md                    */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="text-center space-y-5 py-8 sm:py-12 fade-in-up fade-in-up-1">
        <h2 className="font-serif text-2xl sm:text-4xl md:text-5xl tracking-wide leading-tight" style={{ color: "var(--text-primary)" }}>
          No hay precios absolutos.
        </h2>
        <p className="font-serif italic text-base sm:text-xl md:text-2xl" style={{ color: "var(--accent-green)" }}>
          Solo ratios mal leídos.
        </p>
        <div className="max-w-2xl mx-auto space-y-3">
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            La única forma de saber si un activo está caro o barato es compararlo con otro activo. No con dinero fiat. Aquí medimos activos contra activos.
          </p>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Imagina que quieres saber si una persona es alta. Pero tu metro se encoge cada año.
            Mañana medirías a la misma persona y dirías que creció. No creció. Tu metro se encogió.
            Así funciona medir activos en dólares. El precio &ldquo;sube&rdquo; — pero ¿el activo vale más, o el dólar vale menos?
          </p>
          <p className="text-[11px] sm:text-xs font-medium" style={{ color: "var(--accent-green)" }}>
            La respuesta está en los ratios.
          </p>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* ¿Cómo leer un ratio? — Educational section             */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="fade-in-up fade-in-up-2">
        <div className="card-glass card-accent-left rounded-xl p-6 sm:p-8">
          <h3 className="font-serif text-lg sm:text-xl mb-4" style={{ color: "var(--text-primary)" }}>
            &iquest;C&oacute;mo leer un ratio?
          </h3>
          <div className="grid sm:grid-cols-3 gap-4 sm:gap-6 mb-5">
            <div className="space-y-2">
              <div className="text-sm font-medium" style={{ color: "var(--accent-green)" }}>
                1. El ratio sube
              </div>
              <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                El numerador gana terreno vs el denominador. Si BTC/Oro sube, Bitcoin est&aacute; capturando m&aacute;s valor relativo al oro.
              </p>
            </div>
            {METRICAS_VERIFICADAS ? (<>
            <div className="space-y-2">
              <div className="text-sm font-medium" style={{ color: "var(--accent-amber)" }}>
                2. El z-score extremo
              </div>
              <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                Un z-score de +2&sigma; o -2&sigma; indica que el ratio est&aacute; muy lejos de su media hist&oacute;rica.
              </p>
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium" style={{ color: "var(--accent-cyan)" }}>
                3. La se&ntilde;al de rotaci&oacute;n
              </div>
              <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                Marca un par cuyo ratio est&aacute; en zona extrema de su historia (|z| &ge; 2). Describe d&oacute;nde est&aacute; el ratio respecto de su historia; no indica qu&eacute; hacer ni cu&aacute;ndo.
              </p>
            </div>
            </>) : (
            <div className="space-y-2 sm:col-span-2">
              <div className="text-sm font-medium" style={{ color: "var(--accent-amber)" }}>
                2. Z-score y se&ntilde;ales de rotaci&oacute;n
              </div>
              <p className="text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                {NO_MEDIDO} Por ahora el sitio muestra solo el nivel mensual de cada ratio, sin interpolar. z-score, percentil, bandas y se&ntilde;ales usar&aacute;n &uacute;nicamente los meses aptos para m&eacute;tricas.
              </p>
            </div>
            )}
          </div>
          <div className="divider-gradient mb-4" />
          <p className="text-[10px] sm:text-[11px] leading-relaxed italic" style={{ color: "var(--text-muted)" }}>
            Todo precio es una fracci&oacute;n. El <a href="https://eldenominador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--accent-amber)", textDecoration: "underline", textUnderlineOffset: "2px" }}>denominador</a> se encoge.
            El <a href="https://elnumerador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--accent-cyan)", textDecoration: "underline", textUnderlineOffset: "2px" }}>numerador</a> protege.
            Los ratios miden la distancia entre ambos.
          </p>
        </div>
      </div>

      {/* Controls + fecha del último dato, leída de los CSV */}
      <div className="flex flex-wrap items-center gap-3 fade-in-up fade-in-up-2">
        <TimeRangeSelector range={range} onChange={setRange} />
        <span className="text-[10px] tabular-nums tracking-wider ml-auto flex items-center gap-2" style={{ color: "var(--text-muted)" }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: ultimoMes ? "var(--accent-green)" : "var(--accent-amber)" }} />
          {timestampLabel} · series mensuales le&iacute;das al construir el sitio
        </span>
      </div>

      {/* Último valor de cada par publicado */}
      {publicados.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          {publicados.map((par, i) => {
            const ultimo = par.puntos[par.puntos.length - 1];
            return (
              <MetricCard
                key={par.par}
                label={par.nombre}
                value={ultimo.valor}
                detail={`${formatDateLabel(ultimo.mes)} · ${par.estado}`}
                delay={i + 1}
              />
            );
          })}
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 1 — BTC/Oro: EL RATIO CENTRAL                 */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            BTC ÷ Oro — El ratio central
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            ¿Cuánto market share le está sacando Bitcoin al oro como reserva de valor? Este es el ratio más importante del sitio. Cuando está bajo históricamente, el mercado duda del argumento del &ldquo;digital gold&rdquo;. Cuando está alto, el argumento está ganando.
          </p>
        </div>
        {bloque("btc_oro")}

        {/* Pull quote — shareable moment */}
        <div className="text-center py-6">
          <p className="font-serif italic text-base sm:text-lg md:text-xl leading-relaxed max-w-xl mx-auto" style={{ color: "var(--text-secondary)" }}>
            &ldquo;No preguntes si un activo está caro o barato. Pregunta contra qué lo estás midiendo.&rdquo;
          </p>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 2 — El espectro monetario                      */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            Dentro de los ganadores: ¿hard money o capital productivo?
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Oro/S&P 500 y BTC/S&P 500 juntos cuentan una historia: cuánto está apostando el mercado a la narrativa de escasez pura (oro y Bitcoin) vs la narrativa de crecimiento productivo (acciones).
          </p>
        </div>
        {bloque("oro_sp500")}
        {bloque("btc_sp500")}
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 3 — Growth vs Quality                          */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            Growth vs Quality: el ciclo dentro del ciclo
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Dentro del capital productivo, el Nasdaq (growth/tech) vs el S&P 500 (quality/broad market) marca otro ciclo.
          </p>
        </div>
        {bloque("nasdaq_sp500")}
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 4 — La escasez medida                          */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="space-y-4">
        <div className="max-w-2xl">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>
            ¿Cuánto paga el mercado por escasez?
          </h3>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Oro/Plata mide el apetito por escasez pura (oro) vs escasez con utilidad industrial (plata). Compara el metal monetario con uno de uso mayormente industrial. Conecta con el argumento del Numerador: cuanto más inelástica la oferta, más captura el activo del debasement.
          </p>
        </div>
        {bloque("oro_plata")}
      </div>

      {/* Un par nuevo en pares.csv, todavía sin texto propio */}
      {otrosPares.length > 0 && (
        <div className="space-y-4">{otrosPares.map((par) => bloque(par.par))}</div>
      )}

      {/* ═══════════════════════════════════════════════════════ */}
      {/* SECTION 5 — Tablas de CAGR y poder adquisitivo         */}
      {/* Sin tabla: NO MEDIDO hasta tener series observadas     */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="grid sm:grid-cols-2 gap-3 sm:gap-4">
        <NoMedidoCard title="Poder adquisitivo global" estado={NO_MEDIDO_TABLAS} />
        <NoMedidoCard title="CAGR histórico por activo" estado={NO_MEDIDO_TABLAS} />
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* DISCLAIMER NARRATIVO                                   */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="py-8 space-y-4 fade-in-up fade-in-up-5">
        <div className="divider-gradient max-w-xs mx-auto" />
        <div className="max-w-2xl mx-auto text-center space-y-3">
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Los ratios no predicen. Esto no es asesoría financiera. Es un marco analítico.
          </p>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CTA FINAL                                              */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="text-center py-8 space-y-6 fade-in-up fade-in-up-5">
        <div className="space-y-2">
          <p className="font-serif text-sm sm:text-base" style={{ color: "var(--text-primary)" }}>
            Los precios en fiat son ruido. Los ratios son señal.
          </p>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Ya tienes el marco completo:
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-4 text-[10px] sm:text-[11px] tracking-wider">
          <a href="https://eldenominador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--accent-amber)" }}>
            El Denominador →
          </a>
          <span style={{ color: "var(--text-muted)" }}>por qué el dinero se encoge</span>
        </div>
        <div className="flex flex-wrap justify-center gap-4 text-[10px] sm:text-[11px] tracking-wider">
          <a href="https://elnumerador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--accent-cyan)" }}>
            El Numerador →
          </a>
          <span style={{ color: "var(--text-muted)" }}>por qué los activos se multiplican</span>
        </div>
        <div className="flex flex-wrap justify-center gap-4 text-[10px] sm:text-[11px] tracking-wider">
          <a href="https://losratios.com" className="font-medium" style={{ color: "var(--accent-green)" }}>
            Los Ratios
          </a>
          <span style={{ color: "var(--text-muted)" }}>cómo comparar sin la vara que se encoge</span>
        </div>
        <div className="space-y-1 pt-2">
          <p className="text-[10px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
            {timestampLabel}
          </p>
          <p className="text-[9px]" style={{ color: "var(--text-muted)" }}>
            <Link href="/fuentes" className="transition-opacity hover:opacity-80" style={{ textDecoration: "underline", textUnderlineOffset: "2px" }}>
              Fuentes y metodolog&iacute;a
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
