# Skills Package v6

这是只面向高管追踪和任务追踪的正式瘦身版 skill 包。

## 业务入口

- `executive-tracking`：高管追踪，对应 `feishu-boss-work/`
- `task-tracking`：任务追踪，对应 `feishu-exec-task-extractor/`

## Shared/Internal 依赖

以下目录是两个业务入口运行需要的共享依赖，不作为用户可选 skill 展示：

- `feishu-data-collector-v3/`
- `feishu-calendar-collector/`
- `feishu-task-collector/`
- `feishu-minutes-collector/`
- `feishu-group-collector/`
- `feishu-p2p-collector/`
- `feishu-mail-collector/`
- `feishu-executive-comparison/`

## 安装入口

把 `skills-package-v6.zip` 发给 Agent 后，让 Agent 读取并执行：

```text
full-install-prompt-v6.md
```

安装时只应暴露两个业务入口：高管追踪和任务追踪。
