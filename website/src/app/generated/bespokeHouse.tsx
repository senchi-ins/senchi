"use client"

import React, { Suspense, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, useGLTF, Html } from '@react-three/drei'
import { motion, AnimatePresence } from 'framer-motion'
import dotenv from 'dotenv'

dotenv.config()

type BespokeHouseProps = {
  imageURL: string;
}

type RiskInfo = {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  position: {
    x: number;
    y: number;
    z: number;
  };
}

const riskPoints: RiskInfo[] = [
  {
    id: 'roof',
    title: 'Roof Vulnerability',
    description: 'This area is susceptible to hail damage and wind uplift. Consider reinforcing with impact-resistant materials.',
    severity: 'high',
    position: { x: -0.2, y: 0.7, z: 0 }
  },
  {
    id: 'foundation',
    title: 'Foundation Risk',
    description: 'Located in a flood-prone zone. Consider installing proper drainage and waterproofing measures.',
    severity: 'medium',
    position: { x: 1, y: -0.5, z: -0.5 }
  }
]

// Configuration for the 3D model and risk points
const MODEL_CONFIG = {
  scale: 1.5,
  riskPointScale: 1, // Adjust this to make risk points larger or smaller
  riskPointOffset: { x: 0, y: 0, z: 0 }, // Global offset for all risk points
}

// TODO: Re-route to s3 bucket for secure storage
export default function BespokeHouse({ imageURL }: BespokeHouseProps) {
  const [selectedRisk, setSelectedRisk] = useState<RiskInfo | null>(null);

  // NOTE: Uncomment below when running the actual pipeline
  const proxy = process.env.NEXT_PUBLIC_PROXY_URL;
  const renderURL = proxy + encodeURIComponent(imageURL);
  // const renderURL = imageURL;

  function GLBModel({ url }: { url: string }) {
    const { scene } = useGLTF(url)
    return <primitive object={scene} scale={MODEL_CONFIG.scale} />
  }

  useGLTF.preload(renderURL)

  const RiskDot = ({ risk, position }: { risk: RiskInfo, position: { x: number, y: number, z: number } }) => {
    // Apply global offset and scale to position
    const adjustedPosition = {
      x: position.x + MODEL_CONFIG.riskPointOffset.x,
      y: position.y + MODEL_CONFIG.riskPointOffset.y,
      z: position.z + MODEL_CONFIG.riskPointOffset.z,
    };

    return (
      <Html position={[adjustedPosition.x, adjustedPosition.y, adjustedPosition.z]} style={{ pointerEvents: 'auto' }}>
        <motion.div
          style={{
            width: 12 * MODEL_CONFIG.riskPointScale,
            height: 12 * MODEL_CONFIG.riskPointScale,
            borderRadius: '50%',
            background: '#240DBF',
            cursor: 'pointer',
            position: 'relative',
          }}
          whileHover={{ scale: 1.2 }}
          onClick={() => setSelectedRisk(risk)}
        >
          <motion.div
            style={{
              position: 'absolute',
              top: -4,
              left: -4,
              right: -4,
              bottom: -4,
              borderRadius: '50%',
              border: '2px solid #240DBF',
              opacity: 0.5,
            }}
            animate={{
              scale: [1, 1.5],
              opacity: [0.5, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        </motion.div>
      </Html>
    )
  }

  return (
    <div style={{ width: '100%', height: 500, position: 'relative' }}>
      <Canvas camera={{ position: [2, 2, 4], fov: 60 }} shadows>
        <ambientLight intensity={0.7} />
        <directionalLight position={[5, 10, 7]} intensity={0.7} castShadow />
        <Suspense fallback={null}>
          <GLBModel url={renderURL} />
          {riskPoints.map((risk) => (
            <RiskDot key={risk.id} risk={risk} position={risk.position} />
          ))}
        </Suspense>
        <OrbitControls enablePan enableZoom enableRotate />
      </Canvas>
      <AnimatePresence>
        {selectedRisk && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            style={{
              position: 'absolute',
              left: '65%',
              bottom: 100,
              transform: 'translateX(40%, )',
              width: 320,
              background: 'white',
              borderRadius: 12,
              boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
              padding: 20,
              zIndex: 1000,
            }}
          >
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedRisk(null)}
              style={{
                position: 'absolute',
                top: 12,
                right: 12,
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: 4,
                color: '#666',
                fontSize: 16,
              }}
            >
              ✕
            </motion.button>
            <div>
              <h3 style={{ 
                fontSize: 20, 
                fontWeight: 600, 
                color: '#240DBF',
                marginBottom: 12,
                paddingRight: 24,
              }}>
                {selectedRisk.title}
              </h3>
              <div style={{ 
                padding: '6px 10px', 
                background: selectedRisk.severity === 'high' ? '#FFE5E5' : 
                           selectedRisk.severity === 'medium' ? '#FFF4E5' : '#E5FFE5',
                borderRadius: 6,
                marginBottom: 12,
                display: 'inline-block',
                fontSize: 14,
                fontWeight: 500,
              }}>
                {selectedRisk.severity.charAt(0).toUpperCase() + selectedRisk.severity.slice(1)} Risk
              </div>
              <p style={{ 
                fontSize: 14, 
                lineHeight: 1.5, 
                color: '#2B2C30',
                margin: 0,
              }}>
                {selectedRisk.description}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
