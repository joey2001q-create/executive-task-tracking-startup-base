import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
V6 = ROOT / "skills-package-v6"
FULL_PROMPT = V6 / "full-install-prompt-v6.md"
EXEC_CONFIG = V6 / "agent-exec-config-v6.md"
README = V6 / "README.md"

REQUIRED_SKILL_DIRS = {
    "feishu-boss-work",
    "feishu-exec-task-extractor",
    "feishu-data-collector-v3",
    "feishu-calendar-collector",
    "feishu-task-collector",
    "feishu-minutes-collector",
    "feishu-group-collector",
    "feishu-p2p-collector",
    "feishu-mail-collector",
    "feishu-executive-comparison",
}

FORBIDDEN_PACKAGE_DIRS = {
    "feishu-user-token-registry",
    "hire-recruit",
    "attendance-report",
    "competitor-intelligence-v2",
    "feishu-customer-follow-tracker",
}


REQUIRED_FIELD_LINES = [
    "追踪人：用户字段",
    "追踪报告：文本 / URL 文本",
    "任务编号：公式，主键，自动生成",
    "任务标题：文本",
    "详细描述：文本",
    "负责人：单选用户",
    "任务状态：单选",
    "是否卡点：单选",
    "截止日期：日期",
    "创建人：系统字段，自动",
    "任务跟进：双向链接，自动回填",
    "跟进记录数：查找，自动",
    "跟进记录编号：公式，主键，自动",
    "关联任务：单向链接，关联任务信息表",
    "跟进内容：文本",
    "创建时间：系统字段，自动",
    "任务负责人：查找，自动",
    "任务信息表：双向链接，自动回填",
    "巡检日期：日期",
    "巡检报告：文本 / URL 文本",
]

REQUIRED_OPTIONS = ["待执行", "进行中", "已完成", "已逾期", "阻塞", "是", "否"]
FORBIDDEN_SUBJECTIVE_FIELDS = ["追踪周期", "报告摘要", "巡检摘要", "风险数量"]
FORBIDDEN_ASK_PATTERNS = [
    "请提供 APP_SECRET",
    "请粘贴 APP_SECRET",
    "请提供 AGENT_BASE_TOKEN",
    "请提供 TABLE_ID_高管追踪报告",
    "请提供 TABLE_ID_任务信息表",
    "请提供 TABLE_ID_任务跟进记录表",
    "请提供 TABLE_ID_任务巡检报告",
]


class SkillsPackageV6DocsTests(unittest.TestCase):
    def test_full_prompt_contains_complete_fixed_field_schema(self):
        text = FULL_PROMPT.read_text(encoding="utf-8")

        self.assertIn("本包内置固定字段结构不可变", text)
        self.assertIn("不要查找、索要或依赖任何历史版本包", text)
        self.assertIn("自动创建业务 Base", text)
        for line in REQUIRED_FIELD_LINES:
            self.assertIn(line, text)
        for option in REQUIRED_OPTIONS:
            self.assertIn(option, text)

    def test_exec_config_contains_same_fixed_field_schema(self):
        text = EXEC_CONFIG.read_text(encoding="utf-8")

        self.assertIn("本包内置固定字段结构不可变", text)
        self.assertIn("不要查找、索要或依赖任何历史版本包", text)
        self.assertIn("create_business_base", text)
        self.assertIn("create_business_fields", text)
        for line in REQUIRED_FIELD_LINES:
            self.assertIn(line, text)

    def test_v6_docs_do_not_ask_user_for_generated_business_ids(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in [FULL_PROMPT, EXEC_CONFIG, README]
        )

        self.assertIn("不得向管理员索要 `AGENT_BASE_TOKEN`", combined)
        self.assertIn("不得向管理员索要这四个 table_id", combined)
        self.assertIn("不要在聊天里向管理员索要或要求粘贴 `APP_SECRET`", combined)
        for pattern in FORBIDDEN_ASK_PATTERNS:
            self.assertNotIn(pattern, combined)

    def test_v6_docs_do_not_include_subjective_extra_fields(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in [FULL_PROMPT, EXEC_CONFIG, README]
        )

        for field in FORBIDDEN_SUBJECTIVE_FIELDS:
            self.assertIn(field, combined)
        self.assertIn("不得新增主观字段", combined)

    def test_v6_package_scope_is_two_business_entries_plus_internal_deps(self):
        skill_dirs = {path.parent.name for path in V6.glob("*/SKILL.md")}

        self.assertEqual(REQUIRED_SKILL_DIRS, skill_dirs)
        self.assertEqual(10, len(skill_dirs))
        for forbidden in FORBIDDEN_PACKAGE_DIRS:
            self.assertNotIn(forbidden, skill_dirs)


if __name__ == "__main__":
    unittest.main()
