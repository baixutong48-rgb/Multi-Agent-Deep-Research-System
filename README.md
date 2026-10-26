# DeepSearchPro — Multi-Agent Deep Research System

基于 **LangGraph、DeepAgents 和 FastAPI** 构建的多智能体深度研究系统，面向复杂信息检索、多源数据分析与研究报告生成场景。

系统采用 **Main Agent + Specialized SubAgents** 的分层协作架构，实现任务委派、工具调用、异步研究任务执行，以及 Agent 执行过程的结构化追踪与实时事件推送。

本项目参考开源 DeepSearchPro 的设计思路，重点探索 AI Agent 系统的工程化架构、运行时管理和可观测性设计。

## 1. 核心功能

### 1.1 多智能体协作（Multi-Agent Collaboration）

基于 DeepAgents 构建 Main Agent 与专业化 SubAgent 协作体系。

- **Main Agent**：理解用户研究需求，组织研究流程，委派子任务并整合研究结果。
- **Network Research Agent**：调用网络搜索工具获取外部信息。
- **Database Agent**：通过数据库工具查询结构化数据。
- **Knowledge Agent**：通过知识库接口检索领域知识。

Main Agent 通过 `task` 工具将研究任务委派给不同 SubAgent，实现专业化任务分工。

不同 SubAgent 根据工具配置及服务可用性启用。

### 1.2 模块化工具系统（Modular Tool System）

基于 LangChain Tool 接口封装研究工具：

- Web Search：网络信息检索。
- Database Query：PostgreSQL 数据查询。
- Knowledge Retrieval：知识库 API 检索。
- File Operations：研究文件读取与写入。

通过工厂模式与依赖注入组织工具实例，降低 Agent 逻辑与具体工具实现之间的耦合。

### 1.3 Agent Runtime 与工作空间隔离

设计独立的 Agent Runtime 管理机制：

- **RuntimeIdentity**：维护 `run_id`、`thread_id`、`session_id`、`user_id` 等运行标识。
- **Workspace**：为研究任务管理独立文件工作空间。
- **Agent Factory**：负责 Agent 构建与运行配置装配。
- **Tool Factory**：负责工具初始化与依赖管理。

采用 Run-scoped 设计，将任务级执行资源与应用级配置分离，减少不同研究任务之间的资源混用。

### 1.4 异步研究任务执行（Asynchronous Research Execution）

基于 FastAPI 和 AsyncIO 实现异步研究任务执行机制。

主要能力：

- 创建研究任务。
- 后台异步执行 Agent。
- 查询研究任务状态。
- 获取研究任务结果。
- 记录任务执行失败信息。

研究任务状态：

| 状态 | 说明 |
|------|------|
| `PENDING` | 等待执行 |
| `RUNNING` | 正在执行 |
| `COMPLETED` | 执行完成 |
| `FAILED` | 执行失败 |

通过 ResearchRunner 管理任务生命周期，将长耗时 Agent 执行与 HTTP 请求处理解耦。

### 1.5 Agent Trace 与实时事件流

基于 LangGraph Streaming 获取 Agent 执行过程中的状态更新。

通过 `DeepAgentTraceAdapter` 将 LangGraph 原始更新转换为统一的结构化 Trace Event。

主要设计包括：

- 解析 Main Agent 与 SubAgent 执行事件。
- 识别 Agent 工具调用及执行结果。
- 基于 `tool_call_id` 关联工具调用与结果。
- 使用运行级序列号记录事件顺序。
- 通过 TraceStore 保存研究执行事件。
- 通过 WebSocket 推送研究过程事件。
- 支持按事件序列号查询历史记录，为断线续传提供基础。

TraceStore 与 Agent 执行过程解耦，避免 WebSocket 连接直接驱动 Agent 执行。

> 当前 TraceStore 采用进程内存储方案，主要面向单进程运行环境。多实例部署、持久化恢复及完整端到端可靠性仍需要进一步验证。

---

## 2. 系统架构

