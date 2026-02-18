import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import HaloSection from "./components/HaloSection";
import CoverageSection from "./components/CoverageSection";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f5f0e8]">
      <Header />
      <main>
        <HeroSection />
        <HaloSection />
        <CoverageSection />
      </main>
      <Footer />
    </div>
  );
}
