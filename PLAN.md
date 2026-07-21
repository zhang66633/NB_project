# 数学建模多智能体系统 — 实施计划

> ⚠️ **蓝图说明**：`ARCHITECTURE.md` 为早期废弃方案（Next.js + MUI），**一律不作参考**，以本文档为准。
> 版本: v0.2(对齐版) | 日期: 2026-07-21 | 项目目录: `math_agent/`（原 NB_project 已并入，GitHub 远程 `zhang66633/NB_project`）
>
> ### 📌 当前进度对齐（2026-07-21 审查快照）
> | 维度 | 状态 | 说明 |
> |------|------|------|
> | 后端核心编排 `workflow.py` | ✅ 完成 | 5 阶段 StateGraph + 状态机 + WS 推送 |
> | 5 阶段 Agent 节点 `nodes.py` | ✅ 完成 | 已实现真实 LLM 调用（classify/retrieve/model/solve/verify+write），非占位 |
> | 知识库 RAG（代码） | ✅ 就绪 | 混合检索 + Chroma + Tool 封装 + chain 均已实现 |
> | 知识库（源数据） | 🔴 缺失 | `knowledge_base/` 为空、Chroma 未初始化 → **检索全程失效** |
> | WebSocket 进度推送 | ⚠️ 缺完成信号 | `ws.py` 订阅 Redis 转发；**未推 `task_end`/final_response，不在完成时报断** |
> | 前端页面 / API | ✅ 完成 | Chat / Task / 登录 / 密钥管理 / 认证均接真实 API |
> | 认证 / 密钥管理 | ✅ 完成 | GitHub OAuth + `pages/apikeys` + `/api/apikeys` |
> | **端到端联调** | 🔴 未跑通 | 缺知识库数据 + 未做真实任务冒烟，**下一步首要阻塞** |

---

## Context

构建一个 **Web 版** 多智能体数学建模辅助系统：

