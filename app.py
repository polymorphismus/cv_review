import os
from uuid import uuid4
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from consts import MODEL_NAME
from langchain_openai import ChatOpenAI

from extracting_data.extraction_graph import build_extraction_graph, run_extraction_flow
from extracting_data.extracting_consts import JOB_DESCRIPTION, CV
from extracting_data.receive_text_from_documents import ReadDocuments
from match_evaluation.evaluation_graph import build_evaluation_graph, run_evaluation_flow
from match_evaluation.agent_state import AgentState
from improvement_suggestions.improvement_functions import (
    create_rewrite_state,
    rewrite_cv_initial,
    rewrite_cv_with_feedback,
    markdown_to_docx,
)
from improvement_suggestions.improvement_consts import UPDATED_CV_NAME, AMOUNT_FEEDBACK_ROUNDS


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR = OUTPUT_DIR / "uploads"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


def init_llm():
    if "llm" not in st.session_state:
        load_dotenv()
        st.session_state.llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=0,
            api_key=os.environ["NEBIUS_API_KEY"],
            base_url=os.environ["NEBIUS_BASE_URL"],
        )
    return st.session_state.llm


def init_graphs(llm):
    if "extraction_graph" not in st.session_state:
        st.session_state.extraction_graph = build_extraction_graph(llm)
    if "evaluation_graph" not in st.session_state:
        st.session_state.evaluation_graph = build_evaluation_graph(llm)


def add_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})


def render_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def save_upload(upload):
    file_path = UPLOAD_DIR / f"{uuid4().hex}_{upload.name}"
    file_path.write_bytes(upload.getbuffer())
    return str(file_path)


def prepare_document(topic, raw_text, url_or_path, upload, llm):
    doc_input = None
    saved_path = None

    if raw_text and raw_text.strip():
        doc_input = raw_text.strip()
    elif upload is not None:
        saved_path = save_upload(upload)
        doc_input = saved_path
    elif url_or_path and url_or_path.strip():
        doc_input = url_or_path.strip()
    else:
        return None, None

    description = ReadDocuments(
        doc_input=doc_input, llm=llm, document_topic=topic
    ).full_desciption_text
    return description, saved_path


def _get(state, key, default=None):
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


def render_evaluation_results(state: AgentState):
    st.subheader("Match Assessment")
    top_score = _get(state, "weighted_score")
    final_scoring = _get(state, "final_scoring")
    decision = _get(final_scoring, "decision", "N/A")
    recommendation = _get(final_scoring, "recommendation", "")

    cols = st.columns(3)
    cols[0].metric(
        "Weighted score",
        f"{top_score:.1f}" if isinstance(top_score, float) else (top_score or "N/A"),
    )
    cols[1].metric("Decision", decision)
    cols[2].metric("Focus areas", len(_get(state, "focus_areas", []) or []))

    if recommendation:
        st.info(recommendation)

    score_breakdown = _get(state, "score_breakdown")
    if score_breakdown:
        with st.expander("Show scoring breakdown"):
            st.code(score_breakdown)

    eval_sections = [
        ("Skills", _get(state, "skills_match")),
        ("Qualification", _get(state, "qualification_match")),
        ("Seniority", _get(state, "seniority_match")),
        ("Domain", _get(state, "domain_match")),
        ("Recency / relevance", _get(state, "recency_relevance")),
        ("Requirements coverage", _get(state, "requirements_coverage")),
        ("Keyword match", _get(state, "keyword_match")),
    ]

    for title, result in eval_sections:
        if result is None:
            continue
        score = _get(result, "score", 0)
        reasoning = _get(result, "reasoning", "")
        with st.expander(f"{title}: {score:.1f} — Show reasoning"):
            st.markdown(reasoning)
            red_flags = _get(result, "red_flags", [])
            if red_flags:
                if red_flags:
                    st.warning("Red flags: " + "; ".join(red_flags))


