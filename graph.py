from langgraph.graph import StateGraph, START, END
from functools import partial
from match_evaluation.agent_state import AgentState
from match_evaluation.parallel_execution import * 
from extracting_data.extraction_functions import *
from improvement_suggestions.improvement_functions import *
from improvement_suggestions.improvement_graph import *

def build_graph(llm) -> StateGraph:
    """Build the evaluation graph with parallel execution"""
    builder = StateGraph(AgentState)

    # ---- Data access nodes ----
    builder.add_node("access_data", partial(access_data, llm=llm))
    builder.add_node("extract_job_to_profile", partial(extract_job_to_profile, llm=llm))
    builder.add_node("extract_cv_to_profile", partial(extract_cv_to_profile, llm=llm))
    builder.add_node("join_extraction", partial(join_extraction, llm=llm))

    # ---- Evaluation nodes ----
    builder.add_node("qualification_match", partial(qualification_match_agent_sync, llm=llm))
    builder.add_node("skills_match", partial(skills_match_agent_sync, llm=llm))
    builder.add_node("domain_match", partial(domain_match_agent_sync, llm=llm))
    builder.add_node("seniority_match", partial(seniority_match_agent_sync, llm=llm))
    builder.add_node("recency_relevance", partial(recency_relevance_agent_sync, llm=llm))
    builder.add_node("requirements_coverage", partial(requirements_coverage_agent_sync, llm=llm))
    builder.add_node("keyword_match", partial(keyword_macth_agent_sync, llm=llm))
    builder.add_node("weight_generation", partial(weight_generation_agent_sync, llm=llm))

    builder.add_node("scoring", partial(scoring_agent_sync, llm=llm))
    builder.add_node(
        "run_rewrite_flow",
        partial(run_rewrite_flow, llm=llm),
    )


    builder.add_edge(START, "access_data")
    
    builder.add_edge("access_data", "extract_job_to_profile")
    builder.add_edge("access_data", "extract_cv_to_profile")
    
    builder.add_edge("extract_job_to_profile", "join_extraction")
    builder.add_edge("extract_cv_to_profile", "join_extraction")

    evaluation_nodes = [
        "qualification_match", "skills_match", "domain_match", "seniority_match",
       "recency_relevance", "requirements_coverage", "keyword_match"
    ]
    
    for node in evaluation_nodes:
        builder.add_edge("join_extraction", node)
        builder.add_edge(node, "weight_generation")
    builder.add_edge("weight_generation", "scoring")
    
    builder.add_conditional_edges("scoring",
        prompt_user_to_cv_rewrite,
    {
        'rewrite': "run_rewrite_flow",
        "finish": END,
    },
    )
    builder.add_edge("run_rewrite_flow", END)


    return builder.compile()