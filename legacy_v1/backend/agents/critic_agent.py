import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)


CRITIC_SCHEMA = {
    "type": "object",
    "properties": {
        "needs_revision": {
            "type": "boolean"
        },
        "overall_feedback": {
            "type": "string"
        },
        "revision_instructions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "needs_revision",
        "overall_feedback",
        "revision_instructions"
    ],
    "additionalProperties": False
}


def critique_article(
    article: dict,
    guardrail_result: dict
) -> dict:

    response = client.responses.create(

        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),

        input=[

            {
                "role": "system",

                "content": """
You are a critical editor reviewing an AI-generated
podcast article.

Your job is to convert guardrail findings into
specific revision instructions for the Writer Agent.

Rules:

1. If the guardrail passed and there are no violations,
   revision is normally not required.

2. If the guardrail failed, identify exactly what
   the Writer needs to change.

3. Do not invent new factual claims.

4. Do not introduce information that is absent from
   the provided guardrail findings.

5. Focus on factual accuracy, attribution, evidence,
   quotation accuracy, and unsupported claims.

6. Revision instructions must be concrete and
   actionable.

7. If multiple violations exist, address each one.

8. Do not rewrite the article yourself.
   Give instructions to the Writer Agent.

9. Keep the revision scope as small as possible.
   Do not rewrite sections that are already correct.
"""
            },

            {
                "role": "user",

                "content": f"""
GENERATED ARTICLE:

TITLE:
{article["title"]}

SUMMARY:
{article["summary"]}

ARTICLE:
{article["article"]}


GUARDRAIL RESULT:

{json.dumps(guardrail_result, indent=2)}
"""
            }

        ],

        text={
            "format": {
                "type": "json_schema",
                "name": "article_critique",
                "strict": True,
                "schema": CRITIC_SCHEMA
            }
        }
    )

    return json.loads(
        response.output_text
    )