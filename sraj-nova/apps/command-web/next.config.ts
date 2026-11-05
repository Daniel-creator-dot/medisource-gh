import type { NextConfig } from "next";

const api = process.env.API_URL || "http://127.0.0.1:8010";

const nextConfig: NextConfig = {
  agentRules: false,
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return { fallback: [{ source: "/api/:path*", destination: `${api}/api/:path*` }] };
  },
};

export default nextConfig;
