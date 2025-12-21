from match_evaluation.agent_state import AgentState
from match_evaluation.output_schemas import *
from match_evaluation.agent_prompts import *

def skills_match_agent_sync(state: AgentState, llm):
    print('Assissing skills...')
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
    print('Assissing qualification...')
    cv_education = state.cv.education
    cv_certifications = state.cv.certifications
    cv_projects = state.cv.projects
    technical_skills = state.cv.technical_skills
    education_formatted = [
        f"{e.field} from {e.institution}, finished in ({e.graduation_year})" 
        for e in cv_education
    ]
    
    projects_formatted = [
        f"{p.name}: {p.project_description} (Tech: {', '.join(p.technologies)})" 
        for p in cv_projects
    ]
    
    result = llm.with_structured_output(QualificationMatchResult).invoke(
        QUALIFICATION_MATCH_PROMPT.format(
            must_have_requirements=state.job.required_technical_skills,
            required_years_experience=state.job.required_years_experience,
            required_education = state.job.required_education,
            required_certifications = state.job.required_certifications,
            education_formatted=education_formatted,
            cv_certifications=cv_certifications,
            total_years_experience=state.cv.total_years_experience,
            projects_formatted=projects_formatted,
            technical_skills=technical_skills
        )
    )
    return {"qualification_match": result}  

def seniority_match_agent_sync(state: AgentState, llm) -> SeniorityMatchResult:
    print('Assissing seniority...')
    cv_titles = [exp.title for exp in state.cv.experience]
    
    result = llm.with_structured_output(SeniorityMatchResult).invoke(
        SENIORITY_MATCH_PROMPT.format(
            required_years_experience=state.job.required_years_experience,
            required_seniority=state.job.required_seniority,
            job_title=state.job.job_title,
            total_years_experience=state.cv.total_years_experience,
            cv_titles=cv_titles,
            current_title=state.cv.current_title
        )
    )
    return {'seniority_match': result}

def domain_match_agent_sync(state: AgentState, llm) -> DomainMatchResult:
    print('Assissing domain...')

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
    print('Assissing requirements coverage...')

    must_have = state.job.required_technical_skills
    nice_to_have = state.job.nice_to_have_skills
    other_requirements  = state.job.other_requirements
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
            other_requirements = other_requirements,
            cv_summary=cv_summary
        )
    )
    return {"requirements_coverage" :result}

def recency_relevance_agent_sync(state: AgentState, llm) -> RecencyRelevanceResult:
    print('Assissing relevance...')

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


def keyword_macth_agent_sync(state: AgentState, llm) -> KeywordMatchResult:
    print('Assissing keyword macth...')

    critical_keywords = state.job.critical_keywords
    cv_full_text = state.cv_description_text
        
    result = llm.with_structured_output(KeywordMatchResult).invoke(
        KEYWORD_MATCH_PROMPT.format(
            critical_keywords=critical_keywords,
            cv_full_text=cv_full_text,
        )
    )
    return { "keyword_match" :result}


def weight_generation_agent_sync(state: AgentState, llm) -> dict:
    """Generate dynamic weights based on job characteristics"""
    print('Weighting scores based on importance')
    result = llm.with_structured_output(WeightingStrategy).invoke(
        WEIGHT_GENERATION_PROMPT.format(
            job_title=state.job.job_title,
            required_years_experience=state.job.required_years_experience or "Not specified",
            required_seniority=state.job.required_seniority or "Not specified",
            required_domains=state.job.required_domains,
            required_technical_skills=[s.name for s in state.job.required_technical_skills],
            required_education=state.job.required_education,
            required_certifications=state.job.required_certifications,
            must_have_requirements=state.job.other_requirements,
            role_summary=state.job.role_summary or "Not provided"
        )
    )
    
    # Normalize weights to ensure they sum to 1.0
    total = result.total_weight
    if abs(total - 1.0) > 0.01:  # Allow small floating point errors
        # Normalize
        result.skills_match /= total
        result.keyword_match /= total
        result.requirements_coverage /= total
        result.seniority_match /= total
        result.qualification_match /= total
        result.recency_relevance /= total
        result.domain_match /= total
    
    return {"weighting_strategy": result}


