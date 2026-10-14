from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHAPTERS = [
    (
        "01",
        "What ADK Is",
        [
            ("c01-b01", "An agent framework is not a chatbot wrapper; it is a managed, repeatable task runtime.", "Framework, not a chat toy", [1]),
            ("c01-b02", "Google Agent Development Kit is an open-source framework for building, debugging, and deploying production agents.", "Open-source production framework", [1]),
            ("c01-b03", "ADK is available in Python, TypeScript, Go, Java, and Kotlin.", "Five language SDKs", [1]),
            ("c01-b04", "The homepage positioning is explicit: build production agents, not prototypes.", "Production, not prototypes", [1]),
            ("c01-b05", "You can start with a prompt and tools, then grow into multi-agent orchestration and graph workflows.", "Start simple, grow structured", [1, 2]),
            ("c01-b06", "ADK is designed to be written by both humans and AI coding assistants.", "Human and AI authors", [1]),
            ("c01-b07", "The kit works with Gemini and many other models, including hosted and local options.", "Model-flexible", [1, 2]),
            ("c01-b08", "Context is treated like source code: sessions, memory, tools, and artifacts are assembled, not pasted until overflow.", "Context as source code", [1]),
        ],
    ),
    (
        "02",
        "Core Primitives",
        [
            ("c02-b01", "The fundamental worker is an Agent, usually an LlmAgent for reasoning, or a workflow agent for deterministic control.", "Agent is the worker unit", [2]),
            ("c02-b02", "A Tool gives the agent abilities beyond conversation: APIs, search, code, and other services.", "Tools extend the agent", [2, 5]),
            ("c02-b03", "Callbacks run at defined points so you can inspect, log, or change behavior without rewriting the agent core.", "Callbacks hook the lifecycle", [2, 18]),
            ("c02-b04", "A Session holds one conversation thread: events, history, and working State.", "Session is the thread", [2, 6]),
            ("c02-b05", "Memory is long-term knowledge across sessions, distinct from short-term session State.", "Memory is not State", [2, 7]),
            ("c02-b06", "Artifacts let agents save and load files or binary data associated with a session or user.", "Artifacts persist files", [2]),
            ("c02-b07", "An Event is the unit of communication: user message, agent reply, or tool use.", "Events form history", [2]),
            ("c02-b08", "The Runner is the engine that orchestrates execution from events and coordinates backend services.", "Runner drives execution", [2, 15]),
        ],
    ),
    (
        "03",
        "Build and Run",
        [
            ("c03-b01", "Python ADK requires Python 3.10 or later, then pip install google-adk.", "Install the SDK", [3]),
            ("c03-b02", "adk create scaffolds a project with agent.py, a dotenv file, and package init.", "Scaffold the project", [3]),
            ("c03-b03", "The only required element is a root_agent definition in agent.py.", "root_agent is required", [3]),
            ("c03-b04", "A first agent can be a Gemini model, an instruction, and one Python function used as a tool.", "Model, instruction, tool", [3, 4]),
            ("c03-b05", "Gemini API use needs GOOGLE_API_KEY in the environment, never committed to source control.", "Keep keys out of git", [3, 19]),
            ("c03-b06", "adk run starts an interactive command-line session against your agent folder.", "Test with adk run", [3]),
            ("c03-b07", "adk web starts a local chat UI, typically on port 8000, launched from the parent folder.", "Inspect with adk web", [3]),
            ("c03-b08", "The documentation warns that ADK Web is for development and debugging, not production deployments.", "Web UI is not production", [3]),
        ],
    ),
    (
        "04",
        "Tools and Skills",
        [
            ("c04-b01", "A tool is developer-defined logic. It does not reason on its own; the model chooses when to call it.", "Tools execute, models reason", [5]),
            ("c04-b02", "The loop is reason, select, invoke with arguments, then fold the result back into the next step.", "Reason, select, invoke", [5]),
            ("c04-b03", "Function tools wrap ordinary functions. Clear names and docstrings drive tool selection.", "Function tools first", [5]),
            ("c04-b04", "You can also wrap another agent as AgentTool, or connect MCP and OpenAPI surfaces.", "MCP, OpenAPI, AgentTool", [2, 5]),
            ("c04-b05", "Long-running tools exist for asynchronous work that should not block the whole turn.", "Async tool support", [2]),
            ("c04-b06", "Action confirmations let you gate dangerous tool calls before they execute.", "Confirm before acting", [5]),
            ("c04-b07", "Agent Skills package instructions, resources, and tools, loaded on demand to protect the context window.", "Skills load on demand", [17]),
            ("c04-b08", "The Skills feature is experimental; treat it as evolving, not as a frozen contract.", "Skills are experimental", [17]),
        ],
    ),
    (
        "05",
        "Workflows and Graphs",
        [
            ("c05-b01", "A workflow begins when more than one agent or executable node must cooperate.", "One agent is not a workflow", [4]),
            ("c05-b02", "Split when instructions get unreliable, context overflows, or you need reusable modules.", "When to split", [4]),
            ("c05-b03", "Template workflow agents are Sequential, Parallel, and Loop. They orchestrate without asking a model how to route.", "Sequential, Parallel, Loop", [12]),
            ("c05-b04", "ADK 2.0 adds graph-based workflows: nodes and edges with explicit routing for deterministic control.", "Graphs for control", [11, 14]),
            ("c05-b05", "Dynamic workflows use your own code for loops, branching, and recursion that a static graph cannot express cleanly.", "Code-driven dynamics", [11, 14]),
            ("c05-b06", "Collaborative workflows use coordinator agents and sub-agents working together.", "Coordinator plus specialists", [14]),
            ("c05-b07", "Python ADK 2.0 reached general availability on 19 May 2026.", "Python 2.0 GA date", [14]),
            ("c05-b08", "Agents, tools, and functions become nodes in the workflow graph; review breaking changes before you upgrade 1.x apps.", "Upgrade is a migration", [14]),
        ],
    ),
    (
        "06",
        "Context and Memory",
        [
            ("c06-b01", "Context is the bundle of state, artifacts, memory, and credentials available during one invocation.", "Context is the working set", [15]),
            ("c06-b02", "The framework creates InvocationContext. You rarely construct it by hand.", "Runner supplies context", [15]),
            ("c06-b03", "Session history and State cover the current thread only, such as a cart in this chat.", "State is this thread", [6]),
            ("c06-b04", "Memory is a searchable archive across past sessions or external knowledge.", "Memory is the archive", [6, 7]),
            ("c06-b05", "Memory services can ingest a session, append a delta, add facts, and search. Not every backend implements every method.", "Check backend capabilities", [7]),
            ("c06-b06", "In-memory session and memory implementations are for local testing, not production durability.", "In-memory is for tests", [6]),
            ("c06-b07", "ADK can filter irrelevant events, summarize older turns, lazy-load artifacts, and track token use.", "Compaction is built in", [1, 15]),
            ("c06-b08", "Treat context like source code: every token should earn its place.", "Every token earns its place", [1]),
        ],
    ),
    (
        "07",
        "Runtime, Deploy, Evaluate",
        [
            ("c07-b01", "Development runtimes include the CLI, the web UI, an API server, and ambient event-driven agents.", "Many ways to run", [8]),
            ("c07-b02", "The event loop is a yield, pause, and resume cycle, not a single blocking script.", "Yield, pause, resume", [8]),
            ("c07-b03", "You can resume and cancel runs; design long jobs so interruption is recoverable.", "Resume and cancel", [8]),
            ("c07-b04", "Deploy to Agent Runtime for a managed agent service, Cloud Run for containers, or GKE for Kubernetes control.", "Three Google Cloud paths", [9]),
            ("c07-b05", "You can also containerize and run anywhere Docker or Podman can run, including offline hosts.", "Deploy anywhere", [1, 9]),
            ("c07-b06", "Agent evaluation scores both the final answer and the trajectory of tool steps.", "Score path and answer", [13]),
            ("c07-b07", "Compare expected steps such as determine intent, use tool, review results, then generate the report.", "Trajectory is a checklist", [13]),
            ("c07-b08", "If you intend to leave the prototype stage, automated evaluation is a documented best practice, not optional polish.", "Evaluate before scale", [13]),
        ],
    ),
    (
        "08",
        "Safety, A2A, Production",
        [
            ("c08-b01", "Uncontrolled agents can take misaligned actions, including data exfiltration.", "Safety is a product requirement", [10]),
            ("c08-b02", "Control identity: decide whether the agent acts as itself or as the user.", "Identity and authorization", [10]),
            ("c08-b03", "Use input and output guardrails, in-tool policies, callbacks, plugins, and Gemini content filters.", "Layered guardrails", [10, 18]),
            ("c08-b04", "Sandbox model-generated code, and confine cloud activity with network controls such as VPC Service Controls.", "Sandbox and perimeter", [10]),
            ("c08-b05", "Local sub-agents organize code in-process. Remote A2A agents are separate services on a network.", "Local versus remote", [16]),
            ("c08-b06", "Use A2A when languages, teams, or standalone services must share a formal agent contract.", "A2A is the contract", [16]),
            ("c08-b07", "Do not use ADK Web in production. Authenticate to Google Cloud with ADC or a service account, never committed keys.", "Production auth, not the UI", [3, 19]),
            ("c08-b08", "Start with one LlmAgent and one tool, measure the trajectory, then add graphs, memory, and deployment from evidence.", "Pilot, measure, expand", [3, 13, 4]),
        ],
    ),
]

