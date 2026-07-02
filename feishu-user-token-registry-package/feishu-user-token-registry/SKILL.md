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

This skill does not install executive tracking or task tracking. In v6, the Agent should create the runtime token table by copying the administrator-provided Bitable template, then enable every workflow copied with that template.

## Required Manual Setup

Before running this skill, the administrator must manually finish:

- Configure the Feishu app OAuth redirect/callback URL. This must be the real callback or form receiver URL used by your token collection flow.
- Enable the required tenant/user scopes for calendar, direct messages, group messages, tasks, minutes, docs/search, mail, contact, and `offline_access`.
- Set app availability for all members, or configure availability so later authorization members can use the app. This setup check must not require a target member list.
- Publish the Feishu app.
- Provide the member token storage Bitable template URL, new table name, and optional target folder URL.
- Confirm Feishu app scopes, OAuth callback URL, app availability, and app publishing are manually configured.
- Grant the bot/application management permission on the new token storage Bitable if the copied template does not already provide it.

## Token Table Template Automation

When installing this package, the Agent should:

- Read `install-prompt-v6.md` before taking action.
- Copy the administrator-provided token Bitable template with the Feishu Drive copy-file API.
- Get the copied token table `app_token`, `table_id`, and URL.
- List all workflows in the copied token Bitable.
- Enable every workflow by setting each workflow status to `Enable`.
- List workflows again and verify every workflow status is `Enable`.
- Stop before sending authorization cards if template copy, workflow enabling, field validation, or permission validation fails.

## Secret Storage Policy

The administrator-controlled Feishu Bitable may contain a dedicated configuration row with `app_id`, `app_secret`, `FEISHU_AUTH_REDIRECT_URI`, `TOKEN_BASE_TOKEN`, and `TOKEN_TABLE_ID`.

Do not refuse to send an authorization card only because `app_secret` is stored in that controlled Bitable. This is the intended deployment design.

Do not write real secrets into GitHub, this skill package source, logs, or public docs. Read them only at runtime from the token table, runtime config, or explicit administrator input.

Important: `app_secret` is not required for sending the authorization card. The authorization-card command only needs `APP_ID` and the real `FEISHU_AUTH_REDIRECT_URI`. `app_secret` is required later for code-to-token exchange after the member authorizes.

Important: target member name/open_id is not required during installation or setup verification. Ask for or resolve a target member only after the administrator explicitly says to send an authorization card to that person. Asking for `TARGET_USER_OPEN_ID` during install, setup confirmation, placeholder filling, or token table verification is invalid behavior.

## Runtime Placeholders

The repository must not contain real environment values. The Agent should fill these from the token table, runtime config, or explicit administrator input after manual setup:

```text
LARK_APP_ID={APP_ID}
FEISHU_AUTH_REDIRECT_URI={REAL_CALLBACK_OR_FORM_RECEIVER_URL}
TOKEN_BASE_TOKEN={TOKEN_BASE_TOKEN}
TOKEN_TABLE_ID={TOKEN_TABLE_ID}
```

`FEISHU_AUTH_REDIRECT_URI` must be the real callback/form receiver URL configured by the administrator. It can come from the token table, runtime config, or explicit administrator input. It has no safe default. Do not use `https://open.feishu.cn/open-apis/auth/v1/callback` as the authorization-card redirect URI.

`LARK_APP_SECRET` / `FEISHU_APP_SECRET` must not be required before sending an authorization card. Read it later from the controlled Bitable config row, runtime config, or explicit administrator input when exchanging code for token.

## Usage

```bash
feishu-user-registry auth <open_id> "<member_name>"
```

Run this command only after the administrator asks to send an authorization card to a specific member.

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
