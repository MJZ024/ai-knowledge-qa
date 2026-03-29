import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 智能知识库问答系统 | 学号: 423830107 | 毛坚再",
  description: "基于 RAG 的 AI 智能问答系统，支持参数可视化调整",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
