EXTRACTION_PROMPT = """You are an expert text extraction specialist.

TASK: Extract ONLY the sections and information directly relevant to {topic} from the provided text.

INSTRUCTIONS:
1. Identify all text segments that contain information about {topic}
2. Include complete sentences or bullet points - do not cut off mid-sentence
3. Preserve the original formatting (bullet points, line breaks, etc.)
4. If a section header is relevant to {topic}, include it
5. Exclude any information unrelated to {topic} (personal details, other skills, unrelated experience, etc.)
6. If multiple separate sections contain relevant information, extract all of them
7. Maintain the original order of extracted content

OUTPUT FORMAT:
Return only the extracted relevant text portions. Separate multiple extracted sections with a blank line.

If no relevant information is found, respond with: "No relevant information found for {topic}."

TEXT TO ANALYZE:
{text}"""
