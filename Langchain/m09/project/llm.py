from langchain_groq import ChatGroq

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser
)

from config import MODEL


# =====================================================
# System Prompt
# =====================================================

SYSTEM_PROMPT = """
You are an expert AI assistant for a FastAPI and LangChain course.

Rules:

1. Give short and accurate answers.

2. If code is requested, return clean Python code.

3. Explain concepts simply.

4. Be helpful and professional.

"""


# =====================================================
# Main Chat Model
# =====================================================

llm = ChatGroq(

    model=MODEL,

    temperature=0.7,

    max_retries=3

)


# =====================================================
# Evaluation Model
# =====================================================

eval_llm = ChatGroq(

    model=MODEL,

    temperature=0.1,

    max_retries=3

)


# =====================================================
# Evaluation Prompt
# =====================================================

evaluation_prompt = ChatPromptTemplate.from_messages(

    [

        (
            "system",
            "You are an AI evaluator. Return ONLY JSON."
        ),

        (

            "human",

            """
Question:

{question}

Answer:

{answer}

Return this format only

{
    "relevance":0.0,
    "coherence":0.0,
    "conciseness":0.0,
    "feedback":""
}
"""

        )

    ]

)


# =====================================================
# Evaluation Chain
# =====================================================

eval_chain = (

    evaluation_prompt

    |

    eval_llm

    |

    JsonOutputParser()

)


# =====================================================
# Chat Prompt
# =====================================================

chat_prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            SYSTEM_PROMPT

        ),

        MessagesPlaceholder(

            variable_name="history"

        ),

        (

            "human",

            "{input}"

        )

    ]

)


# =====================================================
# Main Chat Chain
# =====================================================

chain = (

    chat_prompt

    |

    llm

    |

    StrOutputParser()

)