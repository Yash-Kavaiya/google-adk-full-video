from __future__ import annotations

import json
import textwrap
from pathlib import Path

from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30
config.frame_width = 14.222
config.frame_height = 8.0

BG = "#F8FAFD"
WHITE = "#FFFFFF"
INK = "#202124"
MUTED = "#5F6368"
BORDER = "#DADCE0"
BLUE = "#4285F4"
RED = "#EA4335"
YELLOW = "#FBBC04"
GREEN = "#34A853"
PALE_BLUE = "#E8F0FE"
PALE_RED = "#FCE8E6"
PALE_YELLOW = "#FEF7E0"
PALE_GREEN = "#E6F4EA"
FONT = "Arial"
COLORS = [BLUE, RED, YELLOW, GREEN]
PALES = [PALE_BLUE, PALE_RED, PALE_YELLOW, PALE_GREEN]

ROOT = Path(__file__).resolve().parent
STORYBOARD = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
TIMING = json.loads((ROOT / "audio" / "timing.json").read_text(encoding="utf-8"))
TIMES = {row["id"]: float(row["duration"]) for row in TIMING["lines"]}

NODES = {
    "01": ["Idea", "Agent", "Tools", "Production"],
    "02": ["LlmAgent", "Tool", "Session", "Runner"],
    "03": ["pip install", "adk create", "adk run", "adk web"],
    "04": ["Function tool", "MCP", "OpenAPI", "Skills"],
    "05": ["Sequential", "Parallel", "Loop", "Graph"],
    "06": ["Session", "State", "Memory", "Context"],
    "07": ["CLI / Web", "Agent Runtime", "Cloud Run", "GKE"],
    "08": ["Identity", "Guardrails", "A2A", "Evaluate"],
}
MODES = {"01": "flow", "02": "flow", "03": "flow", "04": "grid", "05": "flow", "06": "lanes", "07": "shield", "08": "loop"}
TAGS = {
    "01": [("OPEN SOURCE", "MULTI LANGUAGE", "PRODUCTION"), ("PYTHON", "TYPESCRIPT", "GO"), ("JAVA", "KOTLIN", "CLI"), ("PROMPT", "TOOLS", "GRAPH"), ("HUMAN", "AI CODER", "SKILLS"), ("GEMINI", "HOSTED", "LOCAL"), ("SESSION", "MEMORY", "ARTIFACT"), ("BUILD", "DEBUG", "DEPLOY")],
    "02": [("LLM AGENT", "WORKFLOW", "NODE"), ("API", "SEARCH", "CODE"), ("BEFORE", "AFTER", "CONTROL"), ("EVENTS", "HISTORY", "STATE"), ("LONG TERM", "SEARCHABLE", "ARCHIVE"), ("FILES", "PDF", "IMAGES"), ("USER", "AGENT", "TOOL"), ("ORCHESTRATE", "SERVICES", "FLOW")],
    "03": [("PYTHON 3.10+", "PIP", "VENV"), ("agent.py", ".env", "__init__"), ("root_agent", "REQUIRED", "ENTRY"), ("MODEL", "INSTRUCTION", "TOOL"), ("GOOGLE_API_KEY", "AI STUDIO", "NO GIT"), ("adk run", "CLI", "INTERACTIVE"), ("adk web", "PORT 8000", "PARENT DIR"), ("DEV ONLY", "NOT PROD", "DEBUG")],
    "04": [("EXECUTE", "NO REASONING", "DEVELOPER LOGIC"), ("REASON", "SELECT", "INVOKE"), ("DOCSTRING", "NAME", "ARGS"), ("AGENT TOOL", "MCP", "OPENAPI"), ("LONG RUNNING", "ASYNC", "TURN"), ("CONFIRM", "GATE", "DANGEROUS"), ("L1 META", "L2 INSTRUCT", "ON DEMAND"), ("EXPERIMENTAL", "FEEDBACK", "EVOLVING")],
    "05": [("MULTI AGENT", "MULTI NODE", "WORKFLOW"), ("RELIABILITY", "CONTEXT", "MODULARITY"), ("NO LLM ROUTE", "DETERMINISTIC", "TEMPLATE"), ("NODES", "EDGES", "ROUTING"), ("LOOPS", "BRANCH", "CODE"), ("COORDINATOR", "SUBAGENTS", "TEAM"), ("PYTHON GA", "19 MAY 2026", "2.0"), ("BaseNode", "BREAKING", "MIGRATE")],
    "06": [("STATE", "ARTIFACTS", "MEMORY"), ("InvocationContext", "RUNNER", "IMPLICIT"), ("THIS THREAD", "CART", "PREFERENCE"), ("PAST CHATS", "SEARCH", "FACTS"), ("INGEST", "APPEND", "QUERY"), ("IN-MEMORY", "LOCAL TEST", "NOT DURABLE"), ("FILTER", "SUMMARIZE", "LAZY LOAD"), ("TOKEN BUDGET", "SOURCE CODE", "EARN PLACE")],
    "07": [("CLI", "WEB", "API SERVER"), ("YIELD", "PAUSE", "RESUME"), ("CANCEL", "RECOVER", "LONG JOBS"), ("MANAGED", "CONTAINER", "K8S"), ("DOCKER", "PODMAN", "ANYWHERE"), ("TRAJECTORY", "FINAL ANSWER", "BOTH"), ("INTENT", "TOOL", "REPORT"), ("AUTOMATE EVAL", "BEST PRACTICE", "BEFORE SCALE")],
    "08": [("EXFIL RISK", "MISALIGNED", "ASSESS"), ("AGENT AUTH", "USER AUTH", "WHO ACTS"), ("FILTERS", "CALLBACKS", "PLUGINS"), ("SANDBOX", "VPC-SC", "PERIMETER"), ("IN PROCESS", "REMOTE", "A2A"), ("CONTRACT", "LANGUAGES", "SERVICES"), ("ADC", "SERVICE ACCOUNT", "NO KEYS"), ("ONE AGENT", "ONE TOOL", "THEN EXPAND")],
}

