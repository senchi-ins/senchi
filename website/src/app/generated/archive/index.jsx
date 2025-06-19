import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

const url = "https://tripo-data.rg1.data.tripo3d.com/tcli_452312b4252d418cbd41cff1e5c98d35/20250617/a32d1cef-e70e-4b6c-9e0d-1a187c76dca3/tripo_pbr_model_a32d1cef-e70e-4b6c-9e0d-1a187c76dca3.glb?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly90cmlwby1kYXRhLnJnMS5kYXRhLnRyaXBvM2QuY29tL3RjbGlfNDUyMzEyYjQyNTJkNDE4Y2JkNDFjZmYxZTVjOThkMzUvMjAyNTA2MTcvYTMyZDFjZWYtZTcwZS00YjZjLTllMGQtMWExODdjNzZkY2EzL3RyaXBvX3Bicl9tb2RlbF9hMzJkMWNlZi1lNzBlLTRiNmMtOWUwZC0xYTE4N2M3NmRjYTMuZ2xiIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzUwMjA0ODAwfX19XX0_&Signature=lRLI1LtNkzIMj1GSs1oMPxDoGPmjhMb3~vG5DXf2RMMGKxp8~kVQQvz8b6-Duu-47YrSWdR2lsZeGPn9sG~~oGTnyX1FpP6Gp-bZaMJEXJ~RYu-vUSwlBEsSY0BMd10nBeS9QLv8cSuQ2Z9Hmle-wNQEEfgPVIGt-iJFx~oNdqezURgOIZhde3r0tQiybYGHGq1dfjUOpztM1wZDOn-CkTJVTvmPMAhh683Xx7U-IgpHs6AfuJK5Ksa3NTSo1Km3REsEsrqn6UzDBuCKlhZIe~J7ECKATLJqIk8uiJVYiKOiJk-wouiyJ3ki5Siax4OFS495e8LsDDqepfRJb053Xg__&Key-Pair-Id=K1676C64NMVM2J"

// House component
function House() {
  const houseRef = useRef()

  useFrame((state) => {
    // Gentle house floating animation
    if (houseRef.current) {
      houseRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.02
    }
  })

  return (
    <group ref={houseRef}>
      {/* Foundation */}
      <mesh position={[0, -3.25, 0]} castShadow receiveShadow>
        <boxGeometry args={[8, 0.5, 6]} />
        <meshLambertMaterial color="#B87333" />
      </mesh>

      {/* First floor */}
      <mesh position={[0, -1.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[7, 3, 5]} />
        <meshLambertMaterial color="#B87333" />
      </mesh>

      {/* Second floor */}
      <mesh position={[0, 1.25, 0]} castShadow receiveShadow>
        <boxGeometry args={[6, 2.5, 4]} />
        <meshLambertMaterial color="#B87333" />
      </mesh>

      {/* Main roof */}
      <mesh position={[0, 4, 0]} rotation={[0, Math.PI / 4, 0]} castShadow>
        <coneGeometry args={[4.5, 3, 4]} />
        <meshLambertMaterial color="#2F4F4F" />
      </mesh>

      {/* Garage */}
      <mesh position={[5, -1.75, 0]} castShadow receiveShadow>
        <boxGeometry args={[3, 2.5, 3]} />
        <meshLambertMaterial color="#B87333" />
      </mesh>

      {/* Garage roof */}
      <mesh position={[5, -0.35, 0]} castShadow>
        <boxGeometry args={[3.5, 0.3, 3.5]} />
        <meshLambertMaterial color="#2F4F4F" />
      </mesh>

      {/* Garage door */}
      <mesh position={[5, -1.5, 1.55]}>
        <boxGeometry args={[2.5, 2, 0.1]} />
        <meshLambertMaterial color="#A0A0A0" />
      </mesh>

      {/* Front door */}
      <mesh position={[-1, -1, 2.55]}>
        <boxGeometry args={[0.8, 2, 0.1]} />
        <meshLambertMaterial color="#654321" />
      </mesh>

      {/* Door handle */}
      <mesh position={[-0.7, -1, 2.6]}>
        <sphereGeometry args={[0.05, 8, 6]} />
        <meshLambertMaterial color="#FFD700" />
      </mesh>

      {/* Windows - First floor */}
      <mesh position={[1, -1, 2.55]}>
        <boxGeometry args={[1, 1.2, 0.05]} />
        <meshLambertMaterial color="#87CEEB" />
      </mesh>

      <mesh position={[2.5, -1, 2.55]}>
        <boxGeometry args={[1, 1.2, 0.05]} />
        <meshLambertMaterial color="#87CEEB" />
      </mesh>

      {/* Second floor windows */}
      <mesh position={[-1, 1.2, 2.05]}>
        <boxGeometry args={[1, 1.2, 0.05]} />
        <meshLambertMaterial color="#87CEEB" />
      </mesh>

      <mesh position={[1, 1.2, 2.05]}>
        <boxGeometry args={[1, 1.2, 0.05]} />
        <meshLambertMaterial color="#87CEEB" />
      </mesh>

      {/* Bay window */}
      <mesh position={[0, 1.2, 2.15]}>
        <boxGeometry args={[1.5, 1, 0.3]} />
        <meshLambertMaterial color="#87CEEB" />
      </mesh>

      {/* Chimney */}
      <mesh position={[-2, 4.5, -1]} castShadow>
        <boxGeometry args={[0.8, 2, 0.8]} />
        <meshLambertMaterial color="#8B4513" />
      </mesh>
    </group>
  )
}

// Tree component
function Tree({ position, scale = 1 }) {
  const treeRef = useRef()

  useFrame((state) => {
    // Gentle swaying animation
    if (treeRef.current) {
      treeRef.current.rotation.y = Math.sin(state.clock.elapsedTime + position[0]) * 0.02
    }
  })

  return (
    <group ref={treeRef} position={position}>
      {/* Trunk */}
      <mesh position={[0, -1.5 * scale, 0]} castShadow>
        <cylinderGeometry args={[0.2 * scale, 0.3 * scale, 3 * scale, 8]} />
        <meshLambertMaterial color="#8B4513" />
      </mesh>

      {/* Main foliage */}
      <mesh position={[0, 0.5 * scale, 0]} castShadow>
        <sphereGeometry args={[1.5 * scale, 8, 6]} />
        <meshLambertMaterial color="#228B22" />
      </mesh>

      {/* Foliage clusters */}
      {[0, 1, 2].map((i) => {
        const angle = (i / 3) * Math.PI * 2
        return (
          <mesh
            key={i}
            position={[
              Math.cos(angle) * 0.8 * scale,
              0.3 * scale + Math.random() * 0.4 * scale,
              Math.sin(angle) * 0.8 * scale
            ]}
            castShadow
          >
            <sphereGeometry args={[0.8 * scale, 6, 4]} />
            <meshLambertMaterial color="#228B22" />
          </mesh>
        )
      })}
    </group>
  )
}

// Bush component
function Bush({ position, scale = 1 }) {
  return (
    <mesh position={[position[0], -3 + 0.6 * scale, position[2]]} castShadow>
      <sphereGeometry args={[0.6 * scale, 8, 6]} />
      <meshLambertMaterial color="#32CD32" />
    </mesh>
  )
}

// Car component
function Car({ position, color }) {
  return (
    <group position={position}>
      {/* Car body */}
      <mesh position={[0, -2.7, 0]} castShadow>
        <boxGeometry args={[1.8, 0.6, 4]} />
        <meshLambertMaterial color={color} />
      </mesh>

      {/* Car roof */}
      <mesh position={[0, -2.2, 0]} castShadow>
        <boxGeometry args={[1.6, 0.4, 2.5]} />
        <meshLambertMaterial color={color} />
      </mesh>

      {/* Wheels */}
      {[
        [-1, -2.95, 1.3],
        [1, -2.95, 1.3],
        [-1, -2.95, -1.3],
        [1, -2.95, -1.3]
      ].map((pos, index) => (
        <mesh key={index} position={pos} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.25, 0.25, 0.2, 8]} />
          <meshLambertMaterial color="#333333" />
        </mesh>
      ))}
    </group>
  )
}

