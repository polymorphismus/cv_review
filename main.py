from graph import build_graph
from langchain_openai import ChatOpenAI
import os
from consts import MODEL_NAME
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
load_dotenv() 

if __name__ == "__main__":
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0, api_key=os.environ["NEBIUS_API_KEY"], base_url=os.environ["NEBIUS_BASE_URL"]) 
    graph = build_graph(llm)
    result = graph.invoke({}, config=RunnableConfig(checkpointer=MemorySaver()))
    print('Done')