- **前端**: 复刻 [MathModelAgent](https://github.com/jihe520/MathModelAgent) 开源项目的前端（Vue 3 + shadcn-vue + Tailwind），适配我们自己的后端 API
- **后端**: 自研 **LangChain + LangGraph** 多智能体编排 + FastAPI Web API + WebSocket 实时推送（不参考 MathModelAgent 后端架构）
- **多智能体**: 1 个主编排器 + 5 个子智能体（分析→建模→求解→验证→写作），动态编排 + 验证回退
- **双模式**: 教学模式（苏格拉底式引导）+ 方案输出模式（完整方案）

---

## Technology Stack

| 类别 | 选型 | 说明 |
|------|------|------|
| **前端** | Vue 3.5 + Vite 6 + TypeScript 5.7 | 与源项目一致 |
| **前端 UI** | **shadcn-vue** (Reka UI 2.0) + Tailwind CSS 3 | 与源项目一致，非 Element Plus |
| **前端包管理** | pnpm 10.6 | 与源项目一致 |
| **前端状态** | Pinia 3 + pinia-plugin-persistedstate | 持久化会话 |
| **前端渲染** | Marked + KaTeX + highlight.js + md-editor-v3 | LaTeX 公式 + 代码高亮 + Markdown 编辑 |
| **前端 Notebook** | render-jupyter-notebook-vue | Jupyter 风格代码单元格渲染 |
| **前端图标** | lucide-vue-next | 轻量开源图标 |
| **前端代码质量** | Biome (lint + format) | 与源项目一致 |
| **后端框架** | FastAPI + Uvicorn | 异步 Web + 原生 WebSocket |
| **实时通信** | WebSocket + Redis Pub/Sub | 解耦 agent 执行与消息推送 |
| **Agent 框架** | **LangGraph >= 0.2.0** (Command API) | LangChain 官方多智能体方案 |
| **LLM 抽象** | LangChain >= 0.3.0 | 统一 ChatModel/Tool/Prompt/Retriever |
| **LLM 提供商** | LLMFactory（Anthropic + OpenAI 兼容） | 每 agent 独立模型配置 |
| **向量数据库** | ChromaDB (langchain-chroma) | 本地零运维 |
| **知识库** | YAML + Pydantic 校验 | 人可读，Git 版本控制 |
| **代码沙箱** | subprocess → Docker 升级路径 | 渐进式安全策略 |
| **Python 包管理** | Poetry | 依赖锁定 |
| **部署** | Docker Compose + 本地开发双模式 | 灵活适配 |

---

## Project Structure

```
math_agent/
├── ARCHITECTURE.md                  # 原始架构蓝图
├── PLAN.md                          # 本文件：实施计划
├── README.md
├── docker-compose.yml
│
├── backend/                         # FastAPI + LangGraph 后端
│   ├── pyproject.toml
│   ├── .env.example
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── config.py                # 配置管理
│   │   ├── api/                     # HTTP + WebSocket 接口
│   │   │   ├── router.py
│   │   │   ├── ws.py
│   │   │   └── schemas/
│   │   ├── core/                    # LangGraph 多智能体核心
│   │   │   ├── workflow.py          # StateGraph 构建
│   │   │   ├── state.py             # AgentState 定义
│   │   │   ├── nodes.py             # 图节点函数
│   │   │   ├── router.py            # Command 路由逻辑
│   │   │   ├── agents/              # 5 个子智能体
│   │   │   ├── prompts/             # Prompt 模板
│   │   │   └── llm/                 # LLM 工厂
│   │   ├── tools/                   # LangChain Tool 定义
│   │   ├── knowledge/               # 知识库子系统
│   │   │   ├── schemas.py           # Pydantic 数据模型
│   │   │   ├── loader.py            # YAML 加载器
│   │   │   ├── retriever.py         # 混合检索器
│   │   │   └── embedder.py          # 向量化管道
│   │   ├── sandbox/                 # 代码执行沙箱
│   │   └── services/                # Redis / 会话管理
│   ├── knowledge_base/              # 知识数据（Git 跟踪）
│   │   ├── methods/                 # 方法卡片（YAML）
│   │   ├── papers/                  # 真题论文（YAML）
│   │   └── templates/               # 模板框架（YAML）
│   ├── data/chroma_db/              # 向量持久化
│   └── tests/
│
└── frontend/                        # Vue 3 + Vite 前端
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── biome.json
    ├── components.json              # shadcn-vue 配置
    ├── index.html
    └── src/
        ├── main.ts                  # Vue 入口
        ├── App.vue
        ├── router/index.ts          # 5 条路由
        ├── pages/                   # 页面视图
        │   ├── index.vue            # 首页
        │   ├── login/index.vue      # 登录
        │   ├── chat/index.vue       # 对话
        │   ├── task/index.vue       # 任务工作区
        │   └── example/[id].vue     # 例题详情
        ├── components/
        │   ├── ui/                  # shadcn-vue 组件（24 个）
        │   ├── AgentEditor/         # Agent 配置编辑器
        │   ├── ChatArea.vue         # 对话区域
        │   ├── NotebookArea.vue     # Notebook 展示区
        │   └── ...                  # 其他业务组件
        ├── stores/                  # Pinia 状态管理
        ├── apis/                    # HTTP API 调用
        ├── utils/                   # 工具函数
        ├── lib/                     # shadcn 工具
        └── assets/                  # 静态资源
```

---

## LangGraph Multi-Agent Architecture

### AgentState

```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    mode: Literal["teach", "execute"]
    session_id: str

    # 问题理解
    problem_raw: str
    problem_type: str              # optimization/prediction/evaluation/...
    problem_complexity: Literal["simple", "composite", "innovative"]
    data_dependency: Literal["theoretical", "given_data", "self_collect"]

    # KB 上下文
    kb_methods: List[dict]
    kb_papers: List[dict]
    kb_templates: List[dict]

    # 动态执行计划
    execution_plan: List[str]      # ["analysis", "modeling", "solving", ...]
    current_step_index: int
    retry_count: int
    max_retries: int

    # 各 Agent 输出
    analysis_output: Optional[str]
    model_output: Optional[str]
    solving_output: Optional[str]
    verification_output: Optional[str]
    writing_output: Optional[str]

    # 回退控制
    verification_passed: Optional[bool]
    verification_feedback: Optional[str]
    rollback_target: Optional[str]

    # 进度事件（WebSocket 推送用）
    progress_events: List[dict]
```

### 图拓扑

```
START → classify_problem → retrieve_knowledge → plan_execution
                                                      │
                                         Command(goto=first_agent)
                                                      │
                    ┌─────────────────────────────────┼─────────────────────────────┐
                    ▼                                 ▼                             ▼
            analysis_agent                     modeling_agent                writing_agent
                    │                                 │                             │
                    └────────────┬────────────────────┘─────────────────────────────┘
                                 │
                     每个 agent 返回 Command:
                       → 成功: goto=next_agent (按 plan)
                       → 验证失败: goto=rollback_target
                       → 计划完成: goto=format_response
                                 │
                                 ▼
                        format_response → END
```

### Tool 分配

| Agent | 绑定工具 |
|-------|---------|
| Analysis | `search_method_cards`, `search_similar_papers`, `get_analysis_framework` |
| Modeling | `search_method_cards`, `compare_methods`, `get_analysis_framework` |
| Solving | `execute_python_code`, `install_package`, `generate_synthetic_data` |
| Verification | `execute_python_code`, `search_method_cards` |
| Writing | `search_similar_papers` |

---

## 后端 API 设计

### REST

| Method | Path | 说明 |
|--------|------|------|
| `POST` | `/api/tasks` | 创建建模任务 |
| `GET` | `/api/tasks/{id}` | 获取任务详情 |
| `GET` | `/api/tasks/{id}/messages` | 获取历史消息 |
| `POST` | `/api/tasks/{id}/cancel` | 取消任务 |
| `GET` | `/api/tasks` | 任务列表 |
| `POST` | `/api/files/upload` | 上传文件 |
| `GET` | `/api/files/{id}` | 下载文件 |
| `GET` | `/api/apikeys` | API Key 列表 |
| `POST` | `/api/apikeys` | 添加 API Key |
| `DELETE` | `/api/apikeys/{id}` | 删除 API Key |
| `GET` | `/api/health` | 服务健康检查 |

### WebSocket

| Path | 说明 |
|------|------|
| `WS /ws/task/{task_id}` | 实时推送 agent 执行消息 |

---

## 前端复刻方案

### 源项目与我们的改动

| 改动点 | 源项目 | 我们的方案 |
|--------|--------|-----------|
| Agent 类型 | 4 种 (Coordinator/Modeler/Coder/Writer) | **5 种** (Analysis/Modeling/Solving/Verification/Writing) + Orchestrator |
| 新增 Agent Editor | 无 | 新增 `AnalysisEditor.vue` + `VerificationEditor.vue` |
| API 端点 | 源项目 API 格式 | 适配我们的 FastAPI REST 端点 |
| WebSocket 消息格式 | 源项目消息结构 | 保持兼容，增加我们的 agent 类型 |

### 前端组件清单

**shadcn-vue UI 组件（24 个）**: alert, avatar, breadcrumb, button, card, collapsible, dialog, dropdown-menu, input, label, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, stepper, switch, tabs, tetris, textarea, toast, tooltip

**业务组件**: AppSidebar, Bubble, ChatArea, FileConfirmDialog, Files, LoginForm, ModelingExamples, NavUser, NotebookArea, NotebookCell, SearchForm, ServiceStatus, SystemMessage, Tree, UserStepper, VersionSwitcher

**Agent 编辑器**: CoderEditor, ModelerEditor, WriterEditor, AnalysisEditor (新增), VerificationEditor (新增)

---

## 实施阶段

### Phase 0 — 脚手架 + 知识库 (预计 3-4 天)

**目标**: 前后端骨架可启动 + 知识库可检索

1. 后端: Poetry + FastAPI 骨架，`backend/app/main.py` 可启动
2. 前端: pnpm 安装全部依赖，Vite 可启动
3. shadcn-vue 初始化 + 24 个 ui 组件安装
4. 知识库 Schema (Pydantic) + Loader (YAML)
5. 首批知识内容: 10 张 P0 方法卡片 + 3 篇论文 + 2 个模板
6. ChromaDB 向量化管道
7. Docker Compose 文件 (backend + frontend + redis)

**可交付**: `docker-compose up` 全栈启动；`GET /api/health` 返回 200

### Phase 1 — 前端壳 + 后端编排核心 (预计 5-7 天)

**目标**: 前端主要页面能渲染，后端 LangGraph 图能走通分类→检索→分析

**前端**: Router + 路由配置 / 首页（问题输入+模式选择）/ Chat 页面 / Login 页面 / WebSocket 基础连接

**后端**: AgentState + StateGraph / classify_problem / retrieve_knowledge / plan_execution / analysis_agent / WebSocket 端点 / tasks CRUD

**可交付**: 前端输入问题 → WS 推送分类结果 → Chat 页面展示分析输出

### Phase 2 — 建模 + 求解 + Notebook (预计 5-7 天)

**目标**: 完整的建模流水线 + Notebook 渲染

**前端**: Task 工作区页面 / NotebookArea + NotebookCell / Files + Tree / AgentEditor 系列

**后端**: modeling_agent / sandbox / solving_agent (ReAct) / 代码执行结果推送

**可交付**: 建模问题 → 前端展示模型公式 + 代码 + 执行结果（Notebook 格式）

### Phase 3 — 验证 + 写作 + 回退 (预计 5-7 天)

**目标**: 全部 5 Agent 就位，验证回退循环，论文输出

**后端**: verification_agent / Command 回退逻辑 / writing_agent / 论文 LaTeX 渲染

**前端**: 论文预览页面 / 回退状态展示 / 消息下载功能

**可交付**: 全流程 — 问题 → 实时展示进度 → 验证(含回退) → 论文

### Phase 4 — 双模式 + 完善 (预计 3-4 天)

**目标**: 教学模式可用，体验打磨

1. 所有 agent 的教学模式 prompt 变体（苏格拉底式）
2. 前端模式切换 toggle（teach/solve）
3. 教学模式下引导式对话展示
4. AnalysisEditor + VerificationEditor 新增
5. Example 页面（3 道例题 + 配图）

**可交付**: `/teach` 引导式提问；`/solve` 完整方案输出

### Phase 5 — 持续完善

1. 知识库扩充（P1/P2 → 40-50 张卡片）
2. LLMFactory 多提供商支持
3. 性能优化（LLM 缓存、并行检索）
4. Docker 沙箱升级
5. 测试覆盖

---

## 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 前端 UI | shadcn-vue + Tailwind（非 Element Plus） | 与源项目一致，现代设计，Tree-shaking 好 |
| 前端包管理 | pnpm | 与源项目一致 |
| 后端 | LangGraph + FastAPI（自主设计） | 动态编排+回退远优于源项目的顺序调用 |
| 路由方式 | LangGraph Command API | 路由+状态更新一体化，比条件边更简洁 |
| Agent 数量 | 5 个 + Orchestrator（源项目只有 4 个） | 按 ARCHITECTURE.md 的设计，多了验证 Agent |
| WebSocket | Redis Pub/Sub 解耦 | 匹配前端 TaskWebSocket；支持水平扩展 |
| 代码沙箱 | subprocess → Docker | 渐进式策略 |

---

## RAG 知识库子系统设计

> 内存: KB-RAG-001 | 状态: 代码就绪、源数据缺失（🔴 阻塞） | 更新时间: 2026-07-21

> 🔴 **数据初始化缺口（2026-07-21）**：当前 `knowledge_base/` 目录**为空/不存在**，`data/chroma_db/` 未建立。代码（混合检索 + Chroma + Tool + chain）均已实现，但**不放入 YAML 源数据并跑一次索引构建，检索将全程失效**。待办：① 填充 `knowledge_base/methods|papers|templates` 的 YAML；② 运行 `python -m app.knowledge.indexer`（或增量索引）生成 Chroma；③ 后端冒烟验证 `retrieve_knowledge` 节点返回结果。若索引脚本缺失需补。

### 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户 / 前端                            │
│        ┌──────────────────────────────────────┐         │
│        │  /api/knowledge/*  (管理 API)         │         │
│        │  /api/tasks       (Agent 调用)       │         │
│        └──────────┬───────────────────────────┘         │
└───────────────────┼─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│                 FastAPI 后端                              │
│                                                          │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │ knowledge/       │  │ core/agents/                 │  │
│  │  schemas.py ✅   │  │  analysis_agent.py           │  │
│  │  loader.py   ✅  │  │  modeling_agent.py           │  │
│  │  embedder.py ✅  │  │  ...                          │  │
│  │  indexer.py  ✅  │  │      ↓ 调用                   │  │
│  │  retriever.py🔧  │  │                              │  │
│  │  reranker.py 🆕  │  │  ┌──────────────────────┐   │  │
│  │  chain.py    🆕  │  │  │ tools/kb_tools.py 🆕 │   │  │
│  │  api.py      🆕  │──┤  │ search_method_cards  │   │  │
│  └─────────────────┘  │  │ search_similar_papers │   │  │
│                       │  │ get_analysis_framework│   │  │
│                       │  └──────────┬───────────┘   │  │
│                       │             │                │  │
│                       │  ┌──────────▼───────────┐   │  │
│                       │  │ RAG Chain (chain.py)  │   │  │
│                       │  │ 检索 →重排→格式化→生成 │   │  │
│                       │  └──────────────────────┘   │  │
│                       └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│                   数据层                                   │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │ knowledge_base/  │  │ data/chroma_db/              │  │
│  │  methods/*.yaml  │  │  (向量持久化)                  │  │
│  │  papers/*.yaml   │  │                               │  │
│  │  templates/*.yaml│  │                               │  │
│  └─────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 文件清单

```
backend/app/
├── knowledge/
│   ├── __init__.py          # 导出公共接口
│   ├── schemas.py           # [已有] Pydantic 数据模型
│   ├── loader.py            # [已有] YAML 加载器
│   ├── embedder.py          # [改造] 支持增量索引+可配置 embedding
│   ├── indexer.py           # [改造] 支持 --incremental 模式
│   ├── retriever.py         # [改造] 增加 MMR + 元数据过滤 + 分数返回
│   ├── reranker.py          # 🆕 LLM 重排序模块
│   ├── chain.py             # 🆕 RAG Chain (LangChain Runnable)
│   └── api.py               # 🆕 知识库管理 API 路由
│
├── tools/
│   ├── __init__.py          # [已有]
│   └── kb_tools.py          # 🆕 封装为 LangChain Tool
│
├── core/
│   └── prompts/
│       ├── __init__.py      # [已有]
│       ├── analysis.py      # 🆕 分析 Agent Prompt 模板
│       ├── modeling.py      # 🆕 建模 Agent Prompt 模板
│       └── rag.py           # 🆕 通用 RAG 上下文格式化模板
│
└── api/
    ├── router.py            # [改造] 注册 knowledge 路由
    └── knowledge_routes.py  # 🆕 知识库 CRUD + 搜索 API
```

### 实施步骤

#### Step 1: 增强 HybridRetriever `retriever.py` 🔴 高优先级

**现存问题**:
- 返回结果无相关性分数，无法按质量排序
- 无 MMR (Maximum Marginal Relevance) 去重
- 向量搜索不支持元数据过滤 (type/year/competition/quality_rating)
- `_filter_by_tags` 方法返回的是新建 Document，page_content 不完整

**改造内容**:

```python
class HybridRetriever(BaseRetriever):
    """混合检索器: 标签过滤 + 语义搜索 + MMR 重排"""

    def _get_relevant_documents(
        self,
        query: str,
        *,
        metadata_filter: dict | None = None,  # {"type": "paper", "year": 2023}
        use_mmr: bool = True,
        mmr_lambda: float = 0.5,               # 相关性 vs 多样性
        k: int = 5,
        fetch_k: int = 20,                     # 初检索数量 (用于 MMR)
        **kwargs,
    ) -> list[Document]:
        """检索文档: 语义搜索 → MMR 重排 → 标签补充 → 合并去重"""
        ...

    def similarity_search_with_score(
        self, query: str, k: int = 5
    ) -> list[tuple[Document, float]]:
        """带分数的语义搜索"""
        ...
```

**关键改进**:
- 分数归一化: 标签匹配赋予固定权重 (0.9)，向量分数归一化到 [0,1]
- MMR 算法: `λ * relevance - (1-λ) * max_similarity_to_already_selected`
- `fetch_k > k` 先多取后精选，提升召回率
- 元数据过滤透传给 ChromaDB `where` 参数

---

#### Step 2: LLM 重排序 `reranker.py` 🆕 🟡 中优先级

用 LLM 对候选文档做 pairwise 比较，进一步优化检索精度。

```python
class LLMReranker:
    """用 LLM 对检索结果重排序"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def rerank(
        self, query: str, documents: list[Document], top_k: int = 5
    ) -> list[Document]:
        """
        流程:
        1. 对每个 doc 构造评分 prompt: "文档与问题的相关性(1-5)"
        2. LLM 批量打分
        3. 按分数降序取 top_k
        """
        ...
```

**评分 Prompt 设计**:
```
评估以下文档与用户问题的相关性 (1-5 分):
用户问题: {query}
---
文档 [{i}]: {doc.page_content[:500]}
---
返回 JSON: [{"index": 0, "score": 4, "reason": "..."}, ...]
```

---

#### Step 3: LangChain Tool 封装 `tools/kb_tools.py` 🆕 🔴 高优先级

Agent 通过 Tool 调用知识库。按 PLAN.md 的 Tool 分配表实现 3 个 Tool。

```python
from langchain_core.tools import tool

@tool
def search_method_cards(query: str, problem_type: str = "") -> str:
    """搜索数学建模方法卡片。输入问题描述或关键词，返回最匹配的方法原理、
    适用条件、典型场景和代码示例。

    Args:
        query: 问题描述或方法关键词 (如 "资源分配优化")
        problem_type: 问题类型过滤 (optimization/prediction/evaluation/...)
    """
    ...

@tool
def search_similar_papers(query: str, problem_type: str = "") -> str:
    """搜索历年竞赛真题论文。输入问题描述，返回相似赛题的结构化分析，
    包括建模思路、创新点和可借鉴之处。

    Args:
        query: 问题描述
        problem_type: 问题类型过滤
    """
    ...

@tool
def get_analysis_framework(problem_type: str) -> str:
    """获取问题分析框架模板。根据问题类型返回对应的分析步骤框架，
    包括引导性问题、决策树和检查清单。

    Args:
        problem_type: 问题类型 (optimization/prediction/evaluation/statistics)
    """
    ...
```

**Tool 输出格式** (关键——决定 Agent 能否有效利用):

```
[方法卡片] mc_001 线性规划 (相关性: 0.92)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
适用场景: 生产计划、资源分配、运输调度
核心原理: min c^Tx, s.t. Ax ≤ b, x ≥ 0
适用条件: 目标函数和约束均为线性
常见误用: 忽略非负约束、约束遗漏致无界解
代码示例 (python):
  from scipy.optimize import linprog
  ...
关联卡片: mc_002, mc_006
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Tool → Agent 绑定**:

```python
# core/nodes.py 中创建 agent 节点时
analysis_llm = llm.bind_tools([
    search_method_cards,
    search_similar_papers,
    get_analysis_framework,
])
```

---

#### Step 4: RAG Chain `chain.py` 🆕 🔴 高优先级

将检索→重排→格式化→生成串联为 LangChain Runnable。

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def create_rag_chain(
    llm: BaseChatModel,
    retriever: BaseRetriever,
    prompt_template: ChatPromptTemplate,
) -> Runnable:
    """创建标准 RAG 链: 检索 → 格式化上下文 → 注入 Prompt → LLM 生成"""
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

def format_docs(docs: list[Document]) -> str:
    """将检索结果格式化为 LLM 可消费的上下文字符串"""
    type_labels = {
        "method_card": "方法卡片",
        "paper": "真题论文",
        "template": "分析框架",
    }
    parts = []
    for i, doc in enumerate(docs):
        meta = doc.metadata
        label = type_labels.get(meta.get("type", ""), "文档")
        score = meta.get("score", "")
        score_str = f" (相关性: {score:.2f})" if score else ""
        parts.append(
            f"### [{label}] {meta.get('name', '')}{score_str}\n"
            f"{doc.page_content}\n"
        )
    return "\n---\n".join(parts)
```

---

#### Step 5: Prompt 模板 `core/prompts/` 🆕 🟡 中优先级

为每个 Agent 编写含 RAG 上下文的 System Prompt。

```python
# core/prompts/analysis.py
ANALYSIS_SYSTEM_PROMPT = """你是一个数学建模问题分析专家。你的任务是基于知识库上下文，
对用户问题做结构化分析。

## 可用知识库上下文
{context}

## 分析要求
1. **问题类型判定**: 明确问题属于哪种数学建模类型(优化/预测/评价/...)
2. **关键要素提取**: 决策变量、目标函数、约束条件、隐含假设
3. **方法推荐**: 基于知识库推荐 2-3 个可能适用的方法，说明理由
4. **难度评估**: 单模型可解 / 需组合模型 / 需创新建模

## 引用规范
- 引用知识库内容时标注来源，如 [mc_001]、[paper_2023C_01]
- 如果知识库上下文不足以覆盖当前问题，基于你的数学知识补充
"""
```

---

#### Step 6: 知识库管理 API `api/knowledge_routes.py` 🆕 🟡 中优先级

```python
# REST API 端点
GET    /api/knowledge/search      # 搜索 (q, type, k)
POST   /api/knowledge/reindex     # 触发重新索引
GET    /api/knowledge/stats       # 知识库统计 (各类别数量)
GET    /api/knowledge/methods     # 方法卡片列表
GET    /api/knowledge/methods/{id} # 方法卡片详情
GET    /api/knowledge/papers      # 论文列表
GET    /api/knowledge/papers/{id}  # 论文详情
GET    /api/knowledge/templates   # 模板列表
GET    /api/knowledge/templates/{id} # 模板详情
```

---

### 与 LangGraph Agent 集成

在 `retrieve_knowledge` 节点中调用检索器，结果写入 AgentState：

```python
def retrieve_knowledge(state: AgentState) -> dict:
    """检索知识库: 语义搜索 + 标签过滤 → 写入 state"""
    problem_type = state["problem_type"]
    query = state["problem_raw"]

    # 并行检索三层知识库
    methods = retriever._get_relevant_documents(
        query, metadata_filter={"type": "method_card"},
        problem_type=problem_type, k=5
    )
    papers = retriever._get_relevant_documents(
        query, metadata_filter={"type": "paper"},
        problem_type=problem_type, k=3
    )
    templates = retriever._get_relevant_documents(
        query, metadata_filter={"type": "template"},
        problem_type=problem_type, k=2
    )

    return {
        "kb_methods": [doc_to_dict(d) for d in methods],
        "kb_papers": [doc_to_dict(d) for d in papers],
        "kb_templates": [doc_to_dict(d) for d in templates],
    }
```

流程示意:
```
classify_problem → 识别 problem_type = "optimization"
        │
        ▼
retrieve_knowledge → 三层检索 (并行)
        │              search_method_cards("资源分配优化", "optimization")
        │              search_similar_papers("资源分配", "optimization")
        │              get_analysis_framework("optimization")
        │              结果写入 state.kb_methods/kb_papers/kb_templates
        ▼
analysis_agent → System Prompt 注入 KB 上下文 → 结构化分析输出
```

---

### 实施优先级与工时

| Step | 内容 | 优先级 | 工时 | 依赖 |
|------|------|--------|------|------|
| Step 1 | `retriever.py` 增强 (分数/MMR/过滤) | 🔴 高 | 0.5d | 无 |
| Step 3 | `tools/kb_tools.py` LangChain Tool 封装 | 🔴 高 | 0.5d | Step 1 |
| Step 4 | `chain.py` RAG Chain | 🔴 高 | 0.5d | Step 1 |
| Step 5 | Prompt 模板 (RAG 上下文格式化) | 🟡 中 | 0.5d | Step 4 |
| Step 2 | `reranker.py` LLM 重排序 | 🟡 中 | 0.5d | Step 1 |
| Step 6 | `api/knowledge_routes.py` 管理 API | 🟡 中 | 1d | Step 1 |
| Step 7 | 增量索引 (`embedder.py` 改造) | 🟢 低 | 0.5d | 无 |
| Step 8 | 前端知识库界面 | 🟢 低 | 1.5d | Step 6 |

**执行顺序**: Step 1 → Step 3 → Step 4 → Step 5 → Step 2 → Step 6 → Step 7 → Step 8

核心回路 (Step 1→3→4→5) 打通后，Agent 即具备 RAG 能力。

---

## 如何录入知识

提供三种方式向知识库添加数学建模资料：

### 方式一：LLM 辅助批量导入（推荐）

适合：手头有教材段落、论文摘要、笔记等原始文本

```bash
# 1. 将原始资料 (.txt/.md) 放入 knowledge_base/_import_queue/
#    每个文件放一种方法/一篇论文/一个模板的描述文本

# 2. 运行 LLM 批量提取
cd backend
python -m scripts.import_knowledge --type method --batch    # 批量导入方法卡片
python -m scripts.import_knowledge --type paper --batch     # 批量导入论文
python -m scripts.import_knowledge --type template --batch  # 批量导入模板

# 3. 单文件导入
python -m scripts.import_knowledge --input notes.txt --type method --name "粒子群算法"

# 4. 增量更新向量索引
python -m app.knowledge.indexer --incremental

# 5. 在 /knowledge 页面搜索验证
```

LLM 会自动从原始文本中提取：方法名、原理、公式、适用条件、代码示例等结构化字段。

### 方式二：空白模板生成

适合：想手动编写知识卡片

```bash
cd backend

# 生成方法卡片模板
python -m scripts.generate_template method --name "粒子群算法" --category optimization

# 生成论文模板
python -m scripts.generate_template paper --title "2024国赛A题" --year 2024 --competition 国赛 --problem-id A

# 生成分析框架模板
python -m scripts.generate_template template --name "图论问题分析框架"
```

模板生成后，手动编辑 YAML 文件填写内容，然后运行增量索引。

### 方式三：手动编写 YAML

适合：精确控制内容

目录结构：
```
knowledge_base/
├── methods/                  # 方法卡片（按类别分子目录）
│   ├── optimization/
│   │   └── linear_programming.yaml
│   ├── prediction/
│   │   └── arima.yaml
│   └── evaluation/
│       └── ahp.yaml
├── papers/                   # 真题论文（按竞赛分子目录）
│   └── 国赛/
│       └── 2023C_vegetable_pricing.yaml
├── templates/                # 分析框架
│   └── optimization_framework.yaml
└── _import_queue/            # 待导入的原始文本（临时）
    └── README.md
```

YAML 格式参考已有文件（共 13 个），核心结构：

**方法卡片** `knowledge_base/methods/<类别>/<名称>.yaml`:
```yaml
method_card:
  id: "mc_011"              # mc_ + 三位数字，全局唯一
  name: "方法名"
  category: ["优化", "启发式"]
  principle: |              # 核心原理（支持多行）
    详细描述...
  formulas: []              # 公式列表
  applicable_when: []       # 适用条件
  typical_scenarios: []     # 典型场景
  common_mistakes: []       # 常见误用
  code_snippets: []         # 代码示例
  related_cards: []         # 关联卡片 ID
```

**真题论文** `knowledge_base/papers/<竞赛>/<年份+题号>.yaml`:
```yaml
paper:
  id: "paper_002"
  year: 2024
  competition: "国赛"
  problem_id: "A"
  title: "论文标题"
  tags:
    problem_type: ["优化"]
    core_models: ["方法名"]
  analysis: {...}           # 问题拆解
  model: {...}              # 建模思路
  evaluation: {...}         # 优缺点评价
```

### 完整工作流

```
原始资料 ──→ 方式一 (LLM提取) ──→ 自动生成YAML ──→ indexer --incremental ──→ 可搜索
           │
           ├──→ 方式二 (空模板) ──→ 手动填充 ──→ indexer --incremental ──→ 可搜索
           │
           └──→ 方式三 (手写)   ──→ 直接编写 ──→ indexer --incremental ──→ 可搜索
```

---

## 风险

| 风险 | 缓解 |
|------|------|
| 前端复刻不完整 | 以 GitHub API 返回的文件列表为准；缺失组件按需安装 |
| WebSocket 消息格式不匹配 | Phase 1 做 WS 联调验证 |
| LLM 数学公式/代码错误 | 验证 Agent 做 gate；求解 Agent ReAct 循环自纠错 |
| 源项目 AgentEditor 只含 3 个 | 我们新增 AnalysisEditor + VerificationEditor |

---

## Verification

1. **Phase 0**: `docker-compose up` 全栈启动；`/api/health` 200；`/api/tasks` CRUD 正常
2. **Phase 1**: 前端输入问题 → WS 推送进度 → Chat 页面展示分析结果
3. **Phase 2**: LP 问题 → Notebook 区域展示模型 LaTeX + 代码 + 执行结果
4. **Phase 3**: 人为缺陷模型 → 验证捕获 → 回退提示 → 修正 → 论文输出
5. **Phase 4**: teach 模式无直接答案；solve 模式完整方案；例题页可用
6. **端到端**: 完整国赛真题走通全流程，人工评审输出质量

---

*文档持续更新，随开发进展同步。*
