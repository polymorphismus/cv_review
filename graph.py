from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.config import RunnableConfig
from functools import partial
from match_evaluation.agent_state import AgentState
from extracting_data.description_schemas import CVDescription, JobDescription
from match_evaluation.parallel_execution import * 
from extracting_data.receive_text_from_documents import ReadDocuments
from extracting_data.profile_extraction import trustcall_extract_text_to_schema
from extracting_data.consts import JOB_DESCRIPTION, CV

def access_data(state: AgentState, llm):
    """Read CV and job description documents"""
    if state.path_to_cv is not None:
        cv_description_text = ReadDocuments(doc_input = state.path_to_cv, document_topic=CV).full_desciption_text
    else:
        cv_description_text = ReadDocuments(document_topic=CV).full_desciption_text
    
    if state.path_to_job is not None:
        job_description_text = ReadDocuments(doc_input = state.path_to_job, document_topic=JOB_DESCRIPTION).full_desciption_text
    else:
        job_description_text = ReadDocuments(document_topic=JOB_DESCRIPTION).full_desciption_text
    return {
        'cv_description_text': cv_description_text,
        'job_description_text': job_description_text,
    }

def extract_job_to_profile(state: AgentState, llm):
    """Extract job description to structured format"""
    result = trustcall_extract_text_to_schema(state.job_description_text, JobDescription, llm)
    return {'job': result}
    
def extract_cv_to_profile(state: AgentState, llm):
    """Extract CV to structured format"""
    result = trustcall_extract_text_to_schema(state.cv_description_text, CVDescription, llm)
    return {'cv': result}

def join_extraction(state: AgentState, llm):
    """Join node - waits for both extractions to complete"""
    return {}


def build_graph(llm) -> StateGraph:
    """Build the evaluation graph with parallel execution"""
    builder = StateGraph(AgentState)

    # Add data access and extraction nodes
    builder.add_node("access_data", partial(access_data, llm=llm))
    builder.add_node("extract_job_to_profile", partial(extract_job_to_profile, llm=llm))
    builder.add_node("extract_cv_to_profile", partial(extract_cv_to_profile, llm=llm))
    builder.add_node("join_extraction", partial(join_extraction, llm=llm))

    # Add evaluation nodes directly using the agent functions
    builder.add_node("qualification_match", partial(qualification_match_agent_sync, llm=llm))
    builder.add_node("skills_match", partial(skills_match_agent_sync, llm=llm))
    builder.add_node("domain_match", partial(domain_match_agent_sync, llm=llm))
    builder.add_node("seniority_match", partial(seniority_match_agent_sync, llm=llm))
    builder.add_node("wording_match", partial(wording_match_agent_sync, llm=llm))
    builder.add_node("recency_relevance", partial(recency_relevance_agent_sync, llm=llm))
    builder.add_node("requirements_coverage", partial(requirements_coverage_agent_sync, llm=llm))
    
    builder.add_node("scoring", partial(scoring_agent_sync, llm=llm))

    builder.add_edge(START, "access_data")
    
    builder.add_edge("access_data", "extract_job_to_profile")
    builder.add_edge("access_data", "extract_cv_to_profile")
    
    builder.add_edge("extract_job_to_profile", "join_extraction")
    builder.add_edge("extract_cv_to_profile", "join_extraction")

    evaluation_nodes = [
        "qualification_match", "skills_match", "domain_match", "seniority_match",
        "wording_match", "recency_relevance", "requirements_coverage"
    ]
    
    for node in evaluation_nodes:
        builder.add_edge("join_extraction", node)
        builder.add_edge(node, "scoring")

    builder.add_edge("scoring", END)

    return builder.compile()