URLS = {
    1: "https://google.github.io/adk-docs/",
    2: "https://google.github.io/adk-docs/get-started/about/",
    3: "https://google.github.io/adk-docs/get-started/python/",
    4: "https://google.github.io/adk-docs/agents/",
    5: "https://google.github.io/adk-docs/tools-custom/",
    6: "https://google.github.io/adk-docs/sessions/",
    7: "https://google.github.io/adk-docs/sessions/memory/",
    8: "https://google.github.io/adk-docs/runtime/",
    9: "https://google.github.io/adk-docs/deploy/",
    10: "https://google.github.io/adk-docs/safety/",
    11: "https://google.github.io/adk-docs/graphs/",
    12: "https://google.github.io/adk-docs/agents/workflow-agents/",
    13: "https://google.github.io/adk-docs/evaluate/",
    14: "https://google.github.io/adk-docs/2.0/",
    15: "https://google.github.io/adk-docs/context/",
    16: "https://google.github.io/adk-docs/a2a/intro/",
    17: "https://google.github.io/adk-docs/skills/",
    18: "https://google.github.io/adk-docs/callbacks/",
    19: "https://google.github.io/adk-docs/get-started/google-cloud/",
}


def main() -> None:
    lines = []
    story_chapters = []
    for number, title, beats in CHAPTERS:
        chapter_beats = []
        for beat_id, text, visual, source_ids in beats:
            words = len(text.split())
            if not (5 <= words <= 28):
                raise SystemExit(f"word count {words} for {beat_id}: {text}")
            row = {
                "id": beat_id,
                "scene": f"chapter-{number}",
                "chapter": int(number),
                "chapter_title": title,
                "text": text,
                "visual": visual,
                "source_type": "documented",
                "source_ids": source_ids,
                "source_urls": [URLS[i] for i in source_ids],
            }
            lines.append({"id": beat_id, "scene": f"chapter-{number}", "text": text})
            chapter_beats.append(row)
        story_chapters.append({"number": int(number), "title": title, "beats": chapter_beats})

    (ROOT / "narration.json").write_text(
        json.dumps({"language": "en-IN", "speaker": "priya", "model": "bulbul:v3", "lines": lines}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    (ROOT / "storyboard.json").write_text(
        json.dumps(
            {
                "title": "Google Agent Development Kit: Complete Guide",
                "accuracy_date": "2026-09-03",
                "theme": "Google light",
                "chapters": story_chapters,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"lines={len(lines)} chapters={len(story_chapters)}")


if __name__ == "__main__":
    main()
