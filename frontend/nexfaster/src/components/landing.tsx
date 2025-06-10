import { Header } from '@/components/header'
import { HeroSection } from '@/components/hero-section'
import { FeaturesSection } from '@/components/features-section'
import { TestimonialsSection } from '@/components/testimonials-section'
import { PricingSection } from '@/components/pricing-section'
import { CtaSection } from '@/components/cta-section'
import { Footer } from '@/components/footer'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/20">
      <Header />
      <main>
        <HeroSection />
        <FeaturesSection />
        <TestimonialsSection />
        <PricingSection />
        <CtaSection />
      </main>
      <Footer />
    </div>
  )
}
