# Executive Task Tracking Startup Base

这是一个基于 `AI-Project-Startup-Prompt` 重新初始化的 AI Agent 启动模板仓库。

本仓库不是具体业务项目，也不是 skill 仓库，而是项目启动前的底座仓库。

它的用途是在新项目开始前，给 AI Agent 一套统一的启动、接手和文档更新协议。后续具体项目可以在这个底座之上，只启用 2 个核心 skill：

- 高管追踪
- 任务追踪

这样可以把原本安装了 8 个 skill 的 Agent 收敛到更清晰的工作边界，用于优化高管信息跟进、关键事项沉淀、任务状态追踪和跨会话交接。

适用对象：

- Codex
- Claude Code
- Cursor
- 其他 AI 编程 Agent
- 接手项目的人类开发者

## 文件说明

```text
AI_STARTUP_PROMPT.md   每次项目启动前、AI 会话开始或接手已有项目时给 Agent 的底座提示词
AI_TASK_CHECKLIST.md   每次重要任务结束前的文档更新检查清单
README.md             本仓库说明
```

## 使用方式

### 接手已有项目

把 `AI_STARTUP_PROMPT.md` 发给新的 AI Agent，然后让它读取目标项目中的：

```text
PROJECT_MEMORY.md
PROJECT_CONTEXT.md
DECISIONS.md
README.md
CHANGELOG.md
```

Agent 应先复述项目目标、当前状态和长期约束，再开始开发。

### 启动新项目

把 `AI_STARTUP_PROMPT.md` 发给新的 AI Agent。  
如果新项目还没有项目记忆文件，Agent 应先和用户确认项目目标，再创建：

```text
PROJECT_MEMORY.md
PROJECT_CONTEXT.md
DECISIONS.md
CHANGELOG.md
README.md
AI_STARTUP_PROMPT.md
```

### 防止 Agent 忘记更新文档

把 `AI_TASK_CHECKLIST.md` 作为任务收尾检查清单。  
每次重要任务结束前，Agent 都应判断是否需要更新：

```text
PROJECT_MEMORY.md
PROJECT_CONTEXT.md
DECISIONS.md
README.md
CHANGELOG.md
```

## 维护原则

- `AI_STARTUP_PROMPT.md` 是项目启动前的底座协议。
- 具体项目的信息应写在具体项目自己的 `PROJECT_MEMORY.md`、`PROJECT_CONTEXT.md`、`DECISIONS.md` 等文件中。
- 高管追踪和任务追踪是后续具体项目优先启用的两个 skill，不直接写成这个底座仓库的全部内容。
- 不要把聊天原文、Token、验证码、密钥或敏感路径写入模板仓库。
- 当项目启动、接手或文档更新的底座规范变化时，再更新本仓库。

