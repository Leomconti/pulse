import { Card, CardContent } from "@/components/ui/card"
import { Brain, Zap, Bell, Shield } from "lucide-react"

const features = [
  {
    icon: Brain,
    title: "AI-Powered Monitoring",
    description:
      "Advanced AI agents continuously monitor healthcare processes, detecting anomalies and potential issues before they become critical.",
    gradient: "from-cyan-500 to-cyan-600",
  },
  {
    icon: Zap,
    title: "Fastest Integration",
    description:
      "Connect to any healthcare system in under 5 minutes. Our platform integrates with 100+ processes seamlessly.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Bell,
    title: "Omnichannel Notifications",
    description: "Receive alerts through SMS, email, Slack, Teams, or any communication channel your team prefers.",
    gradient: "from-cyan-500 to-red-400",
  },
  {
    icon: Shield,
    title: "HIPAA Compliant",
    description:
      "Enterprise-grade security with full HIPAA compliance. Your patient data is protected with military-grade encryption.",
    gradient: "from-red-400 to-red-500",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 lg:py-32 bg-white/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Everything You Need to{" "}
            <span className="bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">Save Lives</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Our comprehensive platform provides all the tools healthcare professionals need to monitor critical
            processes and respond instantly to emergencies.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group hover:shadow-xl transition-all duration-300 border-0 bg-gradient-to-br from-white to-cyan-50/30 hover:from-cyan-50/50 hover:to-white"
            >
              <CardContent className="p-8">
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-200`}
                >
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-4">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
