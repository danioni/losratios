"use client";

import { ReactNode } from "react";

interface ChartSectionProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  delay?: number;
}

export default function ChartSection({ title, subtitle, children, delay = 0 }: ChartSectionProps) {
  const parts = title.split(" — ");
  const heading = parts[0];
  const tagline = parts.length > 1 ? parts.slice(1).join(" — ") : null;

  return (
    <div className={`card-glass card-accent-left rounded-xl p-4 sm:p-6 md:p-8 fade-in-up fade-in-up-${delay}`}>
      <div className="mb-4 sm:mb-5">
        <h2 className="mb-2">
          <span
            className="font-serif text-base sm:text-lg tracking-wide"
            style={{ color: "var(--text-primary)" }}
          >
            {heading}
          </span>
          {tagline && (
            <>
              <br className="sm:hidden" />
              <span
                className="font-serif italic text-sm sm:text-base sm:ml-2"
                style={{ color: "var(--text-secondary)", opacity: 0.7 }}
              >
                — {tagline}
              </span>
            </>
          )}
        </h2>
        <p
          className="text-[10px] sm:text-[11px] leading-relaxed max-w-2xl"
          style={{ color: "var(--text-muted)" }}
        >
          {subtitle}
        </p>
      </div>
      <div className="divider-gradient mb-5" />
      {children}
    </div>
  );
}
