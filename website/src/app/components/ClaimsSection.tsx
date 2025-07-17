import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Phone, Camera, FileText, DollarSign, Clock, CheckCircle, AlertCircle, Smartphone } from "lucide-react";

export default function ClaimsSection() {
  const claimsProcess = [
    {
      step: 1,
      icon: AlertCircle,
      title: "Incident Detection",
      description: "Our AI often detects issues before they become claims, but if damage occurs, report it immediately.",
      timeframe: "Immediate"
    },
    {
      step: 2,
      icon: Smartphone,
      title: "Easy Reporting",
      description: "File your claim through our mobile app with photos and details. Our AI assists with documentation.",
      timeframe: "2-5 minutes"
    },
    {
      step: 3,
      icon: Camera,
      title: "Smart Assessment",
      description: "Our adjusters use Halo data for faster, more accurate claim assessment. Many claims processed remotely.",
      timeframe: "24-48 hours"
    },
    {
      step: 4,
      icon: FileText,
      title: "Claim Approval",
      description: "Quick decision making powered by comprehensive data and transparent processes.",
      timeframe: "3-5 days"
    },
    {
      step: 5,
      icon: DollarSign,
      title: "Fast Payment",
      description: "Direct deposit or check payment once approved. No unnecessary delays.",
      timeframe: "1-2 days"
    }
  ];

  const claimsStats = [
    {
      icon: Clock,
      value: "2.3 days",
      label: "Average Claim Resolution",
      comparison: "vs 7-14 days industry average"
    },
    {
      icon: CheckCircle,
      value: "97%",
      label: "Claims Approved",
      comparison: "Industry leading approval rate"
    },
    {
      icon: DollarSign,
      value: "$850M",
      label: "Claims Paid Out",
      comparison: "To satisfied customers nationwide"
    },
    {
      icon: Camera,
      value: "85%",
      label: "Remote Assessments",
      comparison: "Faster processing, less hassle"
    }
  ];

  return (
    <section id="claims" className="py-16 sm:py-24 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Transparent Claims Process
          </h2>
          <p className="text-lg text-gray-600">
            When the unexpected happens, our streamlined claims process and smart technology 
            ensure you get back on your feet quickly with minimal stress.
          </p>
        </div>

        {/* Claims Stats */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {claimsStats.map((stat, index) => (
            <Card key={index} className="text-center border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300">
              <CardHeader className="pb-2">
                <div className="w-12 h-12 bg-senchi-accent-light rounded-lg flex items-center justify-center mx-auto mb-2">
                  <stat.icon className="h-6 w-6 text-senchi-primary" />
                </div>
                <CardTitle className="text-2xl text-senchi-primary">{stat.value}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="font-semibold text-gray-900 mb-1">
                  {stat.label}
                </CardDescription>
                <CardDescription className="text-gray-600 text-sm">
                  {stat.comparison}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Claims Process */}
        <div className="bg-gradient-to-r from-senchi-accent-light/30 to-white rounded-2xl p-8 lg:p-12">
          <div className="text-center mb-12">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              How Claims Work
            </h3>
            <p className="text-gray-600">
              Our technology-enhanced process makes filing and resolving claims faster and more transparent
            </p>
          </div>

          <div className="space-y-8">
            {claimsProcess.map((step, index) => (
              <div key={index} className="flex items-start space-x-6">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-senchi-primary text-white rounded-full flex items-center justify-center text-lg font-bold">
                    {step.step}
                  </div>
                </div>
                <div className="flex-1">
                  <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <step.icon className="h-6 w-6 text-senchi-primary" />
                        <h4 className="font-semibold text-gray-900">{step.title}</h4>
                      </div>
                      <span className="text-sm font-medium text-senchi-primary bg-senchi-accent-light px-3 py-1 rounded-full">
                        {step.timeframe}
                      </span>
                    </div>
                    <p className="text-gray-600">{step.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <AlertCircle className="h-5 w-5 text-blue-600" />
                <h4 className="font-semibold text-blue-900">Need to File a Claim?</h4>
              </div>
              <p className="text-blue-800 text-sm">
                Call our 24/7 claims hotline or use our mobile app to get started immediately
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-senchi-primary hover:bg-senchi-primary/90">
                <Phone className="mr-2 h-4 w-4" />
                Call 1-800-SENCHI-1
              </Button>
              <Button variant="outline" size="lg" className="border-senchi-primary text-senchi-primary hover:bg-senchi-primary hover:text-white">
                Download App
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}