import type { Metadata } from "next";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { METRICAS_VERIFICADAS, NO_MEDIDO, NO_MEDIDO_TABLAS, TABLAS_MEDIDAS } from "@/lib/data";
import { cargarSeries } from "@/lib/series";

export const metadata: Metadata = {
  title: "Fuentes y metodología — Los Ratios",
  description: "De dónde sale cada serie de Los Ratios: fuente, licencia, atribución, validación y descargas.",
};

// Igual que la portada: se genera en el build, con los CSV de senales/data/series/.
export const dynamic = "error";

const REPO = "https://github.com/danioni/losratios/blob/main/senales";

const celda = "py-2.5 px-2 align-top";
const encabezado = "text-left py-2 px-2 tracking-wider uppercase font-medium whitespace-nowrap";
const enlace = { color: "var(--accent-green)", textDecoration: "underline", textUnderlineOffset: "2px" };

export default function Fuentes() {
  const { series, descargas, ultimoMes } = cargarSeries();
  return (
    <main className="min-h-screen">
      <Header ultimoMes={ultimoMes} />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-8 sm:space-y-12 relative z-10">
        <div className="max-w-2xl space-y-3">
          <h2 className="font-serif text-2xl sm:text-3xl tracking-wide" style={{ color: "var(--text-primary)" }}>
            Fuentes y metodolog&iacute;a
          </h2>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            Los ratios del sitio se calculan con series mensuales que se construyen y se validan en el repositorio. El sitio las lee
            de los archivos publicados cuando se construye; si un archivo falta o est&aacute; mal formado, el sitio no se publica.
            No hay precios en vivo ni valores de respaldo.
          </p>
          <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
            La lectura de cada fuente y de su licencia est&aacute; en{" "}
            <a href={`${REPO}/FUENTES.md`} target="_blank" rel="noopener noreferrer" style={enlace}>FUENTES.md</a>
            , y cada supuesto, con su n&uacute;mero, en{" "}
            <a href={`${REPO}/SUPUESTOS.md`} target="_blank" rel="noopener noreferrer" style={enlace}>SUPUESTOS.md</a>.
          </p>
          <p className="text-[11px] sm:text-xs">
            <Link href="/" style={enlace}>&larr; Volver a los ratios</Link>
          </p>
        </div>

        {/* Una fila por serie, desde series.csv */}
        <section className="space-y-4">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide" style={{ color: "var(--text-primary)" }}>Series</h3>
          <div className="card-glass card-accent-left rounded-xl p-4 sm:p-5">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1100px] text-[10px] sm:text-[11px] leading-relaxed">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)" }}>
                    <th className={encabezado}>Serie</th>
                    <th className={encabezado}>Estado</th>
                    <th className={encabezado}>Fuente</th>
                    <th className={encabezado}>Licencia</th>
                    <th className={encabezado}>Atribuci&oacute;n</th>
                    <th className={encabezado}>Validaci&oacute;n</th>
                    <th className={encabezado}>Supuestos</th>
                    <th className={encabezado}>Meses</th>
                  </tr>
                </thead>
                <tbody>
                  {series.map((serie) => (
                    <tr key={serie.serie} style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>
                      <td className={celda}>
                        <span className="font-medium" style={{ color: "var(--text-primary)" }}>{serie.nombre}</span>
                        <br />
                        <span style={{ color: "var(--text-muted)" }}>{serie.unidad}</span>
                      </td>
                      <td className={celda} style={{ color: serie.publicada ? "var(--text-secondary)" : "var(--accent-amber)" }}>
                        {serie.estado}
                      </td>
                      <td className={celda}>{serie.fuente}</td>
                      <td className={celda}>{serie.licencia}</td>
                      <td className={celda}>{serie.atribucion}</td>
                      <td className={celda}>{serie.validacion}</td>
                      <td className={celda}>{serie.supuestos.join(", ")}</td>
                      <td className={`${celda} tabular-nums whitespace-nowrap`}>
                        {serie.primerMes} a {serie.ultimoMes}
                        <br />
                        <span style={{ color: "var(--text-muted)" }}>{serie.meses} meses</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* El manifiesto de descargas, desde descargas_ratios.csv */}
        <section className="space-y-4">
          <div className="max-w-2xl">
            <h3 className="font-serif text-lg sm:text-xl tracking-wide mb-3" style={{ color: "var(--text-primary)" }}>Descargas</h3>
            <p className="text-[11px] sm:text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
              Cada archivo que us&oacute; la &uacute;ltima corrida, con su direcci&oacute;n, la fecha en que se baj&oacute; y su SHA-256.
            </p>
          </div>
          <div className="card-glass card-accent-left rounded-xl p-4 sm:p-5">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-[10px] sm:text-[11px] leading-relaxed">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)" }}>
                    <th className={encabezado}>Fuente</th>
                    <th className={encabezado}>Fecha</th>
                    <th className={encabezado}>URL</th>
                    <th className={encabezado}>SHA-256</th>
                  </tr>
                </thead>
                <tbody>
                  {descargas.map((descarga) => (
                    <tr key={descarga.fuente} style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>
                      <td className={celda}>
                        <span className="font-medium" style={{ color: "var(--text-primary)" }}>{descarga.fuente}</span>
                        <br />
                        <span style={{ color: "var(--text-muted)" }}>{descarga.licencia}</span>
                      </td>
                      <td className={`${celda} tabular-nums whitespace-nowrap`}>{descarga.fechaDescarga}</td>
                      <td className={`${celda} break-all`}>{descarga.url}</td>
                      <td className={`${celda} break-all tabular-nums`}>{descarga.sha256}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Lo que todavía no se publica */}
        <section className="space-y-4">
          <h3 className="font-serif text-lg sm:text-xl tracking-wide" style={{ color: "var(--text-primary)" }}>Lo que todav&iacute;a no se publica</h3>
          <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6 space-y-3 text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
            {!METRICAS_VERIFICADAS && (
              <div>
                <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Z-score, percentil, bandas y se&ntilde;ales</p>
                <p>{NO_MEDIDO}</p>
              </div>
            )}
            {!TABLAS_MEDIDAS && (
              <div>
                <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Tablas de CAGR y poder adquisitivo</p>
                <p>{NO_MEDIDO_TABLAS}</p>
              </div>
            )}
            <div>
              <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Pares sin permiso de publicaci&oacute;n</p>
              <p>Aparecen en la portada con su nombre y su estado, sin gr&aacute;fico ni valor.</p>
            </div>
          </div>
        </section>
      </div>
      <Footer />
    </main>
  );
}
