# Google Agent Development Kit — Research Notes

Live check: 2026-09-03. Scope: first-party ADK documentation at google.github.io/adk-docs.

## Product
ADK is an open-source framework for building, debugging, and deploying production agents in Python, TypeScript, Go, Java, and Kotlin.[1]
The documented positioning is to build production agents, not prototypes.[1]
Core primitives include Agent, Tool, Callback, Session, State, Memory, Artifact, Event, and Runner.[2]

## Build and run
Python requires 3.10+, then pip install google-adk, adk create, a root_agent in agent.py, adk run, and adk web.[3]
ADK Web is for development and debugging, not production deployments.[3]

## Tools, workflows, 2.0
Tools execute developer-defined logic; the model selects and invokes them.[5]
Template workflows are Sequential, Parallel, and Loop.[12]
ADK 2.0 adds graph, dynamic, and collaborative workflows. Python 2.0 GA is 19 May 2026.[14]

## Context, deploy, safety
Session State is the current thread; Memory is a long-term searchable archive.[6][7]
Deploy to Agent Runtime, Cloud Run, GKE, or any container host.[9]
Evaluate both trajectory and final response.[13]
Safety includes identity, guardrails, callbacks, sandboxes, and VPC-SC.[10]
A2A is for remote agent-to-agent contracts; local sub-agents stay in-process.[16]
Skills are experimental.[17]

## Sources

[1] https://google.github.io/adk-docs
[2] https://google.github.io/adk-docs/get-started/about
[3] https://google.github.io/adk-docs/get-started/python
[5] https://google.github.io/adk-docs/tools-custom
[6] https://google.github.io/adk-docs/sessions
[7] https://google.github.io/adk-docs/sessions/memory
[9] https://google.github.io/adk-docs/deploy
[10] https://google.github.io/adk-docs/safety
[12] https://google.github.io/adk-docs/agents/workflow-agents
[13] https://google.github.io/adk-docs/evaluate
[14] https://google.github.io/adk-docs/2.0
[16] https://google.github.io/adk-docs/a2a/intro
[17] https://google.github.io/adk-docs/skills
