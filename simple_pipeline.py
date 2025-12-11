from extracting_data.receive_text_from_documents import ReadDocuments
from extracting_data.profile_extraction import trustcall_extract_text_to_schema
from extracting_data.consts import JOB_DESCRIPTION, CV
from extracting_data.description_schemas import CVDescription, JobDescription
from langchain_openai import ChatOpenAI
import os
import json
from pathlib import Path

def save_profile(model_obj, path: str):
    path = Path(path)
    path.write_text(model_obj.model_dump_json(indent=2))

def loac_profile(schema_class, path: str):
    data = Path(path).read_text()
    return schema_class.model_validate_json(data)

if __name__ == '__main__':
    cv_path = '/Users/lisapolotskaia/Documents/CVs/round_2/base_cv_ds.pdf'
    job_description_path = '/Users/lisapolotskaia/Downloads/Co Founder Head of AI PigO.pdf' 
    cv_description_text = ReadDocuments(cv_path, CV).full_desciption_text
    job_description_text = ReadDocuments(job_description_path, JOB_DESCRIPTION).full_desciption_text
    llm = ChatOpenAI(model="openai/gpt-oss-120b", temperature=0, api_key=os.environ["NEBIUS_API_KEY"], base_url=os.environ["NEBIUS_BASE_URL"]) 
    job_profile = trustcall_extract_text_to_schema(job_description_text, JobDescription, llm)
    cv_profile = trustcall_extract_text_to_schema(cv_description_text, CVDescription, llm)
    save_profile(job_profile, '/Users/lisapolotskaia/Documents/CVs/round_2/job_profile.json')
    save_profile(cv_profile, '/Users/lisapolotskaia/Documents/CVs/round_2/cv_profile.json')

    