CUES = {
    "01": ["A runtime for repeatable agent work", "Open-source Agent Development Kit", "Five official language SDKs", "Built for production, not demos", "Grow from prompts into graphs", "Humans and AI can author ADK", "Gemini plus many other models", "Context assembled like source code"],
    "02": ["LlmAgent or workflow agent", "Tools reach beyond conversation", "Callbacks without rewriting the core", "One Session is one thread", "Memory spans many sessions", "Artifacts keep files around", "Events are the history units", "The Runner drives the loop"],
    "03": ["Install google-adk on Python 3.10+", "Scaffold with adk create", "Define root_agent in agent.py", "Model, instruction, and one tool", "Keep API keys out of git", "Talk to it with adk run", "Inspect it with adk web", "The web UI is development only"],
    "04": ["Tools execute; models reason", "Reason, select, then invoke", "Function tools start here", "MCP, OpenAPI, and AgentTool", "Long-running tools stay async", "Confirm dangerous actions", "Skills load on demand", "Skills are still experimental"],
    "05": ["Workflows start at two nodes", "Split for quality and limits", "Sequential, Parallel, and Loop", "Graphs add explicit routing", "Dynamic flow lives in code", "Coordinators plus specialists", "Python 2.0 GA: 19 May 2026", "Upgrade 1.x as a migration"],
    "06": ["Context is the working set", "The Runner supplies it", "State belongs to this chat", "Memory is the archive", "Not every backend does everything", "In-memory is for tests", "Compaction is built in", "Every token should earn its place"],
    "07": ["CLI, web, API, ambient", "Yield, pause, resume", "Resume and cancel long runs", "Agent Runtime, Cloud Run, GKE", "Containers run anywhere", "Score path and answer", "Trajectory is a checklist", "Evaluate before you scale"],
    "08": ["Safety is a product feature", "Control who the agent acts as", "Layer guardrails and callbacks", "Sandbox code and networks", "Local modules versus remote A2A", "A2A is the service contract", "Production auth, not ADK Web", "Pilot one agent, then expand"],
}


def label(text: str, size: float = 24, color: str = INK, weight=NORMAL) -> Text:
    mob = Text(text, font=FONT, font_size=size, color=color, weight=weight, disable_ligatures=True)
    return mob


def fit_label(text: str, max_width: float, size: float = 24, color: str = INK, weight=NORMAL) -> Text:
    mob = label(text, size=size, color=color, weight=weight)
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def para(text: str, chars: int, size: float, color: str = INK, weight=NORMAL) -> Paragraph:
    lines = textwrap.wrap(text, width=chars, break_long_words=False, break_on_hyphens=False) or [text]
    mob = Paragraph(*lines, alignment="left", font=FONT, font_size=size, color=color, weight=weight, line_spacing=0.82)
    return mob


def card(text: str, color: str, pale: str, active: bool, width: float = 2.65, height: float = 1.02) -> VGroup:
    box = RoundedRectangle(width=width, height=height, corner_radius=0.16, stroke_color=color if active else BORDER, stroke_width=5 if active else 2)
    box.set_fill(pale if active else WHITE, opacity=1)
    txt = fit_label(text, width - 0.28, size=22, color=INK, weight=BOLD if active else NORMAL)
    return VGroup(box, txt)


def arrow_between(a: Mobject, b: Mobject, color: str = "#80868B") -> Arrow:
    return Arrow(a.get_right(), b.get_left(), buff=0.12, stroke_width=5, color=color, max_tip_length_to_length_ratio=0.16)


