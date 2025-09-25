import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  eslint: {
    // Only run ESLint on the 'pages' and 'utils' directories during production builds
    // This allows builds to complete even with ESLint warnings
    ignoreDuringBuilds: process.env.NODE_ENV === 'production',
  },
  typescript: {
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    ignoreBuildErrors: process.env.NODE_ENV === 'production',
  },
};

export default nextConfig;
