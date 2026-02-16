# support_ai/llm_client.py

import os
from openai import OpenAI
from support_ai.system_prompt import SYSTEM_PROMPT


class LLMUnavailable(Exception):
   """
   Raised when the language model cannot be reached or fails safely.
   """
   pass


def _get_client() -> OpenAI:
   """
   Creates a new OpenAI client instance.
   The client is intentionally lightweight and stateless.
   """
   api_key = os.getenv("OPENAI_API_KEY")
   if not api_key:
       raise LLMUnavailable("OpenAI API key is not configured.")

   return OpenAI(api_key=api_key)


def get_ai_response(*, context: dict) -> str:
   """
   Generates a support response using a locked system prompt
   and a deterministic context payload.

   This function:
   - does NOT infer intent
   - does NOT mutate state
   - does NOT store memory
   - does NOT retry
   - does NOT log
   - does NOT decide anything

   It returns plain text only.
   """

   try:
       client = _get_client()

       response = client.responses.create(
           model="gpt-4.1-mini",
           input=[
               {
                   "role": "system",
                   "content": SYSTEM_PROMPT,
               },
               {
                   "role": "user",
                   "content": (
                       "Use the following context to answer factually and within constraints.\n\n"
                       f"{context}"
                   ),
               },
           ],
           temperature=0.0,
           max_output_tokens=600,
       )

       return response.output_text.strip()

   except Exception as exc:
       raise LLMUnavailable(
           "Support AI is temporarily unavailable. "
           "This does not affect enforcement or system operation."
       ) from exc