import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import scaffold_project


class ScaffoldProjectTests(unittest.TestCase):
    def test_scaffold_creates_agent_baseline_without_bash(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-agent"

            result = scaffold_project.scaffold_project(target, "agent", "3")

            self.assertEqual("3", result.governance_level)
            self.assertEqual("high", result.risk_tier)
            self.assertTrue((target / "README.md").exists())
            self.assertTrue((target / "docs" / "agent-inventory.md").exists())
            self.assertTrue((target / "docs" / "context-map.md").exists())
            self.assertTrue((target / "docs" / "domain-language.md").exists())
            self.assertTrue((target / "docs" / "standards" / "README.md").exists())
            self.assertTrue((target / "docs" / "standards" / "ship-ready-engineering-standard.md").exists())
            self.assertTrue((target / "docs" / "standards" / "context-hygiene-standard.md").exists())
            self.assertTrue((target / "scripts" / "governance-preflight.sh").exists())

            control = (target / "project-control.yaml").read_text(encoding="utf-8")
            self.assertIn("project_name: sample-agent", control)
            self.assertIn("project_type: agent", control)
            self.assertIn("primary: AI agent with tools", control)
            self.assertIn("risk_tier: high", control)
            self.assertIn("governance_level: 3", control)
            self.assertIn("docs/context-map.md", control)
            self.assertIn("agentic_coding:", control)
            self.assertIn("The repository remembers. Agents rent context.", control)
            self.assertIn("applicable: true", control)
            for relative_path in ["AGENTS.md", "AI_BOOTSTRAP.md", "CLAUDE.md"]:
                instructions = (target / relative_path).read_text(encoding="utf-8")
                self.assertIn("Fundamentals-First AI Coding", instructions)
                self.assertIn("AI speed does not make bad code cheap", instructions)
                self.assertIn("smallest safe improvement", instructions)
                self.assertIn("Context Hygiene", instructions)
                self.assertIn("docs/context-map.md", instructions)
                self.assertIn("The repository remembers", instructions)
                self.assertIn("Agents rent context", instructions)
                self.assertIn("context-hygiene-standard.md", instructions)
                self.assertIn("targeted diffs", instructions)
                self.assertIn("lean startup", instructions)
                self.assertIn("git status --short", instructions)
                self.assertIn("risk-triggering", instructions)
                self.assertIn("Draft complete", instructions)
                self.assertIn("Project completion is a human decision", instructions)
                self.assertIn("repeated attempts stop producing new evidence", instructions)
                self.assertIn("Graphify Policy", instructions)
                self.assertIn("Tools/graphify/docs/agent-governance.md", instructions)
                self.assertIn("Tools/graphify/workspace/out/graph.json", instructions)
                self.assertIn("workspace graph for cross-repo routing", instructions)
                self.assertIn("known files", instructions)
                self.assertIn("graphify-setup-project /path/to/repo", instructions)
                self.assertNotIn("/home/adamgoodwin/.local/bin/graphify-setup-project", instructions)
                self.assertIn("/graphify /path/to/repo", instructions)
                self.assertIn("full semantic repo graphs", instructions)
                self.assertIn("Do not trigger a full `/graphify` rebuild", instructions)
                self.assertIn("context clear", instructions)
                self.assertIn("rather than hard-coding a provider", instructions)
                self.assertIn("graphify update . --no-cluster", instructions)
                self.assertNotIn("graphify update . --no-cluster --force", instructions)
                self.assertIn("do not index, print, summarize, or commit secrets", instructions)
            domain_language = (target / "docs" / "domain-language.md").read_text(encoding="utf-8")
            self.assertIn("# Domain Language", domain_language)
            self.assertIn("Avoid Saying", domain_language)
            context_map = (target / "docs" / "context-map.md").read_text(encoding="utf-8")
            self.assertIn("# Context Map", context_map)
            self.assertIn("Load By Task", context_map)
            self.assertIn("budget class", context_map)
            standards_index = (target / "docs" / "standards" / "README.md").read_text(encoding="utf-8")
            self.assertIn("# Engineering Standards Index", standards_index)
            self.assertIn("Ship-Ready Engineering Standard", standards_index)
            self.assertIn("Context Hygiene Standard", standards_index)
            self.assertIn("Context Routing", standards_index)
            ship_ready = (target / "docs" / "standards" / "ship-ready-engineering-standard.md").read_text(encoding="utf-8")
            self.assertIn("# Ship-Ready Engineering Standard", ship_ready)
            self.assertIn("Completion States", ship_ready)
            self.assertIn("Draft complete", ship_ready)
            self.assertIn("Project completion is a human decision", ship_ready)
            self.assertIn("Definition Of Shipped", ship_ready)
            context_hygiene = (target / "docs" / "standards" / "context-hygiene-standard.md").read_text(encoding="utf-8")
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
            pathway = (target / "docs" / "current-build-pathway.md").read_text(encoding="utf-8")
            self.assertIn("lean startup", pathway)
            self.assertIn("Risk-triggering work includes", pathway)
            self.assertIn("Completion target", pathway)
            self.assertIn("Budget class", pathway)
            self.assertIn("Acceptance criteria", pathway)
            self.assertIn("Stop condition", pathway)
            self.assertIn("Known gaps", pathway)

    def test_scaffold_is_copy_if_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing-app"
            target.mkdir()
            (target / "README.md").write_text("# Keep me\n", encoding="utf-8")

            scaffold_project.scaffold_project(target, "application", "2")

            self.assertEqual("# Keep me\n", (target / "README.md").read_text(encoding="utf-8"))

    def test_existing_project_control_is_not_reclassified(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing-app"
            target.mkdir()
            (target / "project-control.yaml").write_text(
                "project_name: existing-app\n"
                "project_type: service\n"
                "use_case:\n"
                "  primary: Backend API / integration service\n"
                "risk_tier: medium\n"
                "governance_level: 2\n"
                "repository_model: single-repo\n",
                encoding="utf-8",
            )

            scaffold_project.scaffold_project(target, "agent", "4")

            control = (target / "project-control.yaml").read_text(encoding="utf-8")
            self.assertIn("project_type: service", control)
            self.assertIn("risk_tier: medium", control)
            self.assertIn("governance_level: 2", control)


if __name__ == "__main__":
    unittest.main()
