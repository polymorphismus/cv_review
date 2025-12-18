EXTRACTION_PROMPT = """You are an expert text extraction specialist.

TASK: Extract ONLY the sections and information directly relevant to {topic} from the provided text.

INSTRUCTIONS:
1. Identify all text segments that contain information about {topic}
2. Include complete sentences or bullet points - do not cut off mid-sentence
3. If a section header is relevant to {topic}, include it
4. Exclude any information unrelated to {topic} (personal details, other skills, unrelated experience, etc.)
5. If multiple separate sections contain relevant information, extract all of them
6. Maintain the original order of extracted content

FORMATTING REQUIREMENTS:
- Remove excessive spacing between letters in headers (e.g., "E D U C A T I O N" → "Education")
- Normalize date ranges to standard format (e.g., "2024 – 2025" or "Jun 2021 – Sep 2022")
- Replace non-breaking spaces and special unicode characters with regular spaces
- Use standard bullet points (•, -, or *) consistently
- Ensure proper line spacing between sections
- Keep section headers in title case (capitalize first letter of each major word)
- Remove any artifacts from PDF extraction (like stray characters or formatting marks)

OUTPUT FORMAT:
Return the extracted content in clean, readable format with:
- Clear section headers
- Properly formatted dates
- Clean bullet points for lists
- Appropriate spacing between sections

If no relevant information is found, respond with: "No relevant information found for {topic}."

TEXT TO ANALYZE:
{text}"""
