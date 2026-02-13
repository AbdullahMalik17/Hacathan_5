"use client"

import { motion, HTMLMotionProps, Variants } from "framer-motion"
import { ReactNode } from "react"

// Fade in animation wrapper
interface FadeInProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  delay?: number
  duration?: number
  direction?: "up" | "down" | "left" | "right" | "none"
}

export function FadeIn({
  children,
  delay = 0,
  duration = 0.5,
  direction = "up",
  ...props
}: FadeInProps) {
  const directions = {
    up: { y: 40 },
    down: { y: -40 },
    left: { x: 40 },
    right: { x: -40 },
    none: {},
  }

  return (
    <motion.div
      initial={{ opacity: 0, ...directions[direction] }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{
        duration,
        delay,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Fade in when in view
interface FadeInViewProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  delay?: number
  duration?: number
  direction?: "up" | "down" | "left" | "right" | "none"
  once?: boolean
}

export function FadeInView({
  children,
  delay = 0,
  duration = 0.6,
  direction = "up",
  once = true,
  ...props
}: FadeInViewProps) {
  const directions = {
    up: { y: 60 },
    down: { y: -60 },
    left: { x: 60 },
    right: { x: -60 },
    none: {},
  }

  return (
    <motion.div
      initial={{ opacity: 0, ...directions[direction] }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once, margin: "-100px" }}
      transition={{
        duration,
        delay,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Stagger container for animating children in sequence
interface StaggerContainerProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  staggerDelay?: number
  delayChildren?: number
}

export function StaggerContainer({
  children,
  staggerDelay = 0.1,
  delayChildren = 0,
  ...props
}: StaggerContainerProps) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: staggerDelay,
            delayChildren,
          },
        },
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Stagger item - use inside StaggerContainer
interface StaggerItemProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  direction?: "up" | "down" | "left" | "right" | "none"
  delay?: number
}

export function StaggerItem({
  children,
  direction = "up",
  delay = 0,
  ...props
}: StaggerItemProps) {
  const directions = {
    up: { y: 30 },
    down: { y: -30 },
    left: { x: 30 },
    right: { x: -30 },
    none: {},
  }

  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, ...directions[direction] },
        visible: {
          opacity: 1,
          x: 0,
          y: 0,
          transition: {
            duration: 0.5,
            delay,
            ease: [0.21, 0.47, 0.32, 0.98],
          },
        },
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Scale animation on hover
interface ScaleOnHoverProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  scale?: number
}

export function ScaleOnHover({
  children,
  scale = 1.05,
  ...props
}: ScaleOnHoverProps) {
  return (
    <motion.div
      whileHover={{ scale }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Floating animation
interface FloatProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  duration?: number
  distance?: number
}

export function Float({
  children,
  duration = 3,
  distance = 10,
  ...props
}: FloatProps) {
  return (
    <motion.div
      animate={{
        y: [-distance, distance, -distance],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Pulse glow animation
interface PulseGlowProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  color?: string
}

export function PulseGlow({
  children,
  color = "rgba(59, 130, 246, 0.5)",
  ...props
}: PulseGlowProps) {
  return (
    <motion.div
      animate={{
        boxShadow: [
          `0 0 20px ${color}`,
          `0 0 60px ${color}`,
          `0 0 20px ${color}`,
        ],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Text reveal animation (character by character)
interface TextRevealProps {
  text: string
  className?: string
  delay?: number
}

export function TextReveal({ text, className, delay = 0 }: TextRevealProps) {
  const letters = text.split("")

  return (
    <motion.span
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.03,
            delayChildren: delay,
          },
        },
      }}
      className={className}
    >
      {letters.map((letter, index) => (
        <motion.span
          key={index}
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: {
              opacity: 1,
              y: 0,
              transition: {
                duration: 0.4,
                ease: [0.21, 0.47, 0.32, 0.98],
              },
            },
          }}
          style={{ display: "inline-block" }}
        >
          {letter === " " ? "\u00A0" : letter}
        </motion.span>
      ))}
    </motion.span>
  )
}

// Counter animation
interface CounterProps {
  from?: number
  to: number
  duration?: number
  className?: string
  suffix?: string
  prefix?: string
}

export function Counter({
  from = 0,
  to,
  duration = 2,
  className,
  suffix = "",
  prefix = "",
}: CounterProps) {
  return (
    <motion.span
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {prefix}
      </motion.span>
      <motion.span
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <CounterNumber from={from} to={to} duration={duration} />
      </motion.span>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {suffix}
      </motion.span>
    </motion.span>
  )
}

function CounterNumber({
  from,
  to,
  duration,
}: {
  from: number
  to: number
  duration: number
}) {
  return (
    <motion.span
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      transition={{ duration }}
      onUpdate={(latest) => {}}
    >
      {to}
    </motion.span>
  )
}

// Slide in from edge
interface SlideInProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  direction?: "left" | "right" | "top" | "bottom"
  delay?: number
  duration?: number
}

export function SlideIn({
  children,
  direction = "left",
  delay = 0,
  duration = 0.6,
  ...props
}: SlideInProps) {
  const directions = {
    left: { x: "-100%" },
    right: { x: "100%" },
    top: { y: "-100%" },
    bottom: { y: "100%" },
  }

  return (
    <motion.div
      initial={{ ...directions[direction], opacity: 0 }}
      animate={{ x: 0, y: 0, opacity: 1 }}
      transition={{
        duration,
        delay,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Blur in animation
interface BlurInProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  delay?: number
  duration?: number
}

export function BlurIn({
  children,
  delay = 0,
  duration = 0.8,
  ...props
}: BlurInProps) {
  return (
    <motion.div
      initial={{ opacity: 0, filter: "blur(20px)" }}
      animate={{ opacity: 1, filter: "blur(0px)" }}
      transition={{
        duration,
        delay,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Rotate in animation
interface RotateInProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  delay?: number
  duration?: number
  degrees?: number
}

export function RotateIn({
  children,
  delay = 0,
  duration = 0.6,
  degrees = -10,
  ...props
}: RotateInProps) {
  return (
    <motion.div
      initial={{ opacity: 0, rotate: degrees, scale: 0.9 }}
      animate={{ opacity: 1, rotate: 0, scale: 1 }}
      transition={{
        duration,
        delay,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Page transition wrapper
interface PageTransitionProps {
  children: ReactNode
}

export function PageTransition({ children }: PageTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{
        duration: 0.3,
        ease: [0.21, 0.47, 0.32, 0.98],
      }}
    >
      {children}
    </motion.div>
  )
}

// Magnetic effect (follows cursor slightly)
interface MagneticProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  strength?: number
}

export function Magnetic({
  children,
  strength = 0.3,
  ...props
}: MagneticProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Bounce animation
interface BounceProps extends HTMLMotionProps<"div"> {
  children: ReactNode
  delay?: number
}

export function Bounce({ children, delay = 0, ...props }: BounceProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.3 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 15,
        delay,
      }}
      {...props}
    >
      {children}
    </motion.div>
  )
}

// Typewriter effect
interface TypewriterProps {
  text: string
  className?: string
  speed?: number
  delay?: number
}

export function Typewriter({
  text,
  className,
  speed = 0.05,
  delay = 0,
}: TypewriterProps) {
  return (
    <motion.span className={className}>
      {text.split("").map((char, index) => (
        <motion.span
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.01,
            delay: delay + index * speed,
          }}
        >
          {char}
        </motion.span>
      ))}
    </motion.span>
  )
}

// Export motion components for direct use
export { motion }
