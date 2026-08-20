import os
from datetime import date

from dotenv import load_dotenv

from llm.prompts import STORYWRITER_SYSTEM_PROMPT
from llm.model import LLM

load_dotenv(override=True)


def get_cute_story(moment_date: date, moment_description: str,
                   image_url: str, nasa_description: str):
    """Stream a short keepsake inspired by a personal moment and its APOD image.
    Args:
        moment_date: The date of the personal moment.
        moment_description: A brief description of the personal moment.
        image_url: The URL of the APOD image.
        nasa_description: The explanation text from NASA for the APOD image.
    Yields:
        Chunks of text that make up the keepsake story.
    """

    llm = LLM(
        model_name=os.getenv("MODEL"),
        provider=os.getenv("PROVIDER")
    )
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": STORYWRITER_SYSTEM_PROMPT
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": image_url,
                    "detail": "auto"
                },
                {
                    "type": "input_text",
                    "text": (
                        f"Date: {moment_date:%B %d, %Y}\n"
                        f"Their moment: {moment_description}\n"
                        f"NASA's image description: {nasa_description}"
                    )
                },
            ]
        },
    ]

    yield from llm.generate(messages)