def flow_board(nodes: list[str], active: int) -> VGroup:
    cards = [card(n, COLORS[i], PALES[i], i == active) for i, n in enumerate(nodes)]
    row = VGroup(*cards).arrange(RIGHT, buff=0.42).move_to([0, 0.18, 0])
    arrows = VGroup(*[arrow_between(cards[i], cards[i + 1]) for i in range(3)])
    return VGroup(row, arrows)


def grid_board(nodes: list[str], active: int) -> VGroup:
    cards = [card(n, COLORS[i], PALES[i], i == active, width=3.6, height=0.9) for i, n in enumerate(nodes)]
    positions = [(-2.1, 0.62), (2.1, 0.62), (-2.1, -0.52), (2.1, -0.52)]
    for mob, (x, y) in zip(cards, positions):
        mob.move_to([x, y, 0])
    arrows = VGroup(arrow_between(cards[0], cards[1]), arrow_between(cards[2], cards[3]))
    return VGroup(*cards, arrows)


def lanes_board(nodes: list[str], active: int) -> VGroup:
    lane1 = RoundedRectangle(width=10.5, height=0.86, corner_radius=0.16, stroke_color=BLUE, stroke_width=2).set_fill(PALE_BLUE, 0.45).move_to([0, 0.62, 0])
    lane2 = RoundedRectangle(width=10.5, height=0.86, corner_radius=0.16, stroke_color=GREEN, stroke_width=2).set_fill(PALE_GREEN, 0.45).move_to([0, -0.52, 0])
    labels = VGroup(fit_label(nodes[0], 2.2, 23, BLUE, BOLD), fit_label(nodes[1], 2.2, 23, RED, BOLD), fit_label(nodes[2], 2.2, 23, YELLOW, BOLD), fit_label(nodes[3], 2.2, 23, GREEN, BOLD))
    for mob, pos in zip(labels, [(-3.2, 0.62), (2.5, 0.62), (-3.2, -0.52), (2.5, -0.52)]):
        mob.move_to([*pos, 0])
    focus = SurroundingRectangle(labels[active], color=COLORS[active], buff=0.16, corner_radius=0.1, stroke_width=5)
    return VGroup(lane1, lane2, labels, focus)


def shield_board(nodes: list[str], active: int) -> VGroup:
    rings = VGroup(Circle(1.0, color=BLUE, stroke_width=5), Circle(0.7, color=GREEN, stroke_width=4), fit_label("TRUST", 1.1, 25, INK, BOLD)).move_to(ORIGIN)
    cards = [card(n, COLORS[i], PALES[i], i == active, width=2.75, height=0.78) for i, n in enumerate(nodes)]
    for mob, pos in zip(cards, [(-3.4, 0.72), (0, 1.05), (3.4, 0.72), (0, -1.05)]):
        mob.move_to([*pos, 0])
    return VGroup(rings, *cards)


def loop_board(nodes: list[str], active: int) -> VGroup:
    cards = [card(n, COLORS[i], PALES[i], i == active, width=2.65, height=0.82) for i, n in enumerate(nodes)]
    positions = [(-3.4, 0.72), (0, 0.72), (3.4, 0.72), (0, -0.6)]
    for mob, pos in zip(cards, positions):
        mob.move_to([*pos, 0])
    arrows = VGroup(arrow_between(cards[0], cards[1]), arrow_between(cards[1], cards[2]), Arrow(cards[2].get_bottom(), cards[3].get_right(), buff=0.1, color=MUTED, stroke_width=3), Arrow(cards[3].get_left(), cards[0].get_bottom(), buff=0.1, color=MUTED, stroke_width=3))
    return VGroup(*cards, arrows)


def board_for(chapter: str, beat: int) -> VGroup:
    mode = MODES[chapter]
    active = beat % 4
    if mode == "flow":
        return flow_board(NODES[chapter], active)
    if mode == "grid":
        return grid_board(NODES[chapter], active)
    if mode == "lanes":
        return lanes_board(NODES[chapter], active)
    if mode == "shield":
        return shield_board(NODES[chapter], active)
    return loop_board(NODES[chapter], active)


def static_chrome() -> VGroup:
    dots = VGroup(*[Circle(radius=0.075, color=c, fill_color=c, fill_opacity=1, stroke_width=0) for c in COLORS]).arrange(RIGHT, buff=0.09).move_to([-6.25, 3.58, 0])
    brand = label("GOOGLE  •  AGENT DEVELOPMENT KIT", 20, INK, BOLD).next_to(dots, RIGHT, buff=0.22)
    badge_box = RoundedRectangle(width=2.26, height=0.34, corner_radius=0.12, stroke_color=BORDER, stroke_width=1).set_fill(WHITE, 1).move_to([5.55, 3.58, 0])
    badge = fit_label("INDEPENDENT EXPLAINER", 2.0, 12, MUTED, BOLD).move_to(badge_box)
    rule = VGroup(*[Rectangle(width=3.125, height=0.055, fill_color=c, fill_opacity=1, stroke_width=0) for c in COLORS]).arrange(RIGHT, buff=0).move_to([0, 3.29, 0])
    return VGroup(dots, brand, badge_box, badge, rule)


