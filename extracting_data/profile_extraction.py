from trustcall import create_extractor
from typing import Type
from pydantic import BaseModel


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
        tool_choice="auto"
    )

    result = extractor.invoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Extract the structured information strictly according to the given schema. "
                        "If a field is missing, return null or an empty list."
                    ),
                },
                {
                    "role": "user",
                    "content": text,
                },
            ]
        }
    )

    return result["responses"][0]
