# Multi-Agent CV ↔ Job Matching System

This project implements a **multi-agent orchestration system** for
evaluating how well a candidate's CV matches a specific job description
and, when appropriate, generating **targeted rewrite recommendations**.

The system is built as a **decision-driven agent graph** with parallel
evaluators, centralized scoring, conditional routing, and optional
human-in-the-loop rewriting.

It is designed as a **product-style GenAI system**, not a simple prompt
chain.

------------------------------------------------------------------------

## Core Idea

Input: - CV (PDF / DOCX / TXT) - Job description (plain text)

Output: - Match score (0--100) - Structured explanation: - what fits
well - what is missing or weak - Recommendation: - no rewrite needed -
rewrite recommended - position not relevant - Optional: - fully rebuilt
CV aligned to the target role

The system separates **evaluation, decision-making, and generation**
into independent agents.

------------------------------------------------------------------------

## System Architecture Overview

1.  **Text Ingestion**
    -   CV and job description are converted into clean, normalized
        text.
2.  **Structured Extraction**
    -   Both texts are converted into validated structured objects:
        -   `CVDescription`
        -   `JobDescription`
3.  **Parallel Evaluation (Multi-Agent)** Independent agents analyze
    different alignment dimensions at the same time:
    -   hard qualification requirements
    -   technical skills
    -   domain relevance
    -   seniority and experience level
    -   wording and positioning quality
4.  **Centralized Scoring** A dedicated scoring agent:
    -   aggregates all evaluation signals
    -   computes the final match score
    -   generates a structured explanation
5.  **Decision Routing** A decision agent determines whether:
    -   the CV is already a strong match
    -   a rewrite is recommended
    -   the position is not relevant
6.  **Conditional Rewrite (Optional)** If the user approves rewriting:
    -   only weak sections are rewritten
    -   the full CV is reassembled into a consistent updated version

------------------------------------------------------------------------

## Why This Is a True Multi-Agent System

-   Each agent has a **single, narrow responsibility**
-   Agents operate **in parallel on shared structured state**
-   A centralized agent performs **final aggregation**
-   A separate decision node performs **routing**
-   The rewrite flow is **conditionally activated**
-   The system supports **human-in-the-loop control**

This ensures: - explainable decisions - controlled generation - no
"black-box" end-to-end prompting

------------------------------------------------------------------------

## Agents Overview

-   Ingest Agent\
    Converts files into clean text.

-   Structuring Agent\
    Extracts structured objects from text.

-   Qualification Match Agent\
    Evaluates hard job requirements.

-   Skills Match Agent\
    Evaluates technical stack alignment.

-   Domain Match Agent\
    Evaluates industry relevance.

-   Seniority Match Agent\
    Evaluates experience level.

-   Wording Match Agent\
    Evaluates clarity and role positioning.

-   Scoring Agent\
    Aggregates all evaluations into a final score and explanation.

-   Decision Agent\
    Decides whether a rewrite is recommended.

-   Rewrite Agent\
    Rewrites only weak CV sections.

-   CV Assembly Agent\
    Rebuilds a consistent final CV.

------------------------------------------------------------------------

## Orchestration Graph

``` mermaid
graph TD

A[User Uploads CV + Job] --> B[Ingest Agent]
B --> C[Structuring Agent]

C --> D1[Qualification Match Agent]
C --> D2[Skills Match Agent]
C --> D3[Domain Match Agent]
C --> D4[Seniority Match Agent]
C --> D5[Wording Match Agent]

D1 --> E[Scoring Agent]
D2 --> E
D3 --> E
D4 --> E
D5 --> E

E --> F[Decision Agent]

F -->|Strong Match| G[Final Report]
F -->|Not Relevant| G
F -->|Rewrite Recommended| H[Rewrite Agent]

H --> I[CV Assembly Agent]
I --> G
```

------------------------------------------------------------------------

## Key Properties

-   Deterministic decision flow
-   Explainable scoring
-   Modular agent design
-   Parallel evaluation
-   No unnecessary full-CV rewriting
-   Human-controlled rewrite activation

------------------------------------------------------------------------

## Technology Direction

The system is designed to be implemented using: - agent orchestration
graph - structured extraction - schema-validated state - centralized
scoring and conditional routing

Exact implementation details are intentionally decoupled from this
high-level design.

------------------------------------------------------------------------

## Project Status

This repository focuses on: - multi-agent orchestration logic -
decision-driven CV alignment - explainable AI evaluation - safe
controlled rewriting
