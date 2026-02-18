import type { Metadata } from "next";
import "./globals.css";
import React from "react";
import { Analytics } from "@vercel/analytics/next";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "Senchi Chemical Supply Co. - Commodity-Derived Chemical Products",
  description:
    "Manufacturer and distributor of high-purity chemicals synthesized from commodity feedstocks. Serving industrial, agricultural, and municipal clients across North America since 1987.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        style={{ fontFamily: "'Georgia', 'Times New Roman', 'Times', serif" }}
      >
        <AuthProvider>{children}</AuthProvider>
        <Analytics />
      </body>
    </html>
  );
}
