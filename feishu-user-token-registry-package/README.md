# Feishu User Token Registry Package

This is a standalone prerequisite package. Install and verify it before installing `skills-package-v6`.

## What It Contains

- `feishu-user-token-registry/`: sends Feishu OAuth authorization cards to target members.

It does not contain executive tracking or task tracking.

## Manual Configuration

The administrator must manually configure:

- Feishu OAuth callback URL: `https://open.feishu.cn/open-apis/auth/v1/callback`
- Required tenant/user scopes for calendar, messages, chat, task, minutes, search/docs, mail, contact, and `offline_access`
- App availability and app publishing
- Member token storage Bitable fields:
  `成员`, `应用ID`, `应用秘钥`, `授权链接`, `回调地址`, `授权码`, `user_access_token`, `refresh_token`, `授权状态`, `授权时间`, `过期时间`
- Bot management permission on the token storage Bitable

## Runtime Placeholders

Do not write real values into this repository. The Agent should fill these after the administrator adds configuration to Bitable:

```text
LARK_APP_ID={APP_ID}
LARK_APP_SECRET={APP_SECRET}
FEISHU_AUTH_REDIRECT_URI={FEISHU_AUTH_REDIRECT_URI}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

## Install Prompt

Give this package to the Agent and ask it to read:

```text
install-prompt.md
```
