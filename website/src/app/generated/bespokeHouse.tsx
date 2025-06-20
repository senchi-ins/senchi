"use client"

import React, { Suspense, useState, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, useGLTF, Html } from '@react-three/drei'
import { motion, AnimatePresence } from 'framer-motion'
import dotenv from 'dotenv'
import { AnalyzeHouseResponse } from '@/utils/api'

dotenv.config()

type BespokeHouseProps = {
  imageURL: string;
  labellingResponse: AnalyzeHouseResponse;
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

// Configuration for the 3D model and risk points
const MODEL_CONFIG = {
  scale: 1.8,
  riskPointScale: 1, // Adjust this to make risk points larger or smaller
  riskPointOffset: { x: 0, y: 0, z: 0 }, // Global offset for all risk points
}

// TODO: Re-route to s3 bucket for secure storage
export default function BespokeHouse({ imageURL, labellingResponse }: BespokeHouseProps) {
  const [selectedRisk, setSelectedRisk] = useState<RiskInfo | null>(null);

  const riskPoints = useMemo(() => {
    if (!labellingResponse || !labellingResponse.recommendations || !labellingResponse.category_scores) {
      return [];
    }

    const { recommendations, category_scores } = labellingResponse;
    const imageWidth = 640;
    const imageHeight = 640;

    return recommendations.map((rec, index) => {
      const scoreCategory = category_scores.find(cat => cat.title === rec.title);
      const severity = (scoreCategory?.score as 'low' | 'medium' | 'high') || 'medium';

      // Normalize 2D image coordinates to 3D model space [-1, 1]
      const x = (parseInt(rec.x, 10) - imageWidth / 2) / (imageWidth / 2);
      const y = (imageHeight / 2 - parseInt(rec.y, 10)) / (imageHeight / 2);

      return {
        id: rec.title || `risk-${index}`,
        title: rec.title,
        description: rec.explanation || rec.description,
        severity,
        position: {
          x,
          y,
          z: -0.5,
        },
      };
    });
  }, [labellingResponse]);

  // Construct the full, absolute URL to our own backend proxy
  const backendUrl = process.env.NEXT_PUBLIC_SENCHI_API_URL || 'http://localhost:8000';
  const proxyURL = `${backendUrl}/api/v1/proxy?url=${encodeURIComponent(imageURL)}`;

  function GLBModel({ url }: { url: string }) {
    const { scene } = useGLTF(url)
    return <primitive object={scene} scale={MODEL_CONFIG.scale} />
  }

  useGLTF.preload(proxyURL)

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
          <group position={[0, -0.7, 0]}>
            <GLBModel url={proxyURL} />
            {riskPoints.map((risk) => (
              <RiskDot key={risk.id} risk={risk} position={risk.position} />
            ))}
          </group>
        </Suspense>
        <OrbitControls enablePan enableZoom enableRotate />
      </Canvas>
      <AnimatePresence>
        {selectedRisk && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            style={{
              position: 'absolute',
              top: 20,
              left: '10%',
              transform: 'translateX(-30%)',
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
