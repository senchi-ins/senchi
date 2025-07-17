import { Shield, Award, Lock, Users, Star } from "lucide-react";
import { Card, CardContent } from "./ui/card";

export function TrustSection() {
  const certifications = [
    {
      icon: Shield,
      title: "A+ Rated",
      subtitle: "AM Best Rating",
      description: "Superior financial strength"
    },
    {
      icon: Award,
      title: "Licensed",
      subtitle: "All 50 States",
      description: "Fully regulated insurance carrier"
    },
    {
      icon: Lock,
      title: "SOC 2 Certified",
      subtitle: "Data Security",
      description: "Enterprise-grade security"
    },
    {
      icon: Users,
      title: "10,000+",
      subtitle: "Satisfied Customers",
      description: "Trusted by homeowners nationwide"
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      location: "San Francisco, CA",
      rating: 5,
      text: "Senchi predicted a water leak in our basement before it caused any damage. Saved us thousands and our deductible stayed low.",
      savings: "$8,500"
    },
    {
      name: "Mike Rodriguez",
      location: "Austin, TX", 
      rating: 5,
      text: "The Do Good program means our insurance payments help local charities. It feels great knowing we're making a difference.",
      savings: "$2,100"
    },
    {
      name: "Jennifer Walsh",
      location: "Denver, CO",
      rating: 5,
      text: "Their AI caught an electrical issue before it became a fire hazard. The proactive approach gives us real peace of mind.",
      savings: "$12,000"
    }
  ];

  return (
    <section className="py-16 sm:py-24 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Trust Indicators */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Trusted Insurance Partner
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            As a fully licensed insurance carrier, we're committed to protecting your home 
            with the highest standards of security, compliance, and financial stability.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {certifications.map((cert, index) => (
            <Card key={index} className="text-center border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300">
              <CardContent className="pt-6">
                <div className="w-16 h-16 bg-senchi-accent-light rounded-full flex items-center justify-center mx-auto mb-4">
                  <cert.icon className="h-8 w-8 text-senchi-primary" />
                </div>
                <h3 className="font-bold text-xl text-gray-900 mb-1">{cert.title}</h3>
                <p className="font-semibold text-senchi-primary mb-2">{cert.subtitle}</p>
                <p className="text-sm text-gray-600">{cert.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Customer Testimonials */}
        <div className="bg-gradient-to-r from-senchi-accent-light/30 to-white rounded-2xl p-8 lg:p-12">
          <div className="text-center mb-12">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              Real Stories, Real Savings
            </h3>
            <p className="text-gray-600">
              See how Senchi has helped homeowners prevent claims and save money
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="bg-white border-gray-100">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <blockquote className="text-gray-700 mb-4">
                    "{testimonial.text}"
                  </blockquote>
                  <div className="border-t pt-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold text-gray-900">{testimonial.name}</div>
                        <div className="text-sm text-gray-600">{testimonial.location}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">Potential savings</div>
                        <div className="font-bold text-green-600">{testimonial.savings}</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>


      </div>
    </section>
  );
}