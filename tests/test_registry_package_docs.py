import pathlib
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "feishu-user-token-registry-package"
PROMPT = PKG / "install-prompt-v6.md"
README = PKG / "README.md"
LEGACY_PROMPT = PKG / "install-prompt.md"
ZIP = ROOT / "feishu-user-token-registry-package-v6.zip"


class RegistryPackageDocsTests(unittest.TestCase):
    def test_registry_keeps_only_v6_install_prompt(self):
        self.assertTrue(PROMPT.exists())
        self.assertFalse(LEGACY_PROMPT.exists())

        readme = README.read_text(encoding="utf-8")
        self.assertIn("install-prompt-v6.md", readme)
        self.assertNotIn("install-prompt.md", readme)

    def test_registry_permission_flow_is_explicit(self):
        text = PROMPT.read_text(encoding="utf-8")

        self.assertIn("Agent 自动转移新 Token 表所有者给管理员", text)
        self.assertIn("手动把 bot 加为新 Token 表的“可管理”协作者", text)
        self.assertIn("Agent 必须暂停提醒，不能跳过，不能假装已完成", text)
        self.assertIn("只有管理员确认 bot 已经是“可管理”协作者后，才能进入本步骤", text)
        self.assertLess(text.index("Agent 自动转移新 Token 表所有者给管理员"), text.index("手动把 bot 加为新 Token 表"))
        self.assertLess(text.index("手动把 bot 加为新 Token 表"), text.index("开启所有 Workflows"))

    def test_registry_prompt_does_not_handle_target_member_during_install(self):
        text = PROMPT.read_text(encoding="utf-8")

        self.assertIn("只有当管理员明确说类似下面的话后，才进入目标成员处理", text)
        self.assertIn("给张三发授权卡片", text)
        self.assertIn("不要在安装、模板复制、所有者转移、bot 可管理权限确认、workflow 开启、字段校验或权限校验阶段询问目标成员", text)

    def test_registry_zip_contains_only_v6_prompt_when_present(self):
        if not ZIP.exists():
            self.skipTest("registry v6 zip has not been built yet")

        with zipfile.ZipFile(ZIP) as archive:
            names = archive.namelist()

        self.assertIn("feishu-user-token-registry-package/install-prompt-v6.md", names)
        self.assertNotIn("feishu-user-token-registry-package/install-prompt.md", names)
        forbidden_fragments = [".DS_Store", "__MACOSX", "__pycache__", ".pyc"]
        for name in names:
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, name)


if __name__ == "__main__":
    unittest.main()
