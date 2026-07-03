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


FORBIDDEN_SUBJECTIVE_FIELDS = ["追踪周期", "报告摘要", "巡检摘要", "风险数量"]
FORBIDDEN_EXPLICIT_FIELD_LINES = [
    "追踪人：用户字段",
    "任务编号：公式，主键，自动生成",
    "任务状态选项：待执行、进行中、已完成、已逾期、阻塞",
    "是否卡点选项：是、否",
]
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

        self.assertIn("业务表字段结构以指定模板 Base 为准", text)
        self.assertIn("不要查找、索要或依赖任何历史版本包", text)
        self.assertIn("TEMPLATE_BASE_TOKEN=XDvOblimtagfxzsyD5ncxuWHn5I", text)
        self.assertIn("--without-content", text)
        self.assertIn("不要自行新建空 Base", text)
        self.assertIn("字段结构以业务模板 Base 为准", text)
        for line in FORBIDDEN_EXPLICIT_FIELD_LINES:
            self.assertNotIn(line, text)

    def test_exec_config_contains_same_fixed_field_schema(self):
        text = EXEC_CONFIG.read_text(encoding="utf-8")

        self.assertIn("业务表字段结构以模板 Base 为准", text)
        self.assertIn("不要查找、索要或依赖任何历史版本包", text)
        self.assertIn("copy_business_template_base", text)
        self.assertIn("verify_business_fields", text)
        self.assertIn("XDvOblimtagfxzsyD5ncxuWHn5I", text)
        for line in FORBIDDEN_EXPLICIT_FIELD_LINES:
            self.assertNotIn(line, text)

    def test_v6_docs_do_not_ask_user_for_generated_business_ids(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in [FULL_PROMPT, EXEC_CONFIG, README]
        )

        self.assertIn("不得向管理员索要 `AGENT_BASE_TOKEN`", combined)
        self.assertIn("不得向管理员索要这四个 table_id", combined)
        self.assertIn("不要在聊天里向管理员索要或要求粘贴 `APP_SECRET`", combined)
        self.assertIn("复制模板 Base 后按返回结果和表名自动解析", combined)
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

    def test_task_cron_uses_beijing_time(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in [FULL_PROMPT, EXEC_CONFIG, README]
        )

        self.assertIn("北京时间", combined)
        self.assertIn("Asia/Shanghai", combined)
        self.assertIn("TASK_TRACKING_CRON_TZ=Asia/Shanghai", combined)
        self.assertIn("TASK_TRACKING_CRON_TIME_DESC=北京时间每天 21:00", combined)

    def test_business_template_workflows_are_verified_after_copy(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in [FULL_PROMPT, EXEC_CONFIG, README]
        )

        self.assertIn("verify_business_workflows", combined)
        self.assertIn("验证业务模板 workflow", combined)
        self.assertIn("列出复制后 Base 的 workflows", combined)
        self.assertIn("模板里的业务 workflow 已随模板复制", combined)
        self.assertIn("所有业务 workflow 都是 Enable/已启用状态", combined)
        self.assertIn("API 因权限限制无法开启", combined)
        self.assertIn("管理员手动开启后", combined)
        self.assertIn("/open-apis/bitable/v1/apps/{AGENT_BASE_TOKEN}/workflows", combined)


if __name__ == "__main__":
    unittest.main()
