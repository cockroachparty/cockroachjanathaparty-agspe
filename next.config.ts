import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Vercel deployment - standard Next.js build */
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
};

export default nextConfig;
