# Feishu User Token Registry v6 Install Prompt

You received `feishu-user-token-registry-package-v6.zip`. This is the v6 prerequisite authorization package for executive tracking and task tracking.

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
10. Do not require `LARK_APP_SECRET` / `FEISHU_APP_SECRET` before sending an authorization card. The authorization-card step only needs `APP_ID` and the real `FEISHU_AUTH_REDIRECT_URI`.
11. `app_secret` is needed later for code-to-token exchange, and may be read from the controlled Bitable config row, runtime config, or explicit administrator input.
12. Do not ask for a target member name or open_id during installation or setup verification.
13. Ask for or resolve the target member only after the administrator explicitly says "send an authorization card to XX".

## Step 1: Install Registry

```bash
mkdir -p /home/gem/workspace/agent/skills
unzip feishu-user-token-registry-package-v6.zip -d /home/gem/workspace/agent/skills/
```

If the package was delivered with the legacy compatible name `feishu-user-token-registry-package.zip`, use that filename in the unzip command. If the zip extracts an outer `feishu-user-token-registry-package/` directory, move its `feishu-user-token-registry/` directory into `/home/gem/workspace/agent/skills/`.

Verify:

```bash
test -f /home/gem/workspace/agent/skills/feishu-user-token-registry/SKILL.md
test -f /home/gem/workspace/agent/skills/feishu-user-token-registry/bin/feishu-user-registry
```

After this step, stop in "waiting for administrator manual setup" state.

Do not ask for a target member at this stage.

## Step 2: Wait For Manual Feishu Setup

Ask the administrator to confirm all items are complete:

- Feishu app OAuth redirect/callback URL is configured.
- The configured callback/form receiver URL is available in the token table, runtime config, or explicit administrator input.
- Required tenant and user scopes are imported and enabled.
- App availability is configured for all members, or it is configured so later authorization members can use the app. Do not require a target member list for this check.
- Feishu app is published.
- Member token storage Bitable is created or copied.
- Required token table fields are created.
- Bot has management permission on the token storage Bitable.
- App ID, App Secret, Token Base Token, and Token Table ID are available.

Do not send authorization cards before all items above are confirmed.

The app secret may be stored in a dedicated configuration row in the administrator-controlled token Bitable. The Agent may read it from there at runtime.

Do not ask for a target member during setup confirmation. Setup confirmation only verifies app/table/config readiness.

## Step 3: Fill Runtime Placeholders

Read the administrator-provided config and set runtime values:

```text
LARK_APP_ID={APP_ID}
FEISHU_AUTH_REDIRECT_URI={REAL_CALLBACK_OR_FORM_RECEIVER_URL}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

For sending the authorization card, `LARK_APP_SECRET` is optional and must not block card sending.

For code-to-token exchange after the member authorizes, read:

```text
LARK_APP_SECRET={APP_SECRET}
```

from the controlled Bitable config row, runtime config, or explicit administrator input.

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

Do not block this command only because `LARK_APP_SECRET` is not currently exported. This command only builds the OAuth URL and sends the card.

Target member handling:

- Before the administrator asks "send an authorization card to XX", do not ask for member name or open_id.
- After the administrator asks "send an authorization card to XX", resolve XX to `open_id` from Feishu contacts or ask the administrator for that one target's open_id.
- Do not ask for a batch of target members during installation.
- Invalid behavior: asking for `TARGET_USER_OPEN_ID`, target member `open_id`, or target member details during install, manual setup confirmation, runtime placeholder filling, or token table structure verification.

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
