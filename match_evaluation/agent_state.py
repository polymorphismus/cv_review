from pydantic import BaseModel
from typing import Optional
from extracting_data.description_schemas import CVDescription, JobDescription
from match_evaluation.output_schemas import *

class AgentState(BaseModel):
    path_to_cv: Optional[str] = None
    path_to_job: Optional[str] = None

    cv_description_text: Optional[str] = None
    job_description_text: Optional[str] = None
    
    cv: Optional[CVDescription] = None
    job: Optional[JobDescription] = None

    qualification_match: Optional[QualificationMatchResult] = None    
    skills_match: Optional[SkillsMatchResult] = None
    domain_match: Optional[DomainMatchResult] = None
    seniority_match: Optional[SeniorityMatchResult] = None
    wording_match: Optional[WordingMatchResult] = None
    recency_relevance: Optional[RecencyRelevanceResult] = None
    requirements_coverage: Optional[RequirementsCoverageResult] = None
    
    final_score: Optional[FinalScoringResult] = None
    decision: Optional[str] = None
    conclusion: Optional[str] = None
    focus_areas: List[str] = None
    all_red_flags: List[str] = None
    weaknesses: List[str] = None
    strengths: List[str] = None