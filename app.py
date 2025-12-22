import os
import io
import contextlib
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
INITIAL_MESSAGE = {
    "role": "assistant",
    "content": "Provide your CV and the target job description. You can paste text, upload a file, or share a link.",
}


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


class StreamlitProgressLogger(io.StringIO):
    """
    Captures stdout prints from background execution without calling Streamlit
    from worker threads. Render with `render(placeholder)` on the main thread.
    """

    def __init__(self):
        super().__init__()
        self.steps = []

    def write(self, s):
        for raw_line in s.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if self.steps and self.steps[-1]["status"] == "running":
                self.steps[-1]["status"] = "done"
            self.steps.append({"text": line, "status": "running"})
        return len(s)

    def finish(self):
        if self.steps and self.steps[-1]["status"] == "running":
            self.steps[-1]["status"] = "done"

    def render(self, placeholder):
        with placeholder.container():
            st.markdown("### Assesing match between CV and position")
            for step in self.steps:
                icon = "✅" if step["status"] == "done" else "⏳"
                st.markdown(f"{icon} {step['text']}")


def render_steps(title, steps, placeholder):
    with placeholder.container():
        st.markdown(f"<h2 style='margin-bottom:0'>{title}</h2>", unsafe_allow_html=True)
        for step in steps:
            icon = "✅" if step["status"] == "done" else "⏳"
            st.markdown(f"{icon} {step['text']}")


def render_evaluation_results(state: AgentState):
    st.subheader("Match Assessment")
    top_score = _get(state, "weighted_score")
    final_scoring = _get(state, "final_scoring")
    decision = _get(final_scoring, "decision", "N/A")
    recommendation = _get(final_scoring, "recommendation", "")

    st.metric("Decision", decision)

    if recommendation:
        st.info(recommendation)

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
        with st.expander(f"{title}"):
            st.markdown(reasoning)
            red_flags = _get(result, "red_flags", [])
            if red_flags:
                if red_flags:
                    st.warning("Red flags: " + "; ".join(red_flags))

        # After keyword match, show focus areas dropdown if available
        if title == "Keyword match":
            focus_areas = _get(state, "focus_areas", []) or _get(final_scoring, "focus_areas", [])
            if focus_areas:
                with st.expander("Focus areas / recommendations"):
                    st.markdown("\n".join(f"- {fa}" for fa in focus_areas))


