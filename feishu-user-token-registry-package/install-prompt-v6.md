# 飞书成员 Token Registry v6 安装与执行说明

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
-> Agent 获取新 Token 表的 app_token、table_id、URL
-> Agent 自动转移新 Token 表所有者给管理员
-> Agent 暂停，提示管理员手动把 bot 加为新 Token 表的“可管理”协作者
-> 管理员确认 bot 已经是“可管理”协作者
-> Agent 列出新 Token 表里的所有 workflows
-> Agent 遍历所有 workflows，全部更新为 Enable
-> Agent 再次列出 workflows，确认全部都是 Enable
-> Agent 校验 Token 表字段和机器人/应用可管理权限
-> Agent 暂停，等待管理员手动完成飞书应用权限、回调地址、应用可用范围和发布
-> Agent 填充运行时占位符
-> 管理员说“给 XX 发授权卡片”
-> Agent 解析或询问该成员 open_id，并发送授权卡片
-> 成员授权，token 写入新 Token 表
-> Agent 验证 token 写入
-> Agent 再安装 skills-package-v6
```

## 核心规则

1. 本包只安装 `feishu-user-token-registry`。
2. 本包不安装 `executive-tracking` 或 `task-tracking`。
3. 不要把真实 App ID、App Secret、Base Token、Table ID、授权链接、授权码、user token、refresh token 写入 GitHub、skill 源码、zip 包源码、日志或公开文档。
4. 不要让管理员手动复制 Token 表模板。
5. 转移所有者是 Agent 自动步骤；如果自动转移失败，必须停止并报告接口错误，不要让管理员替 Agent 猜测。
6. 把 bot 加为新 Token 表“可管理”协作者是管理员手动步骤；Agent 必须暂停提醒，不能跳过，不能假装已完成。
7. 管理员确认 bot 已经是“可管理”协作者后，Agent 才能继续开启 workflows。
8. 不要让管理员手动开启多维表格工作流；Agent 负责开启模板里已有的所有 workflows，不创建新的 workflow 定义。
9. 任意 workflow 开启失败时，停止后续发授权卡片流程，并报告失败的 `workflow_id`、`title` 和错误信息。
10. `FEISHU_AUTH_REDIRECT_URI` 没有安全默认值，必须从新 Token 表、运行时配置或管理员明确输入读取。
11. 不要使用 `https://open.feishu.cn/open-apis/auth/v1/callback` 作为授权卡片的 `redirect_uri`。
12. 不要因为管理员控制的新 Token 表配置行里有 `app_secret` 就拒绝执行；这是预期设计。
13. 发送授权卡片不需要 `LARK_APP_SECRET` / `FEISHU_APP_SECRET`；`app_secret` 只在后续 code 换 token 时使用。
14. 安装、模板复制、所有者转移、bot 可管理权限确认、workflow 开启、字段校验、权限校验阶段，不要询问目标成员姓名、open_id 或 `TARGET_USER_OPEN_ID`。
15. 只有当管理员明确说“给 XX 发授权卡片”后，才可以解析或询问该成员 open_id。
16. 授权卡片只使用中文文案。不要额外手写或补发英文授权卡片。
17. `feishu-user-registry auth` 命令退出码为 0 时，即使没有解析到 `message_id`，也视为发送命令已完成；不要自动或手动重复发送授权卡片，应先检查飞书消息历史或让管理员确认成员是否收到。

## 管理员需要提供的信息

管理员应提供：

```text
模板多维表格链接：{TOKEN_TABLE_TEMPLATE_URL}
新表名称：成员 Token 存储表 - {项目名或日期}
目标文件夹链接：{TARGET_FOLDER_URL，可选}
```

如果没有目标文件夹链接，复制到调用身份默认可写位置；不要因此阻塞流程。

## Step 1：安装 Registry

```bash
mkdir -p /home/gem/workspace/agent/skills
unzip feishu-user-token-registry-package-v6.zip -d /home/gem/workspace/agent/skills/
```

