import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

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
      <body className={`${inter.className} bg-gray-50 dark:bg-gray-900`}>
        <main className="container mx-auto min-h-screen p-4 sm:p-8">
          {children}
        </main>
        <Toaster richColors />
      </body>
    </html>
  );
}