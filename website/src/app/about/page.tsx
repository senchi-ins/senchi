import { Header } from '@/app/components/Header';
import { Footer } from '@/app/components/Footer';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">About Senchi</h1>
        <p className="text-lg text-gray-600">
          We're building the future of home protection through AI-powered prediction and charitable giving.
        </p>
      </main>
      <Footer />
    </div>
  );
} 