from match_evaluation.agent_state import AgentState
from match_evaluation.output_schemas import *
from match_evaluation.agent_prompts import *

def skills_match_agent_sync(state: AgentState, llm):
    cv_skills = state.cv.technical_skills
    required_skills = state.job.required_technical_skills
    nice_to_have = state.job.nice_to_have_skills
    
    experience_skills = []
    for exp in state.cv.experience:
        experience_skills.extend(exp.technologies)
    
    result = llm.with_structured_output(SkillsMatchResult).invoke(
        SKILL_MATCH_PROMPT.format(
            required_skills=required_skills,
            nice_to_have=nice_to_have,
            cv_skills=cv_skills,
            experience_skills=experience_skills
        )
    )
    return {"skills_match": result} 



def qualification_match_agent_sync(state: AgentState, llm) -> QualificationMatchResult:
    
    cv_education = state.cv.education
    cv_certifications = state.cv.certifications
    cv_projects = state.cv.projects
    
    education_formatted = [
        f"{e.certification} in {e.field} from {e.institution} ({e.graduation_year})" 
        for e in cv_education
    ]
    
    projects_formatted = [
        f"{p.name}: {p.project_description} (Tech: {', '.join(p.technologies)})" 
        for p in cv_projects
    ]
    
    result = llm.with_structured_output(QualificationMatchResult).invoke(
        QUALIFICATION_MATCH_PROMPT.format(
            must_have_requirements=state.job.must_have_requirements,
            required_years_experience=state.job.required_years_experience,
            education_formatted=education_formatted,
            cv_certifications=cv_certifications,
            total_years_experience=state.cv.total_years_experience,
            projects_formatted=projects_formatted
        )
    )
    return {"qualification_match": result}  

def seniority_match_agent_sync(state: AgentState, llm) -> SeniorityMatchResult:
    
    cv_titles = [exp.title for exp in state.cv.experience]
    
    result = llm.with_structured_output(SeniorityMatchResult).invoke(
        SENIORITY_MATCH_PROMPT.format(
            required_years_experience=state.job.required_years_experience,
            job_title=state.job.job_title,
            total_years_experience=state.cv.total_years_experience,
            cv_titles=cv_titles,
            current_title=state.cv.current_title
        )
    )
    return {'seniority_match': result}

def domain_match_agent_sync(state: AgentState, llm) -> DomainMatchResult:
    
    cv_domains = state.cv.domains
    cv_experience_domains = [exp.domain for exp in state.cv.experience if exp.domain]
    required_domains = state.job.required_domains
    
    result = llm.with_structured_output(DomainMatchResult).invoke(
        DOMAIN_MATCH_PROMPT.format(
            required_domains=required_domains,
            company=state.job.company,
            cv_domains=cv_domains,
            cv_experience_domains=cv_experience_domains
        )
    )
    return {"domain_match" : result}

def requirements_coverage_agent_sync(state: AgentState, llm) -> RequirementsCoverageResult:
    
    must_have = state.job.must_have_requirements
    nice_to_have = state.job.nice_to_have_requirements
    
    cv_summary = {
        "skills": state.cv.technical_skills,
        "experience": [{"title": e.title, "responsibilities": e.responsibilities} for e in state.cv.experience],
        "education": [f"{e.certification} in {e.field}" for e in state.cv.education],
        "certifications": state.cv.certifications,
        "years": state.cv.total_years_experience
    }
    
    result = llm.with_structured_output(RequirementsCoverageResult).invoke(
        REQUIREMENTS_COVERAGE_PROMPT.format(
            must_have=must_have,
            nice_to_have=nice_to_have,
            cv_summary=cv_summary
        )
    )
    return {"requirements_coverage" :result}

def recency_relevance_agent_sync(state: AgentState, llm) -> RecencyRelevanceResult:
    
    experiences = state.cv.experience
    required_skills = state.job.required_technical_skills
    
    experiences_formatted = [
        f"{e.title} at {e.company} ({e.start_date} to {e.end_date}): {', '.join(e.technologies)}" 
        for e in experiences
    ]
    
    result = llm.with_structured_output(RecencyRelevanceResult).invoke(
        RECENCY_RELEVANCE_PROMPT.format(
            required_skills=required_skills,
            job_title=state.job.job_title,
            experiences_formatted=experiences_formatted
        )
    )
    return { "recency_relevance" :result}

def wording_match_agent_sync(state: AgentState, llm) -> WordingMatchResult:
    
    cv_summary = state.cv.cv_summary
    job_summary = state.job.role_summary
    cv_soft_skills = state.cv.soft_skills
    job_soft_skills = state.job.soft_skills
    
    result = llm.with_structured_output(WordingMatchResult).invoke(
        WORDING_MATCH_PROMPT.format(
            job_summary=job_summary,
            job_soft_skills=job_soft_skills,
            cv_summary=cv_summary,
            cv_soft_skills=cv_soft_skills
        )
    )
    return {"wording_match": result}


def scoring_agent_sync(state: AgentState, llm) -> FinalScoringResult:
    
    weights = {
        'skills_match': 0.25,
        'requirements_coverage': 0.20,
        'seniority_match': 0.15,
        'qualification_match': 0.12,
        'recency_relevance': 0.10,
        'domain_match': 0.10,
        'wording_match': 0.08,
    }
    final_score = 0
    for k in list(weights.keys()):
        final_score += weights[k] * getattr(state, k).score
    result = llm.with_structured_output(FinalScoringResult).invoke(
        SCORING_PROMPT.format(
            final_score=final_score,
            skills_match_score=state.skills_match.score,
            skills_match=state.skills_match.model_dump(),
            requirements_coverage_score=state.requirements_coverage.score,
            requirements_coverage=state.requirements_coverage.model_dump(),
            seniority_match_score=state.seniority_match.score,
            seniority_match=state.seniority_match.model_dump(),
            qualification_match_score=state.qualification_match.score,
            qualification_match=state.qualification_match.model_dump(),
            recency_relevance_score=state.recency_relevance.score,
            recency_relevance=state.recency_relevance.model_dump(),
            domain_match_score=state.domain_match.score,
            domain_match=state.domain_match.model_dump(),
            wording_match_score=state.wording_match.score,
            wording_match=state.wording_match.model_dump(),
            weights=weights
        )
    )
    return {"decision": result.decision, 
    "final_score": final_score,
    "conclusion": result.conclusion,
    "focus_areas": result.focus_areas,
    "all_red_flags": result.all_red_flags,
    "weaknesses": result.weaknesses,
    "strengths": result.strengths,
    } 