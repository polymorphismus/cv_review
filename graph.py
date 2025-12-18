from langgraph.graph import StateGraph, START, END
from functools import partial
from match_evaluation.agent_state import AgentState
from match_evaluation.evaluation_graph import build_evaluation_graph, run_evaluation_flow
from extracting_data.extraction_graph import build_extraction_graph, run_extraction_flow
from improvement_suggestions.improvement_graph import build_rewrite_graph, run_rewrite_flow
from improvement_suggestions.improvement_functions import prompt_user_to_cv_rewrite


def build_graph(llm) -> StateGraph:
    builder = StateGraph(AgentState)

    extraction_graph = build_extraction_graph(llm)
    evaluation_graph = build_evaluation_graph(llm)
    rewrite_graph = build_rewrite_graph(llm)

    builder.add_node(
        "run_extraction_flow",
        partial(run_extraction_flow, llm=llm, extraction_graph=extraction_graph),
    )
    builder.add_node(
        "run_evaluation_flow",
        partial(run_evaluation_flow, llm=llm, evaluation_graph=evaluation_graph),
    )
    builder.add_node(
        "run_rewrite_flow",
        partial(run_rewrite_flow, llm=llm, rewrite_graph=rewrite_graph),
    )
    builder.add_edge(START, "run_extraction_flow")
    builder.add_edge("run_extraction_flow", "run_evaluation_flow")
    builder.add_conditional_edges(
        "run_evaluation_flow",prompt_user_to_cv_rewrite,
        {"rewrite": "run_rewrite_flow", "finish": END},
    )
    builder.add_edge("run_rewrite_flow", END)

    return builder.compile()
