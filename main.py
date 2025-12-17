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
    cv_path = '/Users/lisapolotskaia/Downloads/lisa_polotckaia_cv.pdf'
    job_description_path = '/Users/lisapolotskaia/Downloads/job_description_ds.txt'
    result = graph.invoke({'path_to_cv': cv_path, 
                            'path_to_job': job_description_path}, config=RunnableConfig(checkpointer=MemorySaver()))