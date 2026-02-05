/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Disable the old pages router for cleaner App Router structure
  // The src/pages directory will be removed after verification
}

module.exports = nextConfig
