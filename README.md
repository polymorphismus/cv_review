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
    -   recency and relevance of experience
    -   requirements coverage (must-haves/nice-to-haves)
    -   ATS keyword match
4.  **Weight Generation** A dedicated agent produces dynamic weights
    based on the role type and requirements.
5.  **Centralized Scoring** A dedicated scoring agent:
    -   aggregates all evaluation signals
    -   computes the final match score
    -   generates a structured explanation and recommendation
6.  **Decision Routing** The user is prompted to decide whether to
    rewrite the CV.
7.  **Conditional Rewrite (Optional)** If the user approves rewriting:
    -   an optimized CV is generated
    -   a feedback loop refines the output
    -   a DOCX is exported at the end

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

-   Structuring Agents\
    Extract structured objects from text.

-   Qualification Match Agent\
    Evaluates hard job requirements.

-   Skills Match Agent\
    Evaluates technical stack alignment.

-   Domain Match Agent\
    Evaluates industry relevance.

-   Seniority Match Agent\
    Evaluates experience level.

-   Recency/Relevance Agent\
    Evaluates how current the experience is.

-   Requirements Coverage Agent\
    Evaluates must-haves and nice-to-haves coverage.

-   Keyword Match Agent\
    Evaluates ATS keyword alignment.

-   Weight Generation Agent\
    Produces dynamic weights per role.

-   Scoring Agent\
    Aggregates all evaluations into a final score and explanation.

-   Rewrite Flow\
    Builds an optimized CV with optional feedback loop and DOCX export.

------------------------------------------------------------------------

## Orchestration Graph

``` mermaid
graph TD

A[User Uploads CV + Job] --> B[Ingest Agent]
B --> C1[Extract Job Profile]
B --> C2[Extract CV Profile]
C1 --> D[Join Extraction]
C2 --> D

D --> E1[Qualification Match]
D --> E2[Skills Match]
D --> E3[Domain Match]
D --> E4[Seniority Match]
D --> E5[Recency/Relevance]
D --> E6[Requirements Coverage]
D --> E7[Keyword Match]

E1 --> F[Weight Generation]
E2 --> F
E3 --> F
E4 --> F
E5 --> F
E6 --> F
E7 --> F

F --> G[Scoring]

G --> H[User Prompt: Rewrite?]
H -->|No| Z[Final Report]
H -->|Yes| I[Create Rewrite State]
I --> J[Rewrite CV Initial]
J --> K{User Satisfied?}
K -->|Yes| L[Markdown → DOCX]
K -->|No| M[Receive Feedback]
M --> N[Rewrite with Feedback]
N --> K
L --> Z
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

For an interactive experience, you can also run the Streamlit app in
`cv_agent/app.py` to upload/paste a CV and job description, assess the
match, and optionally rewrite/download the CV.