```text
                   Client / API Consumer
                            |
                            v
                        FastAPI
                            |
                            v
                      ResearchRunner
                            |
                 +----------+----------+
                 |                     |
                 v                     v
           Agent Runtime           Run Status
                 |
                 v
              Main Agent
                 |
           Task Delegation
                 |
       +---------+----------+
       |         |          |
       v         v          v
    Network   Database   Knowledge
    SubAgent  SubAgent   SubAgent
       |         |          |
       v         v          v
   Web Search   SQL     Knowledge API

                 |
                 v
         LangGraph Streaming
                 |
                 v
       DeepAgentTraceAdapter
                 |
                 v
              TraceStore
                 |
                 v
            WebSocket API
                 |
                 v
               Client
```

### 架构分层

系统主要分为四个层次：

**API Layer**

负责 HTTP 请求处理、研究任务创建、状态查询以及 WebSocket 通信。

**Runtime Layer**

负责研究任务生命周期管理、Agent 构建、后台执行及工作空间管理。

**Agent Layer**

负责 Main Agent 编排、SubAgent 任务委派与工具调用。

**Observability Layer**

负责 Agent 执行事件解析、标准化、存储及实时推送。

---

## 3. 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python 3.12 |
| Agent 框架 | LangGraph、DeepAgents、LangChain |
| Web 框架 | FastAPI |
| 异步编程 | AsyncIO |
| 实时通信 | WebSocket |
| 数据验证与配置 | Pydantic |
| 数据库 | PostgreSQL、AsyncPG |
| 网络搜索 | Tavily API |
| LLM 服务 | Ollama |
| 包管理 | uv |
| 测试 | pytest |

---

## 4. 快速开始（Quick Start）

### 4.1 环境要求

- Python 3.12
- uv
- Git
- Ollama 或其他项目支持的 LLM 服务
- PostgreSQL（启用数据库工具时）
- Tavily API Key（启用网络搜索工具时）
- Knowledge API（启用知识库工具时）

### 4.2 克隆项目

```bash
git clone https://github.com/baixutong48-rgb/Multi-Agent-Deep-Research-System.git

cd Multi-Agent-Deep-Research-System
```

### 4.3 安装依赖

项目使用 `uv` 管理 Python 依赖。

```bash
uv sync
```

### 4.4 配置环境变量

复制示例配置：

Linux / macOS：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

修改 `.env`，填写实际配置：

```dotenv
# LLM Configuration
LLM__MODEL_NAME=your_model_name
LLM__TEMPERATURE=0.0
LLM__TIMEOUT=30
LLM__PROVIDER=ollama

# PostgreSQL
DB__URL=postgresql+asyncpg://your_user:your_password@localhost:5432/your_database
DB__QUERY_TIMEOUT=10
DB__MAX_ROWS=100

# Knowledge API
KNOWLEDGE__BASE_URL=http://localhost:8001
KNOWLEDGE__API_KEY=
KNOWLEDGE__TIMEOUT=20
KNOWLEDGE__TOP_K=5

# Workspace
WORKSPACE__ROOT=
WORKSPACE__MAX_READ_BYTES=5242880

# Tavily
TAVILY__API_KEY=your_tavily_api_key
TAVILY__TIMEOUT=15.0
```

如果使用 Ollama，请确保 Ollama 服务已启动，并且配置的模型已经下载。

例如：

```bash
ollama pull <model_name>
```

> `.env` 包含敏感配置，不应提交到 Git 仓库。请使用 `.env.example` 提供配置模板。

### 4.5 启动服务

如果 FastAPI 实例定义在 `main.py` 中，且名称为 `app`：

```bash
uv run uvicorn main:app --reload
```

如果实际 ASGI 入口位于其他模块，需要根据项目代码调整启动路径。

启动成功后，可以访问 FastAPI 自动生成的 API 文档：

```text
http://127.0.0.1:8000/docs
```

---

## 5. 研究任务执行流程

### Step 1：创建研究任务

客户端向 FastAPI 发送研究请求。

系统创建 Research Run，并分配独立的 `run_id`。

### Step 2：初始化运行环境

ResearchRunner 初始化运行上下文、Workspace 和 Main Agent。

### Step 3：Agent 规划与任务委派

