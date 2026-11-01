import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: [
    "@medisource/ui",
    "@medisource/api-client",
    "@medisource/shared-types",
  ],
};

export default nextConfig;
