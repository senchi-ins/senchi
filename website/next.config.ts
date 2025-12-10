import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async redirects() {
    return [
      {
        source: '/:path*',
        destination: 'https://joinaerium.com',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
