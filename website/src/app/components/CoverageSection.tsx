"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Home, Building } from "lucide-react";
import Image from 'next/image';
import { motion } from "framer-motion";

export default function CoverageSection() {
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
        staggerChildren: 0.2,
        delayChildren: 0.1
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

  const listItemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.4 }
    }
  };
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
        <motion.div 
          className="text-center max-w-3xl mx-auto mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <motion.h2 
            className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4"
            variants={fadeInUp}
          >
            External Protective Plans for Residences
          </motion.h2>
          <motion.p 
            className="text-lg text-gray-600"
            variants={fadeInUp}
          >
            Professional external protection for homeowners and property managers. These are not insurance products, but proactive plans enhanced with smart technology for unprecedented claim prevention and peace of mind.
          </motion.p>
        </motion.div>

        {/* Plan Options */}
        <motion.div 
          className="grid lg:grid-cols-2 gap-8 max-w-4xl mx-auto"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          {planOptions.map((option, index) => (
            <motion.div
              key={index}
              variants={scaleIn}
              whileHover={{ y: -8, transition: { duration: 0.3 } }}
            >
              <Card className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300 h-full">
                <CardHeader className="text-center">
                  <motion.div 
                    className="w-32 h-32 mx-auto mb-4 flex items-center justify-center"
                    whileHover={{ scale: 1.05 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                    >
                      <Image
                        src={option.image}
                        alt={`${option.title} insurance illustration`}
                        width={128}
                        height={128}
                        className="w-50 h-50 object-contain mx-auto mb-4"
                      />
                    </motion.div>
                  </motion.div>
                  <CardTitle className="text-2xl text-gray-900">
                    {option.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <CardDescription className="text-gray-600 text-center">
                    {option.description}
                  </CardDescription>
                  <motion.ul 
                    className="space-y-2 flex flex-col items-center w-full mx-auto max-w-xs ml-8"
                    variants={staggerContainer}
                  >
                    {option.features.map((feature, featureIndex) => (
                      <motion.li 
                        key={featureIndex} 
                        className="flex items-center space-x-2 w-full justify-start"
                        variants={listItemVariants}
                      >
                        <motion.div 
                          className="w-1.5 h-1.5 bg-senchi-primary rounded-full flex-shrink-0"
                          animate={{ scale: [1, 1.5, 1] }}
                          transition={{ repeat: Infinity, duration: 2, delay: featureIndex * 0.2 }}
                        />
                        <span className="text-sm text-gray-600 text-left">{feature}</span>
                      </motion.li>
                    ))}
                  </motion.ul>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button 
                      asChild
                      className="w-full bg-senchi-primary hover:bg-senchi-primary/90 mt-6"
                      size="lg"
                    >
                      <a href="#waitlist-email">Get {option.title}</a>
                    </Button>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Call to Action */}
        <motion.div 
          className="text-center mt-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeInUp}
        >
          <motion.p 
            className="text-gray-600 mb-6"
            variants={fadeInUp}
          >
            All plans include Senchi Halo smart monitoring and Do Good charitable giving program
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}