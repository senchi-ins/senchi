import Footer from "./components/footer";
import Header from "./components/header";
import Hero from "./components/hero";

import { style } from '../config'

export default function Home() {
  return (
    <div 
      className={`items-center justify-items-center min-h-screen gap-16 font-[family-name:var(--font-geist-sans)] ${style.colors.sections.main.bg}`}
    >
        <Header />
        <Hero />
        <Footer />
    </div>
  );
}
