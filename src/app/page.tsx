import Header from "@/components/Header";
import Dashboard from "@/components/Dashboard";
import Footer from "@/components/Footer";
import { CurrencyBaseProvider } from "@/components/CurrencyContext";
import { cargarSeries } from "@/lib/series";

// La página se genera en el build, con las series de senales/data/series/. Si un
// CSV falta o está mal formado, cargarSeries() lanza y el build falla.
export const dynamic = "error";

export default function Home() {
  const { pares, ultimoMes } = cargarSeries();
  return (
    <CurrencyBaseProvider>
      <main className="min-h-screen">
        <Header ultimoMes={ultimoMes} />
        <Dashboard pares={pares} ultimoMes={ultimoMes} />
        <Footer />
      </main>
    </CurrencyBaseProvider>
  );
}
