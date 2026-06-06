import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response(messages) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=200
    )

    content = response.choices[0].message.content

    if content is None:
        return "I could not generate a response. Please try again."

    return content


def explain_code_result(code: str, result_text: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Python debugging assistant. "
                    "Explain code errors or outputs in simple beginner-friendly language. "
                    "If there is an error, explain the reason and how to fix it. "
                    "If there is output, explain why that output appeared."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here is the Python code:\n{code}\n\n"
                    f"Here is the output/error:\n{result_text}\n\n"
                    "Explain this clearly."
                )
            }
        ],
        temperature=0.3,
        max_tokens=300
    )

    content = response.choices[0].message.content

    if content is None:
        return "I could not explain the result. Please try again."

    return content

def get_rag_response(question: str, context: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Data Structures expert.\n"
                    "Answer using ONLY the given context.\n"
                    "Make answer structured:\n"
                    "- Definition\n"
                    "- Key points\n"
                    "- Example\n"
                    "- Applications\n"
                    "Do NOT be vague.\n"
                    "If answer not in context, say so."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ],
        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content