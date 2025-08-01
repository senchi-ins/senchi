"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Heart, Users, Globe } from "lucide-react";
import { motion } from "framer-motion";

export default function DoGoodSection() {
  // Animation Variants
  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.6 }
    }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const scaleIn = {
    hidden: { scale: 0.9, opacity: 0 },
    visible: { 
      scale: 1, 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  const slideInFromLeft = {
    hidden: { x: -60, opacity: 0 },
    visible: { 
      x: 0, 
      opacity: 1,
      transition: { duration: 0.7 }
    }
  };

  const slideInFromRight = {
    hidden: { x: 60, opacity: 0 },
    visible: { 
      x: 0, 
      opacity: 1,
      transition: { duration: 0.7 }
    }
  };

  const heartBeat = {
    scale: [1, 1.1, 1],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      repeatType: "reverse" as const
    }
  };
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
        <motion.div 
          className="text-center max-w-3xl mx-auto mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <motion.div 
            className="inline-flex items-center rounded-full bg-pink-100 px-4 py-2 text-sm mb-4"
            variants={scaleIn}
          >
            <motion.div animate={heartBeat}>
              <Heart className="h-4 w-4 text-pink-600 mr-2" />
            </motion.div>
            Senchi Do Good Program
          </motion.div>
          <motion.h2 
            className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4"
            variants={fadeInUp}
          >
            Protection That Gives Back
          </motion.h2>
          <motion.p 
            className="text-lg text-gray-600"
            variants={fadeInUp}
          >
            Every dollar we save you does double duty: we take a flat fee and donate the rest to charitable causes making a real difference.
          </motion.p>
        </motion.div>

        {/* How It Works */}
        <motion.div 
          className="bg-white rounded-2xl p-8 lg:p-12 shadow-xl border border-gray-100 mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={scaleIn}
        >
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div variants={slideInFromLeft}>
              <motion.h3 
                className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6"
                variants={fadeInUp}
              >
                How Do Good Works
              </motion.h3>
              <motion.div 
                className="space-y-6"
                variants={staggerContainer}
              >
                {[
                  { num: "1", title: "You Get Protection", desc: "Purchase your smart home protection policy" },
                  { num: "2", title: "We Take Our Fee", desc: "Senchi takes only a small, flat fee to cover our operations and ensure sustainability." },
                  { num: "3", title: "Excess Goes to Charity", desc: "All remaining profits are donated to vetted charitable organizations making real impact." }
                ].map((step, index) => (
                  <motion.div 
                    key={index}
                    className="flex items-start space-x-4"
                    variants={fadeInUp}
                  >
                    <motion.div 
                      className="flex-shrink-0 w-8 h-8 bg-pink-500 text-white rounded-full flex items-center justify-center text-sm font-bold"
                      whileHover={{ scale: 1.1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      {step.num}
                    </motion.div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">{step.title}</h4>
                      <p className="text-gray-600">{step.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>

            <motion.div 
              className="relative"
              variants={slideInFromRight}
            >
              <motion.div 
                className="bg-gradient-to-br from-pink-50 to-white rounded-xl p-6 border border-pink-100"
                whileHover={{ borderColor: "rgb(251 207 232)" }}
                transition={{ duration: 0.3 }}
              >
                <div className="text-center space-y-4">
                  <motion.div 
                    className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto"
                    animate={heartBeat}
                  >
                    <Heart className="h-8 w-8 text-pink-600" />
                  </motion.div>
                  <h4 className="font-semibold text-gray-900">Your Monthly Impact</h4>
                  <motion.div 
                    className="space-y-2"
                    initial="hidden"
                    animate="visible"
                    variants={staggerContainer}
                  >
                    {[
                      { label: "Subscription", amount: "$20", bgColor: "bg-white", borderColor: "border" },
                      { label: "Senchi Fee", amount: "$10", bgColor: "bg-white", borderColor: "border" },
                      { label: "Donated", amount: "$10", bgColor: "bg-pink-50", borderColor: "border border-pink-200", textColor: "text-pink-700" }
                    ].map((item, index) => (
                      <motion.div 
                        key={index}
                        className={`${item.bgColor} rounded-lg p-3 ${item.borderColor}`}
                        variants={fadeInUp}
                        whileHover={{ scale: 1.02 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <div className="flex justify-between text-sm">
                          <span className={item.textColor || "text-gray-600"}>{item.label}</span>
                          <motion.span 
                            className={`font-semibold ${item.textColor || ""}`}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.8 + index * 0.2 }}
                          >
                            {item.amount}
                          </motion.span>
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                  <motion.p 
                    className="text-xs text-gray-600"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.5 }}
                  >
                    *Numbers are illustrative
                  </motion.p>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>



        {/* Focus Areas */}
        <motion.div 
          className="max-w-4xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.h3 
            className="text-2xl sm:text-3xl font-bold text-gray-900 text-center mb-12"
            variants={fadeInUp}
          >
            Our Focus Areas
          </motion.h3>
          <motion.div 
            className="grid md:grid-cols-3 gap-8 mb-12"
            variants={staggerContainer}
          >
            {focusAreas.map((area, index) => (
              <motion.div
                key={index}
                variants={scaleIn}
                whileHover={{ y: -8, transition: { duration: 0.3 } }}
              >
                <Card className="border-gray-100 hover:border-pink-200 hover:shadow-lg transition-all duration-300 h-full">
                  <CardHeader>
                    <motion.div 
                      className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mb-4"
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.6 }}
                    >
                      <area.icon className="h-6 w-6 text-pink-600" />
                    </motion.div>
                    <CardTitle className="text-xl">{area.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-600">
                      {area.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>


        </motion.div>
      </div>
    </section>
  );
}