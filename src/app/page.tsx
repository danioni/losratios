import Header from "@/components/Header";
import Dashboard from "@/components/Dashboard";
import Footer from "@/components/Footer";
import { CurrencyBaseProvider } from "@/components/CurrencyContext";
import { DataStatusProvider } from "@/components/DataStatusContext";

export default function Home() {
  return (
    <CurrencyBaseProvider>
      <DataStatusProvider>
        <main className="min-h-screen">
          <Header />
          <Dashboard />
          <Footer />
        </main>
      </DataStatusProvider>
    </CurrencyBaseProvider>
  );
}