def render_rewrite_section(agent_state: AgentState, llm):
    st.subheader("Updated CV")
    if isinstance(agent_state, dict):
        try:
            agent_state = AgentState.model_validate(agent_state)
        except Exception:
            pass
    # Only block if core profiles are missing; other signals are helpful but not strictly required
    if not getattr(agent_state, "cv", None) or not getattr(agent_state, "job", None):
        st.info("Complete an assessment before rewriting.")
        return
    rewrite_state = st.session_state.get("rewrite_state")
    if st.session_state.get("rewrite_running"):
        st.info("CV rewrite in progress...")

    # Initialize download state flags
    if "docx_ready" not in st.session_state:
        st.session_state.docx_ready = False
    if "docx_downloaded" not in st.session_state:
        st.session_state.docx_downloaded = False
    if "download_requested" not in st.session_state:
        st.session_state.download_requested = False

    if rewrite_state is None:
        if st.button("Rewrite my CV to fit this job"):
            st.session_state.rewrite_running = True
            try:
                with st.spinner("Generating rewritten CV..."):
                    rewrite_state = create_rewrite_state(agent_state, llm)
                    updates = rewrite_cv_initial(rewrite_state, llm)
                    rewrite_state = rewrite_state.model_copy(update=updates)
                    st.session_state.rewrite_state = rewrite_state
                    st.session_state.docx_ready = False
                    st.session_state.docx_downloaded = False
                    st.session_state.docx_path = None
            finally:
                st.session_state.rewrite_running = False
            add_message("assistant", "CV draft is ready")
            st.rerun()
        return

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
                st.session_state.rewrite_running = True
                try:
                    with st.spinner("Updating CV with feedback..."):
                        rewrite_state.user_feedback = feedback.strip()
                        updates = rewrite_cv_with_feedback(rewrite_state, llm)
                        rewrite_state = rewrite_state.model_copy(update=updates)
                        st.session_state.rewrite_state = rewrite_state
                        st.session_state.docx_ready = False
                        st.session_state.docx_downloaded = False
                        st.session_state.docx_path = None
                finally:
                    st.session_state.rewrite_running = False
                add_message("assistant", "Updated the CV based on your feedback")
                st.rerun()
    else:
        st.info("Feedback limit reached.")

    # Handle download flow
    if st.session_state.download_requested or (not st.session_state.docx_ready and rewrite_state.updated_cv_text):
        with st.spinner("Preparing CV as doc..."):
            doc_info = markdown_to_docx(rewrite_state, llm)
            st.session_state.docx_path = doc_info.get("docx_path")
        st.session_state.docx_ready = True
        st.session_state.download_requested = False

    docx_path = st.session_state.get("docx_path")
    if docx_path and Path(docx_path).exists():
        with open(docx_path, "rb") as f:
            clicked = st.download_button(
                "Download updated CV" if not st.session_state.docx_downloaded else "Current version of CV downloaded",
                f,
                file_name=Path(docx_path).name or UPDATED_CV_NAME,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                disabled=st.session_state.docx_downloaded,
                key="download_cv_button",
                use_container_width=True,
            )
            if clicked:
                st.session_state.docx_downloaded = True
                st.rerun()
            if st.session_state.docx_downloaded:
                st.markdown(
                    """
                    <style>
                    div[data-testid="stDownloadButton"][key="download_cv_button"] button {
                        background-color: #1b4332 !important;
                        color: #ffffff !important;
                        border: 1px solid #1b4332 !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        if st.button("Download updated CV", use_container_width=True, key="download_request_btn"):
            st.session_state.download_requested = True
            st.session_state.docx_downloaded = False
            st.rerun()


def main():
    st.set_page_config(page_title="CV ↔ Job Match", layout="wide")
    if "messages" not in st.session_state:
        st.session_state.messages = [INITIAL_MESSAGE.copy()]
    if "assessment_running" not in st.session_state:
        st.session_state.assessment_running = False
    if "rewrite_running" not in st.session_state:
        st.session_state.rewrite_running = False

    llm = init_llm()
    init_graphs(llm)

    # Sticky sidebar on the right column with scrollable messages
    st.markdown(
        """
        <style>
        .sidebar-inner {
            position: sticky;
            top: 0.5rem;
            max-height: calc(100vh - 1rem);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .scroll-messages {
            flex: 1;
            overflow-y: auto;
            padding-right: 4px;
        }
        .download-complete button {
            background-color: #1b4332 !important;
            color: #ffffff !important;
            border: 1px solid #1b4332 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_main, col_sidebar = st.columns([0.72, 0.28], gap="large")
    progress_placeholder = col_main.empty()

    # Initialize persisted form fields (cache values, not widget keys)
    for key in ["cv_text", "job_text", "cv_link_cached", "job_link_cached", "path_to_cv", "path_to_job"]:
        if key not in st.session_state:
            st.session_state[key] = ""
    if "assessment_button_hidden" not in st.session_state:
        st.session_state.assessment_button_hidden = False

    def reset_inputs(clear_cv: bool, clear_job: bool, reset_messages: bool = False):
        if clear_cv:
            st.session_state.cv_text = ""
            st.session_state.cv_link_cached = ""
            st.session_state["cv_link_input"] = ""
            st.session_state.pop("path_to_cv", None)
            st.session_state.pop("cv_upload", None)
        if clear_job:
            st.session_state.job_text = ""
            st.session_state.job_link_cached = ""
            st.session_state["job_link_input"] = ""
            st.session_state.pop("path_to_job", None)
            st.session_state.pop("job_upload", None)
        for key in ["agent_state", "rewrite_state", "docx_path", "docx_ready", "docx_downloaded", "download_requested"]:
            st.session_state.pop(key, None)
        st.session_state.assessment_running = False
        st.session_state.assessment_button_hidden = False
        if reset_messages:
            st.session_state.messages = [INITIAL_MESSAGE.copy()]
        st.rerun()

    def cache_from_state(cache_cv: bool = False, cache_job: bool = False):
        state = st.session_state.get("agent_state")
        if not state:
            return
        try:
            state = AgentState.model_validate(state)
        except Exception:
            pass
        if cache_cv:
            st.session_state.cv_text = getattr(state, "cv_description_text", st.session_state.get("cv_text", ""))
            st.session_state.path_to_cv = getattr(state, "path_to_cv", st.session_state.get("path_to_cv"))
            st.session_state.cv_link_cached = st.session_state.path_to_cv or st.session_state.get("cv_link_cached", "")
        if cache_job:
            st.session_state.job_text = getattr(state, "job_description_text", st.session_state.get("job_text", ""))
            st.session_state.path_to_job = getattr(state, "path_to_job", st.session_state.get("path_to_job"))
            st.session_state.job_link_cached = st.session_state.path_to_job or st.session_state.get("job_link_cached", "")

    def reset_for_another_position():
        cache_from_state(cache_cv=True, cache_job=False)
        reset_inputs(clear_cv=False, clear_job=True, reset_messages=False)

    def reset_for_another_cv():
        cache_from_state(cache_cv=False, cache_job=True)
        reset_inputs(clear_cv=True, clear_job=False, reset_messages=False)

    def reset_for_new_assessment():
        reset_inputs(clear_cv=True, clear_job=True, reset_messages=True)

    with col_sidebar:
        with st.container():
            st.markdown('<div class="sidebar-inner">', unsafe_allow_html=True)
            if st.button("Assess with another position", use_container_width=True, key="btn_another_position"):
                reset_for_another_position()
            if st.button("Assess with another CV", use_container_width=True, key="btn_another_cv"):
                reset_for_another_cv()
            if st.button("New assessment", use_container_width=True, key="btn_new_assessment"):
                reset_for_new_assessment()
            st.divider()
            st.markdown('<div class="scroll-messages">', unsafe_allow_html=True)
            render_messages()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # If results exist, make sure any running flag is cleared so status banners vanish
    if st.session_state.get("agent_state") and st.session_state.assessment_running:
        st.session_state.assessment_running = False
        st.session_state.assessment_button_hidden = False

    show_form = (
        not st.session_state.assessment_running
        and not st.session_state.get("agent_state")
        and not st.session_state.assessment_button_hidden
    )

    if show_form:
        form_placeholder = col_main.empty()
        with form_placeholder.container():
            st.markdown("### Provide documents")
            col_cv, col_job = st.columns(2)
            with col_cv:
                st.markdown("**CV**: choose option to provide it below")
                cv_text = st.text_area("Paste CV text", height=200, key="cv_text")
                cv_upload = st.file_uploader("Upload CV file (.pdf, .docx, .txt)", key="cv_upload")
                cv_link = st.text_input(
                    "CV link or local path",
                    value=st.session_state.get("cv_link_cached", ""),
                    key="cv_link_input",
                )
            with col_job:
                st.markdown("**Job description**: choose option to provide it below")
                job_text = st.text_area("Paste job description text", height=200, key="job_text")
                job_upload = st.file_uploader("Upload job description file (.pdf, .docx, .txt)", key="job_upload")
                job_link = st.text_input(
                    "Job link or local path",
                    value=st.session_state.get("job_link_cached", ""),
                    key="job_link_input",
                )
            run_btn_placeholder = st.empty()

        if run_btn_placeholder.button("Run match assessment"):
            st.session_state.assessment_running = True
            st.session_state.assessment_button_hidden = True
            form_placeholder.empty()
            run_btn_placeholder.empty()
            add_message("assistant", "Running extraction and evaluation...")
            extraction_steps = [
                {"text": "Extracting job information...", "status": "running"},
                {"text": "Extracting CV information...", "status": "running"},
            ]
            evaluation_steps = [
                {"text": "Assessing domain...", "status": "pending"},
                {"text": "Assessing keyword match...", "status": "pending"},
                {"text": "Assessing qualification...", "status": "pending"},
                {"text": "Assessing relevance...", "status": "pending"},
                {"text": "Assessing requirements coverage...", "status": "pending"},
                {"text": "Assessing seniority...", "status": "pending"},
                {"text": "Assessing skills...", "status": "pending"},
                {"text": "Weighting scores based on importance", "status": "pending"},
            ]
            render_steps("<span style='font-size:28px'>Running assessment...</span>", extraction_steps + evaluation_steps, progress_placeholder)
            try:
                cv_desc, cv_path = prepare_document(CV, cv_text, cv_link, cv_upload, llm)
                job_desc, job_path = prepare_document(JOB_DESCRIPTION, job_text, job_link, job_upload, llm)
                st.session_state.path_to_cv = cv_path
                st.session_state.path_to_job = job_path
                if cv_path:
                    st.session_state.cv_link_cached = cv_path
                if job_path:
                    st.session_state.job_link_cached = job_path

                if not cv_desc or not job_desc:
                    st.error("Please provide both CV and job description (text, file, or link).")
                    st.session_state.assessment_running = False
                    st.session_state.assessment_button_hidden = False
                else:
                    base_state = AgentState(
                        path_to_cv=cv_path,
                        path_to_job=job_path,
                        cv_description_text=cv_desc,
                        job_description_text=job_desc,
                    )
                    render_steps("<span style='font-size:28px'>Running assessment...</span>", extraction_steps + evaluation_steps, progress_placeholder)
                    extracted_state = run_extraction_flow(
                        base_state, llm=llm, extraction_graph=st.session_state.extraction_graph
                    )
                    for step in extraction_steps:
                        step["status"] = "done"
                    for step in evaluation_steps:
                        step["status"] = "running"
                    render_steps("<span style='font-size:28px'>Running assessment...</span>", extraction_steps + evaluation_steps, progress_placeholder)
                    evaluated_state = run_evaluation_flow(
                        extracted_state, llm=llm, evaluation_graph=st.session_state.evaluation_graph
                    )
                    for step in evaluation_steps:
                        step["status"] = "done"
                    render_steps("<span style='font-size:28px'>Running assessment...</span>", extraction_steps + evaluation_steps, progress_placeholder)
                    try:
                        evaluated_state = AgentState.model_validate(evaluated_state)
                    except Exception:
                        pass
                    st.session_state.agent_state = evaluated_state
                    st.session_state.rewrite_state = None
                    st.session_state.docx_path = None
                    st.session_state.assessment_running = False
                    add_message("assistant", "Match assessment complete")
                    st.rerun()
            except Exception:
                st.session_state.assessment_running = False
                st.session_state.assessment_button_hidden = False
    elif st.session_state.assessment_running and not st.session_state.get("agent_state"):
        with col_main:
            st.info("Running assessment...")
    else:
        progress_placeholder.empty()

    if "agent_state" in st.session_state:
        progress_placeholder.empty()
        with col_main:
            render_evaluation_results(st.session_state.agent_state)
            render_rewrite_section(st.session_state.agent_state, llm)


if __name__ == "__main__":
    main()
