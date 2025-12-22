from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class SkillsMatchResult(BaseModel):
    score: float = Field(description="Match score from 0-100")
    matched_items: List[str] = Field(description="Required skills the candidate has")
    missing_items: List[str] = Field(description="Required skills the candidate lacks")
    partial_matches: List[str] = Field(description="Related but not exact skill matches")
    bonus_items: List[str] = Field(description="Nice-to-have skills the candidate has")
    reasoning: str = Field(description="2-3 sentence explanation of the score")
    red_flags: List[str] = Field(description="Critical missing skills")


class QualificationMatchResult(BaseModel):
    score: float = Field(description="Match score from 0-100")
    matched_items: List[str] = Field(description="Education/certs that meet requirements")
    missing_items: List[str] = Field(description="Required qualifications not met")
    portfolio_quality: str = Field(description="Assessment: excellent/good/fair/poor")
    reasoning: str = Field(description="Explanation including portfolio impact")
    red_flags: List[str] = Field(description="Critical qualification gaps")
    portfolio_boost: float = Field(description="Points added for strong portfolio (0-20)")


class SeniorityMatchResult(BaseModel):
    score: float = Field(description="Match score from 0-100")
    candidate_level: str = Field(description="junior/mid/senior/lead/principal")
    required_level: str = Field(description="junior/mid/senior/lead/principal")
    reasoning: str = Field(description="Assessment of seniority fit")
    red_flags: List[str] = Field(description="Concerns about over/under qualification")
    years_gap: float = Field(description="Positive if overqualified, negative if underqualified")
    title_alignment: str = Field(description="well-aligned/slight-mismatch/significant-mismatch")



class DomainMatchResult(BaseModel):
    score: float = Field(description="Match score from 0-100")
    matched_items: List[str] = Field(description="Domains that match or are highly related")
    missing_items: List[str] = Field(description="Required domains candidate lacks")
    transferable_experience: List[str] = Field(description="Domains that could transfer well")
    reasoning: str = Field(description="Assessment of domain fit")
    red_flags: List[str] = Field(description="Domain experience gaps that matter")
    domain_diversity: int = Field(description="Number of different domains candidate has worked in")


class RequirementsCoverageResult(BaseModel):
    score: float = Field(description="Match score from 0-100+, can exceed 100 with nice-to-haves")
    must_have_satisfied: List[str] = Field(description="Must-have requirements met")
    must_have_missing: List[str] = Field(description="Must-have requirements NOT met")
    nice_to_have_satisfied: List[str] = Field(description="Nice-to-have requirements met")
    reasoning: str = Field(description="Explanation of coverage")
    red_flags: List[str] = Field(description="Critical must-have requirements missing")
    bonus_points: float = Field(description="Extra points from nice-to-haves (0-20)")
    coverage_percentage: float = Field(description="Percentage of must-haves satisfied")


class RecencyRelevanceResult(BaseModel):
    score: float = Field(description="Match score from 0-100")
    recent_relevant_experience: List[str] = Field(description="Skills/roles from last 2-3 years")
    outdated_experience: List[str] = Field(description="Skills not used recently")
    most_recent_role_match: str = Field(description="How well does latest role align with job?")
    reasoning: str = Field(description="Assessment of experience recency")
    red_flags: List[str] = Field(description="Concerns about outdated skills")
    technology_freshness: str = Field(description="current/somewhat-current/outdated")


class KeywordMatchResult(BaseModel):
    score: float = Field(ge=0, le=100, description="Match score from 0-100 based on keyword presence")
    matched_keywords: List[str] = Field(description="Critical keywords found in CV (exact matches)")
    missing_keywords: List[str] = Field(description="Critical keywords NOT found in CV")
    reasoning: str = Field(description="Explanation of keyword match results and ATS implications")
    red_flags: List[str] = Field(description="Critical keywords missing that could cause ATS rejection")
    keyword_frequency: dict = Field(description="How many times each matched keyword appears, e.g. {'Python': 5, 'AWS': 3}")

class FinalScoringResult(BaseModel):
    decision: Literal["Strong Match", "Good Match", "Partial Match","Weak Match", "Poor Match"]  = Field(description="Strong Match/Good Match/Partial Match/Weak Match/Poor Match")
    strengths: List[str] = Field(description="Top 3-5 candidate strengths")
    weaknesses: List[str] = Field(description="Top 3-5 gaps or concerns")
    recommendation: str = Field(description="Detailed 2-3 sentence recommendation on wheather it is worth for candidate to apply to this role or not")
    focus_areas: List[str] = Field(description="What the candidate need to work on in order to match the required position")
 
class WeightingStrategy(BaseModel):
    """Dynamic weights tailored to specific job requirements"""
    
    skills_match: float = Field(ge=0, le=1, description="Weight for technical skills matching")
    keyword_match: float = Field(ge=0, le=1, description="Weight for ATS keyword matching")
    requirements_coverage: float = Field(ge=0, le=1, description="Weight for must-have requirements")
    seniority_match: float = Field(ge=0, le=1, description="Weight for experience level")
    qualification_match: float = Field(ge=0, le=1, description="Weight for education/certs/portfolio")
    recency_relevance: float = Field(ge=0, le=1, description="Weight for how current experience is")
    domain_match: float = Field(ge=0, le=1, description="Weight for industry experience")
    
    reasoning: str = Field(description="Why these weights were chosen for this role")
    role_archetype: str = Field(description="E.g., 'senior-technical', 'entry-level', 'domain-specialist', 'leadership'")
    
    @property
    def total_weight(self) -> float:
        """Ensure weights sum to 1.0"""
        return (
            self.skills_match + self.keyword_match + self.requirements_coverage +
            self.seniority_match + self.qualification_match +
            self.recency_relevance + self.domain_match
        )
