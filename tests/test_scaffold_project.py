import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "automation"))

import scaffold_project
import schema_validation

# Documentation projects skip these; every other type gets them.
OPERATIONAL_DOCS = ("docs/deployment-guide.md", "docs/runbook.md")


def required_docs(control_file: Path) -> list[str]:
    control = schema_validation.load_project_control(control_file)
    return schema_validation.get_path(control, "controls.required_docs")


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
            self.assertTrue(
                (target / "docs" / "standards" / "ship-ready-engineering-standard.md").exists()
            )
            self.assertTrue(
                (target / "docs" / "standards" / "context-hygiene-standard.md").exists()
            )
            self.assertTrue(
                (target / "docs" / "standards" / "code-complexity-control-standard.md").exists()
            )
            self.assertTrue(
                (target / "docs" / "standards" / "governance-source-alignment-standard.md").exists()
            )
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
            self.assertIn("cyclomatic_complexity:", control)
            self.assertIn("mode: advisory", control)
            self.assertIn("governance_alignment:", control)
            self.assertIn("review_cadence_days: 90", control)
            self.assertIn("applicable: true", control)
            self.assertEqual("@AGENTS.md\n", (target / "CLAUDE.md").read_text(encoding="utf-8"))
            bootstrap = (target / "AI_BOOTSTRAP.md").read_text(encoding="utf-8")
            self.assertIn("- Lint:", bootstrap)
            self.assertIn("- Test:", bootstrap)
            self.assertIn("- Build:", bootstrap)
            self.assertIn("AGENTS.md", bootstrap)
            self.assertNotIn("Graphify Policy", bootstrap)
            for relative_path in ["AGENTS.md"]:
                instructions = (target / relative_path).read_text(encoding="utf-8")
                self.assertLessEqual(len(instructions.splitlines()), 80)
                self.assertIn("(hook: guard-protected-paths)", instructions)
                self.assertIn("fresh session (`/clear`), not `/compact`", instructions)
                self.assertIn("Fundamentals-First AI Coding", instructions)
                self.assertIn("AI speed does not make bad code cheap", instructions)
                self.assertIn("smallest safe improvement", instructions)
                self.assertIn("review signal, not a verdict", instructions)
                self.assertIn("code-complexity-control-standard.md", instructions)
                self.assertIn("more than 90 days old", instructions)
                self.assertIn("not an ordinary-startup requirement", instructions)
                self.assertIn("governance-source-alignment-standard.md", instructions)
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
                self.assertIn("active plan named by `START_HERE.md`", instructions)
                self.assertIn("After a compaction, context clear, or fresh restart", instructions)
                self.assertIn("Graphify Policy", instructions)
                self.assertIn("docs/agent-governance.md", instructions)
                self.assertIn("graphify global path", instructions)
                self.assertIn("configured global graph for cross-repo routing", instructions)
                self.assertIn("known files", instructions)
                self.assertIn("graphify-setup-project /path/to/repo", instructions)
                self.assertNotIn(
                    "/home/adamgoodwin/.local/bin/graphify-setup-project", instructions
                )
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
            standards_index = (target / "docs" / "standards" / "README.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("# Engineering Standards Index", standards_index)
            self.assertIn("Ship-Ready Engineering Standard", standards_index)
            self.assertIn("Context Hygiene Standard", standards_index)
            self.assertIn("Code Complexity Control Standard", standards_index)
            self.assertIn("Governance Source Alignment Standard", standards_index)
            self.assertIn("Context Routing", standards_index)
            complexity = (
                target / "docs" / "standards" / "code-complexity-control-standard.md"
            ).read_text(encoding="utf-8")
            self.assertIn("smoke alarm, not a verdict", complexity)
            self.assertIn("21+", complexity)
            self.assertIn("Do not create shallow wrappers", complexity)
            alignment = (
                target / "docs" / "standards" / "governance-source-alignment-standard.md"
            ).read_text(encoding="utf-8")
            self.assertIn("at least every 90 days", alignment)
            self.assertIn("not automatic adoption", alignment)
            self.assertIn("This is not an ordinary-startup requirement", alignment)
            ship_ready = (
                target / "docs" / "standards" / "ship-ready-engineering-standard.md"
            ).read_text(encoding="utf-8")
            self.assertIn("# Ship-Ready Engineering Standard", ship_ready)
            self.assertIn("Completion States", ship_ready)
            self.assertIn("Draft complete", ship_ready)
            self.assertIn("Project completion is a human decision", ship_ready)
            self.assertIn("Definition Of Shipped", ship_ready)
            context_hygiene = (
                target / "docs" / "standards" / "context-hygiene-standard.md"
            ).read_text(encoding="utf-8")
            self.assertIn("# Context Hygiene Standard", context_hygiene)
            self.assertIn("Context Tiers And Budgets", context_hygiene)
            self.assertIn("Cache-Friendly Prompting", context_hygiene)
            self.assertIn("Token-Friendly Done", context_hygiene)
            self.assertIn("summary-only", context_hygiene)
            self.assertIn("Lean Startup And Preflight", context_hygiene)
            self.assertIn("Do not trigger a full `/graphify` rebuild", context_hygiene)
            self.assertIn("On restart after compaction or a context clear", context_hygiene)
            self.assertIn("query existing Graphify output", context_hygiene)
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
            self.assertIn("After compaction or a context clear", pathway)
            self.assertIn("### P-01 - ", pathway)
            self.assertIn("Status: Ready", pathway)
            self.assertIn("Runner:", pathway)
            self.assertIn("Files:", pathway)
            self.assertIn("Plan once", pathway)

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


class OperationalDocsTests(unittest.TestCase):
    """A scaffold must not require docs it does not create (AUD-ENG-004 B-6)."""

    def test_documentation_project_neither_gets_nor_requires_operational_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "handbook"

            scaffold_project.scaffold_project(target, "documentation", "2")

            for path in OPERATIONAL_DOCS:
                self.assertFalse((target / path).exists(), path)
            template_docs = required_docs(
                scaffold_project.TEMPLATE_ROOT / "project-control.template.yaml"
            )
            self.assertEqual(
                [path for path in template_docs if path not in OPERATIONAL_DOCS],
                required_docs(target / "project-control.yaml"),
            )

    def test_other_projects_get_and_require_operational_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-app"

            scaffold_project.scaffold_project(target, "application", "2")

            required = required_docs(target / "project-control.yaml")
            for path in OPERATIONAL_DOCS:
                self.assertTrue((target / path).exists(), path)
                self.assertIn(path, required)

    def test_existing_documentation_control_file_is_left_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "handbook"
            target.mkdir()
            existing = (
                "project_name: handbook\n"
                "project_type: documentation\n"
                "controls:\n"
                "  required_docs:\n"
                "    - README.md\n"
                "    - docs/runbook.md\n"
            )
            (target / "project-control.yaml").write_text(existing, encoding="utf-8")

            scaffold_project.scaffold_project(target, "documentation", "2")

            control = (target / "project-control.yaml").read_text(encoding="utf-8")
            self.assertEqual(existing, control)


class AgentHarnessScaffoldTests(unittest.TestCase):
    def test_agent_project_records_undecided_harness_when_topology_not_asked(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "plain-agent"

            scaffold_project.scaffold_project(target, "agent", "2")

            readme = (target / "docs" / "harness" / "README.md").read_text(encoding="utf-8")
            control = (target / "project-control.yaml").read_text(encoding="utf-8")
            self.assertIn("Profile: undecided", readme)
            self.assertIn("harness_profile: undecided", control)

    def test_agent_project_records_chosen_topology(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "router-agent"

            scaffold_project.scaffold_project(
                target,
                "agent",
                "2",
                harness_topology="combination",
                harness_description="Routes work.",
            )

            readme = (target / "docs" / "harness" / "README.md").read_text(encoding="utf-8")
            self.assertIn("Profile: multi-model", readme)
            self.assertIn("> Routes work.", readme)

    def test_unknown_topology_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                scaffold_project.scaffold_project(
                    Path(tmp) / "bad", "agent", "2", harness_topology="swarm"
                )

    def test_non_agent_projects_get_no_harness_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "plain-app"

            scaffold_project.scaffold_project(target, "application", "2")

            self.assertFalse((target / "docs" / "harness").exists())


class BuildPlaybookTests(unittest.TestCase):
    def test_every_project_type_has_a_playbook_template(self):
        for project_type in sorted(scaffold_project.GOV_TYPES):
            name = scaffold_project.PLAYBOOK_BY_TYPE[project_type]
            template = scaffold_project.TEMPLATE_ROOT / "docs" / "playbooks" / f"{name}.template.md"
            self.assertTrue(template.exists(), project_type)

    def test_scaffold_delivers_the_matching_playbook(self):
        cases = {
            "website": "Website",
            "infrastructure": "Infrastructure",
            "agent": "AI Agent (Harness)",
            "agentic-harness": "AI Agent (Harness)",
        }
        for project_type, title in cases.items():
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / f"p-{project_type}"

                scaffold_project.scaffold_project(target, project_type, "2")

                playbook = (target / "docs" / "build-playbook.md").read_text(encoding="utf-8")
                self.assertEqual(f"# Build Playbook: {title}", playbook.splitlines()[0])

    def test_agents_file_routes_to_the_playbook(self):
        agents = (scaffold_project.TEMPLATE_ROOT / "AGENTS.template.md").read_text(encoding="utf-8")
        self.assertIn("`docs/build-playbook.md`", agents)


if __name__ == "__main__":
    unittest.main()