Main Agent 分析研究目标，根据任务需要调用 `task` 工具，将子任务委派给专业 SubAgent。

### Step 4：工具调用

SubAgent 根据职责调用相应工具：

- Network Agent：Web Search
- Database Agent：Database Query
- Knowledge Agent：Knowledge Retrieval

### Step 5：研究结果整合

Main Agent 汇总不同 SubAgent 返回的研究信息，形成最终研究结果。

### Step 6：执行链路追踪

通过 LangGraph Streaming 获取执行更新。

DeepAgentTraceAdapter 将原始更新转换为统一 Trace Event，并交由 TraceStore 保存。

### Step 7：结果查询与实时事件推送

客户端通过 HTTP 查询任务状态与研究结果，通过 WebSocket 获取研究执行事件。

---

## 6. API 设计

研究任务 API 主要提供以下能力：

| 功能 | 描述 |
|------|------|
| Create Research | 创建研究任务 |
| Get Research Status | 查询任务状态 |
| Get Research Result | 获取最终研究结果 |
| Stream Research Events | 订阅研究执行事件 |

WebSocket 路由设计：

```text
/api/v1/research/{run_id}/stream
```

系统通过事件序列号支持历史事件查询，为客户端重新连接后的事件补收提供基础。

具体 HTTP 路由、请求参数及响应结构以项目实际代码和 `/docs` 文档为准。

---

## 7. 核心设计特点

### 7.1 Multi-Agent Orchestration

通过 Main Agent 与专业化 SubAgent 协作，实现不同研究能力之间的任务分工与结果整合。

### 7.2 Modular Tool Architecture

通过统一工具接口与工厂模式组织外部能力，便于扩展新的搜索、数据库或知识库工具。

### 7.3 Run-scoped Runtime

通过 RuntimeIdentity 与独立 Workspace 管理运行级资源，为不同研究任务提供明确的执行边界。

### 7.4 Asynchronous Execution

利用 FastAPI 与 AsyncIO 将长耗时研究任务放入后台执行，避免 HTTP 请求持续等待整个 Agent 研究过程。

### 7.5 Structured Agent Tracing

将 LangGraph 原始流事件转换为结构化 Trace Event，支持研究执行过程分析、调试和实时展示。

### 7.6 Streaming Decoupling

通过 TraceStore 解耦 Agent 执行与 WebSocket 消费，为历史事件回放和后续持久化扩展提供基础。

---

## 8. 当前限制与后续规划

当前版本重点关注：

- 多 Agent 编排
- 模块化工具集成
- Agent Runtime 管理
- 异步研究任务执行
- Agent Trace 与 WebSocket 事件通信

后续可以进一步扩展：

**Context Engineering**

增加上下文选择、摘要压缩、工具结果过滤及多 Agent 上下文交接优化。

**Persistent Runtime**

引入 Redis 或数据库持久化研究任务状态和执行事件，支持多实例部署。

**Observability**

接入 Langfuse 或 LangSmith，实现 LLM 调用链路分析、Token 统计与运行监控。

**Evaluation**

建立 Agent 研究任务评估体系，衡量研究质量、工具调用表现和任务完成情况。

**Reliability**

完善任务取消、超时控制、重试机制、并发限制与错误恢复。

**Deployment**

增加 Docker、CI/CD 和生产环境部署配置。

以上内容属于后续规划，不代表当前版本已经实现。

---

## 9. 项目目标

本项目主要用于探索 AI Agent 应用的工程化设计与实现，重点实践以下技术方向：

- Multi-Agent Architecture
- Agent Orchestration
- Tool Calling
- Agent Runtime Management
- Asynchronous Task Execution
- Agent Execution Tracing
- WebSocket Streaming

项目不仅关注 Agent 的研究任务执行能力，也关注多智能体系统的模块化设计、运行时管理及执行过程可观测性。

---

## 10. 致谢（Acknowledgements）

本项目参考开源项目 [DeepSearchPro](https://github.com/waseens/deep-search-pro) 的相关设计思路，并结合 LangGraph、DeepAgents、FastAPI 等技术进行工程化学习与实践。