EXTRACTION_PROMPT = """You are an expert text extraction specialist.

TASK:
Extract ONLY the sections and information directly relevant to {topic} from the provided text, including implicit sections that do not have explicit headers.

INSTRUCTIONS:
1. Identify all text segments that contain information about {topic}.
2. Include complete sentences or bullet points — do not cut off mid-sentence.
3. If a section header is relevant to {topic}, include it.
4. Exclude any information unrelated to {topic} (personal details, unrelated skills, unrelated experience, etc.).
5. If multiple separate sections contain relevant information, extract all of them.
6. Maintain the original order of extracted content.
7. If the text begins with an introductory paragraph summarizing experience, skills, or background (even without a section header), treat it as a Profile/Summary section and include it.

WHEN TOPIC IS "CV":
- Treat the opening paragraphs of the document as part of the CV, even if no section header is present.
- Include professional summaries, role overviews, or background descriptions at the top of the text.

MUST FOLLOW:
- This is a copy-and-filter task, NOT interpretation or summarization.
- Extract only text that is explicitly present in the source. Do NOT infer, guess, or enrich information.
- Preserve all factual content EXACTLY as written, including names, titles, institutions, companies, tools, abbreviations, degrees, and dates.
- Formatting changes are allowed ONLY if they do NOT change meaning.
  Allowed: spacing cleanup, bullet normalization, line breaks, header capitalization.
  Disallowed: paraphrasing, synonym replacement, abbreviation expansion, title rewriting, or content merging.
- Do NOT normalize or reinterpret roles, seniority, responsibilities, or skills.
- Do NOT merge information from separate sections or non-contiguous text spans.
- Dates may be reformatted for consistency, but original time spans must be preserved exactly.
- If unsure whether a change alters meaning, DO NOT make the change.


FORMATTING REQUIREMENTS:
- Remove excessive spacing between letters in headers (e.g., "E D U C A T I O N" → "Education").
- Normalize date ranges to standard format (e.g., "2024 – 2025" or "Jun 2021 – Sep 2022").
- Replace non-breaking spaces and special unicode characters with regular spaces.
- Use standard bullet points (•, -, or *) consistently.
- Ensure proper line spacing between sections.
- Keep section headers in title case (capitalize the first letter of each major word).
- Remove any artifacts from PDF extraction (such as stray characters or formatting marks).


OUTPUT FORMAT:
Return the extracted content in a clean, readable format with:
- Clear section headers.
- Properly formatted dates.
- Clean bullet points for lists.
- Appropriate spacing between sections.

If no relevant information is found, respond with:
"No relevant information found for {topic}."

TEXT TO ANALYZE:
{text}
"""

SYSTEM_RULES = """
You are extracting structured information from text into a schema.

GENERAL RULES:
- Extract only information explicitly present in the text
- Do NOT infer, assume, or fabricate information
- If a field is missing or ambiguous, return null or an empty list
- Prefer omission over incorrect inference

NORMALIZATION RULES:
- Titles must contain only the core role name
- Remove locations, employment type, team names, and work mode
- Remove text in parentheses
- Remove text after separators: "-", "–", "|"

CV RULES (when schema is CVDescription or related models):
- Extract skills only if explicitly mentioned
- Do NOT infer proficiency or years of experience
- Populate proficiency or years_experience only if directly stated
- seniority_level must be extracted only if explicitly written
- domain must be populated only if clearly stated or directly implied

EXPERIENCE RULES:
- Responsibilities describe tasks and duties
- Quantifiable achievements must include explicit numbers or metrics
- Do NOT duplicate the same sentence in multiple fields

PROJECT RULES:
- If project responsibilities are written as a single sentence with multiple actions, split them into separate responsibility items by verbs or commas.
- Extract projects only if explicitly labeled as projects or portfolio work
- Do NOT convert work experience into projects
- When a responsibility sentence contains an explicitly named technology (e.g. SCADA, PLC, OPC UA, Python), extract the technology name into the technologies field while keeping the full sentence in responsibilities.
- Do NOT convert verbs or actions into technologies.


TOTAL EXPERIENCE RULES:
- Calculate total_years_experience only if sufficient date information exists
- If dates are missing or ambiguous, leave it null

JD (when schema is JobDescription or related models) SKILL EXPERIENCE RULES:
- If a required skill explicitly states a minimum number of years (e.g. "2+ years", "minimum 2 years", "at least 3 years"):
  - Extract the numeric value and set years_experience accordingly
  - Use the minimum stated value (e.g. "2+ years" → 2.0)
- Do NOT infer years_experience if no numeric value is stated

JD (when schema is JobDescription or related models) DOMAIN RULES:
- required_domains may include either:
  - industry domains (e.g. fintech, healthcare, e-commerce), OR
  - functional domains explicitly stated in the text (e.g. product analytics, growth analytics, marketing analytics)
- Extract a domain only if it is clearly stated or strongly implied by repeated responsibilities or requirements
- Do NOT invent domains that are not supported by the text
- Prefer specific functional domains over generic terms like "data"
- Do NOT infer domains solely from the job title
- Domains must be supported by role responsibilities or requirements

FORMATTING RULES (ADD):
- Treat bullet symbols such as "•" the same as "-" for list extraction.

EDUCATION RULES:
- If an education entry contains a date range (e.g. "2008 – 2013"):
  - Treat the end year as graduation_year.
- Do NOT infer graduation_year if no year or range is present.

"""

SYSTEM_INSTRUCTIONS = (
    "Extract the structured information strictly using the tool. "
    "You MUST call the tool. Do NOT output JSON directly. "
    "If a field is missing, return null or an empty list.\n\n" + SYSTEM_RULES
)
