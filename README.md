# MathModelAgent — 数学建模多智能体辅助系统

基于 FastAPI + LangGraph + Vue 3 的数学建模辅助系统。三种使用模式：

| 模式 | 入口 | 说明 |
|------|------|------|
| **自由问答** | `/chat` | 纯对话咨询，SSE 流式输出，多轮上下文（滑动窗口），响应快 |
| **教学模式** | `/teach` | 苏格拉底式引导提问，培养建模思维，不直接给答案 |
| **方案模式** | `/solution` | 多智能体流水线（分析→建模→求解→验证→写作），WebSocket 实时进度 |

另有知识库管理（`/knowledge`，仅贡献者）、API Key 管理（`/apikeys`）、设置（`/settings`）页面。未登录也可使用对话与设置功能（本地游客模式）。

## 快速开始

### 1. 配置 LLM API Key

启动前端后访问 `http://localhost:5173/apikeys` 添加 DeepSeek Key（默认模型 `deepseek-chat`），
或直接写 `backend/data/apikeys.json`。支持任何 OpenAI 兼容协议的服务商。

### 2. 启动后端

```bash
cd backend
pip install -e .          # 或 poetry install
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> 建议不带 `--reload`（reloader 在本项目中有静默退出现象）。
> Redis 非必须：无 Redis 时自动回退 fakeredis（同进程 pub/sub），WebSocket 进度推送照常工作。

### 3. 启动前端

```bash
cd frontend
pnpm install
pnpm dev                  # http://localhost:5173
```

前端通过 Vite 代理将 `/api` 转发到 `127.0.0.1:8000`；WebSocket 直连后端（见 `frontend/.env.development`）。

### Docker Compose

```bash
docker-compose up
```

## 项目结构

```
math_agent/
├── PLAN.md                    # 实施计划与进度（权威文档）
├── docker-compose.yml
│
├── backend/                   # FastAPI + LangGraph 后端
│   ├── app/
│   │   ├── main.py            # 入口（/api 前缀）
│   │   ├── config.py          # 配置（含各 agent 角色模型，CHAT_MODEL 可配）
│   │   ├── api/
│   │   │   ├── router.py      # REST：任务/API Key/文件/认证
│   │   │   ├── chat_routes.py # POST /api/chat — SSE 流式对话（chat/teach 双模式）
│   │   │   ├── ws.py          # /api/ws/task/{id} — 任务进度推送
│   │   │   └── knowledge_routes.py
│   │   ├── core/              # LangGraph 编排（agents/prompts/llm 工厂）
│   │   ├── knowledge/         # 知识库子系统（ChromaDB 混合检索）
│   │   └── services/          # 会话 / Redis Pub-Sub（fakeredis 回退）
│   └── knowledge_base/        # 知识数据（YAML 真源）
│
└── frontend/                  # Vue 3 + Vite + shadcn-vue 前端
    └── src/
        ├── pages/             # chat / teach / solution / knowledge / apikeys / settings ...
        ├── components/        # ChatArea / Bubble（Markdown+KaTeX 流式渲染）/ AppSidebar ...
        ├── composables/       # useStreamChat（SSE 对话复用逻辑）
        ├── stores/            # Pinia：chatSession（会话持久化）/ task（WS 进度）/ auth
        └── apis/              # chatApi（fetch+ReadableStream 解析 SSE）等
```

## 技术栈

- **前端**: Vue 3 + Vite + TypeScript + shadcn-vue + Tailwind CSS + Pinia
- **后端**: FastAPI + LangGraph（多智能体编排）+ LangChain
- **实时**: SSE（对话流式）+ WebSocket（任务进度，Redis Pub/Sub 或 fakeredis）
- **知识库**: YAML 真源 + ChromaDB（BM25 + 向量 + rerank 混合检索）
- **LLM**: DeepSeek（默认）/ 任意 OpenAI 兼容接口，按 agent 角色配置模型

## 备注

- `ARCHITECTURE.md` 为早期 Next.js 方案蓝图，**已废弃**，以 `PLAN.md` 与实际代码为准。
- `backend/data/`（apikeys/sessions/chroma_db）含本地密钥与运行时数据，已被 `.gitignore` 排除，勿提交。
- 默认分支为 `main`。

## 开发阶段

参见 [PLAN.md](./PLAN.md) 了解完整的实施计划和开发路线图。