def render_rewrite_section(agent_state: AgentState, llm):
    st.subheader("Rewrite CV")
    rewrite_state = st.session_state.get("rewrite_state")

    if rewrite_state is None:
        if st.button("Rewrite my CV to fit this job"):
            rewrite_state = create_rewrite_state(agent_state, llm)
            updates = rewrite_cv_initial(rewrite_state, llm)
            rewrite_state = rewrite_state.model_copy(update=updates)
            st.session_state.rewrite_state = rewrite_state
            add_message("assistant", "Here's a rewritten CV draft in Markdown.")
            st.rerun()
        return

    st.markdown("#### Updated CV (Markdown)")
    st.markdown(rewrite_state.updated_cv_text)

    if rewrite_state.feedback_round < AMOUNT_FEEDBACK_ROUNDS:
        feedback = st.text_area(
            "Need changes? Share feedback and I'll update it.",
            key=f"feedback_round_{rewrite_state.feedback_round}",
        )
        if st.button("Apply feedback"):
            if not feedback.strip():
                st.warning("Please add feedback before applying changes.")
            else:
                rewrite_state.user_feedback = feedback.strip()
                updates = rewrite_cv_with_feedback(rewrite_state, llm)
                rewrite_state = rewrite_state.model_copy(update=updates)
                st.session_state.rewrite_state = rewrite_state
                add_message("assistant", "Updated the CV based on your feedback.")
                st.rerun()
    else:
        st.info("Feedback limit reached.")

    if st.button("Finalize and prepare DOCX"):
        doc_info = markdown_to_docx(rewrite_state, llm)
        st.session_state.docx_path = doc_info.get("docx_path")
        add_message("assistant", "Your updated CV is ready to download.")
        st.rerun()

    docx_path = st.session_state.get("docx_path")
    if docx_path and Path(docx_path).exists():
        with open(docx_path, "rb") as f:
            st.download_button(
                "Download updated CV (DOCX)",
                f,
                file_name=Path(docx_path).name or UPDATED_CV_NAME,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


def main():
    st.set_page_config(page_title="CV ↔ Job Match", layout="wide")
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Provide your CV and the target job description. You can paste text, upload a file, or share a link.",
            }
        ]

    llm = init_llm()
    init_graphs(llm)
    render_messages()

    st.markdown("### Provide documents")
    col_cv, col_job = st.columns(2)
    with col_cv:
        st.markdown("**CV**")
        cv_text = st.text_area("Paste CV text", height=200, key="cv_text")
        cv_upload = st.file_uploader("Upload CV file (.pdf, .docx, .txt)", key="cv_upload")
        cv_link = st.text_input("CV link or local path", key="cv_link")
    with col_job:
        st.markdown("**Job description**")
        job_text = st.text_area("Paste job description text", height=200, key="job_text")
        job_upload = st.file_uploader("Upload job description file (.pdf, .docx, .txt)", key="job_upload")
        job_link = st.text_input("Job link or local path", key="job_link")

    if st.button("Run assessment"):
        cv_desc, cv_path = prepare_document(CV, cv_text, cv_link, cv_upload, llm)
        job_desc, job_path = prepare_document(JOB_DESCRIPTION, job_text, job_link, job_upload, llm)

        if not cv_desc or not job_desc:
            st.error("Please provide both CV and job description (text, file, or link).")
        else:
            add_message("assistant", "Running extraction and evaluation...")
            base_state = AgentState(
                path_to_cv=cv_path,
                path_to_job=job_path,
                cv_description_text=cv_desc,
                job_description_text=job_desc,
            )
            extracted_state = run_extraction_flow(
                base_state, llm=llm, extraction_graph=st.session_state.extraction_graph
            )
            evaluated_state = run_evaluation_flow(
                extracted_state, llm=llm, evaluation_graph=st.session_state.evaluation_graph
            )
            try:
                evaluated_state = AgentState.model_validate(evaluated_state)
            except Exception:
                pass
            st.session_state.agent_state = evaluated_state
            st.session_state.rewrite_state = None
            st.session_state.docx_path = None
            add_message("assistant", "Assessment complete. See details below.")
            st.rerun()

    if "agent_state" in st.session_state:
        render_evaluation_results(st.session_state.agent_state)
        render_rewrite_section(st.session_state.agent_state, llm)


if __name__ == "__main__":
    main()
