#!/usr/bin/env python3
"""
New Build Governance Agent — GUI
Pop!_OS build machine project launcher.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import traceback
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

# paths
GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
REGISTRY = GOVERNANCE_HOME / "automation" / "project_registry.py"
CHANGE_CONTROL = GOVERNANCE_HOME / "automation" / "change_control.py"
PROMOTION_PLAN = GOVERNANCE_HOME / "automation" / "promotion_plan.py"
PROMOTION_CHECKS = GOVERNANCE_HOME / "automation" / "promotion_checks.py"
PROMOTION_REMEDIATE = GOVERNANCE_HOME / "automation" / "promotion_remediate.py"
PROMOTION_EXECUTE = GOVERNANCE_HOME / "automation" / "promotion_execute.py"
GOVERNANCE_AUDIT = GOVERNANCE_HOME / "automation" / "governance_audit.py"
LOG_PATH = GOVERNANCE_HOME / "data" / "new-build-governance-agent" / "logs" / "gui-startup.log"

sys.path.insert(0, str(GOVERNANCE_HOME / "automation"))
from project_naming import (  # noqa: E402
    GOVERNANCE_TO_RISK,
    render_initial_scope,
    slug_error,
    slugify,
)
from scaffold_project import scaffold_project  # noqa: E402
from self_update import (
    STATUS_UP_TO_DATE,
    STATUS_WOULD_UPDATE,
    self_update,
)  # noqa: E402
from self_update import (
    format_result as format_self_update_result,
)
from update_check import check_for_updates  # noqa: E402
from update_check import format_result as format_update_check_result
from version import get_version  # noqa: E402
from workspace_paths import default_code_root, ensure_category_roots  # noqa: E402

CODE_ROOT = default_code_root(GOVERNANCE_HOME)
AGENTS_ROOT, APPS_ROOT = ensure_category_roots(GOVERNANCE_HOME)

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except Exception:  # pragma: no cover - startup fallback
    tk = None  # type: ignore[assignment]
    filedialog = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]
    ttk = None  # type: ignore[assignment]

if TYPE_CHECKING:
    TkBase = tk.Tk
else:
    TkBase = tk.Tk if tk is not None else object

# theme
BG = "#f4f1e8"
SURFACE = "#fffaf0"
SURFACE_ALT = "#e7eadf"
BORDER = "#c9c3b2"
FG = "#25251f"
FG_DIM = "#6d6659"
ACCENT = "#5f7f68"
ACCENT_DARK = "#4d6955"
CTA_FG = "#fbfaf4"
ENTRY_BG = "#ffffff"
SUCCESS = "#3f7d4f"
ERROR = "#a6534d"
INFO = "#536f8a"

FONT_SCALE = 2


def ui_font(size: int, *style: str, family: str = "Sans") -> tuple:
    return (family, size * FONT_SCALE, *style)


FONT = ui_font(10)
SMALL = ui_font(9)
TITLE = ui_font(18, "bold")
MONO = ui_font(9, family="Monospace")
LABEL_BOLD = ui_font(10, "bold")
BUTTON_FONT = ui_font(10, "bold")
SMALL_BOLD = ui_font(9, "bold")
CARD_TITLE = ui_font(12, "bold")
FLOW_SEPARATOR = ui_font(13, "bold")
BUSY_TITLE = ui_font(18, "bold")
BUSY_LABEL = ui_font(12, "bold")
ACTIVITY_LOG_EXPANDED_HEIGHT = 6
ACTIVITY_LOG_COLLAPSED_BY_DEFAULT = True
PAD = 16

TYPE_MAP = {
    "app": ("application", APPS_ROOT),
    "website": ("website", APPS_ROOT),
    "agent": ("agent", AGENTS_ROOT),
    "harness": ("agentic-harness", AGENTS_ROOT),
    "tool": ("internal-tool", APPS_ROOT),
    "automation": ("automation", APPS_ROOT),
    "other": ("automation", APPS_ROOT),
}

PURPOSE_OPTIONS = [
    (
        "website",
        "A website",
        "Pages for people to read, browse, contact you, or learn about something.",
    ),
    (
        "app",
        "An app or portal",
        "People log in, manage information, or complete a workflow.",
    ),
    (
        "automation",
        "An automation",
        "A process runs for you, connects tools, sends updates, or handles repeat work.",
    ),
    (
        "agent",
        "An AI helper",
        "An assistant that can answer, draft, inspect files, or use tools.",
    ),
    (
        "harness",
        "An agentic harness",
        "A product that uses AI — single agent, multi-agent, non-LLM, or a combination. Adds governance guidance for your AI topology.",
    ),
    (
        "tool",
        "A small internal tool",
        "A focused utility for you or your team.",
    ),
    (
        "other",
        "I am not sure yet",
        "Start with safe defaults and decide the technical shape later.",
    ),
]

HARNESS_TOPOLOGY_OPTIONS = [
    (
        "single-llm",
        "Single LLM",
        "One language model handles the complete task.",
    ),
    (
        "multi-llm",
        "Multi-LLM",
        "Multiple language models with defined roles work in sequence or parallel.",
    ),
    (
        "non-llm",
        "Non-LLM AI",
        "Machine learning without a language model.\ne.g. DiNO, JEPA, Phi-4 (inference-only), YOLO, Whisper, custom classifiers.",
    ),
    (
        "combination",
        "Combination",
        "Both language models and other ML models (vision, audio, forecasting) participate together.",
    ),
]

AUDIENCE_OPTIONS = [
    ("just_me", "Just me", "A personal or local project."),
    ("team", "My team", "People inside your organization will use it."),
    ("client", "A client", "A project delivered to a specific client or stakeholder."),
    ("customers", "Customers or the public", "People outside your organization will rely on it."),
]

GOVERNANCE_OPTIONS = [
    "0 - Full autonomy",
    "1 - Light guardrails",
    "2 - Standard supervised",
    "3 - Strict review",
    "4 - Critical controls",
]


def governance_level_from_label(value: str) -> str:
    level = value.strip()[:1]
    return level if level in GOVERNANCE_TO_RISK else "2"


def log_startup_error(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip() + "\n")


def build_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    preferred: list[str] = []
    if os.name != "nt":
        preferred = [
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
        ]
    existing = [item for item in env.get("PATH", "").split(os.pathsep) if item]
    merged: list[str] = []
    for item in preferred + existing:
        if item not in merged:
            merged.append(item)
    env["PATH"] = os.pathsep.join(merged)
    env.setdefault("GOVERNANCE_HOME", str(GOVERNANCE_HOME))
    return env


def project_name_error(name: str) -> str | None:
    """Return the canonical rejection reason for a project name, or None."""
    return slug_error(name, slugify(name))


def write_initial_scope(target: Path, d: dict) -> None:
    text = render_initial_scope(
        project_name=d["name"],
        slug=d["slug"],
        governance_type=d["gov_type"],
        governance_level=d["governance_level"],
        risk_tier=d["risk_tier"],
        stack=d["stack"],
        primary_builder=d["builder"],
        target_dir=d["target_dir"],
        scope_problem=d.get("problem", ""),
        scope_user=d.get("user_desc", ""),
        scope_mvp=d.get("mvp", ""),
    )
    (target / "INITIAL_SCOPE.md").write_text(text, encoding="utf-8")


def build_update_affordance_summary(update_status: str, dry_run_status: str) -> tuple[str, bool]:
    allow_update = dry_run_status == STATUS_WOULD_UPDATE
    lines = [
        f"Version status: {update_status}",
        f"Git status: {dry_run_status}",
    ]
    if allow_update:
        lines.append("Safe fast-forward update is available.")
    elif dry_run_status == STATUS_UP_TO_DATE:
        lines.append("Checkout is already up to date.")
    else:
        lines.append("Update action is blocked by repo state.")
    return "\n".join(lines), allow_update


def read_project_metadata(project_path: Path) -> dict[str, str]:
    metadata = {
        "project_name": project_path.name,
        "project_type": "unknown",
        "risk_tier": "unknown",
        "builder": "unknown",
        "stack": "not specified",
    }
    control = project_path / "project-control.yaml"
    if not control.exists():
        return metadata
    for line in control.read_text(encoding="utf-8").splitlines():
        if line.startswith("project_name:"):
            metadata["project_name"] = line.split(":", 1)[1].strip() or project_path.name
        elif line.startswith("project_type:"):
            metadata["project_type"] = line.split(":", 1)[1].strip() or "unknown"
        elif line.startswith("risk_tier:"):
            metadata["risk_tier"] = line.split(":", 1)[1].strip() or "unknown"
    return metadata


class App(TkBase):
    def __init__(self):
        super().__init__()
        self.title("New Build Governance Agent")
        self.configure(bg=BG)
        self.geometry("1500x920")
        self.minsize(1180, 820)
        self.resizable(True, True)

        self.v_name = tk.StringVar()
        self.v_type = tk.StringVar(value="app")
        self.v_stack = tk.StringVar()
        self.v_builder = tk.StringVar(value="claude")
        self.v_risk = tk.StringVar(value=GOVERNANCE_OPTIONS[2])
        self.v_scope = tk.BooleanVar(value=True)
        self.v_problem = tk.StringVar()
        self.v_user = tk.StringVar()
        self.v_mvp = tk.StringVar()
        self.v_intake_step = tk.IntVar(value=0)
        self.v_plain_purpose = tk.StringVar(value="app")
        self.v_harness_topology = tk.StringVar(value="single-llm")
        self.v_audience = tk.StringVar(value="team")
        self.v_has_private_data = tk.BooleanVar(value=False)
        self.v_has_accounts = tk.BooleanVar(value=False)
        self.v_handles_money = tk.BooleanVar(value=False)
        self.v_external_actions = tk.BooleanVar(value=False)
        self.v_production_ops = tk.BooleanVar(value=False)
        self.v_advanced_settings = tk.BooleanVar(value=False)
        self.v_intake_summary = tk.StringVar()
        self.v_step_label = tk.StringVar()

        self.v_change_project = tk.StringVar()
        self.v_manifest = tk.StringVar()
        self.v_promotion_plan = tk.StringVar()
        self.v_commit_message = tk.StringVar()
        self.v_execution_report = tk.StringVar()
        self.v_known_project = tk.StringVar()
        self.v_doc_known_project = tk.StringVar()
        self.v_doc_project = tk.StringVar()
        self.v_doc_manifest = tk.StringVar()
        self.v_doc_summary = tk.StringVar(
            value="Choose an existing repo, then preview the document-control update."
        )
        self.v_known_count = tk.StringVar(value="Known governed projects: scanning...")
        self.v_change_summary = tk.StringVar()
        self.v_workflow_hint = tk.StringVar(
            value="Choose a project to begin the governance pathway."
        )
        self.v_update_summary = tk.StringVar(
            value="Check for agent updates before starting a release workflow."
        )
        self.v_activity_summary = tk.StringVar(value="Ready.")
        self.known_projects: dict[str, dict] = {}
        self._pending_known_project_path: str | None = None
        self._busy_job: str | None = None
        self._busy_step = 0
        self._staged_file_vars: list[tuple[str, tk.BooleanVar]] = []
        self._intake_refreshing = False
        self._self_update_allowed = False
        self._activity_log_expanded = not ACTIVITY_LOG_COLLAPSED_BY_DEFAULT

        self.v_name.trace_add("write", lambda *_: self._refresh_preview())
        self.v_type.trace_add("write", lambda *_: self._refresh_preview())
        for var in [
            self.v_plain_purpose,
            self.v_harness_topology,
            self.v_audience,
            self.v_has_private_data,
            self.v_has_accounts,
            self.v_handles_money,
            self.v_external_actions,
            self.v_production_ops,
            self.v_advanced_settings,
            self.v_stack,
            self.v_builder,
            self.v_risk,
        ]:
            var.trace_add("write", lambda *_: self._refresh_intake_summary())

        self._setup_style()
        self._build_ui()
        self._refresh_preview()
        self._show_intake_step(0)
        self._refresh_intake_summary()
        self._refresh_change_project()
        self._update_workflow_hint()
        self.after_idle(self._size_window_for_screen)
        self.after(40, self._load_known_projects_async)

    def _load_known_projects_async(self):
        threading.Thread(target=self._load_known_projects, daemon=True).start()

    def _refresh_window_anchor(self):
        try:
            self.update_idletasks()
            self.geometry(self.geometry())
        except tk.TclError:
            pass

    def _size_window_for_screen(self):
        try:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            width = min(max(1400, int(screen_width * 0.82)), max(1180, screen_width - 80))
            height = min(max(900, int(screen_height * 0.86)), max(820, screen_height - 80))
            x = max(0, (screen_width - width) // 2)
            y = max(0, (screen_height - height) // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except tk.TclError:
            pass

    def _setup_style(self):
        self.option_add("*Font", FONT)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=SURFACE,
            foreground=FG_DIM,
            font=BUTTON_FONT,
            padding=(18, 11),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ENTRY_BG)],
            foreground=[("selected", FG)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=ENTRY_BG,
            background=SURFACE,
            foreground=FG,
            selectbackground=SURFACE,
            selectforeground=FG,
            bordercolor=BORDER,
            arrowcolor=FG_DIM,
            insertcolor=FG,
            lightcolor=BORDER,
            darkcolor=BORDER,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", ENTRY_BG)],
            foreground=[("readonly", FG)],
        )

    def _build_ui(self):
        header = tk.Frame(self, bg=BG, padx=PAD, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="New Build Governance Agent", bg=BG, fg=FG, font=TITLE).pack(
            anchor="w"
        )
        tk.Label(header, text=f"Version {get_version()}", bg=BG, fg=INFO, font=LABEL_BOLD).pack(
            anchor="w", pady=(2, 0)
        )
        tk.Label(
            header,
            text="A guided workspace for starting projects, preparing releases, and keeping engineering standards and agent guidance aligned.",
            bg=BG,
            fg=FG_DIM,
            font=SMALL,
        ).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        notebook = ttk.Notebook(body)
        notebook.pack(fill="both", expand=True)

        self.create_tab = tk.Frame(notebook, bg=BG)
        self.change_tab = tk.Frame(notebook, bg=BG)
        self.doc_control_tab = tk.Frame(notebook, bg=BG)
        notebook.add(self.create_tab, text="New Build")
        notebook.add(self.change_tab, text="Governance & Release")
        notebook.add(self.doc_control_tab, text="Document Control")

        self._build_create_tab()
        self._build_change_tab()
        self._build_doc_control_tab()
        self._build_output(body)
        self._build_busy_overlay(body)

    def _card(self, parent, title: str, subtitle: str | None = None) -> tk.Frame:
        frame = tk.Frame(
            parent,
            bg=SURFACE,
            highlightthickness=1,
            highlightbackground=BORDER,
            bd=0,
            padx=14,
            pady=12,
        )
        frame.pack(fill="x", pady=(0, 12))
        tk.Label(frame, text=title, bg=SURFACE, fg=FG, font=CARD_TITLE).pack(anchor="w")
        if subtitle:
            tk.Label(
                frame,
                text=subtitle,
                bg=SURFACE,
                fg=FG_DIM,
                font=SMALL,
                wraplength=760,
                justify="left",
            ).pack(anchor="w", pady=(4, 10))
        return frame

    def _scrollable_frame(self, parent) -> tk.Frame:
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=BG, padx=2, pady=2)
        window_id = canvas.create_window((0, 0), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda *_: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window_id, width=event.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        def bind_scroll(_event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            canvas.bind_all("<Button-4>", on_scroll_up)
            canvas.bind_all("<Button-5>", on_scroll_down)

        def unbind_scroll(_event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_scroll_up(_event):
            canvas.yview_scroll(-3, "units")

        def on_scroll_down(_event):
            canvas.yview_scroll(3, "units")

        canvas.bind("<Enter>", bind_scroll)
        canvas.bind("<Leave>", unbind_scroll)
        frame.bind("<Enter>", bind_scroll)
        frame.bind("<Leave>", unbind_scroll)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return frame

    def _build_create_tab(self):
        wrap = self._scrollable_frame(self.create_tab)

        intro_card = self._card(
            wrap,
            "Start A New Build",
            "Answer one small question at a time. Technical settings are inferred and shown before anything is created.",
        )
        self._step_header = tk.Label(
            intro_card,
            textvariable=self.v_step_label,
            bg=SURFACE,
            fg=INFO,
            font=LABEL_BOLD,
            anchor="w",
            justify="left",
        )
        self._step_header.pack(fill="x")

        self._intake_host = tk.Frame(wrap, bg=BG)
        self._intake_host.pack(fill="both", expand=True)
        self._intake_steps: list[tk.Frame] = []

        self._build_intake_purpose_step()
        self._build_intake_harness_step()
        self._build_intake_audience_step()
        self._build_intake_first_result_step()
        self._build_intake_risk_step()
        self._build_intake_review_step()
        self._HARNESS_STEP_INDEX = 1

        action_row = tk.Frame(wrap, bg=BG)
        action_row.pack(fill="x", pady=(4, 4))
        self._back_btn = tk.Button(
            action_row,
            text="Back",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._previous_intake_step,
        )
        self._back_btn.pack(side="left")
        self._next_btn = tk.Button(
            action_row,
            text="Continue",
            bg=ACCENT,
            fg=CTA_FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=22,
            pady=10,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground=CTA_FG,
            command=self._next_intake_step,
        )
        self._next_btn.pack(side="left", padx=(10, 0))
        self._create_btn = tk.Button(
            action_row,
            text="Create New Build",
            bg=ACCENT,
            fg=CTA_FG,
            font=ui_font(11, "bold"),
            relief="flat",
            bd=0,
            padx=26,
            pady=10,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground=CTA_FG,
            command=self._on_create,
        )
        self._create_btn.pack(side="left", padx=(10, 0))

    def _new_intake_step(self, title: str, subtitle: str) -> tk.Frame:
        frame = tk.Frame(self._intake_host, bg=BG)
        self._intake_steps.append(frame)
        card = self._card(frame, title, subtitle)
        card.pack_configure(pady=(0, 12))
        frame._content_card = card  # type: ignore[attr-defined]
        return card

    def _build_intake_purpose_step(self):
        card = self._new_intake_step(
            "What are you trying to make?",
            "Choose the closest fit. You can change the technical classification on the review step.",
        )
        grid = tk.Frame(card, bg=SURFACE)
        grid.pack(fill="x")
        for index, (value, title, description) in enumerate(PURPOSE_OPTIONS):
            button = tk.Radiobutton(
                grid,
                text=f"{title}\n{description}",
                variable=self.v_plain_purpose,
                value=value,
                bg=ENTRY_BG,
                fg=FG,
                selectcolor=SURFACE_ALT,
                activebackground=SURFACE_ALT,
                activeforeground=FG,
                font=FONT,
                justify="left",
                anchor="w",
                indicatoron=True,
                padx=12,
                pady=10,
                command=self._refresh_intake_summary,
                wraplength=350,
            )
            row = index // 2
            column = index % 2
            button.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 8, 0),
                pady=(0, 8),
            )
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def _build_intake_harness_step(self):
        card = self._new_intake_step(
            "What kind of AI will this use?",
            "Choose the closest topology. This sets the governance profile for your harness.",
        )
        for value, title, description in HARNESS_TOPOLOGY_OPTIONS:
            tk.Radiobutton(
                card,
                text=f"{title}\n{description}",
                variable=self.v_harness_topology,
                value=value,
                bg=ENTRY_BG,
                fg=FG,
                selectcolor=SURFACE_ALT,
                activebackground=SURFACE_ALT,
                activeforeground=FG,
                font=FONT,
                justify="left",
                anchor="w",
                indicatoron=True,
                padx=12,
                pady=10,
                command=self._refresh_intake_summary,
                wraplength=700,
            ).pack(fill="x", pady=4)

        tk.Frame(card, bg=SURFACE, height=10).pack()
        tk.Label(
            card,
            text="Describe what your harness will do and the intended outcome:",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL_BOLD,
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(0, 4))
        self._harness_desc_text = tk.Text(
            card,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            height=5,
            wrap="word",
        )
        self._harness_desc_text.pack(fill="x")
        tk.Label(
            card,
            text="Your description is written into docs/harness/README.md so the development agent can read it and suggest governance rules.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=700,
        ).pack(fill="x", pady=(6, 0))

    def _build_intake_audience_step(self):
        card = self._new_intake_step(
            "Who is this for?",
            "This helps set the level of review and documentation without asking you to know governance terminology.",
        )
        for value, title, description in AUDIENCE_OPTIONS:
            tk.Radiobutton(
                card,
                text=f"{title} — {description}",
                variable=self.v_audience,
                value=value,
                bg=SURFACE,
                fg=FG,
                selectcolor=SURFACE_ALT,
                activebackground=SURFACE,
                activeforeground=FG,
                font=FONT,
                justify="left",
                anchor="w",
                command=self._refresh_intake_summary,
                wraplength=760,
            ).pack(fill="x", pady=4)

    def _build_intake_first_result_step(self):
        card = self._new_intake_step(
            "What should exist first?",
            "Keep this small. The first build should be useful, reviewable, and easy to continue from.",
        )
        self._row(card, "Project name", lambda p: self._entry(p, self.v_name))
        self._row(card, "First useful result", lambda p: self._entry(p, self.v_mvp))
        self._row(card, "Problem it solves", lambda p: self._entry(p, self.v_problem))
        self._row(card, "Main user", lambda p: self._entry(p, self.v_user))
        target_row = tk.Frame(card, bg=SURFACE)
        target_row.pack(fill="x", pady=(8, 0))
        tk.Label(
            target_row,
            text="Where it will go",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            width=14,
            anchor="w",
        ).pack(side="left")
        self._lbl_preview = tk.Label(
            target_row, text="", bg=SURFACE, fg=INFO, font=MONO, anchor="w", justify="left"
        )
        self._lbl_preview.pack(side="left", fill="x", expand=True)

    def _build_intake_risk_step(self):
        card = self._new_intake_step(
            "Will it touch anything sensitive?",
            "These simple checks help the agent choose safer defaults before any code is written.",
        )
        for label, variable in [
            ("Private or customer data", self.v_has_private_data),
            ("Accounts, login, or permissions", self.v_has_accounts),
            ("Payments, billing, or money handling", self.v_handles_money),
            (
                "External actions like sending, posting, deleting, deploying, or changing records",
                self.v_external_actions,
            ),
            (
                "Production infrastructure, secrets, databases, or release automation",
                self.v_production_ops,
            ),
        ]:
            tk.Checkbutton(
                card,
                text=label,
                variable=variable,
                bg=SURFACE,
                fg=FG,
                selectcolor=SURFACE_ALT,
                activebackground=SURFACE,
                activeforeground=FG,
                font=FONT,
                justify="left",
                anchor="w",
                command=self._refresh_intake_summary,
                wraplength=760,
            ).pack(fill="x", pady=4)

    def _build_intake_review_step(self):
        card = self._new_intake_step(
            "Review before creating",
            "Nothing is created until you confirm this summary.",
        )
        tk.Label(
            card,
            textvariable=self.v_intake_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(0, 12))

        tk.Checkbutton(
            card,
            text="Show advanced settings",
            variable=self.v_advanced_settings,
            bg=SURFACE,
            fg=FG,
            selectcolor=SURFACE_ALT,
            activebackground=SURFACE,
            activeforeground=FG,
            font=SMALL,
            command=self._toggle_advanced_settings,
        ).pack(anchor="w")

        self._advanced_frame = tk.Frame(card, bg=SURFACE)
        self._row(
            self._advanced_frame,
            "Build type",
            lambda p: self._combo(
                p, self.v_type, ["website", "app", "agent", "tool", "automation", "other"]
            ),
        )
        self._row(self._advanced_frame, "Likely stack", lambda p: self._entry(p, self.v_stack))
        self._row(
            self._advanced_frame,
            "Builder",
            lambda p: self._combo(p, self.v_builder, ["claude", "codex", "local", "hybrid"]),
        )
        self._row(
            self._advanced_frame,
            "Review level",
            lambda p: self._combo(p, self.v_risk, GOVERNANCE_OPTIONS),
        )

    def _build_change_tab(self):
        wrap = self._scrollable_frame(self.change_tab)

        flow_card = self._card(
            wrap,
            "Release Pathway",
            "Move one step at a time: select, preview, apply, plan, check, publish.",
        )
        flow_row = tk.Frame(flow_card, bg=SURFACE)
        flow_row.pack(fill="x")
        for index, label in enumerate(
            [
                "Select Project",
                "Preview Compliance",
                "Bring To Compliance",
                "Generate Plan",
                "Run Checks",
                "Execute GitHub",
            ]
        ):
            chip = tk.Label(
                flow_row,
                text=f"{index + 1}. {label}",
                bg=SURFACE_ALT if index % 2 == 0 else ENTRY_BG,
                fg=FG,
                font=SMALL_BOLD,
                padx=12,
                pady=8,
            )
            chip.pack(side="left")
            if index < 5:
                tk.Label(
                    flow_row,
                    text="/",
                    bg=SURFACE,
                    fg=ACCENT,
                    font=FLOW_SEPARATOR,
                    padx=8,
                ).pack(side="left")

        layout = tk.Frame(wrap, bg=BG)
        layout.pack(fill="both", expand=True)

        rail = tk.Frame(layout, bg=BG, width=250)
        rail.pack(side="left", fill="y")
        rail.pack_propagate(False)

        main = tk.Frame(layout, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=(12, 0))

        next_card = self._card(
            rail,
            "Next Move",
            "The next comfortable step for the selected project.",
        )
        tk.Label(
            next_card,
            textvariable=self.v_workflow_hint,
            bg=SURFACE,
            fg=INFO,
            font=LABEL_BOLD,
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x")

        rail_card = self._card(
            rail,
            "Pathway",
            "Use these in order.",
        )
        tk.Label(
            rail_card,
            text=(
                "1. Pick the target project\n\n"
                "2. Generate the compliance preview\n\n"
                "3. Apply reviewed local changes\n\n"
                "4. Generate the external plan\n\n"
                "5. Run validation checks\n\n"
                "6. Publish only after approval"
            ),
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x")

        helper = self._card(
            rail,
            "Guardrails",
            "This path keeps changes reviewable.",
        )
        tk.Label(
            helper,
            text=(
                "Creates missing governance files and appends marked instruction blocks only.\n\n"
                "Does not rename folders, delete files, or rewire dependencies."
            ),
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x")

        update_card = self._card(
            rail,
            "Agent Updates",
            "Check this tool before continuing.",
        )
        tk.Label(
            update_card,
            textvariable=self.v_update_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x", pady=(0, 10))
        update_controls = tk.Frame(update_card, bg=SURFACE)
        update_controls.pack(fill="x")
        self._update_check_btn = tk.Button(
            update_controls,
            text="Check",
            bg=SURFACE_ALT,
            fg=FG,
            font=SMALL_BOLD,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_check_agent_updates,
        )
        self._update_check_btn.pack(side="left")
        self._self_update_btn = tk.Button(
            update_controls,
            text="Update",
            bg=SURFACE_ALT,
            fg=FG_DIM,
            font=SMALL_BOLD,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            state="disabled",
            command=self._on_self_update_agent,
        )
        self._self_update_btn.pack(side="left", padx=(8, 0))

        project_card = self._card(
            main,
            "1. Choose The Repo",
            "Pick a known project or browse to a local folder.",
        )

        selector_row = tk.Frame(project_card, bg=SURFACE)
        selector_row.pack(fill="x", pady=(0, 8))
        tk.Label(
            selector_row,
            text="Known project",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            width=14,
            anchor="w",
        ).pack(side="left")
        self._known_project_combo = ttk.Combobox(
            selector_row,
            textvariable=self.v_known_project,
            values=[],
            state="readonly",
            font=FONT,
        )
        self._configure_combobox_anchor(self._known_project_combo)
        self._known_project_combo.pack(side="left", fill="x", expand=True)
        self._known_project_combo.bind(
            "<<ComboboxSelected>>", lambda *_: self._on_known_project_selected()
        )
        tk.Button(
            selector_row,
            text="Refresh",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._load_known_projects_async,
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            project_card,
            textvariable=self.v_known_count,
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self._row(project_card, "Project path", self._change_project_entry)

        summary = tk.Label(
            project_card,
            textvariable=self.v_change_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        )
        summary.pack(fill="x", pady=(2, 10))

        preview_card = self._card(
            main,
            "2. Preview Local Updates",
            "The preview shows every governance file or instruction block before apply.",
        )

        manifest_controls = tk.Frame(preview_card, bg=SURFACE)
        manifest_controls.pack(fill="x", pady=(0, 10))
        self._generate_btn = tk.Button(
            manifest_controls,
            text="Preview Compliance",
            bg=ACCENT,
            fg=CTA_FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground=CTA_FG,
            command=self._on_generate_manifest,
        )
        self._generate_btn.pack(side="left")
        tk.Label(
            manifest_controls,
            text="Review the generated manifest before applying it.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))

        manifest_row = tk.Frame(preview_card, bg=SURFACE)
        manifest_row.pack(fill="x", pady=4)
        tk.Label(
            manifest_row,
            text="Manifest file",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            width=14,
            anchor="w",
        ).pack(side="left")
        self._manifest_entry = tk.Entry(
            manifest_row,
            textvariable=self.v_manifest,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._manifest_entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            manifest_row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_manifest,
        ).pack(side="left", padx=(8, 0))

        audit_card = self._card(
            main,
            "2b. Run Governance Audit",
            "Generate an AUD-class audit report with actionable checkboxes.",
        )

        audit_controls = tk.Frame(audit_card, bg=SURFACE)
        audit_controls.pack(fill="x", pady=(0, 10))
        self._audit_btn = tk.Button(
            audit_controls,
            text="Run Governance Audit",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_run_governance_audit,
        )
        self._audit_btn.pack(side="left")
        tk.Label(
            audit_controls,
            text="Writes to docs/audits/ and opens in VS Code.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))

        apply_card = self._card(
            main,
            "3. Apply Reviewed Updates",
            "Apply only the reviewed missing files and marked instruction blocks.",
        )

        controls = tk.Frame(apply_card, bg=SURFACE)
        controls.pack(fill="x", pady=(0, 4))
        self._apply_btn = tk.Button(
            controls,
            text="Bring To Compliance",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_apply_manifest,
        )
        self._apply_btn.pack(side="left")

        tk.Label(
            apply_card,
            text=(
                "This preserves existing files. Instruction updates are appended inside marked governance blocks."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(10, 0))

        promotion_card = self._card(
            main,
            "4. Plan And Check Release",
            "Generate the release plan and run the checks it lists.",
        )

        promotion_summary = tk.Label(
            promotion_card,
            text=(
                "Planning inspects project signals and writes a reviewable path for checks, external sync prep, approval, post-checks, and rollback readiness."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        )
        promotion_summary.pack(fill="x", pady=(0, 10))

        plan_row = tk.Frame(promotion_card, bg=SURFACE)
        plan_row.pack(fill="x", pady=4)
        tk.Label(
            plan_row, text="Plan file", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w"
        ).pack(side="left")
        self._promotion_entry = tk.Entry(
            plan_row,
            textvariable=self.v_promotion_plan,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._promotion_entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            plan_row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_promotion_plan,
        ).pack(side="left", padx=(8, 0))

        promotion_controls = tk.Frame(promotion_card, bg=SURFACE)
        promotion_controls.pack(fill="x", pady=(10, 0))
        self._promotion_btn = tk.Button(
            promotion_controls,
            text="Generate External Plan",
            bg=ACCENT,
            fg=CTA_FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground=CTA_FG,
            command=self._on_generate_promotion_plan,
        )
        self._promotion_btn.pack(side="left")

        self._precheck_btn = tk.Button(
            promotion_controls,
            text="Run Pre-Checks",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_run_prechecks,
        )
        self._precheck_btn.pack(side="left", padx=(10, 0))

        self._postcheck_btn = tk.Button(
            promotion_controls,
            text="Run Post-Checks",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_run_postchecks,
        )
        self._postcheck_btn.pack(side="left", padx=(10, 0))

        self._remediate_btn = tk.Button(
            promotion_controls,
            text="Fix Missing Test Tools",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_fix_missing_test_tools,
        )
        self._remediate_btn.pack(side="left", padx=(10, 0))

        staged_card = self._card(
            main,
            "4b. Review Changed Files",
            "Select which changed files to include in the commit. At least one file must be checked before GitHub publish is enabled.",
        )
        staged_controls = tk.Frame(staged_card, bg=SURFACE)
        staged_controls.pack(fill="x", pady=(0, 8))
        tk.Button(
            staged_controls,
            text="Refresh",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_refresh_staged_files,
        ).pack(side="left")
        tk.Label(
            staged_controls,
            text="Run after generating the release plan to see current changes.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))
        self._staged_files_inner = tk.Frame(staged_card, bg=SURFACE)
        self._staged_files_inner.pack(fill="x")
        tk.Label(
            self._staged_files_inner,
            text="No changes loaded — click Refresh to inspect git status.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(anchor="w")

        execute_card = self._card(
            main,
            "5. Publish To GitHub",
            "This mirrors the local git workflow: stage changes, create a commit, push the current branch, and record rollback instructions before any live issue needs a response.",
        )

        self._row(execute_card, "Commit message", lambda p: self._entry(p, self.v_commit_message))

        execute_controls = tk.Frame(execute_card, bg=SURFACE)
        execute_controls.pack(fill="x", pady=(6, 8))
        self._execute_btn = tk.Button(
            execute_controls,
            text="Execute GitHub Publish",
            bg=ACCENT,
            fg=CTA_FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground=CTA_FG,
            command=self._on_execute_github,
            state="disabled",
        )
        self._execute_btn.pack(side="left")
        tk.Label(
            execute_controls,
            text="Use only after compliance and checks look acceptable.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))

        report_row = tk.Frame(execute_card, bg=SURFACE)
        report_row.pack(fill="x", pady=4)
        tk.Label(
            report_row,
            text="Execute report",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            width=14,
            anchor="w",
        ).pack(side="left")
        self._execute_entry = tk.Entry(
            report_row,
            textvariable=self.v_execution_report,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._execute_entry.pack(side="left", fill="x", expand=True)

        tk.Label(
            execute_card,
            text=(
                "Rollback safety: the execution report records the pre-push commit, the new commit, "
                "the published branch, and the revert commands to run if production must be backed out."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(10, 0))

        final_card = self._card(
            main,
            "6. Safety Notes",
            "The compliance path stays intentionally conservative.",
        )
        tk.Label(
            final_card,
            text=(
                "What it does now:\n"
                "- creates missing governance docs from trusted templates\n"
                "- appends marked instruction guidance when needed\n"
                "- previews every local change in a manifest before apply\n\n"
                "What it does not do:\n"
                "- rename or move project folders\n"
                "- delete files\n"
                "- rewrite dependency wiring or remap connections\n\n"
                "If we later add dependency-changing upgrades, they should ship as a separate preview-first workflow with stronger checks."
            ),
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(anchor="w")

    def _build_doc_control_tab(self):
        wrap = self._scrollable_frame(self.doc_control_tab)

        intro_card = self._card(
            wrap,
            "Document Control Update",
            "Send the portable document-control standard into an existing repo with a small reviewable manifest.",
        )
        tk.Label(
            intro_card,
            text=(
                "Use this when another repo should follow the same document shape: metadata, timestamps, audits, pathways, registers, runbooks, and ADRs."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x")

        project_card = self._card(
            wrap,
            "1. Choose The Repo",
            "Pick a known project or browse to the folder that should receive the standard.",
        )
        selector_row = tk.Frame(project_card, bg=SURFACE)
        selector_row.pack(fill="x", pady=(0, 8))
        tk.Label(
            selector_row,
            text="Known project",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            width=14,
            anchor="w",
        ).pack(side="left")
        self._doc_known_project_combo = ttk.Combobox(
            selector_row,
            textvariable=self.v_doc_known_project,
            values=[],
            state="readonly",
            font=FONT,
        )
        self._configure_combobox_anchor(self._doc_known_project_combo)
        self._doc_known_project_combo.pack(side="left", fill="x", expand=True)
        self._doc_known_project_combo.bind(
            "<<ComboboxSelected>>", lambda *_: self._on_doc_known_project_selected()
        )
        tk.Button(
            selector_row,
            text="Refresh",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._load_known_projects_async,
        ).pack(side="left", padx=(8, 0))

        self._row(project_card, "Repo path", self._doc_project_entry)

        tk.Label(
            project_card,
            textvariable=self.v_doc_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(2, 0))

        preview_card = self._card(
            wrap,
            "2. Preview The Standard Update",
            "Create a manifest showing whether the document-control standard will be added or refreshed.",
        )
        doc_controls = tk.Frame(preview_card, bg=SURFACE)
        doc_controls.pack(fill="x", pady=(0, 10))
        self._doc_preview_btn = tk.Button(
            doc_controls,
            text="Preview Document Control",
            bg=ACCENT,
            fg=CTA_FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground=CTA_FG,
            command=self._on_generate_doc_control_manifest,
        )
        self._doc_preview_btn.pack(side="left")
        tk.Label(
            doc_controls,
            text="No other files are included in this update.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))

        manifest_row = tk.Frame(preview_card, bg=SURFACE)
        manifest_row.pack(fill="x", pady=4)
        tk.Label(
            manifest_row,
            text="Manifest file",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            width=14,
            anchor="w",
        ).pack(side="left")
        self._doc_manifest_entry = tk.Entry(
            manifest_row,
            textvariable=self.v_doc_manifest,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._doc_manifest_entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            manifest_row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_doc_manifest,
        ).pack(side="left", padx=(8, 0))

        apply_card = self._card(
            wrap,
            "3. Apply Document Control",
            "After review, copy the current standard into the selected repo.",
        )
        self._doc_apply_btn = tk.Button(
            apply_card,
            text="Apply Document Control",
            bg=SURFACE_ALT,
            fg=FG,
            font=BUTTON_FONT,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_apply_doc_control_manifest,
        )
        self._doc_apply_btn.pack(anchor="w")
        tk.Label(
            apply_card,
            text="Target file: docs/standards/document-control-standard.md",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(10, 0))

    def _build_output(self, parent):
        output_card = self._card(
            parent,
            "Activity",
            "Latest workflow status. Open the log only when you need the details.",
        )
        status_row = tk.Frame(output_card, bg=SURFACE)
        status_row.pack(fill="x")
        tk.Label(
            status_row,
            textvariable=self.v_activity_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=1040,
        ).pack(side="left", fill="x", expand=True)
        self._output_toggle_btn = tk.Button(
            status_row,
            text="Show Log",
            bg=SURFACE_ALT,
            fg=FG,
            font=SMALL_BOLD,
            relief="flat",
            bd=0,
            padx=12,
            pady=7,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._toggle_output_log,
        )
        self._output_toggle_btn.pack(side="left", padx=(10, 0))
        self._output_frame = tk.Frame(output_card, bg=SURFACE)
        self._output = tk.Text(
            self._output_frame,
            bg=ENTRY_BG,
            fg=FG,
            font=MONO,
            relief="flat",
            bd=0,
            state="disabled",
            height=ACTIVITY_LOG_EXPANDED_HEIGHT,
            wrap="word",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self._output.pack(fill="both", expand=True)
        self._output.tag_configure("ok", foreground=SUCCESS)
        self._output.tag_configure("err", foreground=ERROR)
        self._output.tag_configure("dim", foreground=FG_DIM)
        self._output.tag_configure("info", foreground=INFO)
        if self._activity_log_expanded:
            self._output_frame.pack(fill="both", expand=True, pady=(10, 0))

    def _toggle_output_log(self):
        self._set_output_log_expanded(not self._activity_log_expanded)

    def _set_output_log_expanded(self, expanded: bool):
        self._activity_log_expanded = expanded
        if expanded:
            self._output_frame.pack(fill="both", expand=True, pady=(10, 0))
            self._output_toggle_btn.config(text="Hide Log")
        else:
            self._output_frame.pack_forget()
            self._output_toggle_btn.config(text="Show Log")

    def _build_busy_overlay(self, parent):
        self._busy_overlay = tk.Frame(
            parent,
            bg=ENTRY_BG,
            highlightthickness=1,
            highlightbackground=ACCENT,
            bd=0,
            padx=28,
            pady=24,
        )
        self._busy_icon = tk.Label(
            self._busy_overlay,
            text="Working",
            bg=ENTRY_BG,
            fg=ACCENT,
            font=BUSY_TITLE,
        )
        self._busy_icon.pack()
        self._busy_label = tk.Label(
            self._busy_overlay,
            text="Working...",
            bg=ENTRY_BG,
            fg=FG,
            font=BUSY_LABEL,
        )
        self._busy_label.pack(pady=(8, 2))
        tk.Label(
            self._busy_overlay,
            text="Running the selected workflow and updating the control surface.",
            bg=ENTRY_BG,
            fg=FG_DIM,
            font=SMALL,
            justify="center",
        ).pack()

    def _animate_busy(self):
        if not self._busy_overlay.winfo_ismapped():
            self._busy_job = None
            return
        frames = [
            "Working",
            "Working.",
            "Working..",
            "Working...",
        ]
        self._busy_icon.config(text=frames[self._busy_step % len(frames)])
        self._busy_step += 1
        self._busy_job = self.after(120, self._animate_busy)

    def _update_workflow_hint(self):
        project = self.v_change_project.get().strip()
        manifest = self.v_manifest.get().strip()
        plan = self.v_promotion_plan.get().strip()
        execution_report = self.v_execution_report.get().strip()

        if not project:
            text = "Choose a project first."
        elif not manifest:
            text = "Generate the compliance preview next."
        elif Path(manifest).exists() and not plan:
            text = "Review the preview, then apply it or move on to the external plan."
        elif not Path(plan).exists():
            text = "Generate the external sync plan next."
        elif not execution_report:
            text = (
                "Run the pre-checks next, then execute GitHub publish when you approve the rollout."
            )
        else:
            text = "GitHub publish has an execution report. Use post-checks and rollback notes if production validation fails."
        self.v_workflow_hint.set(text)

    def _row(self, parent, label: str, make_widget):
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill="x", pady=4)
        tk.Label(
            row, text=label, bg=parent["bg"], fg=FG_DIM, font=SMALL, width=14, anchor="w"
        ).pack(side="left")
        make_widget(row).pack(side="left", fill="x", expand=True)

    def _scope_row(self, parent, label: str, var: tk.StringVar):
        row = tk.Frame(parent, bg=SURFACE)
        tk.Label(row, text=label, bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(
            side="left"
        )
        self._entry(row, var).pack(side="left", fill="x", expand=True)
        return row

    def _entry(self, parent, var):
        return tk.Entry(
            parent,
            textvariable=var,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )

    def _combo(self, parent, var, values):
        combo = ttk.Combobox(
            parent, textvariable=var, values=values, state="readonly", font=FONT, width=24
        )
        self._configure_combobox_anchor(combo)
        return combo

    def _configure_combobox_anchor(self, combo: ttk.Combobox):
        try:

            def _anchor(w: ttk.Combobox = combo) -> None:
                self._anchor_combobox_popdown(w)

            combo.configure(postcommand=_anchor)
            combo.bind(
                "<ButtonPress-1>",
                lambda *_args, w=combo: self.after_idle(lambda: self._anchor_combobox_popdown(w)),
                add="+",
            )
        except tk.TclError:
            pass

    def _anchor_combobox_popdown(self, combo: ttk.Combobox):
        try:
            self.update_idletasks()
            combo.update_idletasks()
            popdown = self.tk.eval(f"ttk::combobox::PopdownWindow {combo}")
            x = combo.winfo_rootx()
            y = combo.winfo_rooty() + combo.winfo_height()
            self.tk.call("wm", "geometry", popdown, f"+{x}+{y}")
            self.tk.call("raise", popdown)
        except tk.TclError:
            pass

    def _change_project_entry(self, parent):
        row = tk.Frame(parent, bg=SURFACE)
        entry = tk.Entry(
            row,
            textvariable=self.v_change_project,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_project,
        ).pack(side="left", padx=(8, 0))
        return row

    def _doc_project_entry(self, parent):
        row = tk.Frame(parent, bg=SURFACE)
        entry = tk.Entry(
            row,
            textvariable=self.v_doc_project,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_doc_project,
        ).pack(side="left", padx=(8, 0))
        return row

    def _toggle_scope(self):
        for row in getattr(self, "_scope_rows", []):
            if self.v_scope.get():
                row.pack(fill="x", pady=4)
            else:
                row.pack_forget()

    def _infer_intake_profile(self) -> dict[str, str]:
        purpose = self.v_plain_purpose.get()
        audience = self.v_audience.get()
        project_type = {
            "website": "website",
            "app": "app",
            "automation": "automation",
            "agent": "agent",
            "harness": "harness",
            "tool": "tool",
            "other": "other",
        }.get(purpose, "app")

        risk_score = 0
        if audience in {"team", "client"}:
            risk_score += 1
        if audience == "customers":
            risk_score += 2
        if purpose in {"app", "automation"}:
            risk_score += 1
        if purpose in {"agent", "harness"}:
            risk_score += 2
        if self.v_has_private_data.get():
            risk_score += 2
        if self.v_has_accounts.get():
            risk_score += 2
        if self.v_handles_money.get():
            risk_score += 3
        if self.v_external_actions.get():
            risk_score += 2
        if self.v_production_ops.get():
            risk_score += 3

        critical_signal = (
            self.v_handles_money.get()
            or self.v_production_ops.get()
            or (purpose in {"agent", "harness"} and self.v_external_actions.get())
        )
        if risk_score >= 7 and critical_signal:
            governance_level = "4"
        elif risk_score >= 4:
            governance_level = "3"
        elif risk_score >= 2:
            governance_level = "2"
        else:
            governance_level = "1"
        risk_tier = GOVERNANCE_TO_RISK[governance_level]

        stack = self.v_stack.get().strip()
        if not stack:
            stack = {
                "website": "website",
                "app": "web app",
                "automation": "python / workflow automation",
                "agent": "AI agent",
                "harness": "AI / ML harness",
                "tool": "local utility",
                "other": "not specified yet",
            }.get(purpose, "not specified yet")

        builder = self.v_builder.get() or "claude"
        if self.v_advanced_settings.get():
            project_type = self.v_type.get() or project_type
            governance_level = governance_level_from_label(self.v_risk.get())
            risk_tier = GOVERNANCE_TO_RISK[governance_level]
            stack = self.v_stack.get().strip() or stack
        return {
            "project_type": project_type,
            "governance_level": governance_level,
            "risk_tier": risk_tier,
            "stack": stack,
            "builder": builder,
        }

    def _apply_inferred_profile(self):
        if self.v_advanced_settings.get() or self._intake_refreshing:
            return
        profile = self._infer_intake_profile()
        try:
            self._intake_refreshing = True
            self.v_type.set(profile["project_type"])
            level = profile["governance_level"]
            matching = next(
                (option for option in GOVERNANCE_OPTIONS if option.startswith(f"{level} ")),
                GOVERNANCE_OPTIONS[2],
            )
            self.v_risk.set(matching)
        finally:
            self._intake_refreshing = False

    def _refresh_intake_summary(self):
        if self._intake_refreshing:
            return
        profile = self._infer_intake_profile()
        if not self.v_advanced_settings.get():
            self._apply_inferred_profile()
        purpose_label = next(
            (title for value, title, _ in PURPOSE_OPTIONS if value == self.v_plain_purpose.get()),
            "Not sure",
        )
        audience_label = next(
            (title for value, title, _ in AUDIENCE_OPTIONS if value == self.v_audience.get()),
            "Not sure",
        )
        name = self.v_name.get().strip() or "Untitled project"
        first_result = self.v_mvp.get().strip() or "First useful result not captured yet"
        risk_flags = []
        if self.v_has_private_data.get():
            risk_flags.append("private data")
        if self.v_has_accounts.get():
            risk_flags.append("accounts or permissions")
        if self.v_handles_money.get():
            risk_flags.append("money handling")
        if self.v_external_actions.get():
            risk_flags.append("external actions")
        if self.v_production_ops.get():
            risk_flags.append("production operations")
        risk_text = ", ".join(risk_flags) if risk_flags else "none selected"
        _, root = TYPE_MAP.get(profile["project_type"], ("application", APPS_ROOT))
        target = root / slugify(name) if name != "Untitled project" else root
        summary_lines = [
            f"Project: {name}",
            f"Intent: {purpose_label}",
        ]
        if self.v_plain_purpose.get() == "harness":
            topology_label = next(
                (
                    title
                    for value, title, _ in HARNESS_TOPOLOGY_OPTIONS
                    if value == self.v_harness_topology.get()
                ),
                self.v_harness_topology.get(),
            )
            summary_lines.append(f"AI topology: {topology_label}")
        summary_lines.extend(
            [
                f"Audience: {audience_label}",
                f"First useful result: {first_result}",
                f"Sensitive areas: {risk_text}",
                "",
                "Inferred setup:",
                f"- Build type: {profile['project_type']}",
                f"- Review level: {profile['governance_level']} ({profile['risk_tier']} risk)",
                f"- Likely stack: {profile['stack']}",
                f"- Destination: {target}",
            ]
        )
        self.v_intake_summary.set("\n".join(summary_lines))
        self._refresh_preview()

    def _toggle_advanced_settings(self):
        if self.v_advanced_settings.get():
            self._advanced_frame.pack(fill="x", pady=(10, 0))
        else:
            self._advanced_frame.pack_forget()
            self._apply_inferred_profile()
        self._refresh_intake_summary()

    def _validate_current_intake_step(self) -> bool:
        step = self.v_intake_step.get()
        if step == 2 and not self.v_name.get().strip():
            messagebox.showerror(
                "Project name needed", "Give the build a project name before continuing."
            )
            return False
        if step == 2 and not self.v_mvp.get().strip():
            messagebox.showerror(
                "First result needed", "Describe the first useful thing this build should create."
            )
            return False
        return True

    def _visible_step_indices(self) -> list[int]:
        is_harness = self.v_plain_purpose.get() == "harness"
        harness_step = getattr(self, "_HARNESS_STEP_INDEX", 1)
        return [i for i in range(len(self._intake_steps)) if is_harness or i != harness_step]

    def _show_intake_step(self, step: int):
        if not hasattr(self, "_intake_steps"):
            return
        visible = self._visible_step_indices()
        if not visible:
            return
        step = max(visible[0], min(step, visible[-1]))
        if step not in visible:
            step = min(visible, key=lambda s: abs(s - step))
        self.v_intake_step.set(step)
        for index, frame in enumerate(self._intake_steps):
            if index == step:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
        visible_pos = visible.index(step) + 1
        total_visible = len(visible)
        self.v_step_label.set(f"Step {visible_pos} of {total_visible}")
        self._back_btn.config(state="disabled" if step == visible[0] else "normal")
        if step == visible[-1]:
            self._next_btn.pack_forget()
            if not self._create_btn.winfo_ismapped():
                self._create_btn.pack(side="left", padx=(10, 0))
        else:
            if not self._next_btn.winfo_ismapped():
                self._next_btn.pack(side="left", padx=(10, 0))
            self._create_btn.pack_forget()
        self._refresh_intake_summary()

    def _next_intake_step(self):
        if not self._validate_current_intake_step():
            return
        visible = self._visible_step_indices()
        current = self.v_intake_step.get()
        try:
            pos = visible.index(current)
            self._show_intake_step(visible[pos + 1])
        except (ValueError, IndexError):
            pass

    def _previous_intake_step(self):
        visible = self._visible_step_indices()
        current = self.v_intake_step.get()
        try:
            pos = visible.index(current)
            if pos > 0:
                self._show_intake_step(visible[pos - 1])
        except ValueError:
            pass

    def _refresh_preview(self):
        name = self.v_name.get().strip()
        if not hasattr(self, "_lbl_preview") or not name:
            if hasattr(self, "_lbl_preview"):
                self._lbl_preview.config(text="")
            return
        self._apply_inferred_profile()
        if not name:
            self._lbl_preview.config(text="")
            return
        _, root = TYPE_MAP.get(self.v_type.get(), ("application", APPS_ROOT))
        self._lbl_preview.config(text=str(root / slugify(name)))

    def _refresh_change_project(self):
        if not self.v_change_project.get():
            self.v_change_project.set(str(AGENTS_ROOT))
        if not self.v_doc_project.get():
            self.v_doc_project.set(str(AGENTS_ROOT))

    def _load_known_projects(self):
        values: list[str] = []
        registry_by_path: dict[str, dict] = {}

        try:
            proc = subprocess.run(
                [sys.executable, str(REGISTRY), "list"],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    registry_by_path[item.get("path", "")] = item
        except Exception:
            registry_by_path = {}

        discovered: list[dict] = []
        seen_paths: set[str] = set()

        def classify_project(child: Path, root_name: str) -> dict | None:
            if not child.is_dir():
                return None
            markers = [
                child / "project-control.yaml",
                child / "package.json",
                child / "pyproject.toml",
                child / "requirements.txt",
                child / "README.md",
            ]
            has_governance = markers[0].exists()
            has_project_signals = any(marker.exists() for marker in markers[1:])
            if not has_governance and not has_project_signals:
                return None

            item = dict(registry_by_path.get(str(child), {}))
            item.setdefault("project_name", child.name)
            item.setdefault("project_type", "unknown")
            item.setdefault("risk_tier", "unknown")
            item.setdefault("latest_audit_status", "unverified")
            item["path"] = str(child)
            item["slug"] = child.name
            item["root_group"] = root_name
            item["discovery_class"] = "governed" if has_governance else "candidate"
            item["display_status"] = item.get("latest_audit_status") or "unverified"
            if item["discovery_class"] == "candidate":
                item["display_status"] = "candidate"
            return item

        for root_name, root in (
            ("code", CODE_ROOT),
            ("agents", AGENTS_ROOT),
            ("applications", APPS_ROOT),
        ):
            if not root.exists():
                continue
            for child in sorted(root.iterdir()):
                resolved = str(child.resolve())
                if resolved in seen_paths:
                    continue
                item = classify_project(child, root_name)
                if item is None:
                    continue
                discovered.append(item)
                seen_paths.add(resolved)

        governed_count = 0
        candidate_count = 0
        for item in discovered:
            if item["discovery_class"] == "governed":
                governed_count += 1
            else:
                candidate_count += 1
            label = (
                f"{item['project_name']} — {item['root_group']} / {item['discovery_class']} "
                f"[{item.get('display_status') or 'unverified'}]"
            )
            self.known_projects[label] = item
            values.append(label)

        summary = (
            f"Found {governed_count} governed and {candidate_count} candidate projects across "
            f"{CODE_ROOT}, {AGENTS_ROOT}, and {APPS_ROOT}"
        )
        self.after(0, lambda: self._apply_known_projects(discovered, values, summary))

    def _apply_known_projects(self, discovered: list[dict], values: list[str], summary: str):
        self.known_projects = {
            (
                f"{item['project_name']} — {item['root_group']} / {item['discovery_class']} "
                f"[{item.get('display_status') or 'unverified'}]"
            ): item
            for item in discovered
        }
        self.v_known_count.set(summary)
        self._known_project_combo.configure(values=values)
        self._doc_known_project_combo.configure(values=values)
        self._refresh_window_anchor()
        if self._pending_known_project_path:
            match = next(
                (
                    label
                    for label, item in self.known_projects.items()
                    if item.get("path") == self._pending_known_project_path
                ),
                None,
            )
            self._pending_known_project_path = None
            if match:
                self.v_known_project.set(match)
                self._on_known_project_selected()
            elif values and (
                not self.v_known_project.get()
                or self.v_known_project.get() not in self.known_projects
            ):
                self.v_known_project.set(values[0])
                self._on_known_project_selected()
            else:
                self._update_change_summary()
        else:
            if values and (
                not self.v_known_project.get()
                or self.v_known_project.get() not in self.known_projects
            ):
                self.v_known_project.set(values[0])
                self._on_known_project_selected()
            else:
                self._update_change_summary()
        if values and (
            not self.v_doc_known_project.get()
            or self.v_doc_known_project.get() not in self.known_projects
        ):
            self.v_doc_known_project.set(values[0])
            self._on_doc_known_project_selected()
        else:
            self._update_doc_summary()
        self.after(80, self._refresh_window_anchor)

    def _refresh_known_project_for_path(self, project_path: str):
        self._pending_known_project_path = project_path
        threading.Thread(target=self._load_known_projects, daemon=True).start()
        self.after(0, self._refresh_window_anchor)

    def _on_known_project_selected(self):
        item = self.known_projects.get(self.v_known_project.get())
        if not item:
            self._update_change_summary()
            return
        self.v_change_project.set(item["path"])
        self.v_execution_report.set("")
        self._update_change_summary(item)

    def _on_doc_known_project_selected(self):
        item = self.known_projects.get(self.v_doc_known_project.get())
        if not item:
            self._update_doc_summary()
            return
        self.v_doc_project.set(item["path"])
        self.v_doc_manifest.set("")
        self._update_doc_summary(item)

    def _sync_project_registry(self, project_path: str) -> None:
        project = Path(project_path).expanduser().resolve()
        metadata = read_project_metadata(project)
        subprocess.run(
            [
                sys.executable,
                str(REGISTRY),
                "register",
                "--project-name",
                metadata["project_name"],
                "--slug",
                project.name,
                "--path",
                str(project),
                "--project-type",
                metadata["project_type"],
                "--risk-tier",
                metadata["risk_tier"],
                "--builder",
                metadata["builder"],
                "--stack",
                metadata["stack"],
            ],
            check=True,
            env=build_subprocess_env(),
        )

        proc = subprocess.run(
            ["bash", str(GOVERNANCE_HOME / "automation" / "governance_check.sh"), str(project)],
            capture_output=True,
            text=True,
            check=False,
            env=build_subprocess_env(),
        )
        missing_files = []
        warnings = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("FAIL: Missing required file "):
                missing_files.append(line.removeprefix("FAIL: Missing required file "))
            elif line.startswith("WARN: "):
                warnings.append(line.removeprefix("WARN: "))

        subprocess.run(
            [
                sys.executable,
                str(REGISTRY),
                "record-audit",
                "--slug",
                project.name,
                "--path",
                str(project),
                "--status",
                "pass" if proc.returncode == 0 else "fail",
                "--missing-files",
                *missing_files,
                "--warnings",
                *warnings,
            ],
            check=True,
            env=build_subprocess_env(),
        )

    def _update_change_summary(self, item: dict | None = None, manifest: dict | None = None):
        if item is None:
            item = next(
                (
                    v
                    for k, v in self.known_projects.items()
                    if v.get("path") == self.v_change_project.get()
                ),
                None,
            )

        lines = []
        if item:
            lines.append(
                f"Selected project: {item.get('project_name', item.get('slug', 'unknown'))}"
            )
            lines.append(f"Class: {item.get('discovery_class', 'unknown')}")
            if item.get("discovery_class") == "candidate":
                lines.append("Verification: candidate project detected from local project signals")
                lines.append("Governance status: not compliant yet")
            else:
                lines.append(f"Audit status: {item.get('latest_audit_status') or 'unverified'}")
            lines.append(f"Path: {item.get('path', '')}")
        elif self.v_change_project.get():
            lines.append(f"Selected path: {self.v_change_project.get()}")

        if manifest is not None:
            actions = manifest.get("actions", [])
            if actions:
                creates = [
                    action.get("relative_path", "?")
                    for action in actions
                    if action.get("action") == "create_file"
                ]
                appends = [
                    action.get("relative_path", "?")
                    for action in actions
                    if action.get("action") == "append_managed_block"
                ]
                if creates:
                    lines.append(f"Planned file creates: {', '.join(creates)}")
                if appends:
                    lines.append(f"Planned instruction appends: {', '.join(appends)}")
            else:
                lines.append(
                    "Planned changes: none; the selected project already has the guided baseline docs and instructions."
                )

        lines.append(
            "Safety: this workflow creates missing governance docs and appends marked instruction blocks only."
        )
        lines.append(
            "It does not rename, move, delete, rewrite existing files, or remap dependencies."
        )
        lines.append(
            "Candidate projects can be guided into governance, but they are not treated as fully governed yet."
        )
        lines.append(
            "A candidate label means the app recognized a project; it is not a failure state."
        )
        self.v_change_summary.set("\n".join(lines))
        self._update_workflow_hint()

    def _update_doc_summary(self, item: dict | None = None, manifest: dict | None = None):
        if item is None:
            item = next(
                (
                    v
                    for v in self.known_projects.values()
                    if v.get("path") == self.v_doc_project.get()
                ),
                None,
            )

        lines = []
        if item:
            lines.append(f"Selected repo: {item.get('project_name', item.get('slug', 'unknown'))}")
            lines.append(f"Path: {item.get('path', '')}")
        elif self.v_doc_project.get():
            lines.append(f"Selected path: {self.v_doc_project.get()}")

        if manifest is not None:
            actions = manifest.get("actions", [])
            if actions:
                lines.append("Planned update: refresh docs/standards/document-control-standard.md")
            else:
                lines.append("Planned update: none; the repo already has the current standard.")

        lines.append("Scope: document-control standard only.")
        lines.append("Review the manifest before applying it.")
        self.v_doc_summary.set("\n".join(lines))

    def _browse_project(self):
        selected = filedialog.askdirectory(
            title="Select governed project",
            initialdir=str(Path(self.v_change_project.get()).expanduser().resolve().parent)
            if self.v_change_project.get()
            else str(Path.home() / "code"),
        )
        if selected:
            self.v_change_project.set(selected)
            self.v_execution_report.set("")
            self._update_change_summary()

    def _browse_doc_project(self):
        selected = filedialog.askdirectory(
            title="Select repo for document control",
            initialdir=str(Path(self.v_doc_project.get()).expanduser().resolve().parent)
            if self.v_doc_project.get()
            else str(Path.home() / "code"),
        )
        if selected:
            self.v_doc_project.set(selected)
            self.v_doc_manifest.set("")
            self._update_doc_summary()

    def _browse_manifest(self):
        selected = filedialog.askopenfilename(
            title="Select manifest",
            initialdir=str(
                (GOVERNANCE_HOME / "data" / "new-build-governance-agent" / "exports").resolve()
            ),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_manifest.set(selected)
            self.v_execution_report.set("")
            self._update_workflow_hint()

    def _browse_doc_manifest(self):
        selected = filedialog.askopenfilename(
            title="Select document-control manifest",
            initialdir=str(
                (GOVERNANCE_HOME / "data" / "new-build-governance-agent" / "exports").resolve()
            ),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_doc_manifest.set(selected)
            self._update_doc_summary()

    def _browse_promotion_plan(self):
        selected = filedialog.askopenfilename(
            title="Select release plan",
            initialdir=str(
                (GOVERNANCE_HOME / "data" / "new-build-governance-agent" / "exports").resolve()
            ),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_promotion_plan.set(selected)
            self.v_execution_report.set("")
            self._update_workflow_hint()

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self._create_btn.config(state=state)
        self._generate_btn.config(state=state)
        self._apply_btn.config(state=state)
        self._promotion_btn.config(state=state)
        self._precheck_btn.config(state=state)
        self._postcheck_btn.config(state=state)
        self._remediate_btn.config(state=state)
        self._execute_btn.config(state=state)
        self._doc_preview_btn.config(state=state)
        self._doc_apply_btn.config(state=state)
        if hasattr(self, "_update_check_btn"):
            self._update_check_btn.config(state=state)
        if hasattr(self, "_self_update_btn"):
            if busy:
                self._self_update_btn.config(state="disabled")
            else:
                self._set_self_update_button_state(self._self_update_allowed)
        if busy:
            self._busy_step = 0
            self._busy_overlay.place(relx=0.5, rely=0.5, anchor="center")
            self._busy_overlay.lift()
            if self._busy_job is None:
                self._animate_busy()
        else:
            if self._busy_job is not None:
                self.after_cancel(self._busy_job)
                self._busy_job = None
            self._busy_overlay.place_forget()

    def _set_self_update_button_state(self, allowed: bool):
        self._self_update_allowed = allowed
        if not hasattr(self, "_self_update_btn"):
            return
        if allowed:
            self._self_update_btn.config(
                state="normal",
                bg=ACCENT,
                fg=CTA_FG,
                activebackground=ACCENT_DARK,
                activeforeground=CTA_FG,
            )
        else:
            self._self_update_btn.config(
                state="disabled",
                bg=SURFACE_ALT,
                fg=FG_DIM,
                activebackground=BORDER,
                activeforeground=FG,
            )

    def _on_check_agent_updates(self):
        self._set_busy(True)
        self._clear_output()
        self._set_self_update_button_state(False)
        threading.Thread(target=self._run_check_agent_updates, daemon=True).start()

    def _run_check_agent_updates(self):
        try:
            update_result = check_for_updates(timeout=5.0)
            dry_run_result = self_update(dry_run=True)
            summary, allow_update = build_update_affordance_summary(
                update_result.status, dry_run_result.status
            )

            self.after(0, lambda text=summary: self.v_update_summary.set(text))
            self.after(0, lambda allowed=allow_update: self._set_self_update_button_state(allowed))
            self._out(format_update_check_result(update_result), "info")
            self._out(format_self_update_result(dry_run_result), "ok" if allow_update else "dim")
        except Exception as exc:
            self.after(
                0,
                lambda: self.v_update_summary.set("Update check failed. Review the activity log."),
            )
            self._out(f"Update check failed: {exc}", "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_self_update_agent(self):
        if not self._self_update_allowed:
            messagebox.showinfo(
                "Update unavailable",
                "Run Check first. The Update action is available only when a safe fast-forward is possible.",
            )
            return
        if not messagebox.askyesno(
            "Update agent",
            "This will fast-forward this checkout from its upstream branch.\n\nThe updater refuses dirty, detached, missing-upstream, ahead, or diverged checkouts.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        self._set_self_update_button_state(False)
        threading.Thread(target=self._run_self_update_agent, daemon=True).start()

    def _run_self_update_agent(self):
        try:
            result = self_update()
            self._out(
                format_self_update_result(result),
                "ok" if result.status in {"updated", "up_to_date"} else "err",
            )
            self.after(
                0,
                lambda: self.v_update_summary.set(
                    f"Self-update status: {result.status}\nRestart the GUI after an update."
                ),
            )
            if result.status == "updated":
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Agent updated",
                        "The checkout was fast-forwarded. Restart the GUI to load updated code.",
                    ),
                )
            elif result.status == "up_to_date":
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Already current", "The checkout is already up to date."
                    ),
                )
            else:
                self.after(
                    0,
                    lambda: messagebox.showwarning(
                        "Update blocked", "Self-update did not run. Review the activity log."
                    ),
                )
        except Exception as exc:
            self.after(
                0, lambda: self.v_update_summary.set("Self-update failed. Review the activity log.")
            )
            self._out(f"Self-update failed: {exc}", "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_create(self):
        name = self.v_name.get().strip()
        if not name:
            messagebox.showerror("Required", "Project name cannot be empty.")
            return
        name_problem = project_name_error(name)
        if name_problem:
            messagebox.showerror(
                "Invalid project name", f"Cannot create this project: {name_problem}."
            )
            return
        if not self.v_mvp.get().strip():
            messagebox.showerror(
                "Required", "Describe the first useful result before creating the build."
            )
            return

        self._apply_inferred_profile()
        profile = self._infer_intake_profile()
        gov_type, root = TYPE_MAP.get(profile["project_type"], ("application", APPS_ROOT))
        slug = slugify(name)
        target_dir = root / slug
        governance_level = profile["governance_level"]
        risk_tier = profile["risk_tier"]
        builder = profile["builder"]
        stack = profile["stack"]
        audience_label = next(
            (title for value, title, _ in AUDIENCE_OPTIONS if value == self.v_audience.get()), ""
        )

        data = dict(
            name=name,
            slug=slug,
            gov_type=gov_type,
            governance_level=governance_level,
            risk_tier=risk_tier,
            stack=stack,
            builder=builder,
            target_dir=str(target_dir),
        )

        if self.v_scope.get():
            data.update(
                problem=self.v_problem.get().strip(),
                user_desc=self.v_user.get().strip() or audience_label,
                mvp=self.v_mvp.get().strip(),
            )

        if target_dir.exists():
            if not messagebox.askyesno(
                "Directory exists",
                f"{target_dir}\nalready exists. Existing files will not be overwritten.\nContinue?",
            ):
                return

        harness_topology = ""
        harness_description = ""
        if profile["project_type"] == "harness":
            harness_topology = self.v_harness_topology.get()
            if hasattr(self, "_harness_desc_text"):
                harness_description = self._harness_desc_text.get("1.0", "end-1c").strip()

        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_create,
            args=(
                target_dir,
                gov_type,
                governance_level,
                risk_tier,
                builder,
                data,
                harness_topology,
                harness_description,
            ),
            daemon=True,
        ).start()

    def _run_create(
        self,
        target_dir,
        gov_type,
        governance_level,
        risk_tier,
        builder,
        data,
        harness_topology="",
        harness_description="",
    ):
        try:
            scaffold_result = scaffold_project(
                target_dir,
                gov_type,
                governance_level,
                harness_topology=harness_topology,
                harness_description=harness_description,
            )
            for message in scaffold_result.messages:
                self._out(message, "dim")

            for directory in ["docs/adr", "docs/specs", "docs/runbooks", "archive"]:
                (target_dir / directory).mkdir(parents=True, exist_ok=True)
            self._out("Created: docs/adr  docs/specs  docs/runbooks  archive", "info")

            pc = target_dir / "project-control.yaml"
            if pc.exists():
                txt = pc.read_text(encoding="utf-8")
                txt = txt.replace("name: Technical Lead", f"name: {builder} session")
                pc.write_text(txt, encoding="utf-8")

            write_initial_scope(target_dir, data)
            self._out("Created: INITIAL_SCOPE.md", "info")

            if REGISTRY.exists():
                subprocess.run(
                    [
                        sys.executable,
                        str(REGISTRY),
                        "register",
                        "--project-name",
                        data["name"],
                        "--slug",
                        data["slug"],
                        "--path",
                        str(target_dir),
                        "--project-type",
                        gov_type,
                        "--risk-tier",
                        risk_tier,
                        "--governance-level",
                        governance_level,
                        "--builder",
                        builder,
                        "--stack",
                        data["stack"],
                        "--problem",
                        data.get("problem", ""),
                        "--user-desc",
                        data.get("user_desc", ""),
                        "--mvp",
                        data.get("mvp", ""),
                    ],
                    check=True,
                    env=build_subprocess_env(),
                )
                self._out("Registered project in local inventory", "info")

            self.after(0, lambda: self.v_change_project.set(str(target_dir)))
            self._out("Created baseline docs: manual + roadmap", "info")
            self._out(f"Ready: {target_dir}", "ok")

        except Exception as exc:
            self._out(f"Error: {exc}", "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_generate_manifest(self):
        project = self.v_change_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a governed project path first.")
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_generate_manifest, args=(project,), daemon=True).start()

    def _run_generate_manifest(self, project: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(CHANGE_CONTROL), "propose", "--project", project],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Compliance preview generation failed.", "err")
                return
            manifest = proc.stdout.strip()
            self.after(0, lambda: self.v_manifest.set(manifest))
            self.after(0, lambda: self.v_execution_report.set(""))
            self._out(f"Generated compliance preview: {manifest}", "ok")
            if Path(manifest).exists():
                manifest_data = json.loads(Path(manifest).read_text(encoding="utf-8"))
                self.after(0, partial(self._update_change_summary, manifest=manifest_data))
                self._out(Path(manifest).read_text(encoding="utf-8").strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_run_governance_audit(self):
        project = self.v_change_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a governed project path first.")
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_governance_audit, args=(project,), daemon=True).start()

    def _run_governance_audit(self, project: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(GOVERNANCE_AUDIT), project, "--open"],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
                return
            output_lines = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
            if not output_lines:
                self._out("Governance audit produced no output.", "err")
                return
            self._out(f"Governance audit report: {output_lines[0].strip()}", "ok")
            if len(output_lines) > 1:
                self._out(output_lines[1].strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_refresh_staged_files(self):
        project = self.v_change_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a governed project path first.")
            return
        threading.Thread(
            target=self._run_refresh_staged_files, args=(project,), daemon=True
        ).start()

    def _run_refresh_staged_files(self, project: str):
        try:
            proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project,
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
            self.after(0, lambda: self._rebuild_staged_files_list(lines))
            if not lines:
                self._out("No local changes detected in git status.", "info")
        except subprocess.TimeoutExpired:
            self._out("git status timed out.", "err")
        except Exception as exc:
            self._out(f"Could not read git status: {exc}", "err")

    def _rebuild_staged_files_list(self, porcelain_lines: list[str]):
        for widget in self._staged_files_inner.winfo_children():
            widget.destroy()
        self._staged_file_vars = []
        for line in porcelain_lines:
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()
            var = tk.BooleanVar(value=False)
            self._staged_file_vars.append((path, var))
            tk.Checkbutton(
                self._staged_files_inner,
                text=f"{line[:2].strip()}  {path}",
                variable=var,
                bg=SURFACE,
                fg=FG,
                selectcolor=ENTRY_BG,
                activebackground=SURFACE,
                activeforeground=FG,
                font=SMALL,
                anchor="w",
                command=self._update_execute_btn_state,
            ).pack(fill="x", pady=1)
        if not porcelain_lines:
            tk.Label(
                self._staged_files_inner,
                text="No changes — working tree is clean.",
                bg=SURFACE,
                fg=FG_DIM,
                font=SMALL,
            ).pack(anchor="w")
        self._staged_files_inner.update_idletasks()
        self._update_execute_btn_state()

    def _update_execute_btn_state(self):
        any_checked = any(var.get() for _, var in self._staged_file_vars)
        self._execute_btn.config(state="normal" if any_checked else "disabled")

    def _on_apply_manifest(self):
        manifest = self.v_manifest.get().strip()
        if not manifest:
            messagebox.showerror("Required", "Preview or choose a compliance manifest first.")
            return
        if not Path(manifest).exists():
            messagebox.showerror("Missing file", f"Compliance manifest not found:\n{manifest}")
            return
        if not messagebox.askyesno(
            "Bring to compliance",
            "This will create missing governed files and append marked instruction blocks listed in the preview.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_apply_manifest, args=(manifest,), daemon=True).start()

    def _run_apply_manifest(self, manifest: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(CHANGE_CONTROL), "apply", "--manifest", manifest],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Manifest apply failed.", "err")
                return
            if proc.stdout.strip():
                self._out(proc.stdout.strip(), "ok")
            manifest_path = Path(manifest)
            if manifest_path.exists():
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                project_path = manifest_data.get("project_path", self.v_change_project.get())
                self._sync_project_registry(project_path)
                self.after(0, partial(self._refresh_known_project_for_path, project_path))
                self.after(0, partial(self._update_change_summary, manifest=manifest_data))
                self._out(manifest_path.read_text(encoding="utf-8").strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_generate_doc_control_manifest(self):
        project = self.v_doc_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a repo path first.")
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_generate_doc_control_manifest, args=(project,), daemon=True
        ).start()

    def _run_generate_doc_control_manifest(self, project: str):
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CHANGE_CONTROL),
                    "propose-document-control",
                    "--project",
                    project,
                ],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(
                    proc.stderr.strip() or "Document-control preview generation failed.", "err"
                )
                return
            manifest = proc.stdout.strip()
            self.after(0, lambda: self.v_doc_manifest.set(manifest))
            self._out(f"Generated document-control preview: {manifest}", "ok")
            if Path(manifest).exists():
                manifest_data = json.loads(Path(manifest).read_text(encoding="utf-8"))
                self.after(0, partial(self._update_doc_summary, manifest=manifest_data))
                self._out(Path(manifest).read_text(encoding="utf-8").strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_apply_doc_control_manifest(self):
        manifest = self.v_doc_manifest.get().strip()
        if not manifest:
            messagebox.showerror("Required", "Preview or choose a document-control manifest first.")
            return
        if not Path(manifest).exists():
            messagebox.showerror(
                "Missing file", f"Document-control manifest not found:\n{manifest}"
            )
            return
        if not messagebox.askyesno(
            "Apply document control",
            "This will update only docs/standards/document-control-standard.md in the selected repo.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_apply_doc_control_manifest, args=(manifest,), daemon=True
        ).start()

    def _run_apply_doc_control_manifest(self, manifest: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(CHANGE_CONTROL), "apply", "--manifest", manifest],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Document-control apply failed.", "err")
                return
            if proc.stdout.strip():
                self._out(proc.stdout.strip(), "ok")
            manifest_path = Path(manifest)
            if manifest_path.exists():
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                project_path = manifest_data.get("project_path", self.v_doc_project.get())
                self.after(0, partial(self.v_doc_project.set, project_path))
                self.after(0, partial(self._update_doc_summary, manifest=manifest_data))
                self._out(manifest_path.read_text(encoding="utf-8").strip(), "dim")
                sup = subprocess.run(
                    [
                        sys.executable,
                        str(CHANGE_CONTROL),
                        "supersession-status",
                        "--project",
                        project_path,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    env=build_subprocess_env(),
                )
                if sup.returncode == 0 and sup.stdout.strip():
                    self._out(f"Supersession: {sup.stdout.strip()}", "ok")
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Document control updated",
                        "The document-control standard update is complete.",
                    ),
                )
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_generate_promotion_plan(self):
        project = self.v_change_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a project path first.")
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_generate_promotion_plan, args=(project,), daemon=True
        ).start()

    def _on_run_prechecks(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a release plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Release plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Run pre-checks",
            "This will run the safe local pre-release checks listed in the plan.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_prechecks, args=(plan_path,), daemon=True).start()

    def _on_run_postchecks(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a release plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Release plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Run re-check",
            "This will run the post-release re-checks listed in the plan.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_postchecks, args=(plan_path,), daemon=True).start()

    def _on_fix_missing_test_tools(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a release plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Release plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Install missing test tools",
            (
                "This will try to install missing local test tooling for the selected project, "
                "starting with pytest in the project's detected Python environment, and then rerun pre-checks.\n\nContinue?"
            ),
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_fix_missing_test_tools, args=(plan_path,), daemon=True
        ).start()

    def _on_execute_github(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a release plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Release plan not found:\n{plan_path}")
            return
        include_files = [path for path, var in self._staged_file_vars if var.get()]
        if not include_files:
            messagebox.showerror(
                "No files selected",
                "Use 'Refresh' in step 4b to load changed files, then check at least one file to include in the commit.",
            )
            return
        if not messagebox.askyesno(
            "Execute GitHub publish",
            (
                "This will stage the reviewed local changes in the selected project, create a git commit, push the current branch, "
                "and record rollback instructions in an execution report.\n\nContinue?"
            ),
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_execute_github,
            args=(plan_path, self.v_commit_message.get().strip(), include_files),
            daemon=True,
        ).start()

    def _run_generate_promotion_plan(self, project: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(PROMOTION_PLAN), "--project", project],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "External plan generation failed.", "err")
                return
            plan_path = proc.stdout.strip()
            self.after(0, lambda: self.v_promotion_plan.set(plan_path))
            self.after(0, lambda: self.v_execution_report.set(""))
            self._out(
                "Generated staged release plan with pre-checks, approval-and-execute guidance, post-checks, and rollback readiness.",
                "ok",
            )
            self._out(f"Plan file: {plan_path}", "info")
            if Path(plan_path).exists():
                plan_data = json.loads(Path(plan_path).read_text(encoding="utf-8"))
                stages = plan_data.get("stages", [])
                if stages:
                    for stage in stages:
                        self._out(f"{stage.get('name')}: {stage.get('status')}", "dim")
                sync_stage = next(
                    (stage for stage in stages if stage.get("name") == "prepare_external_sync"),
                    None,
                )
                if sync_stage:
                    targets = sync_stage.get("targets", {})
                    relevant = [name for name, data in targets.items() if data.get("relevant")]
                    if relevant:
                        self._out("Detected targets: " + ", ".join(relevant), "info")
                    else:
                        self._out(
                            "Detected targets: none yet; this project still has a planning shell for future external sync.",
                            "info",
                        )
                self._out(Path(plan_path).read_text(encoding="utf-8").strip(), "dim")
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "External plan ready",
                        "A staged external plan was created.\n\nIt includes pre-checks, approval-and-execute guidance, post-checks, and rollback readiness notes for GitHub, Vercel, Supabase, Stripe, and Resend.",
                    ),
                )
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_prechecks(self, plan_path: str):
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PROMOTION_CHECKS),
                    "--plan",
                    plan_path,
                    "--stage",
                    "pre_promotion_checks",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Pre-check report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                self._sync_project_registry(report_data["project_path"])
                self.after(
                    0, partial(self._refresh_known_project_for_path, report_data["project_path"])
                )
                self._out(
                    f"Pre-check status: {report_data.get('overall_status', 'unknown')}",
                    "ok" if report_data.get("overall_status") == "passed" else "info",
                )
                for result in report_data.get("results", []):
                    tag = (
                        "ok"
                        if result.get("status") == "passed"
                        else ("err" if result.get("status") == "failed" else "info")
                    )
                    self._out(f"{result.get('name')}: {result.get('status')}", tag)
                    if result.get("stdout"):
                        self._out(result.get("stdout").strip(), "dim")
                    if result.get("stderr"):
                        self._out(result.get("stderr").strip(), "err")
                if report_data.get("overall_status") == "passed":
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Pre-checks passed",
                            "Local pre-release checks passed. External targets still require explicit approval.",
                        ),
                    )
                elif report_data.get("overall_status") == "manual_required":
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Manual review required",
                            "Some pre-checks require manual review before release.",
                        ),
                    )
                else:
                    self.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Pre-checks failed",
                            "One or more pre-release checks failed. Review the report before proceeding.",
                        ),
                    )
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_postchecks(self, plan_path: str):
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PROMOTION_CHECKS),
                    "--plan",
                    plan_path,
                    "--stage",
                    "post_promotion_checks",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Re-check report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                self._sync_project_registry(report_data["project_path"])
                self.after(
                    0, partial(self._refresh_known_project_for_path, report_data["project_path"])
                )
                self._out(
                    f"Re-check status: {report_data.get('overall_status', 'unknown')}",
                    "ok" if report_data.get("overall_status") == "passed" else "info",
                )
                for result in report_data.get("results", []):
                    tag = (
                        "ok"
                        if result.get("status") == "passed"
                        else ("err" if result.get("status") == "failed" else "info")
                    )
                    self._out(f"{result.get('name')}: {result.get('status')}", tag)
                    if result.get("stdout"):
                        self._out(result.get("stdout").strip(), "dim")
                    if result.get("stderr"):
                        self._out(result.get("stderr").strip(), "err")
                if report_data.get("overall_status") == "passed":
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Re-checks passed", "Post-release re-checks passed."
                        ),
                    )
                elif report_data.get("overall_status") == "manual_required":
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Manual review required",
                            "Some post-release re-checks require manual review.",
                        ),
                    )
                else:
                    self.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Re-checks failed",
                            "One or more post-release re-checks failed. Review the report before proceeding.",
                        ),
                    )
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_fix_missing_test_tools(self, plan_path: str):
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PROMOTION_REMEDIATE),
                    "--plan",
                    plan_path,
                    "--tool",
                    "pytest",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Remediation report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                status = report_data.get("status", "unknown")
                if status == "failed":
                    self._out(report_data.get("error", "Test tool remediation failed."), "err")
                    self.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Remediation failed",
                            "The missing test tool could not be installed automatically.",
                        ),
                    )
                    return
                if status == "already_present":
                    self._out(
                        "pytest is already available in the detected project environment.", "ok"
                    )
                else:
                    self._out("Installed pytest in the detected project environment.", "ok")
                python_command = " ".join(report_data.get("python_command", []))
                if python_command:
                    self._out(f"Python environment: {python_command}", "info")
                if report_data.get("stdout"):
                    self._out(report_data["stdout"], "dim")
                self._out("Re-running pre-checks after remediation...", "info")
                self._run_prechecks(plan_path)
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_execute_github(self, plan_path: str, commit_message: str, include_files: list[str]):
        try:
            command = [
                sys.executable,
                str(PROMOTION_EXECUTE),
                "--plan",
                plan_path,
                "--target",
                "github",
            ]
            for f in include_files:
                command.extend(["--include-file", f])
            if commit_message:
                command.extend(["--commit-message", commit_message])
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self.after(0, partial(self.v_execution_report.set, report_path))
                self.after(0, self._update_workflow_hint)
                self._out(f"Execute report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                status = report_data.get("status", "unknown")
                self._out(
                    f"GitHub execute status: {status}",
                    "ok" if status == "executed" else "err",
                )
                if status == "executed":
                    self._out(f"Repo: {report_data.get('repo_name', 'unknown')}", "info")
                    self._out(f"Branch: {report_data.get('branch', 'unknown')}", "info")
                    self._out(
                        f"Previous head: {report_data.get('previous_head', 'unknown')}", "dim"
                    )
                    self._out(f"New head: {report_data.get('new_head', 'unknown')}", "ok")
                    self._out(f"Stage mode: {report_data.get('stage_mode', 'unknown')}", "info")
                    for staged_file in report_data.get("staged_files", []):
                        self._out(f"Staged: {staged_file}", "dim")
                    if report_data.get("pr_url"):
                        self._out(f"Draft PR: {report_data['pr_url']}", "info")
                    self._out(report_data.get("rollback_note", ""), "info")
                    for command_text in report_data.get("rollback_commands", []):
                        self._out(command_text, "dim")
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "GitHub publish complete",
                            "GitHub publish completed and rollback instructions were recorded.",
                        ),
                    )
                else:
                    self._out(report_data.get("error", "GitHub publish failed."), "err")
                    self.after(
                        0,
                        lambda: messagebox.showwarning(
                            "GitHub publish failed",
                            "The GitHub publish step failed. Review the execution report and output log.",
                        ),
                    )
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _clear_output(self):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        self._output.config(state="disabled")
        self.v_activity_summary.set("Ready.")

    def _out(self, text: str, tag: str = ""):
        if not text:
            return

        def _do():
            self.v_activity_summary.set(text)
            if tag == "err":
                self._set_output_log_expanded(True)
            self._output.config(state="normal")
            self._output.insert("end", text + "\n", tag)
            self._output.see("end")
            self._output.config(state="disabled")

        self.after(0, _do)


def main() -> None:
    try:
        if tk is None:
            raise RuntimeError(
                "Tkinter is not available for this Python installation. "
                "Install python3-tk and relaunch New Build Governance Agent."
            )
        App().mainloop()
    except Exception as exc:
        details = "".join(traceback.format_exception(exc))
        log_startup_error(details)
        if messagebox is not None and tk is not None:
            try:
                fallback = tk.Tk()
                fallback.withdraw()
                messagebox.showerror(
                    "New Build Governance Agent failed to start",
                    f"{exc}\n\nStartup log: {LOG_PATH}",
                )
                fallback.destroy()
            except Exception:
                pass
        print(f"New Build Governance Agent failed to start: {exc}", file=sys.stderr)
        print(f"Startup log: {LOG_PATH}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
