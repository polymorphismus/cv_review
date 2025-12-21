from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from extracting_data.description_schemas import CVDescription, JobDescription

class CVRewriteState(BaseModel):
    """Streamlined state containing only information needed for CV rewriting"""
    original_cv_folder_path: str = Field(description="Path to the folder containing original cv")
    output_dir: Optional[str] = Field(default=None, description="Folder to save generated artifacts (docx)")
    # Original content
    original_cv: CVDescription = Field(description="Complete original CV data")
    target_job: JobDescription = Field(description="Target job description")
    original_cv_text: str = Field(description='original text extracted from cv')
    # Critical matching results
    matched_skills: List[str] = Field(description="Skills candidate has that JD requires")
    partial_skill_matches: List[str] = Field(description="Related skills that should be reworded")
    matched_keywords: List[str] = Field(description="ATS-critical keywords found in CV")
    missing_keywords: List[str] = Field(description="Keywords missing (DO NOT fabricate)")
    
    # Requirements alignment
    must_haves_satisfied: List[str] = Field(description="Must-have requirements met - highlight these")
    must_haves_missing: List[str] = Field(description="Must-haves missing - acknowledge gaps")
    nice_to_haves_satisfied: List[str] = Field(description="Bonus requirements met")
    
    # Experience relevance
    recent_relevant_experience: List[str] = Field(description="Skills/roles from last 2-3 years to prioritize")
    matched_domains: List[str] = Field(description="Relevant industry experience to emphasize")
    transferable_domains: List[str] = Field(description="Adjacent experience that transfers well")
    
    # Seniority context
    candidate_level: str = Field(description="Current seniority level")
    required_level: str = Field(description="Required seniority level")
    title_alignment: str = Field(description="How well titles align")
    
    # Strategic guidance
    top_strengths: List[str] = Field(description="Top 3-5 strengths to emphasize")
    key_weaknesses: List[str] = Field(description="Gaps to be aware of (not to hide)")
    red_flags: List[str] = Field(description="Critical issues to address or acknowledge")
    
    # Optimization priorities
    keyword_frequency_targets: Dict[str, int] = Field(
        description="How many times each critical keyword should appear",
        default_factory=dict
    )
    focus_areas: List[str] = Field(
        description="What to emphasize most in rewrite",
        default_factory=list
    )

    user_feedback: Optional[str] = Field(
        default=None,
        description="Feedback user gave to update the created cv"
    )

    updated_cv_text: Optional[str] = Field(
        default=None,
        description="Full rewritten CV in clean Markdown format, optimized for ATS parsing and human review"
    )

    feedback_round: int = 0

    class Config:
        arbitrary_types_allowed = True
