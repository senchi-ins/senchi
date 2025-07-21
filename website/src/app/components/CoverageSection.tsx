import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Home, Building } from "lucide-react";
import Image from 'next/image';

export default function CoverageSection() {
  const planOptions = [
    {
      icon: Home,
      title: "For Homeowners",
      description: "Predictive monitoring to protect your most valuable asset.",
      image: '/assets/abnb_home.png',
      features: [
        "24/7 leak monitoring and alerts",
        "Smart water shutoff",
        "Smart leak detection",
        "Smart water usage tracking",
      ]
    },
    {
      icon: Building,
      title: "For Property Managers",
      description: "Predictive monitoring to give you peace of mind on your portfolio.",
      image: '/assets/abnb_condo.png',
      features: [
        "Multi-property smart monitoring",
        "Consolidated view of all properties",
        "Emergency event alerts",
        "Tenant support tools",
      ]
    }
  ];

  return (
    <section id="plans" className="py-16 sm:py-24 bg-gradient-to-b from-white to-senchi-accent-light/20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            External Protective Plans for Residences
          </h2>
          <p className="text-lg text-gray-600">
            Professional external protection for homeowners and property managers. These are not insurance products, but proactive plans enhanced with smart technology for unprecedented claim prevention and peace of mind.
          </p>
        </div>

        {/* Plan Options */}
        <div className="grid lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {planOptions.map((option, index) => (
            <Card key={index} className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300">
              <CardHeader className="text-center">
                <div className="w-32 h-32 mx-auto mb-4 flex items-center justify-center">
                  <Image
                    src={option.image}
                    alt={`${option.title} insurance illustration`}
                    width={128}
                    height={128}
                    className="w-50 h-50 object-contain mx-auto mb-4"
                  />
                </div>
                <CardTitle className="text-2xl text-gray-900">
                  {option.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <CardDescription className="text-gray-600 text-center">
                  {option.description}
                </CardDescription>
                <ul className="space-y-2 flex flex-col items-center w-full mx-auto max-w-xs ml-8">
                  {option.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-2 w-full justify-start">
                      <div className="w-1.5 h-1.5 bg-senchi-primary rounded-full flex-shrink-0"></div>
                      <span className="text-sm text-gray-600 text-left">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  asChild
                  className="w-full bg-senchi-primary hover:bg-senchi-primary/90 mt-6"
                  size="lg"
                >
                  <a href="#waitlist-email">Get {option.title}</a>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <p className="text-gray-600 mb-6">
            All plans include Senchi Halo smart monitoring and Do Good charitable giving program
          </p>
        </div>
      </div>
    </section>
  );
}