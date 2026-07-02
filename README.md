# 高管追踪与任务追踪启动底座

这个仓库是飞书高管追踪和任务追踪的两阶段安装底座，用来给 Agent 准备授权前置包和正式业务 skill 包。

它不是完整业务项目，也不是把所有旧 skill 都装进去的合集。当前目标是只保留两个业务入口：

- 高管追踪
- 任务追踪

## 正确测试流程

```text
Agent 安装 registry
-> 你手动配置飞书应用和多维表
-> 你说“给 XX 发授权卡片”
-> Agent 发授权卡片
-> 成员授权，token 写入多维表
-> Agent 验证 token 表
-> Agent 安装 skills-package-v6
-> Agent 配置任务追踪定时任务
-> 通过对话测试高管追踪和任务追踪
```

## 下载这两个安装包

开始测试时下载并按顺序安装：

```text
feishu-user-token-registry-package.zip
skills-package-v6.zip
```

安装顺序不能反：

1. 先安装 `feishu-user-token-registry-package.zip`
2. 你完成飞书应用、多维表、机器人权限和应用发布等手动配置
3. Agent 发授权卡片并验证 token 表
4. 再安装 `skills-package-v6.zip`

## 两个包的职责

`feishu-user-token-registry-package/`

前置授权包。它可以先安装，但必须等你手动完成飞书配置后，Agent 才能发送授权卡片。它负责：

- 生成飞书 OAuth 授权链接
- 给指定成员发送授权卡片
- 处理成员授权后的 code/token
- 把 `user_access_token` 和 `refresh_token` 写入成员 Token 多维表
- 验证目标成员 token 是否有效

`skills-package-v6/`

正式业务包。它只暴露两个业务 skill：

- `executive-tracking`
- `task-tracking`

它不负责发授权卡片，也不创建 token 表，只读取已经验证好的成员 Token 多维表。安装 v6 时，Agent 还要创建任务追踪每日 21:00 的定时巡检任务，并记录实际生成的 cron job id。

## 手动配置与 Agent 配置

你手动配置：

- 飞书应用权限
- OAuth 回调地址
- 应用可用范围
- 应用发布
- 成员 Token 多维表
- 业务多维表
- 机器人多维表权限
- App ID、App Secret、Base Token、Table ID 等真实环境配置

Agent 配置：

- 安装 registry
- 根据你的配置发送授权卡片
- 写入并验证成员 token
- 安装 v6
- 安装 shared/internal collectors
- 写入运行时变量
- 配置任务追踪定时任务
- 通过对话测试高管追踪和任务追踪

## 业务范围

只保留：

- 高管追踪
- 任务追踪

以下旧业务 skill 不再安装、不再暴露：

- 招聘
- 团队氛围
- 考勤
- 竞对分析
- 老板每日简报
- 客户跟进
- 财务、销售、市场、产品子 skill

## 安全规则

- 不要把真实 App ID、App Secret、Base Token、Table ID、授权码、user token、refresh token 写进仓库。
- 不要在包里写死 cron job id。定时任务由 Agent 安装 v6 时创建，并记录实际生成的 id。
- 不要提交 macOS 元数据、临时解压目录、Python 缓存文件。

## 测试入口

把 `feishu-user-token-registry-package.zip` 发给 Agent 时，让它阅读：

```text
feishu-user-token-registry-package/install-prompt.md
```

把 `skills-package-v6.zip` 发给 Agent 时，让它阅读：

```text
skills-package-v6/full-install-prompt-v6.md
```
