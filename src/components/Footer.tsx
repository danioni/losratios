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
              Una herramienta de{" "}
              <a
                href="https://elfaro.capital"
                target="_blank"
                rel="noopener noreferrer"
                className="transition-opacity hover:opacity-80"
                style={{ color: "var(--text-secondary)" }}
              >
                El Faro Capital
              </a>
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
