"use client";

import { useState, useEffect } from "react";

function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const current = document.documentElement.getAttribute("data-theme") as "dark" | "light";
    if (current) setTheme(current);
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  };

  return (
    <button
      onClick={toggle}
      className="w-8 h-8 rounded-lg flex items-center justify-center transition-all"
      style={{
        background: "var(--accent-green-bg)",
        border: "1px solid var(--accent-green-border)",
      }}
      aria-label={theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
    >
      {theme === "dark" ? (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      )}
    </button>
  );
}

export default function Header() {
  return (
    <header
      className="relative"
      style={{
        background: "linear-gradient(180deg, var(--ambient-glow) 0%, transparent 100%)",
      }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 flex items-center justify-between gap-3">
        {/* Logo */}
        <div className="flex items-center gap-2.5 sm:gap-4 min-w-0">
          <div
            className="w-9 h-9 sm:w-11 sm:h-11 rounded-xl flex items-center justify-center shrink-0"
            style={{
              background: "var(--accent-green-bg)",
              border: "1px solid var(--accent-green-border-active)",
              boxShadow: "var(--accent-green-glow)",
            }}
          >
            <svg viewBox="0 0 64 64" className="w-5 h-5 sm:w-6 sm:h-6">
              <defs>
                <filter id="header-neon">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
                  <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0  0 0 0 0 1  0 0 0 0 0.53  0 0 0 1 0" result="green-blur"/>
                  <feMerge>
                    <feMergeNode in="green-blur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <g filter="url(#header-neon)">
                {/* ÷ symbol */}
                <circle cx="22" cy="16" r="5" fill="#00ff88"/>
                <rect x="8" y="28" width="20" height="7" rx="3.5" fill="#00ff88"/>
                <circle cx="22" cy="48" r="5" fill="#00ff88"/>
                {/* × symbol */}
                <line x1="38" y1="20" x2="54" y2="44" stroke="#00ff88" strokeWidth="5" strokeLinecap="round"/>
                <line x1="54" y1="20" x2="38" y2="44" stroke="#00ff88" strokeWidth="5" strokeLinecap="round"/>
              </g>
            </svg>
          </div>
          <div className="min-w-0">
            <h1 className="font-serif text-lg sm:text-xl tracking-wide truncate" style={{ color: "var(--text-primary)" }}>
              Los Ratios
            </h1>
            <p className="text-[8px] sm:text-[9px] tracking-[0.1em] sm:tracking-[0.15em] uppercase mt-0.5 truncate" style={{ color: "var(--text-muted)" }}>
              Numerador ÷ Denominador · Cross-Asset Ratios
            </p>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          <a
            href="https://elfaro.capital"
            target="_blank"
            rel="noopener noreferrer"
            className="label-badge hidden sm:inline-flex hover:opacity-80 transition-opacity"
          >
            <span className="text-[10px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
              El Faro Capital
            </span>
          </a>
          <div className="label-badge">
            <div
              className="w-1.5 h-1.5 rounded-full pulse-dot"
              style={{ background: "var(--accent-green)" }}
            />
            <span className="text-[9px] sm:text-[10px] tracking-wider uppercase" style={{ color: "var(--text-muted)" }}>
              Live
            </span>
          </div>
          <ThemeToggle />
        </div>
      </div>

      {/* Subtle gradient line */}
      <div
        className="absolute bottom-0 left-0 right-0 h-[1px]"
        style={{
          background:
            "linear-gradient(90deg, transparent, var(--accent-green-border-active) 50%, transparent)",
        }}
      />
    </header>
  );
}
