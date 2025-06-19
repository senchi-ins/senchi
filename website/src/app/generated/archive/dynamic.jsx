import React, { useState, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'

// House configuration schema
const createHouseConfig = (addressData) => {
  const {
    stories = 2,
    hasGarage = true,
    roofType = 'gabled', // gabled, hip, flat
    roofColor = '#2F4F4F',
    wallColor = '#B87333',
    hasChimney = true,
    windowCount = 4,
    doorColor = '#654321',
    landscaping = 'suburban', // suburban, urban, rural
    drivewayType = 'concrete', // concrete, asphalt, gravel
    trees = 5,
    cars = 2
  } = addressData

  return {
    stories,
    hasGarage,
    roofType,
    roofColor,
    wallColor,
    hasChimney,
    windowCount,
    doorColor,
    landscaping,
    drivewayType,
    trees,
    cars
  }
}

// Dynamic House Component
function DynamicHouse({ config }) {
  const houseRef = React.useRef()
  const [dotHovered, setDotHovered] = React.useState(false)

  useFrame((state) => {
    if (houseRef.current) {
      houseRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.02
    }
  })

  const houseHeight = config.stories * 3
  const firstFloorY = 1.5 // half of first floor height
  const secondFloorY = config.stories > 1 ? 3 + 1.25 : -100 // Hide if single story
  const roofY = config.stories > 1 ? 3 + 2.5 : 3

  // Calculate roof top position for dot placement
  let dotY = 0
  if (config.roofType === 'gabled') dotY = config.stories > 1 ? 7 + 2 : 4.5 + 2
  else if (config.roofType === 'hip') dotY = config.stories > 1 ? 6.5 + 2 : 4 + 2
  else if (config.roofType === 'flat') dotY = config.stories > 1 ? 6.25 + 1.2 : 3.65 + 1.2

  // Callout offset (pops away from house, e.g., top-right)
  const calloutOffset = [1.5, 2, 0]
  const dotPosition = [0, dotY, 0]
  const calloutPosition = [dotPosition[0] + calloutOffset[0], dotPosition[1] + calloutOffset[1], dotPosition[2] + calloutOffset[2]]

  return (
    <group ref={houseRef} position={[0, 0, 0]}>
      {/* Foundation flush with ground */}
      <mesh position={[0, 0.25, 0]} castShadow receiveShadow>
        <boxGeometry args={[8, 0.5, 6]} />
        <meshLambertMaterial color={config.wallColor} />
      </mesh>

      {/* First floor */}
      <mesh position={[0, 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[7, 3, 5]} />
        <meshLambertMaterial color={config.wallColor} />
      </mesh>

      {/* Second floor (conditional) */}
      {config.stories > 1 && (
        <mesh position={[0, 4.75, 0]} castShadow receiveShadow>
          <boxGeometry args={[6, 2.5, 4]} />
          <meshLambertMaterial color={config.wallColor} />
        </mesh>
      )}

      {/* Dynamic roof based on type, no hover logic here */}
      {config.roofType === 'gabled' && (
        <mesh
          position={[0, config.stories > 1 ? 7 : 4.5, 0]}
          rotation={[0, Math.PI / 4, 0]}
          castShadow
        >
          <coneGeometry args={[4.5, 3, 4]} />
          <meshLambertMaterial color={config.roofColor} />
        </mesh>
      )}

      {config.roofType === 'hip' && (
        <mesh
          position={[0, config.stories > 1 ? 6.5 : 4, 0]}
          castShadow
        >
          <coneGeometry args={[4, 2, 8]} />
          <meshLambertMaterial color={config.roofColor} />
        </mesh>
      )}

      {config.roofType === 'flat' && (
        <mesh
          position={[0, config.stories > 1 ? 6.25 : 3.65, 0]}
          castShadow
        >
          <boxGeometry args={[6.5, 0.3, 4.5]} />
          <meshLambertMaterial color={config.roofColor} />
        </mesh>
      )}

      {/* Senchi-main dot above the roof, highlight on hover */}
      <mesh
        position={dotPosition}
        onPointerOver={() => setDotHovered(true)}
        onPointerOut={() => setDotHovered(false)}
        scale={dotHovered ? 1.4 : 1}
        castShadow
      >
        <sphereGeometry args={[0.35, 24, 24]} />
        <meshStandardMaterial color="#240DBF" emissive="#240DBF" emissiveIntensity={dotHovered ? 1.2 : 0.5} />
      </mesh>
      {/* Line from dot to callout when hovered */}
      {dotHovered && (
        <line>
          <bufferGeometry attach="geometry">
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array([
                dotPosition[0], dotPosition[1], dotPosition[2],
                calloutPosition[0], calloutPosition[1], calloutPosition[2]
              ])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial attach="material" color="#240DBF" linewidth={2} />
        </line>
      )}
      {/* Callout offset away from house, only when dot is hovered */}
      {dotHovered && (
        <Html position={calloutPosition} center distanceFactor={1.2} zIndexRange={[10, 0]}>
          <div style={{
            background: 'white',
            border: '1px solid #888',
            borderRadius: 8,
            padding: '18px 28px',
            boxShadow: '0 2px 16px rgba(0,0,0,0.18)',
            fontSize: 20,
            pointerEvents: 'none',
            minWidth: 320,
            textAlign: 'center',
            fontWeight: 500
          }}>
            Replace with metal to protect from hail
          </div>
        </Html>
      )}

      {/* Garage (conditional) */}
      {config.hasGarage && (
        <>
          <mesh position={[5, 1.25, 0]} castShadow receiveShadow>
            <boxGeometry args={[3, 2.5, 3]} />
            <meshLambertMaterial color={config.wallColor} />
          </mesh>
          <mesh position={[5, 2.65, 0]} castShadow>
            <boxGeometry args={[3.5, 0.3, 3.5]} />
            <meshLambertMaterial color={config.roofColor} />
          </mesh>
          <mesh position={[5, 1.25, 1.55]}>
            <boxGeometry args={[2.5, 2, 0.1]} />
            <meshLambertMaterial color="#A0A0A0" />
          </mesh>
        </>
      )}

      {/* Front door */}
      <mesh position={[-1, 1.25, 2.55]}>
        <boxGeometry args={[0.8, 2, 0.1]} />
        <meshLambertMaterial color={config.doorColor} />
      </mesh>

      {/* Dynamic windows based on count */}
      {Array.from({ length: config.windowCount }, (_, i) => {
        const positions = [
          [1, 1.25, 2.55],
          [2.5, 1.25, 2.55],
          [-1, 4.2, 2.05],
          [1, 4.2, 2.05],
          [-2.5, 1.25, 0],
          [2.5, 1.25, 0]
        ]
        const pos = positions[i] || [0, 1.25, 0]
        return (
          <mesh key={i} position={pos}>
            <boxGeometry args={[1, 1.2, 0.05]} />
            <meshLambertMaterial color="#87CEEB" />
          </mesh>
        )
      })}

      {/* Chimney (conditional) */}
      {config.hasChimney && (
        <mesh position={[-2, config.stories > 1 ? 8.5 : 5.5, -1]} castShadow>
          <boxGeometry args={[0.8, 2, 0.8]} />
          <meshLambertMaterial color="#8B4513" />
        </mesh>
      )}
    </group>
  )
}

// Dynamic landscape based on config
function DynamicLandscape({ config }) {
  const treePositions = useMemo(() => {
    const positions = []
    for (let i = 0; i < config.trees; i++) {
      const angle = (i / config.trees) * Math.PI * 2
      const radius = 8 + Math.random() * 4
      positions.push([
        Math.cos(angle) * radius,
        0,
        Math.sin(angle) * radius
      ])
    }
    return positions
  }, [config.trees])

  const carColors = ['#FF0000', '#0000FF', '#00FF00', '#FFFF00', '#FF00FF']

  return (
    <>
      {/* Driveway flush with ground, starts at garage */}
      <mesh position={[5, 0.05, 6]} receiveShadow>
        <boxGeometry args={[4, 0.1, 12]} />
        <meshLambertMaterial color={
          config.drivewayType === 'concrete' ? '#696969' :
          config.drivewayType === 'asphalt' ? '#36454F' : '#8B7355'
        } />
      </mesh>

      {/* Dynamic trees */}
      {treePositions.map((position, i) => (
        <Tree key={i} position={position} scale={0.8 + Math.random() * 0.6} />
      ))}

      {/* Dynamic cars, flush with ground */}
      {Array.from({ length: config.cars }, (_, i) => (
        <Car 
          key={i} 
          position={[5, 0.3, 3 + i * 4]} 
          color={carColors[i % carColors.length]} 
        />
      ))}

      {/* Landscaping based on type */}
      {config.landscaping === 'suburban' && (
        <>
          <Bush position={[-3, 0, 3]} scale={0.8} />
          <Bush position={[-2, 0, 4]} scale={0.6} />
          <Bush position={[2, 0, 3.5]} scale={0.7} />
        </>
      )}

      {config.landscaping === 'urban' && (
        <>
          <mesh position={[-8, 2, 0]} castShadow>
            <boxGeometry args={[0.2, 4, 0.2]} />
            <meshLambertMaterial color="#333" />
          </mesh>
          <mesh position={[8, 2, 0]} castShadow>
            <boxGeometry args={[0.2, 4, 0.2]} />
            <meshLambertMaterial color="#333" />
          </mesh>
        </>
      )}
    </>
  )
}

// Tree and other components remain the same
function Tree({ position, scale = 1 }) {
  const treeRef = React.useRef()

  useFrame((state) => {
    if (treeRef.current) {
      treeRef.current.rotation.y = Math.sin(state.clock.elapsedTime + position[0]) * 0.02
    }
  })

  return (
    <group ref={treeRef} position={[position[0], 0, position[2]]}>
      <mesh position={[0, 1.5 * scale, 0]} castShadow>
        <cylinderGeometry args={[0.2 * scale, 0.3 * scale, 3 * scale, 8]} />
        <meshLambertMaterial color="#8B4513" />
      </mesh>
      <mesh position={[0, 3 * scale, 0]} castShadow>
        <sphereGeometry args={[1.5 * scale, 8, 6]} />
        <meshLambertMaterial color="#228B22" />
      </mesh>
    </group>
  )
}

function Bush({ position, scale = 1 }) {
  return (
    <mesh position={[position[0], 0.6 * scale, position[2]]} castShadow>
      <sphereGeometry args={[0.6 * scale, 8, 6]} />
      <meshLambertMaterial color="#32CD32" />
    </mesh>
  )
}

function Car({ position, color }) {
  return (
    <group position={[position[0], 0.3, position[2]]}>
      <mesh position={[0, 0.3, 0]} castShadow>
        <boxGeometry args={[1.8, 0.6, 4]} />
        <meshLambertMaterial color={color} />
      </mesh>
      <mesh position={[0, 0.8, 0]} castShadow>
        <boxGeometry args={[1.6, 0.4, 2.5]} />
        <meshLambertMaterial color={color} />
      </mesh>
      {[[-1, 0, 1.3], [1, 0, 1.3], [-1, 0, -1.3], [1, 0, -1.3]].map((pos, i) => (
        <mesh key={i} position={pos} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.25, 0.25, 0.2, 8]} />
          <meshLambertMaterial color="#333333" />
        </mesh>
      ))}
    </group>
  )
}

