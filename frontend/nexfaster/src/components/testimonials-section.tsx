import { Card, CardContent } from "@/components/ui/card"
import { Star } from "lucide-react"

const testimonials = [
  {
    name: "Dr. Sarah Chen",
    role: "Chief Medical Officer",
    hospital: "Metropolitan General Hospital",
    content:
      "Pulse has revolutionized how we monitor patient care. The AI alerts have helped us prevent critical situations and save lives. The integration was seamless.",
    rating: 5,
    avatar: "/placeholder.svg?height=60&width=60",
  },
  {
    name: "Michael Rodriguez",
    role: "IT Director",
    hospital: "St. Mary's Medical Center",
    content:
      "The fastest integration I've ever seen. We had Pulse monitoring our entire ICU within minutes. The omnichannel notifications keep our team connected.",
    rating: 5,
    avatar: "/placeholder.svg?height=60&width=60",
  },
  {
    name: "Dr. Emily Watson",
    role: "Emergency Department Head",
    hospital: "City General Hospital",
    content:
      "Pulse's AI monitoring has become indispensable. It catches things we might miss during busy shifts and ensures no patient falls through the cracks.",
    rating: 5,
    avatar: "/placeholder.svg?height=60&width=60",
  },
]

export function TestimonialsSection() {
  return (
    <section id="testimonials" className="py-20 lg:py-32 bg-gradient-to-br from-slate-50 to-cyan-50/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
            Trusted by Healthcare{" "}
            <span className="bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">
              Professionals
            </span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            See how hospitals worldwide are using Pulse to improve patient outcomes and streamline their operations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {testimonials.map((testimonial, index) => (
            <Card
              key={index}
              className="group hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm hover:bg-white"
            >
              <CardContent className="p-8">
                {/* Rating */}
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>

                {/* Content */}
                <p className="text-slate-600 mb-6 leading-relaxed">"{testimonial.content}"</p>

                {/* Author */}
                <div className="flex items-center">
                  <img
                    src={testimonial.avatar || "/placeholder.svg"}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full mr-4"
                  />
                  <div>
                    <div className="font-semibold text-slate-900">{testimonial.name}</div>
                    <div className="text-sm text-slate-600">{testimonial.role}</div>
                    <div className="text-sm text-cyan-600">{testimonial.hospital}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
