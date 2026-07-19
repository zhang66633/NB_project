# MathModelAgent — 数学建模多智能体辅助系统

基于 LangChain + LangGraph 的多智能体数学建模辅助系统，支持教学与方案输出双模式。

## 项目结构

```
NB_project/
├── PLAN.md                    # 实施计划
├── ARCHITECTURE.md            # 原始架构蓝图
├── docker-compose.yml         # 一键启动
│
├── backend/                   # FastAPI + LangGraph 后端
│   ├── app/
│   │   ├── main.py            # 入口
│   │   ├── config.py          # 配置
│   │   ├── api/               # REST + WebSocket
│   │   ├── core/              # LangGraph 多智能体核心
│   │   │   ├── agents/        # 5 个子智能体
│   │   │   ├── prompts/       # Prompt 模板
│   │   │   └── llm/           # LLM 工厂
│   │   ├── tools/             # LangChain Tool
│   │   ├── knowledge/         # 知识库子系统
│   │   ├── sandbox/           # 代码沙箱
│   │   └── services/          # Redis/会话
│   ├── knowledge_base/        # 知识数据（YAML）
│   └── tests/
│
└── frontend/                  # Vue 3 + shadcn-vue 前端
    └── src/
        ├── pages/             # 页面视图
        ├── components/        # 组件
        ├── stores/            # Pinia
        └── utils/             # 工具
```

## 快速开始

### Docker Compose（推荐）

```bash
docker-compose up
```

### 本地开发

**后端**:
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

**前端**:
```bash
cd frontend
pnpm install
pnpm dev
```

## 技术栈

- **前端**: Vue 3 + Vite + shadcn-vue + Tailwind CSS
- **后端**: FastAPI + LangGraph + LangChain
- **Agent**: LangGraph StateGraph + Command API 动态编排
- **知识库**: YAML + ChromaDB 混合检索

## 开发阶段

参见 [PLAN.md](./PLAN.md) 了解完整的实施计划和开发路线图。
