# 去重规则

每次从报告中提取候选任务后，**必须**先与多维表现有任务对比去重，避免重复入库。

## 多维表主键机制

任务信息表的主键（任务编号）是**公式字段**：
```
fldbZzTVN4 = 任务标题 & "-" & 负责人
```

> 例如：`产品 V2.0上线-张三`

这意味着：**主键 = 标题 + 负责人** 是唯一标识。

## 去重算法（4 级）

### 级别 1：精确匹配（最高优先级）

```python
existing_key = f"{existing_title}_{existing_owner_open_id}"
candidate_key = f"{candidate_title}_{candidate_owner_open_id}"
if existing_key == candidate_key:
    return "EXACT_DUPLICATE"
```

✅ 完全相同 → **视为重复，跳过**

### 级别 2：规范化匹配

去除空格、标点、全半角差异后比较：

```python
def normalize(text):
    return re.sub(r'[\s\W_]+', '', text.lower())

if normalize(existing_title) == normalize(candidate_title) and existing_owner == candidate_owner:
    return "NORMALIZED_DUPLICATE"
```

✅ 例如"产品V2.0上线" vs "产品 v2.0 上线" → **视为重复，跳过**

### 级别 3：模糊匹配（相似度阈值）

使用最长公共子序列（LCS）或编辑距离计算相似度：

```python
def similarity(a, b):
    # LCS-based
    lcs_len = lcs_length(a, b)
    return lcs_len / max(len(a), len(b))

if similarity(normalize(existing_title), normalize(candidate_title)) >= 0.8 and existing_owner == candidate_owner:
    return "FUZZY_DUPLICATE"
```

✅ 例如"产品V2.0上线" vs "产品V2.0 上线发布"（相似度 0.85）→ **视为重复，需要老板确认**

⚠️ **0.8 是默认阈值**（可在 config 中调整）
- 调高到 0.9：更严格，容易漏掉近似任务
- 调低到 0.7：更宽松，容易把不同任务合并

### 级别 4：新任务

以上都不匹配 → **新增**

## 边界情况

### 边界 1：同一任务，不同负责人？

- 例如：原任务负责人"张三"，报告里提到"现在转给李四负责"
- **不算重复**（主键不同）→ 新增一条任务
- 老的更新为"已完成"或"已转交"
- 在跟进表加一条记录："X月X日，从张三转给李四"

### 边界 2：同一任务，不同时间点提到？

- 例如：上周报告里"XX 进行中"，本周报告"XX 已完成"
- **级别 1 匹配**（标题+负责人相同）→ 视为同一任务
- **更新**任务状态：`进行中` → `已完成`
- **追加**跟进记录："X月X日，完成"

### 边界 3：模糊匹配需要人工确认

当相似度在 0.7-0.8 之间的"边界任务"：

```
⚠️ 边界判断（请确认）：

候选新任务：【张三】客户A合同谈判
与现有任务【张三】客户A合同沟通（rec_xxx）相似度 0.75
是同一任务吗？
- [1] 是 → 更新现有任务
- [2] 否 → 新增任务
- [3] 跳过本次
```

老板回复后按选择执行。

### 边界 4：报告里任务标题不全

例如报告写"继续推进 Q3"，没有具体标题：

```
❌ 不入库（黑盒）
⚠️ 提示老板补全："【张三】'继续推进 Q3' 标题不清晰，无法入库"
```

或在跟进表加一条："X月X日，报告提到'继续推进 Q3'，需补全任务信息"

## 性能与限制

- **拉取策略**：单次拉 500 条（飞书 API 上限），超过时分页
- **全量对比 vs 增量**：
  - 默认全量（保证准确）
  - 性能优化：按负责人分组对比（同一负责人的任务只跟其候选对比）
- **缓存**：本次 session 内拉到的多维表数据可缓存 5 分钟，避免反复拉

## 数据结构

```python
# 缓存的多维表数据
existing_tasks = [
  {
    "record_id": "rec_xxx",
    "task_id": "产品V2.0上线-张三",  # 公式主键
    "title": "产品V2.0上线",
    "owner": "ou_xxx",
    "status": "进行中",
    "due_date": "2026-06-15",
    "blocker": "等设计稿",
    "tracking_count": 3
  },
  ...
]
```

## 去重日志

每次同步输出"跳过重复"清单：

```
⏭️ 跳过重复（5 条）：
1.【张三】产品V2.0上线 | 精确匹配 | rec_xxx
2.【李四】客户A合同 | 规范化匹配 | rec_yyy
3.【王五】产品 V2.0 上线 | 模糊匹配 0.92 | rec_zzz
4.【张三】客户A合同谈判 | 模糊匹配 0.75 需确认
5.【李四】老任务 | 标题为空 | 已跳过
```

老板扫一眼就知道哪些跳过了。