// Main dynamic component with address input
const DynamicHouse3D = () => {
  const [address, setAddress] = useState('')
  const [houseData, setHouseData] = useState(null)
  const [loading, setLoading] = useState(false)

  // Simulate API call to get house data from address
  const generateHouseFromAddress = async (address) => {
    setLoading(true)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock data generation based on address
    // In real implementation, this would call your backend
    const mockHouseData = {
      stories: address.toLowerCase().includes('apartment') ? 1 : Math.random() > 0.3 ? 2 : 1,
      hasGarage: !address.toLowerCase().includes('apartment') && Math.random() > 0.2,
      roofType: ['gabled', 'hip', 'flat'][Math.floor(Math.random() * 3)],
      roofColor: ['#2F4F4F', '#8B4513', '#708090'][Math.floor(Math.random() * 3)],
      wallColor: ['#B87333', '#F5DEB3', '#CD853F'][Math.floor(Math.random() * 3)],
      hasChimney: Math.random() > 0.4,
      windowCount: 3 + Math.floor(Math.random() * 4),
      doorColor: ['#654321', '#8B4513', '#2F4F4F'][Math.floor(Math.random() * 3)],
      landscaping: address.toLowerCase().includes('city') ? 'urban' : 'suburban',
      drivewayType: ['concrete', 'asphalt', 'gravel'][Math.floor(Math.random() * 3)],
      trees: 3 + Math.floor(Math.random() * 5),
      cars: Math.floor(Math.random() * 3)
    }
    
    setHouseData(mockHouseData)
    setLoading(false)
  }

  const config = houseData ? createHouseConfig(houseData) : null

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Enter an address..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-senchi-main"
          />
          <button
            onClick={() => generateHouseFromAddress(address)}
            disabled={!address || loading}
            className="px-6 py-2 bg-senchi-main text-white rounded-lg hover:bg-senchi-main/90 disabled:bg-senchi-main/50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate House'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="text-lg">Analyzing address and generating 3D model...</div>
        </div>
      )}

      {config && !loading && (
        <div className="space-y-4">
          <div className="rounded-lg overflow-hidden" style={{ height: '500px' }}>
            <Canvas
              camera={{ position: [8, 8, 8], fov: 75 }}
              shadows
              style={{ background: '#EFEEE7' }}
            >
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

              {/* Ground plane at y=0 */}
              <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
                <planeGeometry args={[20, 20]} />
                <meshLambertMaterial color="#228B22" />
              </mesh>

              {/* House and landscape flush with ground */}
              <DynamicHouse config={config} />
              <DynamicLandscape config={config} />

              <OrbitControls
                autoRotate
                autoRotateSpeed={0.5}
                enableZoom={true}
                enablePan={false}
                maxPolarAngle={Math.PI / 2}
                minDistance={8}
                maxDistance={35}
              />
            </Canvas>
          </div>
        </div>
      )}
    </div>
  )
}

export default DynamicHouse3D