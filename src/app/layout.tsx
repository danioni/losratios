import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Los Ratios — Activos medidos contra activos",
  description:
    "Activos medidos contra activos, con datos mensuales observados, fuentes citadas y supuestos declarados.",
  keywords: [
    "ratios financieros",
    "cross-asset",
    "BTC oro",
    "oro plata",
    "liquidez global",
    "M2",
    "stock-to-flow",
  ],
  openGraph: {
    title: "Los Ratios",
    description:
      "Activos medidos contra activos, con datos mensuales observados, fuentes citadas y supuestos declarados.",
    url: "https://losratios.com",
    siteName: "Los Ratios",
    type: "website",
    locale: "es_CL",
  },
  twitter: {
    card: "summary_large_image",
    title: "Los Ratios",
    description:
      "Activos medidos contra activos, con datos mensuales observados, fuentes citadas y supuestos declarados.",
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" data-theme="dark" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');if(!t)t=window.matchMedia('(prefers-color-scheme:light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',t)}catch(e){}})()`,
          }}
        />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="noise-overlay">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
