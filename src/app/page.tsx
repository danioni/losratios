import Header from "@/components/Header";
import Dashboard from "@/components/Dashboard";
import Footer from "@/components/Footer";
import { CurrencyBaseProvider } from "@/components/CurrencyContext";
import CurrencySelector from "@/components/CurrencySelector";

export default function Home() {
  return (
    <CurrencyBaseProvider>
      <main className="min-h-screen">
        <Header />
        <CurrencySelector />
        <Dashboard />
        <Footer />
      </main>
    </CurrencyBaseProvider>
  );
}
