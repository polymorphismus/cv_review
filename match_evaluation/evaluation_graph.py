from langgraph.graph import StateGraph, START, END
from functools import partial
from match_evaluation.agent_state import AgentState
from match_evaluation.parallel_execution import * 
from extracting_data.extraction_functions import *

def build_evaluation_graph(llm) -> StateGraph:
    g = StateGraph(AgentState)
    g.add_node("qualification_match", partial(qualification_match_agent_sync, llm=llm))
    g.add_node("skills_match", partial(skills_match_agent_sync, llm=llm))
    g.add_node("domain_match", partial(domain_match_agent_sync, llm=llm))
    g.add_node("seniority_match", partial(seniority_match_agent_sync, llm=llm))
    g.add_node("recency_relevance", partial(recency_relevance_agent_sync, llm=llm))
    g.add_node("requirements_coverage", partial(requirements_coverage_agent_sync, llm=llm))
    g.add_node("keyword_match", partial(keyword_macth_agent_sync, llm=llm))
    g.add_node("weight_generation", partial(weight_generation_agent_sync, llm=llm))
    g.add_node("scoring", partial(scoring_agent_sync, llm=llm))

    # fan-out from START is OK
    for node in [
        "qualification_match", "skills_match", "domain_match",
        "seniority_match", "recency_relevance",
        "requirements_coverage", "keyword_match",
    ]:
        g.add_edge(START, node)
        g.add_edge(node, "weight_generation")

    g.add_edge("weight_generation", "scoring")
    g.add_edge("scoring", END)
    return g.compile()


def run_evaluation_flow(state: AgentState, llm, evaluation_graph):
    return evaluation_graph.invoke(state)
