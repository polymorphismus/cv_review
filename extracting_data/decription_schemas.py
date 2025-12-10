from pydantic import BaseModel, Field
from typing import List, Optional


class CVExperience(BaseModel):
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


class CVProject(BaseModel):
    name: str = Field(
        description="Project name or short identifier."
    )
    description: Optional[str] = Field(
        default=None,
        description="Short description of what the project does and its goal."
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Technologies, frameworks, or tools used in the project."
    )
    domain: Optional[str] = Field(
        default=None,
        description="Application domain of the project, e.g. computer vision, NLP, medical imaging."
    )


class CVEducation(BaseModel):
    degree: Optional[str] = Field(
        default=None,
        description="Degree name, e.g. BSc, MSc, Bootcamp certificate."
    )
    field: Optional[str] = Field(
        default=None,
        description="Field of study, e.g. Computer Science, Data Science, Statistics."
    )
    institution: Optional[str] = Field(
        default=None,
        description="University, school, or training provider name."
    )
    graduation_year: Optional[str] = Field(
        default=None,
        description="Graduation year or completion year."
    )


class CVDescription(BaseModel):
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
    technical_skills: List[str] = Field(
        default_factory=list,
        description="List of technical skills, tools, languages, and frameworks."
    )
    soft_skills: List[str] = Field(
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
    languages: List[str] = Field(
        default_factory=list,
        description="Spoken languages (optional proficiency may be included in text)."
    )

    summary: Optional[str] = Field(
        default=None,
        description="Short professional summary or profile section from the CV."
    )


from pydantic import BaseModel, Field
from typing import List, Optional


class JobDescription(BaseModel):
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
    seniority_level: Optional[str] = Field(
        default=None,
        description="Seniority level such as junior, mid, senior, lead."
    )

    required_domains: List[str] = Field(
        default_factory=list,
        description="Domains or industries required for the role."
    )
    required_technical_skills: List[str] = Field(
        default_factory=list,
        description="Mandatory technical skills for the position."
    )
    nice_to_have_skills: List[str] = Field(
        default_factory=list,
        description="Optional or bonus technical skills."
    )

    responsibilities: List[str] = Field(
        default_factory=list,
        description="Main responsibilities and tasks of the role."
    )

    must_have_requirements: List[str] = Field(
        default_factory=list,
        description="Explicit mandatory job requirements."
    )
    nice_to_have_requirements: List[str] = Field(
        default_factory=list,
        description="Optional or bonus job requirements."
    )

    soft_skills: List[str] = Field(
        default_factory=list,
        description="Required soft skills such as communication or teamwork."
    )

    job_summary: Optional[str] = Field(
        default=None,
        description="Short textual summary of the position."
    )
