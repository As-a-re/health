"use client"

import React from "react"
import { useRef, Suspense, useState, useEffect } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import { OrbitControls, Environment, Html } from "@react-three/drei"
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib'
import * as THREE from "three"

// Error boundary for the 3D scene
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('3D Scene Error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-full bg-gray-100 rounded-lg p-4">
          <div className="text-center">
            <div className="text-red-500 text-2xl mb-2">⚠️</div>
            <p className="text-gray-700">Unable to load 3D doctor. Please refresh the page.</p>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

interface Simple3DDoctorProps {
  gender: "male" | "female"
  isSpeaking: boolean
  isListening: boolean
  emotion?: "neutral" | "happy" | "concerned" | "focused"
}

function DoctorAvatar({ gender, isSpeaking, isListening, emotion = "neutral" }: Simple3DDoctorProps) {
  const groupRef = useRef<THREE.Group>(null)
  const headRef = useRef<THREE.Mesh>(null)
  const bodyRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (groupRef.current) {
      // Breathing animation
      const breathingScale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.02
      if (bodyRef.current) {
        bodyRef.current.scale.y = breathingScale
      }

      // Speaking animation - head movement and gestures
      if (isSpeaking && headRef.current) {
        const speakingMovement = Math.sin(state.clock.elapsedTime * 8) * 0.1
        headRef.current.rotation.y = speakingMovement * 0.2
        headRef.current.position.y = 1.7 + speakingMovement * 0.05
        groupRef.current.rotation.y = speakingMovement * 0.05
      }

      // Listening animation - attentive pose
      if (isListening && headRef.current) {
        headRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 3) * 0.1
        headRef.current.rotation.x = -0.1 // Slight forward lean
      }

      // Idle animation - subtle movements
      if (!isSpeaking && !isListening) {
        const idleMovement = Math.sin(state.clock.elapsedTime * 0.5) * 0.02
        groupRef.current.rotation.y = idleMovement
        if (headRef.current) {
          headRef.current.rotation.y = idleMovement * 2
        }
      }
    }
  })

  const skinColor = "#D2B48C"
  const hairColor = gender === "female" ? "#2C1810" : "#1A1A1A"
  const clothingColor = "#FFFFFF"

  return (
    <group ref={groupRef} position={[0, -1, 0]}>
      {/* Head */}
      <mesh ref={headRef} position={[0, 1.7, 0]}>
        <sphereGeometry args={[0.18, 32, 32]} />
        <meshStandardMaterial color={skinColor} />
      </mesh>

      {/* Hair */}
      <mesh position={[0, 1.85, 0]}>
        <sphereGeometry args={gender === "female" ? [0.2, 16, 16] : [0.15, 16, 16]} />
        <meshStandardMaterial color={hairColor} />
      </mesh>

      {/* Eyes */}
      <mesh position={[-0.06, 1.75, 0.15]}>
        <sphereGeometry args={[0.02, 8, 8]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      <mesh position={[0.06, 1.75, 0.15]}>
        <sphereGeometry args={[0.02, 8, 8]} />
        <meshStandardMaterial color="#000000" />
      </mesh>

      {/* Nose */}
      <mesh position={[0, 1.68, 0.16]}>
        <coneGeometry args={[0.02, 0.06, 8]} />
        <meshStandardMaterial color={skinColor} />
      </mesh>

      {/* Body (White Coat) */}
      <mesh ref={bodyRef} position={[0, 1, 0]}>
        <cylinderGeometry args={[0.22, 0.28, 0.9, 8]} />
        <meshStandardMaterial color={clothingColor} />
      </mesh>

      {/* Arms */}
      <mesh position={[-0.35, 1.2, 0]} rotation={[0, 0, 0.3]}>
        <cylinderGeometry args={[0.06, 0.06, 0.7, 8]} />
        <meshStandardMaterial color={skinColor} />
      </mesh>
      <mesh position={[0.35, 1.2, 0]} rotation={[0, 0, -0.3]}>
        <cylinderGeometry args={[0.06, 0.06, 0.7, 8]} />
        <meshStandardMaterial color={skinColor} />
      </mesh>

      {/* Hands */}
      <mesh position={[-0.5, 0.9, 0]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color={skinColor} />
      </mesh>
      <mesh position={[0.5, 0.9, 0]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color={skinColor} />
      </mesh>

      {/* Legs */}
      <mesh position={[-0.12, 0.25, 0]}>
        <cylinderGeometry args={[0.09, 0.09, 0.9, 8]} />
        <meshStandardMaterial color="#000080" />
      </mesh>
      <mesh position={[0.12, 0.25, 0]}>
        <cylinderGeometry args={[0.09, 0.09, 0.9, 8]} />
        <meshStandardMaterial color="#000080" />
      </mesh>

      {/* Stethoscope */}
      <mesh position={[0, 1.4, 0.2]} rotation={[0, 0, 0]}>
        <torusGeometry args={[0.1, 0.015, 8, 16]} />
        <meshStandardMaterial color="#333333" />
      </mesh>

      {/* Medical Badge */}
      <mesh position={[0.15, 1.3, 0.22]}>
        <boxGeometry args={[0.08, 0.06, 0.01]} />
        <meshStandardMaterial color="#FF0000" />
      </mesh>

      {/* Status indicators */}
      {isSpeaking && (
        <Html position={[0, 2.2, 0]} center>
          <div className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold animate-pulse shadow-lg">
            🗣️ Speaking
          </div>
        </Html>
      )}

      {isListening && (
        <Html position={[0, 2.2, 0]} center>
          <div className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-semibold animate-pulse shadow-lg">
            👂 Listening
          </div>
        </Html>
      )}

      {!isSpeaking && !isListening && (
        <Html position={[0, 2.2, 0]} center>
          <div className="bg-gray-500 text-white px-3 py-1 rounded-full text-xs font-semibold">💭 Ready</div>
        </Html>
      )}
    </group>
  )
}

// Loading fallback component
const Loader = () => (
  <div className="flex items-center justify-center h-full">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
  </div>
)

// Safe OrbitControls with error handling
const SafeOrbitControls = (props: any) => {
  const [mounted, setMounted] = useState(false)
  const controls = useRef<OrbitControlsImpl>(null)
  const { camera, gl } = useThree()

  useEffect(() => {
    if (controls.current) {
      // Set the camera position after the first render
      camera.position.set(0, 1, 3)
      camera.lookAt(0, 1, 0)
      setMounted(true)
    }
  }, [camera])

  if (!mounted) return null

  return (
    <OrbitControls
      ref={controls}
      args={[camera, gl.domElement]}
      enablePan={false}
      enableZoom={true}
      maxDistance={5}
      minDistance={2}
      maxPolarAngle={Math.PI / 2}
      minPolarAngle={Math.PI / 6}
      autoRotate={false}
      {...props}
    />
  )
}

export function Simple3DDoctor({ gender, isSpeaking, isListening, emotion = 'neutral' }: Simple3DDoctorProps) {
  const [mounted, setMounted] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    setMounted(true)
    return () => setMounted(false)
  }, [])

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-100 rounded-lg p-4">
        <div className="text-center">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <p className="text-gray-700">Failed to load 3D doctor. Please try again later.</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Reload
          </button>
        </div>
      </div>
    )
  }

  if (!mounted) {
    return <Loader />
  }

  return (
    <ErrorBoundary>
      <div className="w-full h-full bg-gradient-to-b from-blue-50 to-white rounded-lg overflow-hidden">
        <Suspense fallback={<Loader />}>
          <Canvas 
            camera={{ position: [0, 1, 3], fov: 50 }} 
            style={{ width: "100%", height: "100%" }}
            onCreated={({ gl }) => {
              gl.shadowMap.enabled = true
              gl.shadowMap.type = THREE.PCFSoftShadowMap
            }}
          >
            <ambientLight intensity={0.7} />
            <directionalLight 
              position={[5, 5, 5]} 
              intensity={1} 
              castShadow 
              shadow-mapSize-width={1024}
              shadow-mapSize-height={1024}
            />
            <pointLight position={[-5, 5, 5]} intensity={0.5} />
            <spotLight position={[0, 10, 0]} intensity={0.3} />

            <Suspense fallback={null}>
              <DoctorAvatar 
                gender={gender} 
                isSpeaking={isSpeaking} 
                isListening={isListening} 
                emotion={emotion} 
              />
            </Suspense>

            <Environment preset="sunset" />
            <SafeOrbitControls />

            {/* Floor */}
            <mesh 
              position={[0, -2, 0]} 
              rotation={[-Math.PI / 2, 0, 0]} 
              receiveShadow
            >
              <planeGeometry args={[10, 10]} />
              <meshStandardMaterial color="#f0f0f0" />
            </mesh>
          </Canvas>
        </Suspense>
      </div>
    </ErrorBoundary>
  )
}
