# Feishu User Token Registry Install Prompt

You received `feishu-user-token-registry-package.zip`. This is a prerequisite package for executive tracking and task tracking.

## Rules

1. Install only `feishu-user-token-registry`.
2. Do not install executive tracking or task tracking from this package.
3. Do not hardcode App ID, App Secret, Base Token, Table ID, or form URLs.
4. The administrator must manually complete Feishu app and Bitable setup before authorization is considered ready.

## Step 1: Extract

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

## Step 2: Manual Feishu App Setup

Ask the administrator to confirm all items are complete:

- OAuth callback URL configured: `https://open.feishu.cn/open-apis/auth/v1/callback`
- Required scopes imported and enabled
- App availability configured
- App published
- Member token storage Bitable created/copied
- Required fields created
- Bot has management permission on the Bitable

## Step 3: Fill Runtime Placeholders

Read the administrator-provided Bitable/config and set:

```text
LARK_APP_ID={APP_ID}
LARK_APP_SECRET={APP_SECRET}
FEISHU_AUTH_REDIRECT_URI={FEISHU_AUTH_REDIRECT_URI}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

## Step 4: Verify Token Table

```bash
lark-cli --profile {APP_ID} base +field-list --base-token {TOKEN_BASE_TOKEN} --table-id {TOKEN_TABLE_ID} --as bot >/dev/null
```

## Step 5: Send Member Authorization

For each target member:

```bash
feishu-user-registry auth <open_id> "<member_name>"
```

The member must click the link and submit/copy the returned authorization URL into the token storage flow.

## Step 6: Final Verification

The prerequisite is complete only when the token table has:

```text
授权码
user_access_token
refresh_token
授权状态=有效
授权时间
过期时间
```

After this package is verified, install `skills-package-v6`.
