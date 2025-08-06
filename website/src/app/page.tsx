import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import HaloSection from "./components/HaloSection";
import CoverageSection from "./components/CoverageSection";
// import DoGoodSection from "./components/DoGoodSection";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <HeroSection />
        <HaloSection />
        <CoverageSection />
        {/* <DoGoodSection /> */}
      </main>
      <Footer />
    </div>
  );
}
