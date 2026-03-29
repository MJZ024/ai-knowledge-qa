# 🤖 AI 智能知识库问答系统 (AI Knowledge QA System)

> 学号：423830107 | 姓名：毛坚再
> 基于 RAG（检索增强生成）的智能问答系统，支持参数可视化调整

---

## 🎯 项目概述

本项目是一个**前沿 AI 应用**，融合了以下核心技术：

- **RAG（Retrieval-Augmented Generation）** — 检索增强生成，结合知识库检索与 LLM 推理
- **Embedding 向量化** — 将文本转化为向量进行语义检索
- **参数可视化调优** — 实时调整 LLM 参数，观察效果变化
- **前后端分离架构** — Next.js + FastAPI + Docker

---

## 🧩 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Next.js)                       │
│  学号：423830107  姓名：毛坚再   参数调整面板   聊天界面   │
└──────────────────────┬──────────────────────────────────┘
                        │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                   后端 (FastAPI)                         │
│  RAG Pipeline │ LLM 调用 │ 参数管理 │ 知识库检索       │
└───────┬──────────────────────┬──────────────────────────┘
        │                      │
┌───────▼──────┐       ┌───────▼──────┐
│  ChromaDB    │       │  Ollama /    │
│  向量数据库   │       │  OpenAI API  │
└──────────────┘       └──────────────┘
```

---

## 🚀 快速部署

### 方式一：Docker 一键部署（推荐）

```bash
git clone https://github.com/YOUR_USERNAME/ai-knowledge-qa.git
cd ai-knowledge-qa
docker-compose up --build
```

访问 http://localhost:3000

### 方式二：本地开发

**后端：**
```bash
cd backend
pip install -r requirements.txt
# 设置环境变量（见 .env.example）
uvicorn main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ 参数说明

| 参数 | 说明 | 可调范围 | 默认值 |
|------|------|---------|--------|
| `temperature` | 创造性/准确性 | 0.0 ~ 2.0 | 0.7 |
| `top_p` | 核采样 | 0.0 ~ 1.0 | 0.9 |
| `max_tokens` | 最大生成长度 | 64 ~ 4096 | 512 |
| `system_prompt` | 系统提示词 | 自定义 | 助手角色 |
| `retrieval_top_k` | 检索文档数 | 1 ~ 10 | 3 |
| `similarity_threshold` | 相似度阈值 | 0.0 ~ 1.0 | 0.5 |

---

## 📁 项目结构

```
ai-knowledge-qa/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── api/routes.py        # API 路由
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   ├── retriever.py     # RAG 检索器
│   │   └── llm.py           # LLM 调用封装
│   └── requirements.txt
├── frontend/                # Next.js 14 (App Router)
│   ├── src/app/             # 页面
│   ├── src/components/      # 组件
│   └── src/lib/            # 工具函数
├── docs/                    # 文档
├── docker-compose.yml       # 容器编排
└── README.md
```

---

## 📌 依赖说明

- **Ollama**（本地 LLM，可选）: https://ollama.ai
- **ChromaDB**（向量数据库）
- **LangChain**（RAG 框架）
- **Next.js 14**（前端框架）
- **TailwindCSS**（样式）

---

## 📝 作业要求

- ✅ 前端界面显示学号：423830107，姓名：毛坚再
- ✅ AI 问答功能（RAG 检索增强）
- ✅ 参数可视化调整
- ✅ 支持迁移部署（Docker）
- ✅ 代码开源可查

---

> 🎓 本项目为课程作业项目，展示前沿 AI 技术应用
> 学号：423830107 | 姓名：毛坚再
