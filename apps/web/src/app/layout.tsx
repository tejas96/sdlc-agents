import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Layout from "@/components/shared/layout";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "SDLC Agent - Intelligent Development Lifecycle",
  description: "AI-powered software development lifecycle management platform with intelligent agents, workflow automation, and comprehensive project analytics.",
  keywords: ["SDLC", "AI", "Development", "Automation", "Project Management", "DevOps"],
  authors: [{ name: "SDLC Team" }],
  openGraph: {
    title: "SDLC Agent",
    description: "Intelligent Development Lifecycle Management",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Layout>
          {children}
        </Layout>
      </body>
    </html>
  );
}
