import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Heart, Users, Globe } from "lucide-react";

export function DoGoodSection() {
  const focusAreas = [
    {
      icon: Users,
      title: "Disaster Relief",
      description: "Supporting communities affected by natural disasters and helping with recovery efforts."
    },
    {
      icon: Heart,
      title: "Housing Security",
      description: "Helping families secure safe, affordable housing and preventing homelessness."
    },
    {
      icon: Globe,
      title: "Environmental Protection",
      description: "Supporting initiatives that protect our environment and promote sustainable living."
    }
  ];

  return (
    <section id="do-good" className="py-16 sm:py-24 bg-gradient-to-b from-senchi-accent-light/30 to-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center rounded-full bg-pink-100 px-4 py-2 text-sm mb-4">
            <Heart className="h-4 w-4 text-pink-600 mr-2" />
            Senchi Do Good Program
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Protection That Gives Back
          </h2>
          <p className="text-lg text-gray-600">
            Every dollar we save you does double duty: we take a flat fee and donate the rest to charitable causes making a real difference.
          </p>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-2xl p-8 lg:p-12 shadow-xl border border-gray-100 mb-16">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6">
                How Do Good Works
              </h3>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-pink-500 text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">You Get Protection</h4>
                    <p className="text-gray-600">Purchase your smart home protection policy</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-pink-500 text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">We Take Our Fee</h4>
                    <p className="text-gray-600">Senchi takes only a small, flat fee to cover our operations and ensure sustainability.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-pink-500 text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Excess Goes to Charity</h4>
                    <p className="text-gray-600">All remaining profits are donated to vetted charitable organizations making real impact.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="bg-gradient-to-br from-pink-50 to-white rounded-xl p-6 border border-pink-100">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto">
                    <Heart className="h-8 w-8 text-pink-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900">Your Monthly Impact</h4>
                  <div className="space-y-2">
                    <div className="bg-white rounded-lg p-3 border">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Subscription</span>
                        <span className="font-semibold">$20</span>
                      </div>
                    </div>
                    <div className="bg-white rounded-lg p-3 border">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Senchi Fee</span>
                        <span className="font-semibold">$10</span>
                      </div>
                    </div>
                    <div className="bg-pink-50 rounded-lg p-3 border border-pink-200">
                      <div className="flex justify-between text-sm">
                        <span className="text-pink-700">Donated</span>
                        <span className="font-semibold text-pink-700">$10</span>
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600">*Numbers are illustrative</p>
                </div>
              </div>
            </div>
          </div>
        </div>



        {/* Focus Areas */}
        <div className="max-w-4xl mx-auto">
          <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 text-center mb-12">
            Our Focus Areas
          </h3>
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {focusAreas.map((area, index) => (
              <Card key={index} className="border-gray-100 hover:border-pink-200 hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mb-4">
                    <area.icon className="h-6 w-6 text-pink-600" />
                  </div>
                  <CardTitle className="text-xl">{area.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {area.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>


        </div>
      </div>
    </section>
  );
}