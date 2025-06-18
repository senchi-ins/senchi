import React, { useRef, useEffect, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, useTexture, useGLTF } from "@react-three/drei";
import * as THREE from "three";

function Lighting() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[10, 10, 5]}
        intensity={1.2}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
    </>
  );
}

function Ground() {
  return (
    <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
      <planeGeometry args={[50, 50]} />
      <meshStandardMaterial color="#cccccc" />
    </mesh>
  );
}

function House() {
  const brick = useTexture("/textures/brick_diffuse.jpg");
  const roof = useTexture("/textures/roof_tiles_diffuse.jpg");
  const windowGlass = new THREE.MeshStandardMaterial({
    color: "#aad3df",
    metalness: 0.1,
    roughness: 0.1,
    transparent: true,
    opacity: 0.7,
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Main House Structure */}
      <mesh position={[0, 1.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[6, 3, 5]} />
        <meshStandardMaterial map={brick} />
      </mesh>

      {/* Garage */}
      <mesh position={[4.2, 1.1, 0]} castShadow receiveShadow>
        <boxGeometry args={[3, 2.2, 4.8]} />
        <meshStandardMaterial map={brick} />
      </mesh>

      {/* Roof */}
      <mesh position={[0, 3.2, 0]} rotation={[0, 0, 0]} castShadow>
        <coneGeometry args={[4.8, 1.2, 4]} />
        <meshStandardMaterial map={roof} />
      </mesh>

      {/* Windows */}
      <mesh position={[-1.5, 2, 2.52]}>
        <boxGeometry args={[1, 1.2, 0.05]} />
        <primitive object={windowGlass} attach="material" />
      </mesh>

      <mesh position={[0, 2, 2.52]}>
        <boxGeometry args={[1, 1.2, 0.05]} />
        <primitive object={windowGlass} attach="material" />
      </mesh>

      {/* Door */}
      <mesh position={[2, 1, 2.52]}>
        <boxGeometry args={[0.8, 1.8, 0.05]} />
        <meshStandardMaterial color="#654321" />
      </mesh>
    </group>
  );
}

function HouseScene() {
  return (
    <Canvas
      shadows
      camera={{ position: [10, 5, 10], fov: 60 }}
      style={{ height: "100vh", width: "100%" }}
    >
      <color attach="background" args={["#eef1f6"]} />
      <OrbitControls enableZoom={true} />
      <Lighting />
      <Ground />
      <House />
    </Canvas>
  );
}

export default HouseScene;
