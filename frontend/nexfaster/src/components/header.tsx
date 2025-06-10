"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Menu, X, Activity } from "lucide-react"

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-cyan-100/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-red-500 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-red-500 bg-clip-text text-transparent">
              Pulse
            </span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
              Features
            </a>
            <a href="#testimonials" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
              Testimonials
            </a>
            <a href="#pricing" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
              Pricing
            </a>
            <a href="#contact" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
              Contact
            </a>
          </nav>

          {/* CTA Button */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" className="text-slate-600 hover:text-cyan-600">
              Sign In
            </Button>
            <Button className="bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
              Start Free Trial
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button className="md:hidden p-2" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-cyan-100/50">
            <nav className="flex flex-col space-y-4">
              <a href="#features" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
                Features
              </a>
              <a href="#testimonials" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
                Testimonials
              </a>
              <a href="#pricing" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
                Pricing
              </a>
              <a href="#contact" className="text-slate-600 hover:text-cyan-600 transition-colors duration-200">
                Contact
              </a>
              <div className="flex flex-col space-y-2 pt-4">
                <Button variant="ghost" className="text-slate-600 hover:text-cyan-600 justify-start">
                  Sign In
                </Button>
                <Button className="bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700 text-white justify-start">
                  Start Free Trial
                </Button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
