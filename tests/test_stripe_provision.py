import io
import json
import os
import stat
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import stripe_provision

POSIX_ONLY = unittest.skipIf(os.name == "nt", "POSIX file modes do not apply on Windows")

# Short fake values. The module only checks for the _test_ or _live_ marker, and
# short values stay clear of secret scanners (tests/test_secret_hygiene.py, GitHub).
TEST_SECRET_KEY = "sk_test_fake1"
TEST_RESTRICTED_KEY = "rk_test_fake2"
LIVE_SECRET_KEY = "sk_live_fake3"
LIVE_RESTRICTED_KEY = "rk_live_fake4"
WEBHOOK_SECRET = "whsec_fake5"
WEBHOOK_URL = "https://hooks.example/stripe"

# Stripe responses for an account where nothing from the manifest exists yet.
NEW_ACCOUNT = {
    ("GET", "/products/search"): {"data": []},
    ("POST", "/products"): {"id": "prod_new"},
    ("GET", "/prices"): {"data": []},
    ("POST", "/prices"): {"id": "price_new"},
    ("GET", "/webhook_endpoints"): {"data": []},
    ("POST", "/webhook_endpoints"): {"id": "we_new", "url": WEBHOOK_URL, "secret": WEBHOOK_SECRET},
}


def setUpModule():
    # No test may reach Stripe: a real urlopen call fails the test.
    guard = mock.patch.object(
        stripe_provision.urllib.request,
        "urlopen",
        side_effect=AssertionError("a test tried to reach the network"),
    )
    guard.start()
    unittest.addModuleCleanup(guard.stop)


class FakeStripe:
    """A scripted Stripe client: one canned response per (method, path), every call recorded."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def request(self, method, path, params=None):
        self.calls.append((method, path, params))
        if (method, path) not in self.responses:
            raise AssertionError(f"unexpected Stripe call {method} {path}")
        return self.responses[(method, path)]

    def paths(self):
        return [(method, path) for method, path, _ in self.calls]


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class TempProjectCase(unittest.TestCase):
    """A temporary project folder and master env; nothing outside it is read or written."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.project = self.root / "demo-app"
        self.project.mkdir()
        self.master = self.root / ".env.master"

    def write_master(self, **values):
        lines = "".join(f"{key}={value}\n" for key, value in values.items())
        self.master.write_text(lines, encoding="utf-8")

    def write_manifest(self, **changes):
        manifest = stripe_provision.default_manifest(self.project)
        manifest["webhook"]["url"] = WEBHOOK_URL
        manifest.update(changes)
        path = self.project / stripe_provision.DEFAULT_MANIFEST
        path.write_text(json.dumps(manifest), encoding="utf-8")

    def master_values(self):
        return stripe_provision.parse_env_file(self.master)


class FlattenParamsTests(unittest.TestCase):
    def test_nests_dicts_repeats_lists_and_skips_none(self):
        pairs = stripe_provision.flatten_params(
            {
                "name": "Starter",
                "unit_amount": 900,
                "active": True,
                "livemode": False,
                "description": None,
                "metadata": {"project_slug": "demo", "tier": {"level": 1}},
                "enabled_events": ["invoice.paid", "invoice.payment_failed"],
            }
        )
        self.assertEqual(
            pairs,
            [
                ("name", "Starter"),
                ("unit_amount", "900"),
                ("active", "true"),
                ("livemode", "false"),
                ("metadata[project_slug]", "demo"),
                ("metadata[tier][level]", "1"),
                ("enabled_events[]", "invoice.paid"),
                ("enabled_events[]", "invoice.payment_failed"),
            ],
        )


