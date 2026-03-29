"use client";

import { useState, useRef, useEffect } from "react";

const STUDENT_ID = "423830107";
const STUDENT_NAME = "毛坚再";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
  role: "user" | "assistant";
  content: string;
  docs?: string[];
}

interface Params {
  temperature: number;
  top_p: number;
  max_tokens: number;
  system_prompt: string;
  retrieval_top_k: number;
  similarity_threshold: number;
}

const PRESET_SYSTEM_PROMPTS = [
  "你是一个专业、友好的 AI 助手。请根据知识库内容准确回答问题。",
  "你是一位严谨的学术助手。回答时应引用相关文档内容，注明来源。",
  "你是一个简洁高效的助手。请用简短清晰的语言回答。",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showParams, setShowParams] = useState(false);
  const [params, setParams] = useState<Params>({
    temperature: 0.7,
    top_p: 0.9,
    max_tokens: 512,
    system_prompt: PRESET_SYSTEM_PROMPTS[0],
    retrieval_top_k: 3,
    similarity_threshold: 0.5,
  });
  const [presetIdx, setPresetIdx] = useState(0);
  const [expandedDoc, setExpandedDoc] = useState<number | null>(null);
  const [status, setStatus] = useState<"ok" | "error" | "loading">("loading");
  const bottomRef = useRef<HTMLDivElement>(null);

  // 健康检查
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, []);

  // 自动滚动
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: userMsg.content,
          temperature: params.temperature,
          top_p: params.top_p,
          max_tokens: params.max_tokens,
          system_prompt: params.system_prompt,
          retrieval_top_k: params.retrieval_top_k,
          similarity_threshold: params.similarity_threshold,
        }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer, docs: data.retrieved_docs },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ 后端服务未连接，请确保 FastAPI 服务已启动（端口 8000）。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const addSampleDoc = async () => {
    await fetch(`${API_BASE}/api/knowledge/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        texts: [
          "人工智能（AI）是计算机科学的一个分支，旨在创造能够模拟人类智能的机器。",
          "机器学习是 AI 的一个子集，通过数据训练模型使其自动改进。",
          "大语言模型（LLM）是一种基于 Transformer 架构的深度学习模型。",
          "RAG（检索增强生成）结合了检索系统和语言模型，提高回答的准确性。",
        ],
        metadata: { source: "sample" },
      }),
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* 顶部栏 */}
      <header className="border-b border-purple-500/30 bg-black/30 backdrop-blur">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              🤖 AI 智能知识库问答系统
            </h1>
            <p className="text-sm text-gray-400 mt-1">基于 RAG 的检索增强生成 · 参数可视化调优</p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-4">
              <div className="bg-purple-600/30 border border-purple-400/50 rounded-xl px-4 py-2">
                <div className="text-xs text-purple-300">学号</div>
                <div className="text-lg font-mono font-bold text-white">{STUDENT_ID}</div>
              </div>
              <div className="bg-cyan-600/30 border border-cyan-400/50 rounded-xl px-4 py-2">
                <div className="text-xs text-cyan-300">姓名</div>
                <div className="text-lg font-bold text-white">{STUDENT_NAME}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-6 flex gap-6">
        {/* 左侧：聊天区 */}
        <div className="flex-1 flex flex-col min-h-[calc(100vh-180px)]">
          {/* 状态栏 */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className={`w-2.5 h-2.5 rounded-full ${status === "ok" ? "bg-green-400" : status === "error" ? "bg-red-400 animate-pulse" : "bg-yellow-400 animate-pulse"}`} />
              <span className="text-xs text-gray-400">
                {status === "ok" ? "后端已连接" : status === "error" ? "后端未连接" : "检测中..."}
              </span>
            </div>
            <div className="flex gap-2">
              <button onClick={addSampleDoc} className="text-xs px-3 py-1.5 bg-purple-600/30 border border-purple-400/40 rounded-lg hover:bg-purple-600/50 transition">
                📚 加载示例知识库
              </button>
              <button onClick={() => setShowParams(!showParams)} className="text-xs px-3 py-1.5 bg-cyan-600/30 border border-cyan-400/40 rounded-lg hover:bg-cyan-600/50 transition">
                ⚙️ {showParams ? "收起参数" : "调整参数"}
              </button>
            </div>
          </div>

          {/* 参数面板 */}
          {showParams && (
            <div className="bg-white/5 border border-purple-400/30 rounded-2xl p-5 mb-4 space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-purple-400">✦</span>
                <h3 className="font-semibold text-purple-300">LLM 参数调整</h3>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-gray-400 flex justify-between"><span>Temperature（创造性）</span><span className="text-cyan-400">{params.temperature}</span></label>
                  <input type="range" min="0" max="2" step="0.05" value={params.temperature} onChange={e => setParams(p => ({ ...p, temperature: parseFloat(e.target.value) }))} className="w-full accent-purple-500" />
                  <div className="flex justify-between text-xs text-gray-500"><span>精准</span><span>创意</span></div>
                </div>
                <div>
                  <label className="text-xs text-gray-400 flex justify-between"><span>Top_P（核采样）</span><span className="text-cyan-400">{params.top_p}</span></label>
                  <input type="range" min="0" max="1" step="0.05" value={params.top_p} onChange={e => setParams(p => ({ ...p, top_p: parseFloat(e.target.value) }))} className="w-full accent-purple-500" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 flex justify-between"><span>Max Tokens（最大长度）</span><span className="text-cyan-400">{params.max_tokens}</span></label>
                  <input type="range" min="64" max="2048" step="64" value={params.max_tokens} onChange={e => setParams(p => ({ ...p, max_tokens: parseInt(e.target.value) }))} className="w-full accent-purple-500" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 flex justify-between"><span>检索文档数 (Top_K)</span><span className="text-cyan-400">{params.retrieval_top_k}</span></label>
                  <input type="range" min="1" max="10" step="1" value={params.retrieval_top_k} onChange={e => setParams(p => ({ ...p, retrieval_top_k: parseInt(e.target.value) }))} className="w-full accent-purple-500" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 flex justify-between"><span>相似度阈值</span><span className="text-cyan-400">{params.similarity_threshold}</span></label>
                  <input type="range" min="0" max="1" step="0.05" value={params.similarity_threshold} onChange={e => setParams(p => ({ ...p, similarity_threshold: parseFloat(e.target.value) }))} className="w-full accent-purple-500" />
                </div>
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">系统提示词预设</label>
                <div className="flex gap-2 flex-wrap">
                  {PRESET_SYSTEM_PROMPTS.map((p, i) => (
                    <button key={i} onClick={() => { setPresetIdx(i); setParams(pa => ({ ...pa, system_prompt: p })); }} className={`text-xs px-3 py-1.5 rounded-lg border transition ${presetIdx === i ? "bg-purple-600 border-purple-400 text-white" : "bg-white/5 border-gray-600 text-gray-400 hover:border-purple-400"}`}>
                      预设 {i + 1}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 聊天消息 */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2" style={{ maxHeight: "calc(100vh - 340px)" }}>
            {messages.length === 0 && (
              <div className="text-center py-16 text-gray-500">
                <div className="text-5xl mb-4">🔍</div>
                <p className="text-lg font-medium text-gray-400">开始你的 AI 问答之旅</p>
                <p className="text-sm mt-1">输入问题，知识库将为你检索并生成答案</p>
                <p className="text-xs mt-3 text-purple-400/60">⚠️ 请先点击右上角「加载示例知识库」以加载演示数据</p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${msg.role === "user" ? "bg-gradient-to-r from-purple-600 to-cyan-600 text-white" : "bg-white/10 border border-purple-400/30 text-gray-100"}`}>
                  <div className="text-xs opacity-60 mb-1">{msg.role === "user" ? "🙋 你" : "🤖 AI 助手"}</div>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
                  {msg.docs && msg.docs.length > 0 && (
                    <div className="mt-3 border-t border-white/20 pt-3">
                      <div className="text-xs text-purple-300 mb-2">📄 检索到的文档：</div>
                      {msg.docs.map((doc, j) => (
                        <div key={j} className="mb-2">
                          <button onClick={() => setExpandedDoc(expandedDoc === i * 100 + j ? null : i * 100 + j)} className="text-xs text-left w-full bg-black/20 rounded-lg px-3 py-2 hover:bg-black/40 transition flex justify-between items-center">
                            <span className="truncate flex-1">文档 {j + 1}: {doc.substring(0, 60)}...</span>
                            <span className="ml-2 text-purple-400">{expandedDoc === i * 100 + j ? "▲" : "▼"}</span>
                          </button>
                          {expandedDoc === i * 100 + j && <div className="text-xs text-gray-300 mt-1 px-2 pb-2 bg-black/20 rounded-b-lg">{doc}</div>}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/10 border border-purple-400/30 rounded-2xl px-5 py-3">
                  <div className="text-xs text-purple-300 mb-1">🤖 AI 助手</div>
                  <div className="flex gap-1"><span className="text-purple-400 animate-bounce" style={{ animationDelay: "0ms" }}>●</span><span className="text-purple-400 animate-bounce" style={{ animationDelay: "150ms" }}>●</span><span className="text-purple-400 animate-bounce" style={{ animationDelay: "300ms" }}>●</span></div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* 输入框 */}
          <div className="bg-white/5 border border-purple-400/30 rounded-2xl p-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="输入你的问题... (Enter 发送，Shift+Enter 换行)"
              rows={2}
              className="w-full bg-transparent border-none outline-none resize-none text-white placeholder-gray-500 text-sm"
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-500">支持 Enter 发送 · Shift+Enter 换行</span>
              <button onClick={sendMessage} disabled={!input.trim() || loading} className="px-6 py-2 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-xl font-semibold text-sm disabled:opacity-40 hover:opacity-90 transition">
                {loading ? "生成中..." : "🚀 发送"}
              </button>
            </div>
          </div>
        </div>

        {/* 右侧：项目信息 */}
        <div className="w-72 space-y-4">
          <div className="bg-white/5 border border-purple-400/30 rounded-2xl p-5">
            <h3 className="font-bold text-purple-300 mb-3 flex items-center gap-2">📋 项目信息</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">学号</span><span className="font-mono text-white">{STUDENT_ID}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">姓名</span><span className="text-white">{STUDENT_NAME}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">技术</span><span className="text-cyan-400">RAG + LLM</span></div>
              <div className="flex justify-between"><span className="text-gray-400">前端</span><span className="text-cyan-400">Next.js 14</span></div>
              <div className="flex justify-between"><span className="text-gray-400">后端</span><span className="text-cyan-400">FastAPI</span></div>
              <div className="flex justify-between"><span className="text-gray-400">向量库</span><span className="text-cyan-400">ChromaDB</span></div>
            </div>
          </div>

          <div className="bg-white/5 border border-purple-400/30 rounded-2xl p-5">
            <h3 className="font-bold text-purple-300 mb-3">🔬 可调参数</h3>
            <div className="space-y-3 text-xs">
              {[
                { label: "Temperature", val: params.temperature, desc: "创造性" },
                { label: "Top_P", val: params.top_p, desc: "采样范围" },
                { label: "Max Tokens", val: params.max_tokens, desc: "最大长度" },
                { label: "Top_K (检索)", val: params.retrieval_top_k, desc: "文档数" },
                { label: "相似度阈值", val: params.similarity_threshold, desc: "过滤精度" },
              ].map((p) => (
                <div key={p.label}>
                  <div className="flex justify-between text-gray-400 mb-1"><span>{p.label}</span><span className="text-cyan-400">{p.val}</span></div>
                  <div className="h-1.5 bg-black/40 rounded-full overflow-hidden"><div className="h-full bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full" style={{ width: `${(typeof p.val === 'number' && p.label !== 'Max Tokens') ? p.val * 100 / 2 : p.label === 'Max Tokens' ? p.val / 20 : p.val * 100}%` }} /></div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/5 border border-purple-400/30 rounded-2xl p-5">
            <h3 className="font-bold text-purple-300 mb-3">🚀 快速开始</h3>
            <div className="space-y-2 text-xs text-gray-300">
              <div className="bg-black/30 rounded-lg p-2 font-mono">1. 点击「加载示例知识库」</div>
              <div className="bg-black/30 rounded-lg p-2 font-mono">2. 调整右侧参数滑块</div>
              <div className="bg-black/30 rounded-lg p-2 font-mono">3. 输入问题并发送</div>
              <div className="bg-black/30 rounded-lg p-2 font-mono">4. 观察回答与文档检索</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
