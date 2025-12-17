from pydantic import BaseModel, Field
from typing import List, Optional

class Skill(BaseModel):
    """Generic skill model for both technical and soft skills"""
    name: str = Field(
        description="Skill name, e.g. 'Python', 'Project Management', 'Excel', 'Patient Care'"
    )
    category: Optional[str] = Field(
        default=None,
        description="Flexible category based on domain, e.g. 'Programming', 'Marketing', 'Clinical', 'Financial Analysis'"
    )
    proficiency: Optional[str] = Field(
        default=None,
        description="Proficiency level: 'basic', 'intermediate', 'advanced', 'expert'"
    )
    years_experience: Optional[float] = Field(
        default=None,
        description="Years of experience with this skill"
    )
    context: Optional[str] = Field(
        default=None,
        description="Where/how this skill was used, e.g. 'Used in production systems', 'Led team training'"
    )
    priority: Optional[str] = Field(
        default=None,
        description="For job requirements: 'must_have', 'strongly_preferred', 'nice_to_have'"
    )


class CVExperience(BaseModel):
    """General experience"""
    title: str = Field(
        description="Job title or role name, e.g. 'Data Scientist', 'ML Engineer'."
    )
    company: Optional[str] = Field(
        default=None,
        description="Company or organization name."
    )
    domain: Optional[str] = Field(
        default=None,
        description="Industry or application domain of this role, e.g. healthcare, fintech, e-commerce."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Employment start date in free text format (e.g. 'Jan 2022')."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Employment end date in free text format (or 'Present')."
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="List of main responsibilities and achievements in this role."
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="List of tools, languages, and technologies used in this role."
    )
    
    quantifiable_achievements: List[str] = Field(
        default_factory=list,
        description="Measurable achievements with numbers/percentages, e.g. 'Reduced latency by 40%'"
    )

    seniority_level: Optional[str] = Field(
        default=None,
        description="Required level of seniority of the experience"

    )



class CVProject(BaseModel):
    """Projects from CV"""
    name: str = Field(
        description="Project name or short identifier."
    )
    project_description: Optional[str] = Field(
        default=None,
        description="Short description of what the project does and its goal."
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Technologies, frameworks, or tools used in the project."
    )
    experience_link: Optional[str] = Field(
        default=None,
        description="Job place or education that the project was done."
    )


class CVEducation(BaseModel):
    """Education matching"""
    certification: Optional[str] = Field(
        default=None,
        description="Achived certification like BSc, MSc, Bootcamp certificate, graduate"
    )
    field: Optional[str] = Field(
        default=None,
        description="Field of study, e.g. Computer Science, Data Science, Statistics, Literature, Art."
    )
    institution: Optional[str] = Field(
        default=None,
        description="University, school, or training provider name."
    )
    graduation_year: Optional[str] = Field(
        default=None,
        description="Graduation year or completion year."
    )

    is_completed: Optional[bool] = Field(
        default=None,
        description="True if completed, False if in progress"
    )


class CVDescription(BaseModel):
    """Main class for cv"""
    full_name: Optional[str] = Field(
        default=None,
        description="Candidate full name as written in the CV."
    )
    current_title: Optional[str] = Field(
        default=None,
        description="Current or most recent job title."
    )

    total_years_experience: Optional[float] = Field(
        default=None,
        description="Estimated total number of years of professional experience."
    )

    domains: List[str] = Field(
        default_factory=list,
        description="List of industries or domains the candidate has worked in."
    )
    technical_skills: List[Skill] = Field(
        default_factory=list,
        description="List of technical skills, tools, languages, and frameworks."
    )
    soft_skills: List[Skill] = Field(
        default_factory=list,
        description="List of non-technical skills such as communication, leadership, teamwork."
    )

    experience: List[CVExperience] = Field(
        default_factory=list,
        description="Chronological list of professional work experiences."
    )
    projects: List[CVProject] = Field(
        default_factory=list,
        description="List of personal, academic, or portfolio projects."
    )
    education: List[CVEducation] = Field(
        default_factory=list,
        description="Educational background entries."
    )

    certifications: List[str] = Field(
        default_factory=list,
        description="Professional certificates, courses, or official credentials."
    )
    spoken_languages: List[str] = Field(
        default_factory=list,
        description="Spoken languages (optional proficiency may be included in text)."
    )

    cv_summary: Optional[str] = Field(
        default=None,
        description="Short professional summary or profile section from the CV."
    )


class JobDescription(BaseModel):
    """Extracting valuable fields from job description"""
    job_title: str = Field(
        description="Title of the open position."
    )
    company: Optional[str] = Field(
        default=None,
        description="Company or organization offering the job."
    )

    required_years_experience: Optional[float] = Field(
        default=None,
        description="Minimum required years of professional experience for the role."
    )
 
    required_domains: List[str] = Field(
        default_factory=list,
        description="Domains or industries required for the role."
    )
    required_technical_skills: List[Skill] = Field(
        default_factory=list,
        description="Mandatory technical skills for the position."
    )
    nice_to_have_skills: List[Skill] = Field(
        default_factory=list,
        description="Optional or bonus technical skills."
    )
    
    other_requirements: List[str] = Field(
        default_factory=list,
        description="Non-skill requirements"
    )

    responsibilities: List[str] = Field(
        default_factory=list,
        description="Main responsibilities and tasks of the role."
    )

    soft_skills: List[Skill] = Field(
        default_factory=list,
        description="Required soft skills such as communication or teamwork."
    )

    role_summary: Optional[str] = Field(
        default=None,
        description="Short textual summary of the position."
    )

    required_education: List[CVEducation] = Field(
    default_factory=list,
    description="Required education qualifications (degree type, field of study)"
    )

    required_certifications: List[str] = Field(
    default_factory=list,
    description="Mandatory certifications like AWS, PMP, CFA"
    )

    required_spoken_languages: List[str] = Field(
    default_factory=list,
    description="Required languages with optional proficiency levels"
    )

    required_seniority: Optional[str] = Field(
        default=None,
        description="Required level of seniority "

    )
    
    critical_keywords: List[str] = Field(
    default_factory=list,
    description="Key terms that must appear for ATS to flag as match"
    )


