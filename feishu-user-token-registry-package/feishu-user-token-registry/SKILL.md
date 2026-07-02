---
name: feishu-user-token-registry
description: |
  Feishu user OAuth authorization prerequisite.
  Generate a user authorization link and send an authorization card to a target member.
alwaysActive: false
---

# Feishu User Token Registry

## Purpose

This skill is a prerequisite package for executive tracking and task tracking. It only handles member OAuth authorization:

- Generate a Feishu OAuth authorization link.
- Send the authorization card to a target member.
- Let the administrator's Bitable/form automation capture the returned authorization URL, code, `user_access_token`, and `refresh_token`.

This skill does not install executive tracking or task tracking, and it does not create the token table automatically.

## Required Manual Setup

Before running this skill, the administrator must manually finish:

- Configure the Feishu app OAuth redirect/callback URL. This must be the real callback or form receiver URL used by your token collection flow.
- Enable the required tenant/user scopes for calendar, direct messages, group messages, tasks, minutes, docs/search, mail, contact, and `offline_access`.
- Set app availability for all members or the target members who need authorization.
- Publish the Feishu app.
- Create or copy the member token storage Bitable.
- Configure fields: `成员`, `应用ID`, `应用秘钥`, `授权链接`, `回调地址`, `授权码`, `user_access_token`, `refresh_token`, `授权状态`, `授权时间`, `过期时间`.
- Grant the bot management permission on the token storage Bitable.

## Secret Storage Policy

The administrator-controlled Feishu Bitable may contain a dedicated configuration row with `app_id`, `app_secret`, `FEISHU_AUTH_REDIRECT_URI`, `TOKEN_BASE_TOKEN`, and `TOKEN_TABLE_ID`.

Do not refuse to send an authorization card only because `app_secret` is stored in that controlled Bitable. This is the intended deployment design.

Do not write real secrets into GitHub, this skill package source, logs, or public docs. Read them only at runtime from the token table, runtime config, or explicit administrator input.

## Runtime Placeholders

The repository must not contain real environment values. The Agent should fill these from the token table, runtime config, or explicit administrator input after manual setup:

```text
LARK_APP_ID={APP_ID}
LARK_APP_SECRET={APP_SECRET}
FEISHU_AUTH_REDIRECT_URI={REAL_CALLBACK_OR_FORM_RECEIVER_URL}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

`FEISHU_AUTH_REDIRECT_URI` must be the real callback/form receiver URL configured by the administrator. It can come from the token table, runtime config, or explicit administrator input. It has no safe default. Do not use `https://open.feishu.cn/open-apis/auth/v1/callback` as the authorization-card redirect URI.

## Usage

```bash
feishu-user-registry auth <open_id> "<member_name>"
```

Flow:

```text
Agent sends authorization card
Member clicks authorization link
Member copies/submits the returned authorization URL
Administrator's Bitable/form automation extracts code and writes tokens
Agent verifies token table before installing executive/task tracking package
```

## Validation

The prerequisite package is considered ready only when:

- The Feishu app is published.
- The token storage Bitable fields exist.
- The bot can manage the token storage Bitable.
- The real callback/form receiver URL is available to the Agent.
- At least one target member has a valid `user_access_token` and `refresh_token`.
- The token table Base/Table IDs are available to the Agent as placeholders, not hardcoded in this package.
