import { Activity, Mail, Phone, MapPin } from "lucide-react"

export function Footer() {
  return (
    <footer id="contact" className="bg-slate-900 text-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-6">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-red-500 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-red-400 bg-clip-text text-transparent">
                Pulse
              </span>
            </div>
            <p className="text-slate-300 mb-6 max-w-md">
              Empowering healthcare professionals with AI-powered process monitoring to save lives and improve patient
              outcomes.
            </p>
            <div className="space-y-3">
              <div className="flex items-center text-slate-300">
                <Mail className="w-5 h-5 mr-3 text-cyan-400" />
                contact@pulse-health.com
              </div>
              <div className="flex items-center text-slate-300">
                <Phone className="w-5 h-5 mr-3 text-cyan-400" />
                +1 (555) 123-4567
              </div>
              <div className="flex items-center text-slate-300">
                <MapPin className="w-5 h-5 mr-3 text-cyan-400" />
                San Francisco, CA
              </div>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Product</h3>
            <ul className="space-y-3">
              <li>
                <a href="#features" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  Features
                </a>
              </li>
              <li>
                <a href="#pricing" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  Pricing
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  Integrations
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  API Docs
                </a>
              </li>
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-lg font-semibold mb-6">Company</h3>
            <ul className="space-y-3">
              <li>
                <a href="#" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  About
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  Careers
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="text-slate-300 hover:text-cyan-400 transition-colors">
                  Press
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between">
          <p className="text-slate-400 text-sm">© 2024 Pulse. All rights reserved.</p>
          <div className="flex items-center space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">
              Privacy Policy
            </a>
            <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">
              Terms of Service
            </a>
            <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">
              HIPAA Compliance
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
