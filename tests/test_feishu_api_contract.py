import importlib.util
import importlib.machinery
import os
import pathlib
import contextlib
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]

os.environ.setdefault("LARK_APP_ID", "cli_a_fake")
os.environ.setdefault("LARK_APP_SECRET", "fake_secret")
os.environ.setdefault("FEISHU_TOKEN_BASE_TOKEN", "base_fake")
os.environ.setdefault("FEISHU_TOKEN_TABLE_ID", "tbl_fake")


class FakeResponse:
    def __init__(self, payload, headers=None):
        self.payload = payload
        self.headers = headers or {"Content-Type": "application/json"}

    def json(self):
        return self.payload


class FakeRequests:
    def __init__(self):
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        if url.endswith("/tenant_access_token/internal"):
            return FakeResponse({"code": 0, "tenant_access_token": "tenant_fake"})
        if "/records/search" in url:
            return FakeResponse({
                "code": 0,
                "data": {
                    "items": [
                        {"fields": {"user_access_token": [{"text": "u" * 120}]}}
                    ]
                },
            })
        return FakeResponse({"code": 0, "data": {"items": [], "has_more": False}})

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return FakeResponse({"code": 0, "data": {"items": [], "has_more": False}})


def load_module(relative_path, name):
    path = ROOT / relative_path
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class FeishuApiContractTests(unittest.TestCase):
    def test_data_collector_uses_official_task_mail_and_message_contracts(self):
        module = load_module(
            "skills-package-v6/feishu-data-collector-v3/bin/feishu-data-collector-v3",
            "feishu_data_collector_v3_contract",
        )
        fake = FakeRequests()
        with mock.patch.object(module, "requests", fake), mock.patch.object(module.time, "sleep"):
            module.collect_task("u" * 120)
            module.collect_mail("u" * 120)
            module.collect_messages("u" * 120, "2026-07-01T00:00:00+08:00", "2026-07-02T00:00:00+08:00", "group")
            module.collect_messages("u" * 120, "2026-07-01T00:00:00+08:00", "2026-07-02T00:00:00+08:00", "p2p")

        get_calls = [call for call in fake.calls if call[0] == "GET"]
        post_calls = [call for call in fake.calls if call[0] == "POST"]

        task_call = next(call for call in get_calls if call[1].endswith("/open-apis/task/v2/tasks"))
        self.assertEqual(task_call[2]["params"]["type"], "my_tasks")
        self.assertEqual(task_call[2]["params"]["user_id_type"], "open_id")
        self.assertEqual(task_call[2]["params"]["page_size"], 100)

        mail_call = next(call for call in get_calls if call[1].endswith("/open-apis/mail/v1/user_mailboxes/me/messages"))
        self.assertEqual(mail_call[2]["params"]["label_id"], "INBOX")
        self.assertEqual(mail_call[2]["params"]["page_size"], 20)

        message_calls = [call for call in post_calls if call[1].endswith("/open-apis/im/v1/messages/search")]
        self.assertEqual(len(message_calls), 2)
        self.assertEqual({call[2]["json"]["filter"]["chat_type"] for call in message_calls}, {"group", "p2p"})
        for call in message_calls:
            self.assertEqual(call[2]["params"]["page_size"], 30)
            self.assertEqual(call[2]["params"]["user_id_type"], "open_id")
            self.assertIn("time_range", call[2]["json"]["filter"])

    def test_task_collector_token_lookup_and_task_list_contract(self):
        module = load_module(
            "skills-package-v6/feishu-task-collector/bin/feishu-task-collector",
            "feishu_task_collector_contract",
        )
        fake = FakeRequests()
        with mock.patch.object(module, "requests", fake):
            result = module.collect_tasks("ou_fake")

        self.assertTrue(result["ok"])
        bitable_call = next(call for call in fake.calls if "/records/search" in call[1])
        condition = bitable_call[2]["json"]["filter"]["conditions"][0]
        self.assertEqual(condition["field_name"], "成员")
        self.assertEqual(condition["value"], ["ou_fake"])

        task_call = next(call for call in fake.calls if call[1].endswith("/open-apis/task/v2/tasks"))
        self.assertEqual(task_call[0], "GET")
        self.assertEqual(task_call[2]["params"]["type"], "my_tasks")
        self.assertEqual(task_call[2]["params"]["user_id_type"], "open_id")
        self.assertEqual(task_call[2]["params"]["page_size"], 100)

    def test_standalone_collectors_use_member_field_name(self):
        for relative_path, function_name, args in [
            ("skills-package-v6/feishu-calendar-collector/bin/feishu-calendar-collector", "collect_calendar", ("ou_fake", "2026-07-01T00:00:00+08:00", "2026-07-02T00:00:00+08:00")),
            ("skills-package-v6/feishu-group-collector/bin/feishu-group-collector", "collect_group", ("ou_fake", "2026-07-01T00:00:00+08:00", "2026-07-02T00:00:00+08:00")),
            ("skills-package-v6/feishu-p2p-collector/bin/feishu-p2p-collector", "collect_p2p", ("ou_fake", [], "2026-07-01T00:00:00+08:00", "2026-07-02T00:00:00+08:00")),
            ("skills-package-v6/feishu-mail-collector/bin/feishu-mail-collector", "collect_mail", ("ou_fake",)),
        ]:
            with self.subTest(relative_path=relative_path):
                module = load_module(relative_path, f"contract_{function_name}")
                fake = FakeRequests()
                sleep_patch = mock.patch.object(module.time, "sleep") if hasattr(module, "time") else contextlib.nullcontext()
                with mock.patch.object(module, "requests", fake), sleep_patch:
                    getattr(module, function_name)(*args)

                bitable_call = next(call for call in fake.calls if "/records/search" in call[1])
                condition = bitable_call[2]["json"]["filter"]["conditions"][0]
                self.assertEqual(condition["field_name"], "成员")


if __name__ == "__main__":
    unittest.main()
