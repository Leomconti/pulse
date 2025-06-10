import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, Zap } from "lucide-react"

const plans = [
  {
    name: "Starter",
    price: "$299",
    period: "/month",
    description: "Perfect for small clinics and practices",
    features: [
      "Monitor up to 25 processes",
      "Basic AI alerts",
      "Email notifications",
      "Standard support",
      "HIPAA compliant",
    ],
    popular: false,
  },
  {
    name: "Professional",
    price: "$799",
    period: "/month",
    description: "Ideal for medium-sized hospitals",
    features: [
      "Monitor up to 75 processes",
      "Advanced AI monitoring",
      "Omnichannel notifications",
      "Priority support",
      "Custom integrations",
      "Advanced analytics",
    ],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large hospital networks",
    features: [
      "Unlimited process monitoring",
      "Custom AI models",
      "White-label solution",
      "Dedicated support team",
      "SLA guarantees",
      "Advanced security features",
    ],
    popular: false,
  },
]

export function PricingSection() {
  return (
    <section id="pricing" className="py-20 lg:py-32 bg-white/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Simple, Transparent{" "}
            <span className="bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">Pricing</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Choose the plan that fits your healthcare facility's needs. All plans include our core AI monitoring
            features.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <Card
              key={index}
              className={`relative group hover:shadow-xl transition-all duration-300 ${
                plan.popular
                  ? "border-2 border-cyan-200 bg-gradient-to-br from-cyan-50/50 to-white scale-105"
                  : "border-0 bg-white/80 hover:bg-white"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-cyan-500 to-red-500 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center">
                    <Zap className="w-4 h-4 mr-1" />
                    Most Popular
                  </div>
                </div>
              )}

              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold text-slate-900 mb-2">{plan.name}</CardTitle>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
                  <span className="text-slate-600">{plan.period}</span>
                </div>
                <p className="text-slate-600">{plan.description}</p>
              </CardHeader>

              <CardContent className="pt-0">
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <Check className="w-5 h-5 text-cyan-500 mr-3 flex-shrink-0" />
                      <span className="text-slate-600">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  className={`w-full ${
                    plan.popular
                      ? "bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 text-white"
                      : "bg-slate-900 hover:bg-slate-800 text-white"
                  }`}
                  size="lg"
                >
                  {plan.name === "Enterprise" ? "Contact Sales" : "Start Free Trial"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-slate-600 mb-4">All plans include a 14-day free trial. No credit card required.</p>
          <p className="text-sm text-slate-500">
            Need a custom solution?{" "}
            <a href="#contact" className="text-cyan-600 hover:underline">
              Contact our sales team
            </a>
          </p>
        </div>
      </div>
    </section>
  )
}
