import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "feishu-user-token-registry-package" / "feishu-user-token-registry" / "bin" / "feishu-user-registry"
DEFAULT_CALLBACK = "https://open.feishu.cn/open-apis/auth/v1/callback"


class RegistryRedirectUriTests(unittest.TestCase):
    def test_rejects_default_feishu_callback_redirect_uri(self):
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn(f'DEFAULT_FEISHU_CALLBACK="{DEFAULT_CALLBACK}"', script)
        self.assertIn('if [ "$AUTH_REDIRECT_URI" = "$DEFAULT_FEISHU_CALLBACK" ]; then', script)
        self.assertIn("Invalid FEISHU_AUTH_REDIRECT_URI", script)
        self.assertIn("token table, runtime config, or explicit administrator input", script)

    def test_authorization_card_is_chinese_and_prevents_duplicate_resend(self):
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("授权卡片", script)
        self.assertIn("立即授权", script)
        self.assertIn("请点击下方按钮完成飞书应用授权", script)
        self.assertIn("不要自动或手动重复发送授权卡片", script)
        self.assertIn(".data.message_id // .data.message.message_id // .message_id", script)
        self.assertNotIn("Feishu app authorization", script)
        self.assertNotIn("Authorize now", script)
        self.assertNotIn("please authorize the app", script)


if __name__ == "__main__":
    unittest.main()
