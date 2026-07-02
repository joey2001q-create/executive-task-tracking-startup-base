# Feishu User Token Registry Package v6

This is a standalone v6 prerequisite package for executive tracking and task tracking.

## Correct Flow

```text
Agent installs registry
-> Administrator manually configures Feishu app and Bitable
-> Administrator says "send an authorization card to XX"
-> Agent sends the authorization card
-> Member authorizes and token is written to Bitable
-> Agent verifies the token table
-> Agent installs skills-package-v6
```

## What It Contains

- `feishu-user-token-registry/`: sends Feishu OAuth authorization cards and writes member tokens to the configured token Bitable.

It does not contain executive tracking or task tracking.

## Manual Configuration

The administrator must manually configure:

- Feishu app OAuth redirect/callback URL. This must be the real callback or form receiver URL used by your token collection flow.
- Required tenant/user scopes for calendar, messages, chat, task, minutes, search/docs, mail, contact, and `offline_access`.
- App availability for all members, or availability configured so later authorization members can use the app. This setup check must not require a target member list.
- App publishing.
- Member token storage Bitable fields:
  `成员`, `应用ID`, `应用秘钥`, `授权链接`, `回调地址`, `授权码`, `user_access_token`, `refresh_token`, `授权状态`, `授权时间`, `过期时间`.
- Bot management permission on the token storage Bitable.

Do not use `https://open.feishu.cn/open-apis/auth/v1/callback` as `FEISHU_AUTH_REDIRECT_URI` for authorization cards. That default Feishu endpoint is not the environment-specific callback/form receiver that collects the member authorization result.

## Secret Storage Policy

This package allows the administrator-controlled Feishu Bitable to store an app configuration row that includes `app_id`, `app_secret`, `FEISHU_AUTH_REDIRECT_URI`, `TOKEN_BASE_TOKEN`, and `TOKEN_TABLE_ID`.

The Agent must not refuse authorization-card sending only because `app_secret` is stored in that controlled Bitable. This is the intended deployment design.

The Agent must also not refuse authorization-card sending only because `LARK_APP_SECRET` is not exported yet. Sending the authorization card only needs `APP_ID` and the real `FEISHU_AUTH_REDIRECT_URI`; `app_secret` is needed later for code-to-token exchange.

Security boundary:

- Allowed: storing `app_secret` in the administrator-controlled Feishu Bitable configuration row.
- Allowed: reading `app_secret` from Bitable/runtime config/explicit administrator input at runtime.
- Forbidden: writing real `app_secret`, tokens, Base Tokens, Table IDs, authorization codes, or refresh tokens into GitHub, skill source files, zip package source, logs, or public docs.
- Required: token/config Bitable permissions must be limited to the bot and administrators.

## Agent Responsibilities

The Agent may install this package first, but it must wait for administrator confirmation before sending authorization cards.

Installation and setup verification do not require any target member name or open_id. Target member resolution happens only after the administrator explicitly asks to send an authorization card to a specific person. Asking for `TARGET_USER_OPEN_ID` during install or setup verification is invalid behavior.

After manual setup is complete, the Agent should:

- Fill runtime placeholders from the token table, runtime config, or explicit administrator input.
- Verify the token table structure.
- Read the real `FEISHU_AUTH_REDIRECT_URI` from the token table, runtime config, or explicit administrator input.
- Send authorization cards on request.
- Process the returned authorization link/code.
- Write `user_access_token`, `refresh_token`, status, and expiry fields to the token table.
- Verify target members have valid token rows.

## Runtime Placeholders

Do not write real values into this repository. The Agent fills these at runtime:

```text
LARK_APP_ID={APP_ID}
FEISHU_AUTH_REDIRECT_URI={REAL_CALLBACK_OR_FORM_RECEIVER_URL}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

`FEISHU_AUTH_REDIRECT_URI` must come from your manual configuration: token table, runtime config, or explicit administrator input. The package has no safe default for this value.

Read `LARK_APP_SECRET={APP_SECRET}` later for token exchange, not as a blocker for sending the authorization card.

## Install Prompt

Give this package to the Agent and ask it to read:

```text
install-prompt-v6.md
```

`install-prompt.md` is kept as a compatibility alias for older instructions.
