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
        "Set up in <5 minutes",
        "Non-intrusive sensor installation",
      ]
    },
    {
      icon: Building,
      title: "For Property Managers",
      description: "Predictive monitoring to give you peace of mind on your portfolio.",
      image: '/assets/abnb_condo.png',
      features: [
        "Multi-property smart monitoring",
        "Emergency event alerts across portfolio",
        "Tenant support tools",
      ]
    },
    {
      icon: Building,
      title: "For Insurers",
      description: "Improve loss ratios and reduce claims through non-intrusive monitoring.",
      image: '/assets/insurer.png',
      features: [
        "Decrease loss ratio across portfolio",
        "Reduce claims",
        "Improve customer satisfaction",
      ]
    }
  ];

  return (
    <section id="plans" className="py-16 sm:py-24 bg-gradient-to-b from-white to-senchi-accent-light/20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-4xl mx-auto mb-20">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-6 leading-tight">
            External Protective Plans for Residences
          </h2>
          <p className="text-lg text-gray-600 leading-relaxed max-w-3xl mx-auto">
            Professional external protection for homeowners and property managers. These are not insurance products, but proactive plans enhanced with smart technology for unprecedented claim prevention and peace of mind.
          </p>
        </div>

        {/* Plan Options */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {planOptions.map((option, index) => (
            <Card key={index} className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300 h-full flex flex-col">
              <CardHeader className="text-center pb-6">
                <div className="h-28 mx-auto mb-6 flex justify-center">
                  <div className={`flex items-end justify-center ${
                    index === 1 ? 'w-20 h-20' : 'w-28 h-28'
                  }`}>
                    <Image
                      src={option.image}
                      alt={`${option.title} illustration`}
                      width={300}
                      height={300}
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 mb-2">
                  {option.title}
                </CardTitle>
                <CardDescription className="text-gray-600 text-sm leading-relaxed">
                  {option.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <ul className="space-y-3 mb-8 flex-1">
                  {option.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-senchi-primary rounded-full flex-shrink-0 mt-2"></div>
                      <span className="text-sm text-gray-600 leading-relaxed">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  asChild
                  className="w-full bg-senchi-primary hover:bg-senchi-primary/90 text-white font-medium"
                  size="lg"
                >
                  <a href="mailto:mike@senchi.ca?subject=Interest in Senchi HomeGuard">Get {option.title}</a>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Call to Action */}
        <div className="text-center mt-20">
          <p className="text-gray-600 text-lg font-medium">
            All plans include Senchi HomeGuard smart monitoring.
          </p>
        </div>
      </div>
    </section>
  );
}