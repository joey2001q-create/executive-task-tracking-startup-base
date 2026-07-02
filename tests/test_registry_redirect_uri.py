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


if __name__ == "__main__":
    unittest.main()
