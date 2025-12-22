from match_evaluation.agent_state import AgentState
from extracting_data.description_schemas import CVDescription, JobDescription
from extracting_data.receive_text_from_documents import ReadDocuments
from extracting_data.profile_extraction import trustcall_extract_text_to_schema
from extracting_data.extracting_consts import JOB_DESCRIPTION, CV


def access_data(state: AgentState, llm):
    """Read CV and job description documents"""
    if state.cv_description_text:
        cv_description_text = state.cv_description_text
    elif state.path_to_cv is not None:
        cv_description_text = ReadDocuments(
            doc_input=state.path_to_cv, llm=llm, document_topic=CV
        ).full_desciption_text
    else:
        cv_description_text = ReadDocuments(document_topic=CV).full_desciption_text

    if state.job_description_text:
        job_description_text = state.job_description_text
    elif state.path_to_job is not None:
        job_description_text = ReadDocuments(
            doc_input=state.path_to_job, llm=llm, document_topic=JOB_DESCRIPTION
        ).full_desciption_text
    else:
        job_description_text = ReadDocuments(
            document_topic=JOB_DESCRIPTION
        ).full_desciption_text
    return {
        "cv_description_text": cv_description_text,
        "job_description_text": job_description_text,
    }


def extract_job_to_profile(state: AgentState, llm):
    print("Extracting job information...")
    """Extract job description to structured format"""
    result = trustcall_extract_text_to_schema(
        state.job_description_text, JobDescription, llm
    )
    return {"job": result}


def extract_cv_to_profile(state: AgentState, llm):
    """Extract CV to structured format"""
    print("Extracting CV information...")
    result = trustcall_extract_text_to_schema(
        state.cv_description_text, CVDescription, llm
    )
    return {"cv": result}


def join_extraction(state: AgentState, llm):
    """Join node - waits for both extractions to complete"""
    return {}
