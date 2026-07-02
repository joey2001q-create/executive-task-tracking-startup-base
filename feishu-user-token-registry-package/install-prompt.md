# 飞书成员 Token Registry v6 安装与执行说明

本文件是兼容入口，内容与 `install-prompt-v6.md` 的主流程一致。

Agent 必须优先读取并严格执行 `install-prompt-v6.md`。如果只读到本文件，也必须按下面流程执行。

## Agent 必须先读

本文件是 Agent 必须优先读取的主执行说明。

未读完本文件前，不要自行推断流程，不要向管理员索要目标成员 open_id，不要发送授权卡片。

如果用户只上传了 `feishu-user-token-registry-package-v6.zip`，你应主动解压并查找包内 `install-prompt-v6.md`，读取完成后再行动。

管理员可直接对 Agent 说：

```text
请先解压并安装 feishu-user-token-registry-package-v6.zip。
解压后不要自行推断流程，必须先读取包内 install-prompt-v6.md。
读取完成后，严格按照 install-prompt-v6.md 执行。
```

## 正确流程

```text
Agent 安装 registry
-> 管理员提供 Token 多维表格模板链接、新表名称、可选目标文件夹链接
-> Agent 使用飞书复制文件 API 复制模板，生成新的 Token 多维表格
-> Agent 获取新 Token 表的 app_token 和 table_id
-> Agent 列出新 Token 表里的所有 workflows
-> Agent 遍历所有 workflows，全部更新为 Enable
-> Agent 再次列出 workflows，确认全部都是 Enable
-> Agent 校验 Token 表字段和机器人/应用可管理权限
-> 管理员手动完成飞书应用权限、回调地址、应用可用范围和发布
-> 管理员说“给 XX 发授权卡片”
-> Agent 解析或询问该成员 open_id，并发送授权卡片
-> 成员授权，token 写入新 Token 表
-> Agent 验证 token 表
-> Agent 安装 skills-package-v6
-> Agent 创建 task-tracking 定时任务
-> 管理员通过对话测试 executive-tracking 和 task-tracking
```

## 核心规则

1. 本包只安装 `feishu-user-token-registry`。
2. 本包不安装 `executive-tracking` 或 `task-tracking`。
3. 不要把真实 App ID、App Secret、Base Token、Table ID、授权链接、授权码、user token、refresh token 写入 GitHub、skill 源码、zip 包源码、日志或公开文档。
4. 不要让管理员手动复制 Token 表模板。
5. 不要让管理员手动开启多维表格工作流。
6. 你只负责复制模板里已有的 workflows，并把所有 workflows 全部开启；不要创建新的 workflow 定义。
7. 任意 workflow 开启失败时，停止后续发授权卡片流程，并报告失败的 `workflow_id`、`title` 和错误信息。
8. `FEISHU_AUTH_REDIRECT_URI` 没有安全默认值，必须从新 Token 表、运行时配置或管理员明确输入读取。
9. 不要使用 `https://open.feishu.cn/open-apis/auth/v1/callback` 作为授权卡片的 `redirect_uri`。
10. 不要因为管理员控制的新 Token 表配置行里有 `app_secret` 就拒绝执行；这是预期设计。
11. 发送授权卡片不需要 `LARK_APP_SECRET` / `FEISHU_APP_SECRET`；`app_secret` 只在后续 code 换 token 时使用。
12. 安装、模板复制、workflow 开启、字段校验、权限校验阶段，不要询问目标成员姓名、open_id 或 `TARGET_USER_OPEN_ID`。
13. 只有当管理员明确说“给 XX 发授权卡片”后，才可以解析或询问该成员 open_id。

## 管理员需要提供的信息

管理员应提供：

```text
模板多维表格链接：{TOKEN_TABLE_TEMPLATE_URL}
新表名称：成员 Token 存储表 - {项目名或日期}
目标文件夹链接：{TARGET_FOLDER_URL，可选}
```

如果没有目标文件夹链接，复制到调用身份默认可写位置；不要因此阻塞流程。

## 执行步骤

1. 解压并安装 `feishu-user-token-registry`。
2. 使用飞书复制文件 API 复制管理员提供的 Token 多维表格模板。
3. 获取新 Token 表的 `app_token`、`table_id` 和 URL。
4. 调用“列出自动化流程”API，列出所有 workflows。
5. 遍历所有 workflows，逐个调用“更新自动化流程状态”API，把 `status` 设置为 `Enable`。
6. 再次列出 workflows，确认全部都是 `Enable`。
7. 校验 Token 表字段完整性和机器人/应用可管理权限。
8. 等待管理员确认飞书应用权限、回调地址、应用可用范围和发布已完成。
9. 等待管理员明确说“给 XX 发授权卡片”后，再处理目标成员 open_id 并发送授权卡片。

字段必须包含：

```text
成员
应用ID
应用秘钥
授权链接
回调地址
授权码
user_access_token
refresh_token
授权状态
授权时间
过期时间
```

拒绝以下无效 redirect_uri：

```text
https://open.feishu.cn/open-apis/auth/v1/callback
```

验证通过后，再安装 `skills-package-v6`。
