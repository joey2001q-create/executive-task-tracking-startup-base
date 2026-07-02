# 配置 Schema

## 完整配置

```yaml
# 1. 输入模式
input:
  # 三选一：report | data | message
  source: report
  
  # 方式 1：报告文本
  report_text: |
    👤 张三 行动画像
    ...
  
  # 方式 2：自动拉数据
  data:
    executives:
      - name: 张三
        role: 销售VP
      - name: 李四
        role: 技术VP
    time_range:
      relative: "last_24_hours"
  
  # 方式 3：从飞书群读报告
  message:
    chat_id: "oc_5cf6fb15e4bf6f9f6f3b52314db93fab"
    lookback_messages: 50  # 看最近 50 条
    auto_detect: true      # 自动识别带"📋"的报告

# 2. 多维表配置
bitable:
  app_token: "{{AGENT_BASE_TOKEN}}"
  task_table_id: "{{TABLE_ID_任务信息表}}"
  tracking_table_id: "{{TABLE_ID_任务跟进记录表}}"

# 3. 同步策略
sync:
  # 是否新增任务
  add_new: true
  
  # 是否更新现有任务（状态/卡点变化时）
  update_existing: true
  
  # 是否追加跟进记录
  append_tracking: true
  
  # 去重相似度阈值（0-1）
  dedup_threshold: 0.8
  
  # 模糊匹配是否需老板确认
  fuzzy_match_confirm: true
  
  # 干跑模式（只报告不写入）
  dry_run: false
  
  # 单次最大处理任务数
  max_tasks_per_run: 100

# 4. 跟进内容配置
tracking:
  include_metadata: true   # 跟进内容是否包含报告元数据
  mention_owner: true      # 是否 @ 任务负责人
  include_link: true       # 是否附上多维表记录链接

# 5. 推送配置
output:
  push_to: "chat:oc_xxx"  # 可选
  format: "card"          # text | card | markdown
  on_error: "report"     # report | silent
```

## 老板视角的隐含默认

| 配置 | 默认值 | 理由 |
|---|---|---|
| input.source | `report` | 老板最常直接转发报告 |
| sync.add_new | `true` | 新增是核心需求 |
| sync.update_existing | `true` | 状态同步是核心需求 |
| sync.append_tracking | `true` | 审计日志必备 |
| sync.dedup_threshold | `0.8` | 平衡准确率和召回率 |
| sync.fuzzy_match_confirm | `true` | 边界情况让老板拍板 |
| sync.dry_run | `false` | 真正执行（首次手动跑后改 true 看效果）|
| tracking.include_metadata | `true` | 审计需要 |
| output.format | `card` | 飞书消息卡片更美观 |

## 触发方式

### 1. 老板手动触发

老板说："把张三最新报告里的任务都加到多维表"

→ agent 解析为：
```yaml
input:
  source: report
  report_text: <解析老板消息中的报告>
sync:
  dry_run: false
```

### 2. 老板转发报告（自动识别）

老板在群里转发一条报告，附带"加到多维表"

→ agent 抓取转发的报告内容，识别后执行。

### 3. 每日定时

cron job 自动跑（详见后文）。

### 4. 🆕 老板直接布置任务（最高频）

老板日常说："给张三布置个任务：6/15 前完成产品 V2 评审"

→ agent 解析为：
```yaml
input:
  source: command
  command:
    boss_id: "{{BOSS_OPEN_ID}}"
    boss_name: "黄杰"
    source_message_id: <原消息 ID>
    raw_text: "给张三布置个任务：6/15 前完成产品 V2 评审"
    parsed:
      - title: "产品 V2 评审"
        owner_name: "张三"
        owner_open_id: <从通讯录查>
        due_raw: "6/15"
        due_ms: <转毫秒>
        status: "待执行"
```

**关键行为**：
- **姓名 → open_id** 自动查（用 `feishu_search_user` 工具）
- **重名处理**：返回多个匹配 → 反问老板"哪个张三？"
- **日期解析**：今天/明天/下周/几月几日 → 转 ISO + 毫秒时间戳
- **状态**：默认 `待执行`（opt1Y4cCGk）
- **创建人**：自动（系统字段 = bot）
- **详细描述**：
  ```
  布置人: 黄杰
  原话: 给张三布置个任务：6/15 前完成产品 V2 评审
  布置时间: 2026-06-11 19:51
  ```
- **跟进记录**：
  ```
  【老板布置任务 - 黄杰】
  原话: 给张三布置个任务：6/15 前完成产品 V2 评审
  截止: 6/15
  状态: 待执行
  ```
- **去重**：跟"报告同步"共用同一套去重规则（精确 → 规范化 → 模糊）
- **反问触发**：以下情况必须反问老板，不能瞎猜
  - 任务标题/动作不明确（无动词 + 无对象）
  - 截止日期不明确（"尽快/近期/最近"）
  - 负责人重名查不到唯一
  - 任务类型模糊（是日程/任务/通知？）

