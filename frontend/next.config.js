/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  images: { remotePatterns: [{ protocol: "http", hostname: "**" }] },
};

module.exports = nextConfig;
