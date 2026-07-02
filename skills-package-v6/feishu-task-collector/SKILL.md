---
name: feishu-task-collector
description: Internal/shared Feishu task data collector. Reads user_access_token from the member token Bitable and returns normalized task JSON for task-tracking.
---

# Feishu Task Collector

This is an internal/shared dependency for `task-tracking`; do not expose it as a user-selectable business skill.

## Usage

```bash
feishu-task-collector --user <open_id> [--output file.json]
```

## Required Runtime Configuration

The token table is not hardcoded. The agent must fill these values from the configured member token Bitable after the administrator completes the prerequisite setup:

- `LARK_APP_ID` or `FEISHU_APP_ID`
- `LARK_APP_SECRET` or `FEISHU_APP_SECRET`
- `FEISHU_TOKEN_BASE_TOKEN` or `FEISHU_BASE_TOKEN` or `AGENT_BASE_TOKEN`
- `FEISHU_TOKEN_TABLE_ID` or `FEISHU_TABLE_ID`

The member token table must include:

- `成员`
- `user_access_token`

## Official API Contract

- Tenant token: `POST /open-apis/auth/v3/tenant_access_token/internal`
- Token table lookup: `POST /open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/search`
- Task list: `GET /open-apis/task/v2/tasks`

Task list parameters:

- `type=my_tasks`
- `page_size=100`
- `user_id_type=open_id`
- `page_token` when paginating

## Output

```json
{
  "ok": true,
  "source": "task",
  "user": "ou_xxx",
  "count": 2,
  "items": []
}
```