def beat_frame(row: dict, chapter_title: str, chapter: str, beat_index: int, absolute_index: int, total: int) -> VGroup:
    chapter_color = COLORS[(int(chapter) - 1) % 4]
    number = label(f"{chapter} / 08", 16, chapter_color, BOLD).move_to([5.95, 2.84, 0])
    title = fit_label(chapter_title, 11.2, 35, BLUE, BOLD).move_to([-6.25 + 5.6, 2.84, 0]).align_to([-6.25, 2.84, 0], LEFT)
    divider = Line([-6.25, 2.37, 0], [6.25, 2.37, 0], stroke_width=1.5, color=BORDER)

    cue_box = RoundedRectangle(width=12.5, height=0.72, corner_radius=0.16, stroke_color=chapter_color, stroke_width=2).set_fill(WHITE, 1).move_to([0, 1.83, 0])
    cue = fit_label(CUES[chapter][beat_index], 11.85, 23, INK, BOLD).move_to(cue_box)
    board = board_for(chapter, beat_index).move_to([0, 0.35, 0])

    chips = VGroup()
    for text, color, pale in zip(TAGS[chapter][beat_index], COLORS[1:] + COLORS[:1], PALES[1:] + PALES[:1]):
        chip_box = RoundedRectangle(width=2.5, height=0.42, corner_radius=0.15, stroke_color=color, stroke_width=1.5).set_fill(pale, 1)
        chip_text = fit_label(text, 2.2, 14, INK, BOLD)
        chips.add(VGroup(chip_box, chip_text))
    chips.arrange(RIGHT, buff=0.2).move_to([0, -1.14, 0])
    src = label("Official ADK docs  •  source map included", 12, MUTED).move_to([4.85, -1.55, 0])

    cap_box = RoundedRectangle(width=12.5, height=1.25, corner_radius=0.16, stroke_color=BORDER, stroke_width=1.5).set_fill(WHITE, 1).move_to([0, -2.58, 0])
    cap_strip = Rectangle(width=0.09, height=0.9, fill_color=chapter_color, fill_opacity=1, stroke_width=0).move_to([-6.0, -2.58, 0])
    cap = para(row["text"], 80, 22, INK).move_to([-5.75, -2.58, 0]).align_to([-5.75, -2.58, 0], LEFT)
    if cap.width > 10.95:
        cap.scale_to_fit_width(10.95)
    line_no = label(f"BEAT {absolute_index:02d} / {total:02d}", 13, MUTED, BOLD).move_to([5.48, -2.99, 0])

    progress_label = label("PROGRESS", 11, MUTED, BOLD).move_to([-5.78, -3.66, 0])
    base = RoundedRectangle(width=10.65, height=0.09, corner_radius=0.045, stroke_width=0).set_fill(BORDER, 1).move_to([0.78, -3.66, 0])
    progress_width = max(0.08, 10.65 * absolute_index / total)
    progress = RoundedRectangle(width=progress_width, height=0.09, corner_radius=0.045, stroke_width=0).set_fill(chapter_color, 1).move_to([-4.545 + progress_width / 2, -3.66, 0])
    return VGroup(number, title, divider, cue_box, cue, board, chips, src, cap_box, cap_strip, cap, line_no, progress_label, base, progress)


class GoogleADKFullInfo(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(static_chrome())
        rows = [row for chapter in STORYBOARD["chapters"] for row in chapter["beats"]]
        total = len(rows)
        current = None
        absolute = 0
        target = 0.0
        half_frame = 0.5 / config.frame_rate
        for chapter in STORYBOARD["chapters"]:
            chapter_id = f"{int(chapter['number']):02d}"
            for beat_index, row in enumerate(chapter["beats"]):
                absolute += 1
                frame = beat_frame(row, chapter["title"], chapter_id, beat_index, absolute, total)
                duration = TIMES[row["id"]]
                transition = min(0.55, max(0.30, duration * 0.10))
                if current is None:
                    self.play(FadeIn(frame, shift=UP * 0.08), run_time=transition)
                else:
                    self.play(FadeOut(current, shift=UP * 0.03), FadeIn(frame, shift=UP * 0.03), run_time=transition)
                target += duration
                remaining = target - self.renderer.time + half_frame
                if remaining >= 1 / config.frame_rate:
                    self.wait(remaining)
                current = frame