class StripeClientRequestTests(unittest.TestCase):
    def send(self, method, path, params=None):
        with mock.patch.object(
            stripe_provision.urllib.request, "urlopen", return_value=FakeResponse({"id": "obj_1"})
        ) as urlopen:
            result = stripe_provision.StripeClient(TEST_SECRET_KEY).request(method, path, params)
        self.assertEqual(result, {"id": "obj_1"})
        self.assertEqual(urlopen.call_args.kwargs, {"timeout": 30})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), method)
        self.assertEqual(request.get_header("Authorization"), f"Bearer {TEST_SECRET_KEY}")
        return request

    def test_get_sends_params_in_the_query_string(self):
        request = self.send("GET", "/prices", {"lookup_keys": ["starter"], "limit": 1})
        url = urllib.parse.urlsplit(request.full_url)
        self.assertEqual(
            f"https://{url.netloc}{url.path}", f"{stripe_provision.STRIPE_API_BASE}/prices"
        )
        self.assertEqual(
            urllib.parse.parse_qsl(url.query), [("lookup_keys[]", "starter"), ("limit", "1")]
        )
        self.assertIsNone(request.data)

        bare = self.send("GET", "/webhook_endpoints")
        self.assertEqual(bare.full_url, f"{stripe_provision.STRIPE_API_BASE}/webhook_endpoints")
        self.assertIsNone(bare.data)

    def test_post_sends_params_as_a_form_body(self):
        request = self.send("POST", "/products", {"name": "Starter", "metadata": {"slug": "demo"}})
        self.assertEqual(request.full_url, f"{stripe_provision.STRIPE_API_BASE}/products")
        self.assertEqual(request.get_header("Content-type"), "application/x-www-form-urlencoded")
        self.assertEqual(
            urllib.parse.parse_qsl(request.data.decode("utf-8")),
            [("name", "Starter"), ("metadata[slug]", "demo")],
        )

    def test_http_error_becomes_a_runtime_error_without_the_key(self):
        error = urllib.error.HTTPError(
            f"{stripe_provision.STRIPE_API_BASE}/products",
            402,
            "Payment Required",
            {},
            io.BytesIO(b'{"error": {"message": "Your card was declined."}}'),
        )
        with mock.patch.object(stripe_provision.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(RuntimeError) as caught:
                stripe_provision.StripeClient(TEST_SECRET_KEY).request("POST", "/products", {})
        message = str(caught.exception)
        self.assertIn("POST /products failed with 402", message)
        self.assertIn("Your card was declined.", message)
        self.assertNotIn(TEST_SECRET_KEY, message)
        self.assertNotIn("Bearer", message)


class StripeKeyForModeTests(unittest.TestCase):
    def test_prefers_the_restricted_key(self):
        values = {
            "STRIPE_SECRET_KEY": TEST_SECRET_KEY,
            "STRIPE_RESTRICTED_KEY": TEST_RESTRICTED_KEY,
        }
        self.assertEqual(
            stripe_provision.stripe_key_for_mode(values, "test"),
            ("STRIPE_RESTRICTED_KEY", TEST_RESTRICTED_KEY),
        )

    def test_skips_a_key_from_the_other_mode(self):
        test_first = {
            "STRIPE_RESTRICTED_KEY": TEST_RESTRICTED_KEY,
            "STRIPE_SECRET_KEY": LIVE_SECRET_KEY,
        }
        live_first = {
            "STRIPE_RESTRICTED_KEY": LIVE_RESTRICTED_KEY,
            "STRIPE_SECRET_KEY": TEST_SECRET_KEY,
        }
        self.assertEqual(
            stripe_provision.stripe_key_for_mode(test_first, "live"),
            ("STRIPE_SECRET_KEY", LIVE_SECRET_KEY),
        )
        self.assertEqual(
            stripe_provision.stripe_key_for_mode(live_first, "test"),
            ("STRIPE_SECRET_KEY", TEST_SECRET_KEY),
        )

    def test_refusal_names_the_variables_not_their_values(self):
        values = {"STRIPE_RESTRICTED_KEY": "", "STRIPE_SECRET_KEY": LIVE_SECRET_KEY}
        with self.assertRaises(ValueError) as caught:
            stripe_provision.stripe_key_for_mode(values, "test")
        message = str(caught.exception)
        self.assertIn("STRIPE_RESTRICTED_KEY", message)
        self.assertIn("STRIPE_SECRET_KEY", message)
        self.assertNotIn(LIVE_SECRET_KEY, message)


class BuildPlanTests(TempProjectCase):
    def test_names_the_key_variable_but_never_its_value(self):
        self.write_master(STRIPE_SECRET_KEY=TEST_SECRET_KEY)
        self.write_manifest()
        plan = stripe_provision.build_plan(self.project, self.master, None, None)
        self.assertEqual(plan["stripe_key"], {"available": True, "env": "STRIPE_SECRET_KEY"})
        self.assertNotIn(TEST_SECRET_KEY, json.dumps(plan))
        self.assertEqual(
            plan["summary"],
            {
                "project_slug": "demo-app",
                "mode": "test",
                "price_count": 1,
                "webhook_requested": True,
                "ready_for_apply": True,
            },
        )
        self.assertEqual(
            plan["planned_actions"]["products"],
            [
                {
                    "key": "starter",
                    "name": "demo-app Starter",
                    "prices": ["demo-app_starter_monthly"],
                }
            ],
        )
        self.assertEqual(plan["planned_actions"]["webhook"]["secret_env"], "STRIPE_WEBHOOK_SECRET")

    def test_live_override_without_a_live_key_is_not_ready(self):
        self.write_master(STRIPE_SECRET_KEY=TEST_SECRET_KEY)
        self.write_manifest()
        plan = stripe_provision.build_plan(self.project, self.master, None, "live")
        self.assertEqual(plan["mode"], "live")
        self.assertEqual(plan["stripe_key"], {"available": False, "env": None})
        self.assertFalse(plan["summary"]["ready_for_apply"])

    def test_rejects_a_manifest_mode_other_than_test_or_live(self):
        # "Live" used to pass both the key filter and apply's --allow-live check.
        self.write_master(STRIPE_SECRET_KEY=LIVE_SECRET_KEY)
        self.write_manifest(mode="Live")
        with self.assertRaises(ValueError) as caught:
            stripe_provision.build_plan(self.project, self.master, None, None)
        self.assertIn("'Live'", str(caught.exception))


class EnsureHelperTests(unittest.TestCase):
    manifest = {"project_slug": "demo", "currency": "usd"}

    def test_reuses_a_product_found_by_project_and_manifest_key(self):
        client = FakeStripe({("GET", "/products/search"): {"data": [{"id": "prod_old"}]}})
        product = stripe_provision.ensure_product(
            client, self.manifest, {"key": "starter", "name": "Starter"}
        )
        self.assertEqual(product, {"id": "prod_old"})
        self.assertEqual(client.paths(), [("GET", "/products/search")])
        self.assertEqual(
            client.calls[0][2]["query"],
            "metadata['project_slug']:'demo' AND metadata['manifest_key']:'starter'",
        )

    def test_creates_a_missing_product_with_its_manifest_metadata(self):
        client = FakeStripe(NEW_ACCOUNT)
        product = stripe_provision.ensure_product(
            client, self.manifest, {"name": "Pro Plan!", "description": "Pro."}
        )
        self.assertEqual(product, {"id": "prod_new"})
        self.assertEqual(client.paths(), [("GET", "/products/search"), ("POST", "/products")])
        self.assertEqual(
            client.calls[1][2],
            {
                "name": "Pro Plan!",
                "description": "Pro.",
                "active": True,
                "metadata": {"project_slug": "demo", "manifest_key": "pro_plan"},
            },
        )

    def test_reuses_an_active_price_with_the_same_lookup_key(self):
        client = FakeStripe({("GET", "/prices"): {"data": [{"id": "price_old"}]}})
        price = stripe_provision.ensure_price(
            client, self.manifest, "prod_1", {"lookup_key": "demo_monthly", "unit_amount": 900}
        )
        self.assertEqual(price, {"id": "price_old"})
        self.assertEqual(
            client.calls,
            [("GET", "/prices", {"lookup_keys": ["demo_monthly"], "active": True, "limit": 1})],
        )

    def test_creates_a_missing_recurring_price(self):
        client = FakeStripe(NEW_ACCOUNT)
        price = stripe_provision.ensure_price(
            client,
            self.manifest,
            "prod_1",
            {"key": "pro_yearly", "unit_amount": 9000, "interval": "year", "interval_count": 1},
        )
        self.assertEqual(price, {"id": "price_new"})
        self.assertEqual(client.paths(), [("GET", "/prices"), ("POST", "/prices")])
        self.assertEqual(
            client.calls[1][2],
            {
                "product": "prod_1",
                "currency": "usd",
                "unit_amount": 9000,
                "nickname": "pro_yearly",
                "lookup_key": "pro_yearly",
                "metadata": {"project_slug": "demo", "manifest_key": "pro_yearly"},
                "recurring": {"interval": "year", "interval_count": 1},
            },
        )

    def test_updates_the_live_endpoint_with_the_same_url(self):
        client = FakeStripe(
            {
                ("GET", "/webhook_endpoints"): {
                    "data": [
                        {"id": "we_gone", "url": WEBHOOK_URL, "deleted": True},
                        {"id": "we_other", "url": "https://other.example/hook"},
                        {"id": "we_old", "url": WEBHOOK_URL},
                    ]
                },
                ("POST", "/webhook_endpoints/we_old"): {"id": "we_old", "url": WEBHOOK_URL},
            }
        )
        endpoint, created = stripe_provision.ensure_webhook(
            client, {"url": WEBHOOK_URL, "events": ["invoice.paid"]}
        )
        self.assertFalse(created)
        self.assertEqual(endpoint["id"], "we_old")
        self.assertEqual(
            client.calls[1][2], {"enabled_events": ["invoice.paid"], "description": None}
        )

    def test_creates_a_missing_endpoint_with_the_default_events(self):
        client = FakeStripe(NEW_ACCOUNT)
        endpoint, created = stripe_provision.ensure_webhook(client, {"url": WEBHOOK_URL})
        self.assertTrue(created)
        self.assertEqual(endpoint["secret"], WEBHOOK_SECRET)
        self.assertEqual(
            client.calls[1][2],
            {
                "url": WEBHOOK_URL,
                "enabled_events": stripe_provision.DEFAULT_WEBHOOK_EVENTS,
                "description": None,
                "metadata": {},
            },
        )


class ApplyPlanTests(TempProjectCase):
    def apply(self, responses, overwrite_env=False, **manifest_changes):
        self.write_manifest(**manifest_changes)
        self.plan = stripe_provision.build_plan(self.project, self.master, None, None)
        client = FakeStripe(responses)
        with mock.patch.object(
            stripe_provision, "StripeClient", return_value=client
        ) as client_class:
            result = stripe_provision.apply_plan(self.plan, self.master, overwrite_env)
        client_class.assert_called_once_with(TEST_SECRET_KEY)
        return result, client

    def test_new_price_ids_and_webhook_secret_land_in_the_master_env(self):
        self.write_master(STRIPE_SECRET_KEY=TEST_SECRET_KEY)
        result, client = self.apply(NEW_ACCOUNT)
        self.assertEqual(client.paths(), list(NEW_ACCOUNT))
        values = self.master_values()
        self.assertEqual(values["STRIPE_PRICE_STARTER"], "price_new")
        self.assertEqual(values["STRIPE_WEBHOOK_SECRET"], WEBHOOK_SECRET)
        self.assertEqual(values["STRIPE_SECRET_KEY"], TEST_SECRET_KEY)
        self.assertEqual(
            result,
            {
                "mode": "test",
                "stripe_key_env": "STRIPE_SECRET_KEY",
                "products": [{"key": "starter", "id": "prod_new"}],
                "prices": [{"key": "starter_monthly", "id": "price_new"}],
                "webhook": {"id": "we_new", "created": True, "url": WEBHOOK_URL},
                "master_env_updates": {
                    "STRIPE_PRICE_STARTER": "added",
                    "STRIPE_WEBHOOK_SECRET": "added",
                },
                "secret_values_printed": False,
            },
        )
        printed = json.dumps(result)
        self.assertNotIn(WEBHOOK_SECRET, printed)
        self.assertNotIn(TEST_SECRET_KEY, printed)

    @POSIX_ONLY
    def test_master_env_is_owner_only_after_the_write(self):
        self.write_master(STRIPE_SECRET_KEY=TEST_SECRET_KEY)
        os.chmod(self.master, 0o644)
        self.apply(NEW_ACCOUNT)
        self.assertEqual(stat.S_IMODE(self.master.stat().st_mode), 0o600)

    def test_existing_webhook_keeps_the_env_secret_and_returns_a_note(self):
        self.write_master(STRIPE_SECRET_KEY=TEST_SECRET_KEY, STRIPE_WEBHOOK_SECRET="whsec_current")
        responses = dict(NEW_ACCOUNT)
        responses[("GET", "/webhook_endpoints")] = {"data": [{"id": "we_old", "url": WEBHOOK_URL}]}
        responses[("POST", "/webhook_endpoints/we_old")] = {"id": "we_old", "url": WEBHOOK_URL}
        result, client = self.apply(responses)
        self.assertNotIn(("POST", "/webhook_endpoints"), client.paths())
        self.assertEqual(self.master_values()["STRIPE_WEBHOOK_SECRET"], "whsec_current")
        self.assertFalse(result["webhook"]["created"])
        self.assertIn("not retrievable", result["webhook"]["secret_note"])
        self.assertEqual(result["master_env_updates"], {"STRIPE_PRICE_STARTER": "added"})

    def test_new_webhook_secret_goes_where_the_plan_said_without_secret_env(self):
        # The plan names STRIPE_WEBHOOK_SECRET when the manifest has no secret_env, and
        # Stripe returns a new endpoint's secret only once, so apply must not drop it.
        self.write_master(STRIPE_SECRET_KEY=TEST_SECRET_KEY)
        result, _ = self.apply(NEW_ACCOUNT, webhook={"url": WEBHOOK_URL})
        self.assertEqual(
            self.plan["planned_actions"]["webhook"]["secret_env"], "STRIPE_WEBHOOK_SECRET"
        )
        self.assertEqual(self.master_values().get("STRIPE_WEBHOOK_SECRET"), WEBHOOK_SECRET)
        self.assertEqual(result["master_env_updates"].get("STRIPE_WEBHOOK_SECRET"), "added")

    def test_overwrite_env_decides_whether_an_existing_price_id_is_replaced(self):
        for overwrite, kept, status in ((False, "price_old", None), (True, "price_new", "updated")):
            with self.subTest(overwrite_env=overwrite):
                self.write_master(
                    STRIPE_SECRET_KEY=TEST_SECRET_KEY, STRIPE_PRICE_STARTER="price_old"
                )
                result, _ = self.apply(NEW_ACCOUNT, overwrite_env=overwrite)
                self.assertEqual(self.master_values()["STRIPE_PRICE_STARTER"], kept)
                self.assertEqual(result["master_env_updates"].get("STRIPE_PRICE_STARTER"), status)


class ApplyCommandTests(TempProjectCase):
    def run_apply(self, mode):
        self.write_master(STRIPE_SECRET_KEY=LIVE_SECRET_KEY)
        plan_path = self.root / "plan.json"
        plan = {"mode": mode, "master_env": str(self.master), "manifest": {}}
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        args = stripe_provision.build_parser().parse_args(["apply", "--plan", str(plan_path)])
        with mock.patch.object(
            stripe_provision,
            "StripeClient",
            side_effect=AssertionError("a Stripe client was built"),
        ):
            args.func(args)

    def test_refuses_live_mode_without_allow_live(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_apply("live")
        self.assertIn("--allow-live", str(caught.exception))

    def test_refuses_a_mode_spelling_that_would_skip_the_live_check(self):
        with self.assertRaises(ValueError):
            self.run_apply("Live")


if __name__ == "__main__":
    unittest.main()
