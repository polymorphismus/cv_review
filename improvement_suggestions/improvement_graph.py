from improvement_suggestions.improvement_functions import *
from improvement_suggestions.improvement_state import CVRewriteState
from langgraph.graph import StateGraph, START, END
from functools import partial
from match_evaluation.agent_state import AgentState
from match_evaluation.parallel_execution import *
from improvement_suggestions.improvement_functions import *


def build_rewrite_graph(llm) -> StateGraph:
    """Build the CV rewrite subgraph with a dedicated state type."""
    builder = StateGraph(CVRewriteState)

    builder.add_node("rewrite_cv_initial", partial(rewrite_cv_initial, llm=llm))
    builder.add_node("receive_user_feedback", partial(receive_user_feedback, llm=llm))
    builder.add_node(
        "rewrite_cv_with_feedback", partial(rewrite_cv_with_feedback, llm=llm)
    )
    builder.add_node("markdown_to_docx", partial(markdown_to_docx, llm=llm))

    builder.add_edge(START, "rewrite_cv_initial")
    builder.add_conditional_edges(
        "rewrite_cv_initial",
        prompt_user_satisfaction,
        {
            "no change": "markdown_to_docx",
            "change needed": "receive_user_feedback",
        },
    )
    builder.add_edge("receive_user_feedback", "rewrite_cv_with_feedback")
    builder.add_conditional_edges(
        "rewrite_cv_with_feedback",
        prompt_user_satisfaction,
        {
            "no change": "markdown_to_docx",
            "change needed": "receive_user_feedback",
        },
    )
    builder.add_edge("markdown_to_docx", END)

    return builder.compile()


def run_rewrite_flow(state: AgentState, llm, rewrite_graph):
    rewrite_state = create_rewrite_state(state, llm)
    rewrite_graph.invoke(rewrite_state)
    return {}