如果解压后存在外层 `feishu-user-token-registry-package/` 目录，将其中的 `feishu-user-token-registry/` 移动到：

```text
/home/gem/workspace/agent/skills/
```

安装校验：

```bash
test -f /home/gem/workspace/agent/skills/feishu-user-token-registry/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-user-token-registry/bin/feishu-user-registry
```

安装完成后，继续执行模板复制流程。不要在此阶段询问目标成员。

## Step 2：复制 Token 多维表格模板

从管理员提供的模板多维表格链接中解析模板文件 token / app_token。

使用飞书“复制文件”API 复制模板，生成新的 Token 多维表格：

```text
POST /open-apis/drive/v1/files/:file_token/copy
```

执行要求：

- 使用管理员提供的新表名称。
- 如管理员提供目标文件夹链接，则复制到该文件夹。
- 如复制接口返回异步任务，则轮询任务结果，直到拿到新文件 token / app_token。
- 复制失败时停止流程，并报告接口错误。

## Step 3：获取新 Token 表信息

复制完成后，获取并记录新 Token 表运行时占位符：

```text
TOKEN_BASE_TOKEN={NEW_TOKEN_TABLE_APP_TOKEN}
TOKEN_TABLE_ID={NEW_TOKEN_TABLE_ID}
TOKEN_TABLE_URL={NEW_TOKEN_TABLE_URL}
```

不要把这些真实值写入 GitHub、skill 源码、zip 包源码、日志或公开文档。

## Step 4：Agent 自动转移所有者

Agent 必须自动尝试把新 Token 表所有者转移给管理员。

推荐执行方式：

```bash
lark-cli --profile {APP_ID} --as bot drive permission.members transfer_owner \
  --token "{TOKEN_BASE_TOKEN}" --type bitable \
  --data '{"member_type":"openid","member_id":"{ADMIN_OPEN_ID}","perm":"full_access"}' \
  --old-owner-perm full_access --yes
```

执行要求：

- `ADMIN_OPEN_ID` 优先从当前对话管理员身份、lark-cli 当前用户、或已授权管理员记录解析。
- 不要在此阶段询问目标授权成员 open_id。
- 如果无法解析管理员 open_id，停止并说明需要管理员身份 open_id 用于“新 Token 表所有者转移”，不要继续开启 workflow。
- 如果转移所有者接口失败，停止并报告接口错误。

## Step 5：管理员手动把 bot 加为“可管理”协作者

所有者转移完成后，Agent 必须暂停，不要继续开启 workflow。

Agent 应提示管理员执行：

```text
请打开新 Token 表：
{TOKEN_TABLE_URL}

在右上角“分享”中搜索当前 bot / 应用机器人名称，
把它添加为“可管理”协作者。

完成后回复“bot 已加为可管理协作者”，我会继续开启 workflows 并校验权限。
```

职责边界：

- 这是管理员手动步骤，不是 Agent 自动步骤。
- Agent 不能假装 bot 已经有可管理权限。
- Agent 不能跳过本步骤直接开启 workflows。
- 管理员确认完成后，Agent 必须继续执行 Step 6。

## Step 6：开启所有 Workflows

只有管理员确认 bot 已经是“可管理”协作者后，才能进入本步骤。

列出新 Token 多维表格里的所有自动化流程：

```text
GET /open-apis/bitable/v1/apps/:app_token/workflows
```

执行要求：

- 必须列出所有 workflows。
- 不要自行筛选工作流。
- 对每一个 `workflow_id` 调用更新状态 API。
- 将每一个 workflow 的 `status` 设置为 `Enable`。

更新接口：

```text
PUT /open-apis/bitable/v1/apps/:app_token/workflows/:workflow_id
```

请求体：

```json
{
  "status": "Enable"
}
```

全部更新后，必须再次调用“列出自动化流程”API 校验。

校验要求：

