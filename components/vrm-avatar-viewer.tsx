"use client"

import { useRef, useState } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls, Environment, Html } from "@react-three/drei"
import type * as THREE from "three"

interface VRMAvatarProps {
  vrmUrl: string
  isSpeaking: boolean
  isListening: boolean
  emotion?: "neutral" | "happy" | "concerned" | "focused"
}

function DoctorModel({ isSpeaking, isListening, emotion = "neutral" }: Omit<VRMAvatarProps, "vrmUrl">) {
  const meshRef = useRef<THREE.Group>(null)
  const [loading, setLoading] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      // Breathing animation
      const breathingScale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.02
      meshRef.current.scale.y = breathingScale

      // Speaking animation - head movement
      if (isSpeaking) {
        const speakingMovement = Math.sin(state.clock.elapsedTime * 8) * 0.1
        meshRef.current.rotation.y = speakingMovement * 0.1
        meshRef.current.position.y = speakingMovement * 0.05
      }

      // Listening animation - slight head tilt
      if (isListening) {
        meshRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 3) * 0.05
      }

      // Idle animation
      if (!isSpeaking && !isListening) {
        meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.05
      }
    }
  })

  return (
    <group ref={meshRef}>
      {/* Simplified 3D Doctor Representation */}
      <group position={[0, -1, 0]}>
        {/* Head */}
        <mesh position={[0, 1.7, 0]}>
          <sphereGeometry args={[0.15, 32, 32]} />
          <meshStandardMaterial color="#D2B48C" />
        </mesh>

        {/* Body */}
        <mesh position={[0, 1, 0]}>
          <cylinderGeometry args={[0.2, 0.25, 0.8, 8]} />
          <meshStandardMaterial color="#FFFFFF" />
        </mesh>

        {/* Arms */}
        <mesh position={[-0.3, 1.2, 0]} rotation={[0, 0, 0.3]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6, 8]} />
          <meshStandardMaterial color="#D2B48C" />
        </mesh>
        <mesh position={[0.3, 1.2, 0]} rotation={[0, 0, -0.3]}>
          <cylinderGeometry args={[0.05, 0.05, 0.6, 8]} />
          <meshStandardMaterial color="#D2B48C" />
        </mesh>

        {/* Legs */}
        <mesh position={[-0.1, 0.2, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.8, 8]} />
          <meshStandardMaterial color="#000080" />
        </mesh>
        <mesh position={[0.1, 0.2, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.8, 8]} />
          <meshStandardMaterial color="#000080" />
        </mesh>

        {/* Stethoscope */}
        <mesh position={[0, 1.5, 0.1]}>
          <torusGeometry args={[0.08, 0.01, 8, 16]} />
          <meshStandardMaterial color="#333333" />
        </mesh>
      </group>

      {/* Speaking indicator */}
      {isSpeaking && (
        <Html position={[0, 1, 0]} center>
          <div className="bg-green-500 text-white px-2 py-1 rounded-full text-xs animate-pulse">Speaking...</div>
        </Html>
      )}

      {/* Listening indicator */}
      {isListening && (
        <Html position={[0, 1, 0]} center>
          <div className="bg-blue-500 text-white px-2 py-1 rounded-full text-xs animate-pulse">Listening...</div>
        </Html>
      )}
    </group>
  )
}

export function VRMAvatarViewer({ vrmUrl, isSpeaking, isListening, emotion }: VRMAvatarProps) {
  return (
    <div className="w-full h-full bg-gradient-to-b from-blue-50 to-white rounded-lg overflow-hidden">
      <Canvas camera={{ position: [0, 1, 2], fov: 50 }} style={{ width: "100%", height: "100%" }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={0.8} />
        <pointLight position={[-5, 5, 5]} intensity={0.4} />

        <DoctorModel isSpeaking={isSpeaking} isListening={isListening} emotion={emotion} />

        <Environment preset="studio" />
        <OrbitControls
          enablePan={false}
          enableZoom={false}
          maxPolarAngle={Math.PI / 2}
          minPolarAngle={Math.PI / 3}
          autoRotate={false}
        />
      </Canvas>
    </div>
  )
}