def scoring_agent_sync(state: AgentState, llm):
    """Final scoring with dynamic weights and ATS reasoning"""
    
    print("Final scoring...")
    # Use dynamic weights from weight generation
    weights = {
        'skills_match': state.weighting_strategy.skills_match,
        'keyword_match': state.weighting_strategy.keyword_match,
        'requirements_coverage': state.weighting_strategy.requirements_coverage,
        'seniority_match': state.weighting_strategy.seniority_match,
        'qualification_match': state.weighting_strategy.qualification_match,
        'recency_relevance': state.weighting_strategy.recency_relevance,
        'domain_match': state.weighting_strategy.domain_match,
    }
    
    weighted_score = sum(weights[k] * getattr(state, k).score for k in weights)
    
    score_breakdown = "\n".join([
        f"  {k}: {getattr(state, k).score:.1f} × {weights[k]:.2f} = {getattr(state, k).score * weights[k]:.1f}"
        for k in weights
    ])
    
    all_red_flags_list = []
    for dimension in ['skills_match', 'keyword_match', 'requirements_coverage', 
                      'seniority_match', 'qualification_match',
                      'recency_relevance', 'domain_match']:
        all_red_flags_list.extend(getattr(state, dimension).red_flags)
    
    result = llm.with_structured_output(FinalScoringResult, method="json_mode").invoke(
        SCORING_PROMPT.format(
            job_title=state.job.job_title,
            company=state.job.company or "Not specified",
            required_seniority=state.job.required_seniority or "Not specified",
            required_years_experience=state.job.required_years_experience or "Not specified",
            
            # Weights (formatted as percentages)
            weight_skills=weights['skills_match'],
            weight_keyword=weights['keyword_match'],
            weight_requirements=weights['requirements_coverage'],
            weight_seniority=weights['seniority_match'],
            weight_qualification=weights['qualification_match'],
            weight_recency=weights['recency_relevance'],
            weight_domain=weights['domain_match'],
            
            # Skills match details
            skills_match_score=state.skills_match.score,
            skills_matched=", ".join(state.skills_match.matched_items[:5]) or "None",
            skills_missing=", ".join(state.skills_match.missing_items[:5]) or "None",
            skills_red_flags=", ".join(state.skills_match.red_flags) or "None",
            
            # Keyword match details
            keyword_match_score=state.keyword_match.score,
            keyword_missing=", ".join(state.keyword_match.missing_keywords[:5]) or "None",
            keyword_red_flags=", ".join(state.keyword_match.red_flags) or "None",
            
            # Requirements coverage
            requirements_coverage_score=state.requirements_coverage.score,
            requirements_satisfied=len(state.requirements_coverage.must_have_satisfied),
            requirements_total=len(state.requirements_coverage.must_have_satisfied) + len(state.requirements_coverage.must_have_missing),
            requirements_coverage_pct=state.requirements_coverage.coverage_percentage,
            requirements_red_flags=", ".join(state.requirements_coverage.red_flags) or "None",
            
            # Seniority
            seniority_match_score=state.seniority_match.score,
            candidate_level=state.seniority_match.candidate_level,
            required_level=state.seniority_match.required_level,
            years_gap=state.seniority_match.years_gap,
            seniority_red_flags=", ".join(state.seniority_match.red_flags) or "None",
            
            # Qualification
            qualification_match_score=state.qualification_match.score,
            portfolio_quality=state.qualification_match.portfolio_quality,
            portfolio_boost=state.qualification_match.portfolio_boost,
            qualification_red_flags=", ".join(state.qualification_match.red_flags) or "None",
            
            # Recency
            recency_relevance_score=state.recency_relevance.score,
            tech_freshness=state.recency_relevance.technology_freshness,
            recency_red_flags=", ".join(state.recency_relevance.red_flags) or "None",
            
            # Domain
            domain_match_score=state.domain_match.score,
            domain_matched=", ".join(state.domain_match.matched_items) or "None",
            domain_red_flags=", ".join(state.domain_match.red_flags) or "None",
            
            # Calculated values
            weighted_score=weighted_score,
            score_breakdown=score_breakdown,
        )
    )
    formatted_focus_areas = "\n * " + "\n * ".join(result.focus_areas)
    print("\n"* 5)
    print(f"""Weighted score: {weighted_score}
    Areas that you need to work on in order to natually become a better candidate for this poition:
    {formatted_focus_areas}
    Advice on continuing: {result.recommendation}""")
    return {
        "decision": result.decision,
        "recommendation": result.recommendation,
        "final_scoring": result,
        "focus_areas": result.focus_areas,
        "all_red_flags": all_red_flags_list,
        "weaknesses": result.weaknesses,
        "strengths": result.strengths,
    }