**示例交互**：

老板: "给张三布置个任务：6/15 前完成产品 V2 评审"
小阿杰: "✅ 已布置！【张三】产品 V2 评审 | 截止 6/15 | 待执行 → 多维表已建，rec_xxx"

老板: "让李四去跟一下 XXX"（无截止日）
小阿杰: "🟡 布置人李四一个任务，需要确认下：
  - 任务: 跟一下 XXX
  - 截止: ?
  截止是几号？还是没硬性要求？"

老板: "安排王五对接客户"（动作不明确）
小阿杰: "🟡 您想布置的'对接客户'具体是：
  - 方案
  - 报价
  - 合同
  - 跟进
  哪个？或者您直接说"
    executives: <名单>
    time_range:
      relative: "last_24_hours"
sync:
  dry_run: false
output:
  push_to: "chat:{{REPORT_CHAT_ID}}"
```

---

## Cron 配置

### 推荐配置

```yaml
name: 高管任务每日同步
description: 每天 21:00 自动从高管报告同步任务到多维表
schedule:
  kind: cron
  expr: "0 21 * * *"
  tz: "Asia/Shanghai"
  staggerMs: 300000  # 5 分钟内随机延迟
sessionTarget: isolated
enabled: true
payload:
  kind: agentTurn
  message: |
    你是小阿杰。运行 feishu-exec-task-extractor skill。
    
    配置（每日同步模式）：
    ```yaml
    input:
      source: data
      data:
        executives: [张三, 李四, 王五]  # 实际名单
        time_range:
          relative: "last_24_hours"
    
    sync:
      add_new: true
      update_existing: true
      append_tracking: true
      dedup_threshold: 0.8
      fuzzy_match_confirm: false  # 定时任务不打断
      dry_run: false
      max_tasks_per_run: 200
    
    output:
      push_to: "chat:{{REPORT_CHAT_ID}}"
      format: "card"
    ```
    
    执行步骤：
    1. 调 feishu-executive-tracker 拉所有高管的最新数据
    2. 解析每人的行动项
    3. 调本 skill 同步到多维表（多维表 ID 已预置）
    4. 输出同步报告，推送到汇总群
  timeoutSeconds: 600
delivery:
  mode: announce
  channel: feishu
  to: "chat:{{REPORT_CHAT_ID}}"
  failureDestination:
    mode: announce
    channel: feishu
    to: "user:{{BOSS_OPEN_ID}}"  # 失败推送给老板私聊
```

### 首次启用建议

**Step 1**: 老板手动跑一次 `dry_run: true`，看效果：

```
"跑一下高管任务同步，dry_run 模式"
```

**Step 2**: 老板看完"将要做什么"清单，确认无误：

```
"同步下去，dry_run: false"
```

**Step 3**: 创建 cron job，每天 21:00 自动跑。

## 失败处理

| 失败 | 行为 |
|---|---|
| 高管报告拉取失败 | 跳过该高管，报告中标注，继续其他 |
| 多维表写入失败 | 整次同步失败，推送错误给老板 |
| 字段 ID 不对 | 提示老板"多维表字段可能改了，请检查 SKILL 配置"|
| 同步报告推送失败 | 推送到老板私聊 |

## 监控与告警

老板关心的告警：

- **新增任务 > 20 条/天**：可能数据源有误，老板人工审视
- **疑似失联 > 3 条**：可能高管整体状态异常
- **同步失败**：立即重试 + 推送老板

## 报告示例

```
📊 高管任务同步报告（2026-06-11 21:00）

📋 本次扫描：
• 高管：3 人
• 时间窗口：24h
• 候选任务：15 条
• 多维表现有任务：42 条

✅ 同步结果：
• 新增任务：5 条
• 更新任务：3 条
• 跳过重复：7 条
• 失败：0 条

🆕 新增任务：
1. 【张三】产品V2.0上线 | rec_xxx | 截止 6/15
2. 【李四】客户A合同 | rec_yyy | 阻塞
3. 【王五】团队周报上线 | rec_zzz | 已完成
...

🔄 更新任务：
1. 【张三】老任务A | 进行中 → 已完成 | 6/10
2. ...

⏭️ 跳过重复：
1. 【张三】产品V2.0上线（精确匹配 rec_aaa）
2. ...

🔍 状态同步检查：
• 逾期告警：1 条 → 【李四】团队周报 | 截止 6/10 已逾期 1 天
• 疑似失联：2 条 → 【张三】客户A合同谈判 | 7 天未提

🔗 多维表：https://ldkj.feishu.cn/wiki/Ai4QwSldriST7pkaAkgcWj1inYe
```

## 性能预期

- 单次同步（3-5 人，24h 窗口）：30-60 秒
- 单次同步（10 人，24h 窗口）：60-120 秒
- 拉取多维表 50 条任务：~2 秒
- 拉取高管数据（每人）：~10-30 秒
- 写入 50 条任务：~10 秒
- 追加 50 条跟进记录：~10 秒