// Main scene component
function Scene() {
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight
        position={[10, 20, 10]}
        intensity={0.8}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={50}
        shadow-camera-left={-25}
        shadow-camera-right={25}
        shadow-camera-top={25}
        shadow-camera-bottom={-25}
      />

      {/* Ground */}
      <mesh position={[0, -3, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[25, 25]} />
        <meshLambertMaterial color="#228B22" />
      </mesh>

      {/* Driveway */}
      <mesh position={[5, -2.95, 5]} receiveShadow>
        <boxGeometry args={[4, 0.1, 12]} />
        <meshLambertMaterial color="#696969" />
      </mesh>

      {/* House */}
      <House />

      {/* Trees */}
      <Tree position={[-6, 0, -4]} scale={1.2} />
      <Tree position={[-4, 0, 6]} scale={1} />
      <Tree position={[8, 0, -6]} scale={1.1} />
      <Tree position={[6, 0, 4]} scale={0.9} />
      <Tree position={[-8, 0, 1]} scale={1.3} />

      {/* Bushes */}
      <Bush position={[-3, 0, 3]} scale={0.8} />
      <Bush position={[-2, 0, 4]} scale={0.6} />
      <Bush position={[2, 0, 3.5]} scale={0.7} />
      <Bush position={[3, 0, 4]} scale={0.9} />

      {/* Cars */}
      <Car position={[5, 0, 3]} color="#FF0000" />
      <Car position={[5, 0, 7]} color="#0000FF" />
    </>
  )
}

// Main component
const House3D = ({ 
  width = 500, 
  height = 400, 
  autoRotate = true,
  className = "",
  enableZoom = true,
  enablePan = false
}) => {
  return (
    <div className={className} style={{ width, height }}>
      <Canvas
        camera={{ position: [12, 8, 12], fov: 75 }}
        shadows
        style={{ background: 'linear-gradient(135deg, #87CEEB 0%, #E0F6FF 100%)' }}
      >
        <Scene />
        <OrbitControls
          autoRotate={autoRotate}
          autoRotateSpeed={0.5}
          enableZoom={enableZoom}
          enablePan={enablePan}
          maxPolarAngle={Math.PI / 2}
          minDistance={8}
          maxDistance={35}
        />
      </Canvas>
    </div>
  )
}

export default House3D