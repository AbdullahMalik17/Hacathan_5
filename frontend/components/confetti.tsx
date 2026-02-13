"use client"

import { motion } from "framer-motion"
import { useEffect, useState } from "react"

const colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]

interface Particle {
  id: number
  x: number
  y: number
  color: string
  rotation: number
  scale: number
}

export function Confetti() {
  const [particles, setParticles] = useState<Particle[]>([])

  useEffect(() => {
    const particleCount = 50
    const newParticles: Particle[] = []

    for (let i = 0; i < particleCount; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * 100 - 50, // -50% to 50% relative to center
        y: Math.random() * -50, // Start slightly above
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        scale: Math.random() * 0.5 + 0.5,
      })
    }

    setParticles(newParticles)
  }, [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-50 flex justify-center pt-20">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          initial={{
            opacity: 1,
            x: 0,
            y: 0,
            rotate: 0,
          }}
          animate={{
            opacity: 0,
            x: particle.x * 10, // Spread out
            y: 400 + Math.random() * 200, // Fall down
            rotate: particle.rotation + 720, // Spin
          }}
          transition={{
            duration: 2 + Math.random(),
            ease: [0.25, 0.1, 0.25, 1], // Cubic bezier for gravity feel
            delay: Math.random() * 0.2,
          }}
          style={{
            position: "absolute",
            width: "10px",
            height: "10px",
            backgroundColor: particle.color,
            borderRadius: Math.random() > 0.5 ? "50%" : "2px",
          }}
        />
      ))}
    </div>
  )
}
