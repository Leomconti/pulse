import { Button } from "@/components/ui/button"
import { ArrowRight, Play } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative py-20 lg:py-32 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-50/50 via-transparent to-red-50/30" />
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-200/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-red-200/20 rounded-full blur-3xl" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-cyan-100 to-red-100 text-sm font-medium text-slate-700 mb-8">
            <span className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse" />
            Fastest Healthcare AI Integration on the Market
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6 leading-tight">
            Monitor Healthcare Processes.{" "}
            <span className="bg-gradient-to-r from-cyan-600 via-cyan-500 to-red-500 bg-clip-text text-transparent">
              Save Lives.
            </span>
          </h1>

          {/* Description */}
          <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Connect our AI agents to monitor 100+ healthcare processes with the fastest integration available. Get
            omnichannel notifications and help save lives with intelligent process monitoring.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Button
              size="lg"
              className="bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 px-8 py-3"
            >
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button size="lg" variant="outline" className="border-cyan-200 text-slate-700 hover:bg-cyan-50 px-8 py-3">
              <Play className="mr-2 w-5 h-5" />
              Watch Demo
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">
                100+
              </div>
              <div className="text-slate-600 text-sm">Monitored Processes</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">
                {"<5min"}
              </div>
              <div className="text-slate-600 text-sm">Integration Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">
                24/7
              </div>
              <div className="text-slate-600 text-sm">AI Monitoring</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
