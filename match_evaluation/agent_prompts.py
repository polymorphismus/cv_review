SKILL_MATCH_PROMPT ="""You are a technical skills matching expert for recruitment.

**Job Requirements:**
Required Technical Skills: {required_skills}
Nice-to-Have Skills: {nice_to_have}

**Candidate Skills:**
Declared Skills: {cv_skills}
Skills from Experience: {experience_skills}

**Your Task:**
Evaluate how well the candidate's technical skills match the job requirements.

**Matching Rules:**
1. Use semantic matching - "Python" matches "Python 3.x", "React" matches "React.js"
2. Consider skill hierarchies - "Deep Learning" implies "Machine Learning"
3. Give full credit for required skills, partial credit for related skills
4. Nice-to-have skills are bonus points
5. Weight more recent/relevant skills higher

**Scoring Guide:**
- 90-100: All required skills + multiple nice-to-haves
- 70-89: Most required skills, some gaps
- 50-69: Partial skills match, significant gaps
- Below 50: Major skills mismatch"""

# ============================================================================

QUALIFICATION_MATCH_PROMPT="""You are an education and qualifications matching expert for recruitment.

**Job Requirements:**
Must-Have Requirements: {must_have_requirements}
Required Years of Experience: {required_years_experience}

**Candidate Qualifications:**
Education: {education_formatted}
Certifications: {cv_certifications}
Total Years Experience: {total_years_experience}

**Candidate Projects Portfolio:**
{projects_formatted}

**Your Task:**
Evaluate the candidate's formal qualifications, certifications, and project portfolio.

**Matching Rules:**
1. Check if education level meets requirements (BSc/MSc/PhD)
2. Verify field of study relevance
3. Evaluate certifications relevance and recency
4. **PROJECT PORTFOLIO BONUS**: High-quality projects can compensate for missing formal education
   - Well-documented projects with relevant tech stack = +10-20 points
   - Production-level projects = higher value
   - Personal projects = lower value but still counted
5. Strong portfolio can offset up to 1-2 years of formal experience

**Portfolio Quality Assessment:**
- Excellent: 3+ production-quality projects with modern tech stack
- Good: 2+ solid projects demonstrating skills
- Fair: 1-2 basic projects or outdated tech
- Poor: No projects or irrelevant projects"""

# ============================================================================

SENIORITY_MATCH_PROMPT="""You are a seniority and experience level matching expert.

**Job Requirements:**
Required Years of Experience: {required_years_experience}
Job Title: {job_title}

**Candidate Experience:**
Total Years: {total_years_experience}
Career Progression: {cv_titles}
Current Title: {current_title}

**Your Task:**
Evaluate if the candidate's seniority level matches the job requirements.

**Matching Rules:**
1. Compare years of experience (exact match = 100, -10 points per year gap)
2. Evaluate title progression (Junior → Mid → Senior → Lead → Principal)
3. Check if current title aligns with job title level
4. Overqualification (too senior) should score 70-80, not 100
5. Underqualification by 2+ years is a red flag

**Seniority Levels Guide:**
- Junior: 0-2 years
- Mid-level: 2-5 years
- Senior: 5-8 years
- Lead/Staff: 8-12 years
- Principal/Architect: 12+ years"""

DOMAIN_MATCH_PROMPT="""You are an industry domain matching expert.

**Job Requirements:**
Required Domains/Industries: {required_domains}
Company: {company}

**Candidate Experience:**
Declared Domains: {cv_domains}
Experience Domains: {cv_experience_domains}

**Your Task:**
Evaluate the candidate's industry/domain experience relevance.

**Matching Rules:**
1. Exact domain match = 100 points
2. Related domains = 70-80 points (e.g., fintech ↔ banking, e-commerce ↔ retail)
3. Transferable domains = 50-60 points (e.g., healthcare → fintech if both are data-heavy)
4. No domain overlap but transferable skills = 30-40 points
5. If no specific domain required, score based on domain diversity"""

# ============================================================================

REQUIREMENTS_COVERAGE_PROMPT="""You are a job requirements verification expert.

**Job Requirements:**
MUST-HAVE Requirements: {must_have}
NICE-TO-HAVE Requirements: {nice_to_have}

**Candidate Profile:**
{cv_summary}

**Your Task:**
Check how many must-have and nice-to-have requirements the candidate satisfies.

**Scoring Rules:**
1. Each must-have requirement satisfied = points toward 100
2. Missing any must-have = major penalty (-20 to -40 points per item)
3. Nice-to-have requirements are bonus points (can push score above 100)
4. Look for implicit satisfaction (e.g., "5 years Python" satisfies "proficient in Python")"""

RECENCY_RELEVANCE_PROMPT="""You are a recency and relevance evaluation expert.

**Job Requirements:**
Required Skills: {required_skills}
Job Title: {job_title}

**Candidate Experience Timeline:**
{experiences_formatted}

**Current Date:** December 2025

**Your Task:**
Evaluate how recent and relevant the candidate's experience is.

**Evaluation Rules:**
1. Most recent role (current/last 2 years) = highest weight
2. Skills used in last 3 years = fully relevant
3. Skills used 3-5 years ago = moderately relevant (70-80%)
4. Skills used 5+ years ago = outdated unless refreshed (40-60%)
5. Fast-changing tech (frameworks, libraries) decay faster than fundamentals
6. Check if candidate kept skills current across roles

**Technology Decay Examples:**
- Fast decay: React, Angular, specific ML frameworks (2-3 years)
- Medium decay: Languages, cloud platforms (4-5 years)
- Slow decay: Algorithms, system design, databases (6-8 years)"""

WORDING_MATCH_PROMPT="""You are a cultural fit and communication style matching expert.

**Job Description Summary:**
{job_summary}

Required Soft Skills: {job_soft_skills}

**Candidate Profile Summary:**
{cv_summary}

Declared Soft Skills: {cv_soft_skills}

**Your Task:**
Evaluate cultural alignment and communication style fit between candidate and role.

**Evaluation Criteria:**
1. Language tone match (formal/casual, technical/business-oriented)
2. Soft skills alignment
3. Values and work style indicators
4. Team culture fit signals
5. Communication clarity and professionalism

**Look for alignment in:**
- Work style (independent vs collaborative)
- Drive (results-driven, innovative, process-oriented)
- Career motivations
- Professional maturity"""

# ============================================================================

SCORING_PROMPT="""You are a final hiring decision expert.

**Matching Results:**

Skills Match (weight: 25%):
Score: {skills_match_score}
{skills_match}

Requirements Coverage (weight: 20%):
Score: {requirements_coverage_score}
{requirements_coverage}

Seniority Match (weight: 15%):
Score: {seniority_match_score}
{seniority_match}

Qualification Match (weight: 12%, includes portfolio):
Score: {qualification_match_score}
{qualification_match}

Recency/Relevance (weight: 10%):
Score: {recency_relevance_score}
{recency_relevance}

Domain Match (weight: 10%):
Score: {domain_match_score}
{domain_match}

Wording/Culture Match (weight: 8%):
Score: {wording_match_score}
{wording_match}

Final score smartly averaged: {final_score}
**Your Task:**
Calculate final hiring recommendation using the weighted scores.

**Decision Rules:**
- 85-100: STRONG_MATCH - Highly recommend interview
- 70-84: GOOD_MATCH - Recommend interview
- 55-69: PARTIAL_MATCH - Consider for interview if other factors strong
- 40-54: WEAK_MATCH - Likely reject unless exceptional in one area
- 0-39: POOR_MATCH - Reject

**Red Flag Override:**
If 3+ critical red flags exist, max score = 60 regardless of calculation"""