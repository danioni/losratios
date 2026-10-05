"use client";

interface NoMedidoCardProps {
  title: string;
  /** El estado, tal cual: sin gráfico ni valor */
  estado: string;
}

export default function NoMedidoCard({ title, estado }: NoMedidoCardProps) {
  return (
    <div className="card-glass card-accent-left rounded-xl p-4 sm:p-6 md:p-8 fade-in-up fade-in-up-3">
      <h2 className="font-serif text-base sm:text-lg tracking-wide mb-2" style={{ color: "var(--text-primary)" }}>
        {title}
      </h2>
      <p className="text-[10px] sm:text-[11px] leading-relaxed font-medium" style={{ color: "var(--accent-amber)" }}>
        {estado}
      </p>
    </div>
  );
}
