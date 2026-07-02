# 飞书成员 Token Registry Package v6

这是高管追踪和任务追踪的前置授权包。

## 给 Agent 的主入口

把 `feishu-user-token-registry-package-v6.zip` 发给 Agent 后，请引导它先读：

```text
install-prompt-v6.md
```

可直接使用这段提示词：

```text
请先解压并安装 feishu-user-token-registry-package-v6.zip。
解压后不要自行推断流程，必须先读取包内 install-prompt-v6.md。
读取完成后，严格按照 install-prompt-v6.md 执行。
```

`install-prompt.md` 只是兼容入口，也使用中文流程说明。

## 正确流程

```text
Agent 安装 registry
-> 管理员提供 Token 多维表格模板链接、新表名称、可选目标文件夹链接
-> Agent 调用飞书复制文件 API 复制模板
-> Agent 获取新 Token 表 app_token / table_id
-> Agent 列出所有 workflows
-> Agent 将所有 workflows 全部更新为 Enable
-> Agent 校验 workflows、字段和权限
-> 管理员确认飞书应用手动配置完成
-> 管理员说“给 XX 发授权卡片”
-> Agent 发送授权卡片
-> 成员授权，token 写入新 Token 表
-> Agent 验证 token 表
-> Agent 安装 skills-package-v6
```

## 包含内容

- `feishu-user-token-registry/`：生成飞书 OAuth 授权链接并发送授权卡片。
- `install-prompt-v6.md`：Agent 必须优先读取的中文主执行说明。
- `install-prompt.md`：兼容旧入口。

本包不包含高管追踪和任务追踪业务 skill。

## 重要规则

- 不要让管理员手动复制 Token 表模板。
- 不要让管理员手动开启多维表格工作流。
- Agent 应复制模板里已有的所有 workflows，并全部开启为 `Enable`。
- Agent 不创建新的 workflow 定义。
- 安装、模板复制、workflow 开启、字段校验、权限校验阶段，不要询问目标成员 open_id。
- 只有管理员明确说“给 XX 发授权卡片”后，Agent 才处理该成员 open_id。
- 不要使用默认回调地址 `https://open.feishu.cn/open-apis/auth/v1/callback` 作为授权卡片 redirect_uri。
- 发送授权卡片不需要 `LARK_APP_SECRET`；`app_secret` 只在后续 code 换 token 时使用。

## 安全边界

允许：

- 在管理员控制的新 Token 表配置行里保存 `app_id`、`app_secret`、`FEISHU_AUTH_REDIRECT_URI`、`TOKEN_BASE_TOKEN`、`TOKEN_TABLE_ID`。
- Agent 运行时从新 Token 表、运行时配置或管理员明确输入读取这些值。

禁止：

- 将真实 `app_secret`、user token、refresh token、Base Token、Table ID、授权码写入 GitHub、skill 源码、zip 包源码、日志或公开文档。

## 管理员仍需手动完成

- 飞书应用权限开通。
- OAuth 回调地址配置。
- 应用可用范围配置。
- 应用发布。
- 必要时给机器人/应用授予新 Token 表可管理权限。
