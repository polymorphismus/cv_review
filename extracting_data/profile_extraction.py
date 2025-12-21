from trustcall import create_extractor
from typing import Type
from pydantic import BaseModel
from extracting_data.extracting_prompts import SYSTEM_INSTRUCTIONS


def trustcall_extract_text_to_schema(
    text: str,
    schema: Type[BaseModel],
    llm
):
    """
    Extracts structured data from plain text using TrustCall.

    Args:
        text: Raw text of CV or Job Description.
        schema: Pydantic model (CVDescription or JobDescription).
        llm: LangChain-compatible LLM instance.

    Returns:
        Validated Pydantic object.
    """

    extractor = create_extractor(
        llm=llm,
        tools=[schema],
        tool_choice="any",
        enable_inserts=True,
    )

    result = extractor.invoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": text,
                },
            ]
        }
    )

    return result["responses"][0]
