import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import change_control


class ChangeControlTests(unittest.TestCase):
    def test_manifest_adds_use_case_standard_without_overriding_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "sample-agent"
            project.mkdir()
            (project / "README.md").write_text("# Sample\n", encoding="utf-8")
            (project / "AGENTS.md").write_text("# Agent Rules\n", encoding="utf-8")

            manifest = change_control.build_manifest(project)
            paths = {action["relative_path"] for action in manifest["actions"]}

            self.assertIn("docs/standards/engineering-governance-by-use-case.md", paths)
            self.assertIn("docs/policy/durable-development-engineering-policy.md", paths)
            self.assertIn("docs/standards/README.md", paths)
            self.assertIn("docs/standards/ship-ready-engineering-standard.md", paths)
            self.assertIn("docs/standards/context-hygiene-standard.md", paths)
            self.assertIn("docs/context-map.md", paths)
            self.assertIn("docs/domain-language.md", paths)
            self.assertIn("project-control.yaml", paths)
            self.assertTrue(any(action.get("block_id") == change_control.USE_CASE_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.SHIP_READY_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.CONTEXT_HYGIENE_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.LEAN_STARTUP_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.FUNDAMENTALS_BLOCK_ID for action in manifest["actions"]))
            self.assertTrue(any(action.get("block_id") == change_control.GRAPHIFY_BLOCK_ID for action in manifest["actions"]))

            manifest_path = project / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            change_control.apply_manifest(manifest_path)

            control = (project / "project-control.yaml").read_text(encoding="utf-8")
            self.assertIn("project_type: agent", control)
            self.assertIn("risk_tier: low", control)
            self.assertIn("governance_level: 1", control)
            self.assertIn("primary: AI agent with tools", control)
            self.assertIn("docs/context-map.md", control)
            self.assertIn("agentic_coding:", control)
            agent_rules = (project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Fundamentals-First AI Coding", agent_rules)
            self.assertIn("AI speed does not make bad code cheap", agent_rules)
            self.assertIn("smallest safe improvement", agent_rules)
            self.assertIn("Context Hygiene Managed Instructions", agent_rules)
            self.assertIn("docs/context-map.md", agent_rules)
            self.assertIn("The repository remembers", agent_rules)
            self.assertIn("summary-only", agent_rules)
            self.assertIn("context-hygiene-standard.md", agent_rules)
            self.assertIn("targeted diffs", agent_rules)
            self.assertIn("lean startup", agent_rules)
            self.assertIn("Lean Startup And Preflight Managed Instructions", agent_rules)
            self.assertIn("git status --short", agent_rules)
            self.assertIn("risk classification", agent_rules)
            self.assertIn("temporary lean-out guides", agent_rules)
            self.assertIn("Draft complete", agent_rules)
            self.assertIn("Project completion is a human decision", agent_rules)
            self.assertIn("repeated attempts stop producing new evidence", agent_rules)
            self.assertIn("Graphify Policy", agent_rules)
            self.assertIn("Tools/graphify/docs/agent-governance.md", agent_rules)
            self.assertIn("Tools/graphify/workspace/out/graph.json", agent_rules)
            self.assertIn("workspace graph for cross-repo routing", agent_rules)
            self.assertIn("known-file edits", agent_rules)
            self.assertIn("graphify-setup-project /path/to/repo", agent_rules)
            self.assertNotIn("/home/adamgoodwin/.local/bin/graphify-setup-project", agent_rules)
            self.assertIn("/graphify /path/to/repo", agent_rules)
            self.assertIn("full semantic repo graphs", agent_rules)
            self.assertIn("Do not trigger a full `/graphify` rebuild", agent_rules)
            self.assertIn("context clear", agent_rules)
            self.assertIn("rather than hard-coding a provider", agent_rules)
            self.assertIn("graphify update . --no-cluster", agent_rules)
            self.assertNotIn("graphify update . --no-cluster --force", agent_rules)
            self.assertIn("do not index, print, summarize, or commit secrets", agent_rules)
            domain_language = (project / "docs" / "domain-language.md").read_text(encoding="utf-8")
            self.assertIn("# Domain Language", domain_language)
            self.assertIn("Avoid Saying", domain_language)
            context_map = (project / "docs" / "context-map.md").read_text(encoding="utf-8")
            self.assertIn("# Context Map", context_map)
            self.assertIn("Load By Task", context_map)
            self.assertIn("budget class", context_map)
            standards_index = (project / "docs" / "standards" / "README.md").read_text(encoding="utf-8")
            self.assertIn("# Engineering Standards Index", standards_index)
            self.assertIn("Ship-Ready Engineering Standard", standards_index)
            self.assertIn("Context Hygiene Standard", standards_index)
            self.assertIn("Context Routing", standards_index)
            ship_ready = (project / "docs" / "standards" / "ship-ready-engineering-standard.md").read_text(encoding="utf-8")
            self.assertIn("# Ship-Ready Engineering Standard", ship_ready)
            self.assertIn("Completion States", ship_ready)
            self.assertIn("Draft complete", ship_ready)
            self.assertIn("Project completion is a human decision", ship_ready)
            self.assertIn("Definition Of Shipped", ship_ready)
            context_hygiene = (project / "docs" / "standards" / "context-hygiene-standard.md").read_text(encoding="utf-8")
            self.assertIn("# Context Hygiene Standard", context_hygiene)
            self.assertIn("Context Tiers And Budgets", context_hygiene)
            self.assertIn("Cache-Friendly Prompting", context_hygiene)
            self.assertIn("Token-Friendly Done", context_hygiene)
            self.assertIn("summary-only", context_hygiene)
            self.assertIn("Lean Startup And Preflight", context_hygiene)
            self.assertIn("Do not trigger a full `/graphify` rebuild", context_hygiene)
            self.assertIn("lean-out guides", context_hygiene)
            self.assertIn("Stop Low-Yield Loops", context_hygiene)
            self.assertIn("Do Not Expand Scope By Momentum", context_hygiene)
            self.assertIn("Completion status", context_hygiene)
            self.assertIn("Handoff Summary Template", context_hygiene)
            pathway = (project / "docs" / "current-build-pathway.md").read_text(encoding="utf-8")
            self.assertIn("lean startup", pathway)
            self.assertIn("Risk-triggering work includes", pathway)
            self.assertIn("Completion target", pathway)
            self.assertIn("Budget class", pathway)
            self.assertIn("Acceptance criteria", pathway)
            self.assertIn("Stop condition", pathway)
            self.assertIn("Known gaps", pathway)

            second_manifest = change_control.build_manifest(project)
            self.assertEqual([], second_manifest["actions"])

    def test_document_control_manifest_syncs_standard_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "existing-repo"
            project.mkdir()

            manifest = change_control.build_document_control_manifest(project)
            self.assertEqual("document_control_update", manifest["manifest_kind"])
            self.assertEqual(["docs/standards/document-control-standard.md"], [action["relative_path"] for action in manifest["actions"]])

            manifest_path = project / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            change_control.apply_manifest(manifest_path)

            target = project / "docs" / "standards" / "document-control-standard.md"
            self.assertEqual(change_control.DOCUMENT_CONTROL_STANDARD.read_text(encoding="utf-8"), target.read_text(encoding="utf-8"))
            self.assertEqual([], change_control.build_document_control_manifest(project)["actions"])


if __name__ == "__main__":
    unittest.main()
