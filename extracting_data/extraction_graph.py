from langgraph.graph import StateGraph, START, END
from functools import partial
from extracting_data.extraction_functions import *

def build_extraction_graph(llm) -> StateGraph:
    g = StateGraph(AgentState)
    g.add_node("access_data", partial(access_data, llm=llm))
    g.add_node("extract_job_to_profile", partial(extract_job_to_profile, llm=llm))
    g.add_node("extract_cv_to_profile", partial(extract_cv_to_profile, llm=llm))
    g.add_node("join_extraction", partial(join_extraction, llm=llm))

    g.add_edge(START, "access_data")
    g.add_edge("access_data", "extract_job_to_profile")
    g.add_edge("access_data", "extract_cv_to_profile")
    g.add_edge("extract_job_to_profile", "join_extraction")
    g.add_edge("extract_cv_to_profile", "join_extraction")
    g.add_edge("join_extraction", END)
    return g.compile()

def run_extraction_flow(state: AgentState, llm, extraction_graph):
    return extraction_graph.invoke(state)
