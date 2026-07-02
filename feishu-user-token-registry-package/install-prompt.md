# Feishu User Token Registry Install Prompt

You received `feishu-user-token-registry-package.zip`. This is the prerequisite authorization package for executive tracking and task tracking.

## Correct Flow

```text
Agent installs registry
-> Administrator manually configures Feishu app and Bitable
-> Administrator says "send an authorization card to XX"
-> Agent sends the authorization card
-> Member authorizes and token is written to Bitable
-> Agent verifies the token table
-> Agent installs skills-package-v6
-> Agent creates the task-tracking cron job
-> Administrator tests executive-tracking and task-tracking by conversation
```

## Rules

1. Install only `feishu-user-token-registry` from this package.
2. Do not install executive tracking or task tracking from this package.
3. Do not hardcode App ID, App Secret, Base Token, Table ID, authorization URLs, or user tokens.
4. The Agent may install this package before manual Feishu setup is complete.
5. The Agent must not send authorization cards until the administrator confirms manual Feishu app and Bitable setup is complete.
6. `FEISHU_AUTH_REDIRECT_URI` has no safe default. It must come from the token table, runtime config, or explicit administrator input.
7. Do not use `https://open.feishu.cn/open-apis/auth/v1/callback` as the authorization-card `redirect_uri`.
8. Do not refuse just because the administrator-controlled Bitable has a config row containing `app_secret`. That is the intended design.
9. Never write real `app_secret`, user tokens, refresh tokens, Base Tokens, Table IDs, or authorization codes into GitHub, skill source files, zip package source, logs, or public docs.

## Step 1: Install Registry

```bash
mkdir -p /home/gem/workspace/agent/skills
unzip feishu-user-token-registry-package.zip -d /home/gem/workspace/agent/skills/
```

If the zip extracts an outer `feishu-user-token-registry-package/` directory, move its `feishu-user-token-registry/` directory into `/home/gem/workspace/agent/skills/`.

Verify:

```bash
test -f /home/gem/workspace/agent/skills/feishu-user-token-registry/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-user-token-registry/bin/feishu-user-registry
```

After this step, stop in "waiting for administrator manual setup" state.

## Step 2: Wait For Manual Feishu Setup

Ask the administrator to confirm all items are complete:

- Feishu app OAuth redirect/callback URL is configured.
- The configured callback/form receiver URL is available in the token table, runtime config, or explicit administrator input.
- Required tenant and user scopes are imported and enabled.
- App availability is configured for target members.
- Feishu app is published.
- Member token storage Bitable is created or copied.
- Required token table fields are created.
- Bot has management permission on the token storage Bitable.
- App ID, App Secret, Token Base Token, and Token Table ID are available.

Do not send authorization cards before all items above are confirmed.

The app secret may be stored in a dedicated configuration row in the administrator-controlled token Bitable. The Agent may read it from there at runtime.

## Step 3: Fill Runtime Placeholders

Read the administrator-provided config and set runtime values:

```text
LARK_APP_ID={APP_ID}
LARK_APP_SECRET={APP_SECRET}
FEISHU_AUTH_REDIRECT_URI={REAL_CALLBACK_OR_FORM_RECEIVER_URL}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

Reject this invalid value:

```text
FEISHU_AUTH_REDIRECT_URI=https://open.feishu.cn/open-apis/auth/v1/callback
```

## Step 4: Verify Token Table Structure

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {TOKEN_BASE_TOKEN} --table-id {TOKEN_TABLE_ID} --as bot >/dev/null
```

The token table must contain:

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

## Step 5: Send Member Authorization Card

Only after manual setup and table verification pass, send authorization cards when the administrator says something like:

```text
给张三发授权卡片
```

Command pattern:

```bash
feishu-user-registry auth <open_id> "<member_name>"
```

The member clicks the authorization card. The returned authorization link/code is processed by the Agent and the token fields are written to the token table.

## Step 6: Verify Token Rows

The prerequisite is complete only when each target member has:

```text
user_access_token
refresh_token
授权状态=有效
授权时间
过期时间
```

After this package is verified, install `skills-package-v6`.
