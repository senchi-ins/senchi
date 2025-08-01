"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import Image from 'next/image';
import { Brain, AlertTriangle, TrendingDown, Clock, Wifi, Shield, Droplets, Activity, Settings } from "lucide-react";
import { motion } from "framer-motion";


export default function HaloSection() {
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
    hidden: { scale: 0.8, opacity: 0 },
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

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Predictions",
      description: "Advanced machine learning algorithms analyze patterns to predict potential claims before they occur."
    },
    {
      icon: AlertTriangle,
      title: "Early Warning System", 
      description: "Get instant alerts about potential issues in and around your home, from water leaks to incoming severe weather."
    },
    {
      icon: TrendingDown,
      title: "Risk Reduction",
      description: "Proactive maintenance recommendations help prevent costly damage and reduce insurance claims."
    },
    {
      icon: Clock,
      title: "24/7 Monitoring",
      description: "Continuous monitoring of your smart home devices ensures round-the-clock protection."
    },
    {
      icon: Wifi,
      title: "Smart Integration",
      description: "Seamlessly connects with popular smart home platforms and IoT devices."
    },
    {
      icon: Shield,
      title: "Comprehensive Monitoring",
      description: "Combining internal sensors and external data to provide 360 degree monitoring"
    }
  ];

  const sensors = [
    {
      icon: Activity,
      title: "Ultrasonic clamp-on water flow monitor",
      description: "Non-invasive monitoring of water flow rates to detect leaks and unusual usage patterns.",
      image: '/assets/flow_monitor.png'
    },
    {
      icon: Droplets,
      title: "Multi purpose leak detectors",
      description: "Advanced sensor technology that detects water presence and alerts you before damage occurs.",
      image: '/assets/leak_sensor.png'
    },
    {
      icon: Settings,
      title: "Non-intrusive automatic valve control",
      description: "Smart valve control system that can automatically shut off water flow when issues are detected.",
      image: '/assets/valve_control.png'
    }
  ];

  return (
    <section id="halo" className="py-16 sm:py-24 bg-white">
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
            className="inline-flex items-center rounded-full bg-white px-4 py-2 text-sm mb-4"
            variants={scaleIn}
          >
            <Brain className="h-4 w-4 text-senchi-primary mr-2" />
            Senchi Halo Platform
          </motion.div>
          <motion.h2 
            className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4"
            variants={fadeInUp}
          >
            Smart Home Data Platform
          </motion.h2>
          <motion.p 
            className="text-lg text-gray-600"
            variants={fadeInUp}
          >
            Senchi Halo uses cutting-edge AI and IoT integration to predict claims before they happen, 
            saving you money while protecting your home.
          </motion.p>
        </motion.div>

        {/* Features Grid */}
        <motion.div 
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainer}
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={fadeInUp}
              whileHover={{ y: -8, transition: { duration: 0.3 } }}
            >
              <Card className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300 h-full">
                <CardHeader>
                  <motion.div 
                    className="w-12 h-12 bg-senchi-accent-light rounded-lg flex items-center justify-center mb-4"
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <feature.icon className="h-6 w-6 text-senchi-primary" />
                  </motion.div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* How it Works */}
        <motion.div 
          className="bg-gradient-to-r from-senchi-accent-light to-white rounded-2xl p-8 lg:p-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div variants={slideInFromLeft}>
              <motion.h3 
                className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6"
                variants={fadeInUp}
              >
                How Senchi Halo Works
              </motion.h3>
              <motion.div 
                className="space-y-6"
                variants={staggerContainer}
              >
                {[
                  { num: "1", title: "Connect Your Smart Home", desc: "Set up your smart home devices and sensors through our app." },
                  { num: "2", title: "AI Analyzes Data", desc: "Our AI processes real-time data to identify patterns and potential risks." },
                  { num: "3", title: "Prevent Claims", desc: "Receive alerts and recommendations to prevent issues before they become claims." }
                ].map((step, index) => (
                  <motion.div 
                    key={index}
                    className="flex items-start space-x-4"
                    variants={fadeInUp}
                    custom={index}
                  >
                    <motion.div 
                      className="flex-shrink-0 w-8 h-8 bg-senchi-primary text-white rounded-full flex items-center justify-center text-sm font-bold"
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
                className="bg-white rounded-xl p-6 shadow-xl border border-gray-100"
                whileHover={{ boxShadow: "0 20px 40px rgba(0,0,0,0.1)" }}
                transition={{ duration: 0.3 }}
              >
                {/* Dashboard Preview */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-gray-900">Halo Dashboard</h4>
                    <div className="flex items-center space-x-2">
                      <motion.div 
                        className="w-2 h-2 bg-green-500 rounded-full"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                      />
                      <span className="text-sm text-gray-600">Online</span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <motion.div 
                      className="bg-gray-50 rounded-lg p-3"
                      whileHover={{ scale: 1.02 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <div className="text-sm text-gray-600">Risk Score</div>
                      <div className="text-xl font-bold text-green-600">Low</div>
                    </motion.div>
                    <motion.div 
                      className="bg-gray-50 rounded-lg p-3"
                      whileHover={{ scale: 1.02 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <div className="text-sm text-gray-600">Savings</div>
                      <motion.div 
                        className="text-xl font-bold text-senchi-primary"
                        animate={{ opacity: [0.7, 1, 0.7] }}
                        transition={{ repeat: Infinity, duration: 3 }}
                      >
                        $1,247
                      </motion.div>
                    </motion.div>
                  </div>

                  <motion.div 
                    className="bg-green-50 border border-green-200 rounded-lg p-3"
                    initial={{ borderColor: "rgb(187 247 208)" }}
                    animate={{ borderColor: ["rgb(187 247 208)", "rgb(134 239 172)", "rgb(187 247 208)"] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  >
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">All systems protected</span>
                    </div>
                  </motion.div>

                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-900">Recent Alerts</div>
                    {["Increased water usage by dishwasher", "Proper water flow restored", "Outdoor temperature to drop 5 degree in the next week"].map((alert, i) => (
                      <motion.div 
                        key={i}
                        className="text-xs text-gray-600"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + i * 0.1 }}
                      >
                        • {alert}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>

              {/* Floating notification */}
              <motion.div 
                className="absolute -right-4 -top-4 bg-yellow-100 border border-yellow-300 rounded-lg p-3 shadow-lg"
                initial={{ scale: 0, rotate: -10 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ 
                  type: "spring", 
                  stiffness: 200,
                  delay: 0.8
                }}
                whileHover={{ rotate: 5, scale: 1.05 }}
              >
                <div className="flex items-center space-x-2">
                  <motion.div
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ repeat: Infinity, duration: 2, delay: 1 }}
                  >
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  </motion.div>
                  <span className="text-xs font-medium text-yellow-800">Prediction Alert</span>
                </div>
              </motion.div>
            </motion.div>
          </div>

          <div className="text-center mt-12">

          </div>
        </motion.div>

        {/* Smart AI Sensors Section */}
        <motion.div 
          className="mt-16"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.div 
            className="text-center max-w-3xl mx-auto mb-12"
            variants={fadeInUp}
          >
            <motion.h3 
              className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4"
              variants={fadeInUp}
            >
              Smart AI Powered Sensors Provided by Senchi
            </motion.h3>
            <motion.p 
              className="text-lg text-gray-600"
              variants={fadeInUp}
            >
              Our comprehensive sensor suite works together to provide complete home monitoring and protection.
            </motion.p>
          </motion.div>

          <motion.div 
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
            variants={staggerContainer}
          >
            {sensors.map((sensor, index) => (
              <motion.div
                key={index}
                variants={scaleIn}
                whileHover={{ y: -10, transition: { duration: 0.3 } }}
              >
                <Card className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300 h-full">
                  <CardHeader className="text-center">
                    <motion.div 
                      className="w-32 h-32 mx-auto mb-4 flex items-center justify-center"
                      whileHover={{ scale: 1.05 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      {sensor.image ? (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.2 + index * 0.1 }}
                        >
                          <Image 
                            src={sensor.image} 
                            alt={sensor.title}
                            width={128}
                            height={128}
                          />
                        </motion.div>
                      ) : (
                        <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
                          <div className="text-center">
                            <sensor.icon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                            <span className="text-sm text-gray-500">Coming Soon</span>
                          </div>
                        </div>
                      )}
                    </motion.div>
                    <CardTitle className="text-xl">{sensor.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-600 text-center">
                      {sensor.description}
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