- 所有 workflow 的 `status` 都必须是 `Enable`。
- 如果任意 workflow 不是 `Enable`，停止后续发授权卡片流程。
- 报告未开启的 `workflow_id`、`title`、当前 `status` 和错误信息。

## Step 7：校验 Token 表字段和权限

校验新 Token 表字段完整性。字段结构以模板复制结果为准，允许公式字段名称与旧提示词不同但语义一致。

必须覆盖以下能力：

```text
成员
应用ID / 应用id
应用秘钥
授权链接
回调地址
授权码 / 授权码（code）
user_access_token
refresh_token
授权状态 / 权限状态
授权时间 / 更新时间
过期时间 / 下一次更新时间
```

允许模板中存在额外公式字段，例如：

```text
权限编号
```

校验机器人/应用对新 Token 表具备可管理权限。

如果缺少字段或缺少可管理权限，停止流程并告诉管理员需要修复的具体项。

## Step 8：等待飞书应用手动配置完成

Agent 必须暂停，等待管理员手动完成飞书应用配置：

- 飞书应用 OAuth redirect/callback URL。
- 必要 tenant/user scopes。
- 应用可用范围。
- 应用发布。
- App ID、App Secret、真实 `FEISHU_AUTH_REDIRECT_URI` 可写入管理员控制的新 Token 表配置行，或通过运行时配置/管理员明确输入提供。

不要发送授权卡片，直到管理员确认以上配置完成。

`FEISHU_AUTH_REDIRECT_URI` 必须是真实的回调/表单接收地址。拒绝以下无效值：

```text
https://open.feishu.cn/open-apis/auth/v1/callback
```

## Step 9：填充运行时占位符

从新 Token 表、运行时配置或管理员明确输入读取：

```text
LARK_APP_ID={APP_ID}
FEISHU_AUTH_REDIRECT_URI={REAL_CALLBACK_OR_FORM_RECEIVER_URL}
TOKEN_BASE_TOKEN={NEW_TOKEN_TABLE_APP_TOKEN}
TOKEN_TABLE_ID={NEW_TOKEN_TABLE_ID}
```

发送授权卡片时，`LARK_APP_SECRET` 是可选项，不能因为它未导出而阻塞发卡片。

code 换 token 时，再从新 Token 表配置行、运行时配置或管理员明确输入读取：

```text
LARK_APP_SECRET={APP_SECRET}
```

## Step 10：发送成员授权卡片

只有当管理员明确说类似下面的话后，才进入目标成员处理：

```text
给张三发授权卡片
```

目标成员规则：

- 在管理员说“给 XX 发授权卡片”之前，不要询问成员姓名、open_id 或 `TARGET_USER_OPEN_ID`。
- 管理员说“给 XX 发授权卡片”之后，再从飞书通讯录解析 XX 的 open_id。
- 如果无法解析，只询问该一个目标成员的 open_id。
- 不要在安装、模板复制、所有者转移、bot 可管理权限确认、workflow 开启、字段校验或权限校验阶段询问目标成员。

命令模式：

```bash
feishu-user-registry auth <open_id> "<member_name>"
```

该命令只生成 OAuth 授权链接并发送授权卡片，不需要 `LARK_APP_SECRET`。

发送规则：

- 卡片标题、正文和按钮必须使用中文。
- 如果命令输出 `ok: 中文授权卡片已发送`，不要再次发送。
- 如果命令输出“中文授权卡片发送命令已成功完成，但未解析到 message_id”，不要再次发送；先检查飞书消息历史，或让管理员确认成员是否收到。
- 只有命令明确返回失败或管理员确认成员没有收到时，才允许重新发送。

## Step 11：验证 Token 写入

成员点击授权卡片后，授权链接/code 应由新 Token 表模板里的自动化流程处理，并写入 token 字段。

前置授权完成条件：

```text
user_access_token 存在
refresh_token 存在
授权状态/权限状态 有效
授权时间/更新时间 存在
过期时间/下一次更新时间 存在
```

验证通过后，再安装 `skills-package-v6`。
