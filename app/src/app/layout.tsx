import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "周易八字分析",
  description: "基于AI的专业命理分析",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={`${inter.className} bg-black text-white`}>
        <Sidebar />
        <main className="md:ml-16 min-h-screen px-6 py-6">
          {children}
          <Toaster richColors />
        </main>
      </body>
    </html>
  );
}