import { Button } from "@/components/ui/button"
import { ArrowRight, Shield, Clock, Users } from "lucide-react"

export function CtaSection() {
  return (
    <section className="py-20 lg:py-32 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-900/20 to-red-900/20" />
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-red-500/10 rounded-full blur-3xl" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6">
            Ready to Start{" "}
            <span className="bg-gradient-to-r from-cyan-400 to-red-400 bg-clip-text text-transparent">
              Saving Lives?
            </span>
          </h2>

          <p className="text-xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            Join hundreds of healthcare facilities already using Pulse to monitor critical processes and improve patient
            outcomes. Start your free trial today.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Button
              size="lg"
              className="bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3"
            >
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white px-8 py-3"
            >
              Schedule Demo
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500/20 to-cyan-600/20 rounded-xl flex items-center justify-center mb-4">
                <Clock className="w-6 h-6 text-cyan-400" />
              </div>
              <div className="text-white font-semibold mb-1">5-Minute Setup</div>
              <div className="text-slate-400 text-sm">Get started instantly</div>
            </div>
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500/20 to-red-500/20 rounded-xl flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-cyan-400" />
              </div>
              <div className="text-white font-semibold mb-1">HIPAA Compliant</div>
              <div className="text-slate-400 text-sm">Enterprise security</div>
            </div>
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-gradient-to-r from-red-500/20 to-red-600/20 rounded-xl flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-red-400" />
              </div>
              <div className="text-white font-semibold mb-1">24/7 Support</div>
              <div className="text-slate-400 text-sm">Always here to help</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
