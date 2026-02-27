"use client";

const ECOSYSTEM_LINKS = [
  { label: "El Denominador", href: "https://eldenominador.com", desc: "Por qué el dinero se encoge" },
  { label: "El Numerador", href: "https://elnumerador.com", desc: "Por qué los activos se multiplican" },
  { label: "Los Ratios", href: "https://losratios.com", desc: "Cómo comparar sin la vara que se encoge", current: true },
];

export default function Footer() {
  return (
    <footer className="relative mt-16">
      {/* Top gradient line */}
      <div
        className="h-[1px]"
        style={{
          background:
            "linear-gradient(90deg, transparent, var(--accent-green-border) 50%, transparent)",
        }}
      />
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        {/* Ecosystem fracción tagline */}
        <div className="text-center">
          <p className="text-[10px] sm:text-[11px] tracking-[0.15em] uppercase" style={{ color: "var(--text-muted)" }}>
            Todo precio es una fracción: Numerador &divide; Denominador
          </p>
        </div>

        {/* Ecosystem links */}
        <div className="flex flex-wrap justify-center gap-x-4 sm:gap-x-8 gap-y-3">
          {ECOSYSTEM_LINKS.map((link) => (
            <div key={link.label} className="flex items-center gap-2">
              <a
                href={link.href}
                target={link.current ? undefined : "_blank"}
                rel={link.current ? undefined : "noopener noreferrer"}
                className="text-[10px] sm:text-[11px] tracking-wider uppercase font-medium transition-opacity hover:opacity-80"
                style={{ color: link.current ? "var(--accent-green)" : "var(--text-secondary)" }}
              >
                {link.label}
              </a>
              <span className="text-[9px] hidden sm:inline" style={{ color: "var(--text-muted)" }}>
                {link.desc}
              </span>
            </div>
          ))}
        </div>

        {/* Methodology note — collapsible */}
        <details className="rounded-lg" style={{ border: "1px solid var(--border-subtle)" }}>
          <summary
            className="px-4 py-3 cursor-pointer text-[10px] sm:text-[11px] tracking-wider uppercase font-medium select-none"
            style={{ color: "var(--text-muted)" }}
          >
            Metodolog&iacute;a
          </summary>
          <div className="px-4 pb-4 space-y-3 text-[10px] sm:text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
            <div>
              <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Fuentes de precios</p>
              <ul className="space-y-0.5 pl-3">
                <li>BTC: CoinGecko (historia + precio actual)</li>
                <li>Oro (GC=F), Plata (SI=F), S&amp;P 500 (^GSPC), Nasdaq (^IXIC): Yahoo Finance</li>
                <li>M2 Global (M2SL): FRED (Federal Reserve Economic Data)</li>
              </ul>
            </div>
            <div>
              <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Frecuencia de datos</p>
              <p>Series mensuales interpoladas entre puntos de anclaje anuales (1971&ndash;2026). El &uacute;ltimo punto se actualiza con precios en vivo cada hora.</p>
            </div>
            <div>
              <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>CAGR hist&oacute;rico</p>
              <p>El periodo de c&aacute;lculo var&iacute;a por activo seg&uacute;n disponibilidad de datos. BTC desde 2009, acciones individuales desde su IPO, Oro/Plata/S&amp;P/Nasdaq desde 1971. La columna &ldquo;Desde&rdquo; en la tabla muestra el a&ntilde;o de inicio de cada c&aacute;lculo.</p>
            </div>
            <div>
              <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Z-scores</p>
              <p>Calculados sobre la distribuci&oacute;n completa (full-sample) del ratio desde la fecha de inicio del par, no sobre una ventana rolling. Para ratios que abarcan &oacute;rdenes de magnitud (BTC/Oro, BTC/S&amp;P), se usa escala logar&iacute;tmica (media geom&eacute;trica y desviaci&oacute;n est&aacute;ndar en log-space).</p>
            </div>
            <div>
              <p className="font-medium mb-1" style={{ color: "var(--text-secondary)" }}>Se&ntilde;ales</p>
              <p>Las se&ntilde;ales de &ldquo;oportunidad de acumulaci&oacute;n&rdquo; son observaciones estad&iacute;sticas de mean reversion hist&oacute;rica, no predicciones. Un z-score extremo indica que el ratio est&aacute; lejos de su media hist&oacute;rica, no que vaya a revertir en un plazo determinado.</p>
            </div>
          </div>
        </details>

        {/* Ecosystem tagline */}
        <div className="text-center">
          <p className="text-[9px] sm:text-[10px] tracking-[0.15em] uppercase" style={{ color: "var(--text-muted)" }}>
            Parte del ecosistema{" "}
            <a href="https://eldenominador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--text-secondary)" }}>eldenominador</a>
            {" · "}
            <a href="https://elnumerador.com" target="_blank" rel="noopener noreferrer" className="transition-opacity hover:opacity-80" style={{ color: "var(--text-secondary)" }}>elnumerador</a>
            {" · "}
            <span style={{ color: "var(--accent-green)" }}>losratios</span>
          </p>
        </div>

        {/* CTA + attribution */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4" style={{ borderTop: "1px solid var(--border-subtle)" }}>
          <div className="flex items-center gap-3">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
              style={{
                background: "var(--accent-green-bg)",
                border: "1px solid var(--accent-green-border)",
              }}
            >
              <svg viewBox="0 0 64 64" className="w-3.5 h-3.5">
                <defs>
                  <filter id="footer-neon">
                    <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
                    <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0  0 0 0 0 1  0 0 0 0 0.53  0 0 0 1 0" result="green-blur"/>
                    <feMerge>
                      <feMergeNode in="green-blur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <g filter="url(#footer-neon)">
                  <line x1="6" y1="32" x2="16" y2="32" stroke="#00ff88" strokeWidth="2.5" strokeLinecap="round"/>
                  <polyline points="16,32 19,36 22,32" stroke="#00ff88" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  <polyline points="22,32 27,12 32,52 37,18 42,32" stroke="#00ff88" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  <polyline points="42,32 45,28 48,32" stroke="#00ff88" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  <line x1="48" y1="32" x2="58" y2="32" stroke="#00ff88" strokeWidth="2.5" strokeLinecap="round"/>
                </g>
              </svg>
            </div>
            <span className="text-[10px] tracking-wider" style={{ color: "var(--text-muted)" }}>
              losratios.com
            </span>
          </div>
          <span className="text-[9px] tabular-nums" style={{ color: "var(--text-muted)" }}>
            {new Date().getFullYear()}
          </span>
        </div>
      </div>
    </footer>
  );
}
