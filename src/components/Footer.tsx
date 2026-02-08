"use client";

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
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{
              background: "var(--accent-green-bg)",
              border: "1px solid var(--accent-green-border)",
            }}
          >
            <svg viewBox="0 0 64 64" className="w-4 h-4">
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
          <span
            className="text-[11px] tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Una herramienta de El Faro Capital · elfaro.capital
          </span>
        </div>

        <div className="flex items-center gap-6">
          <a
            href="https://eldenominador.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] tracking-wider uppercase transition-opacity hover:opacity-80"
            style={{ color: "var(--text-muted)" }}
          >
            El Denominador
          </a>
          <a
            href="https://elnumerador.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] tracking-wider uppercase transition-opacity hover:opacity-80"
            style={{ color: "var(--text-muted)" }}
          >
            El Numerador
          </a>
          <a
            href="https://elfaro.capital"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] tracking-wider uppercase transition-opacity hover:opacity-80"
            style={{ color: "var(--text-muted)" }}
          >
            El Faro Capital
          </a>
          <span className="text-[10px] tabular-nums" style={{ color: "var(--text-muted)" }}>
            {new Date().getFullYear()}
          </span>
        </div>
      </div>
    </footer>
  );
}
