---
name: feishu-data-collector-v3
description: |
  Unified Feishu data collector for executive tracking and task tracking.
  Reads user_access_token from the external member token Bitable and calls Feishu OpenAPI directly.
alwaysActive: false
---

# Feishu Data Collector v3

## Purpose

This internal skill provides a reusable data collection layer for upper-level tracking skills.

It collects:

- Calendar events
- Native Feishu tasks
- Minutes
- Group message search results
- P2P message search results
- Mail message IDs

## Token Source

User tokens are read from the external member token table:

```text
{{TOKEN_BASE_TOKEN}} / {{TOKEN_TABLE_ID}}
```

The table must already be created and verified by the standalone `feishu-user-token-registry-package`.

Required token table field:

```text
成员
user_access_token
```

## Official API Contract

The endpoints below are aligned with Feishu official LLM documentation.

| Source | Method | Endpoint | Token | Notes |
| --- | --- | --- | --- | --- |
| Calendar | GET | `/open-apis/calendar/v4/calendars/primary/events/instance_view` | `user_access_token` | Uses `start_time` / `end_time` Unix seconds |
| Tasks | GET | `/open-apis/task/v2/tasks` | `user_access_token` | Uses `type=my_tasks`, `page_size`, `page_token` |
| Minutes | POST | `/open-apis/minutes/v1/minutes/search` | `user_access_token` | Uses create time filter |
| Group messages | POST | `/open-apis/im/v1/messages/search` | `user_access_token` | Uses `filter.time_range` and `filter.chat_type=group` |
| P2P messages | POST | `/open-apis/im/v1/messages/search` | `user_access_token` | Uses `filter.time_range` and `filter.chat_type=p2p` |
| Mail | GET | `/open-apis/mail/v1/user_mailboxes/me/messages` | `user_access_token` | Uses `label_id=INBOX`, `page_size<=20` |

## Usage

```bash
python3 feishu-data-collector-v3 <output.json> <open_id:name> [<open_id:name> ...]
```

Example:

```bash
python3 feishu-data-collector-v3 /tmp/executive_data.json 'ou_xxx:张三'
```

The default collection period is the last 7 days.

## Output Shape

```json
{
  "period": {"start": "...", "end": "..."},
  "executives": [
    {
      "user": "张三",
      "open_id": "ou_xxx",
      "period": "...",
      "sources": {
        "calendar": {"ok": true, "code": 0, "data": {"items": []}},
        "task": {"ok": true, "code": 0, "data": {"items": []}},
        "minutes": {"ok": true, "code": 0, "data": {"items": []}},
        "group": {"ok": true, "code": 0, "data": {"items": []}},
        "p2p": {"ok": true, "code": 0, "data": {"items": []}},
        "mail": {"ok": true, "code": 0, "data": {"items": []}}
      }
    }
  ]
}
```

## Required Scopes

- `calendar:calendar`
- `calendar:calendar.event:read`
- `task:task:read`
- `minutes:minutes`
- `minutes:minutes.search:read`
- `minutes:minutes.basic:read`
- `minutes:minutes.transcript:export`
- `search:message`
- `mail:user_mailbox.message:readonly`
- `contact:user.id:readonly`

## Sub-Skills

The v6 package also includes separate collectors for focused calls:

- `feishu-calendar-collector`
- `feishu-task-collector`
- `feishu-minutes-collector`
- `feishu-group-collector`
- `feishu-p2p-collector`
- `feishu-mail-collector`

Each sub-skill reads the same external token table and returns normalized JSON.

## Troubleshooting

- Empty token result: verify the token table has a row whose `成员` field matches the target `open_id`.
- `no permission`: verify the user authorization includes the matching user scope and the app has been published after scope changes.
- Calendar errors: use `start_time` / `end_time` Unix seconds, not `time_min` / `time_max`.
- Message search errors: use `filter.time_range` and `filter.chat_type`; response items are in `data.items`.
- Mail errors: use `/mail/v1/user_mailboxes/me/messages` for current user mailbox access.
