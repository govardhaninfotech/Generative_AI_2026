import time

from config import MODEL

from database import (
    load_history,
    save_message,
    save_chat
)

from llm import chain

from services.eval_service import evaluate_response

from models import ChatResponse


def generate_reply(message, history):

    return chain.invoke(

        {

            "input": message,

            "history": history

        }

    )


def save_conversation(

        session_id,

        user,

        question,

        answer,

        duration

):

    save_message(

        session_id,

        "user",

        question

    )

    save_message(

        session_id,

        "assistant",

        answer

    )

    return save_chat(

        session_id,

        user,

        question,

        answer,

        MODEL,

        0,

        0,

        round(duration, 2)

    )


def process_chat(

        request,

        user

):

    history = load_history(

        request.session_id

    )

    start = time.time()

    reply = generate_reply(

        request.message,

        history

    )

    duration = (

        time.time() - start

    ) * 1000

    chat_id = save_conversation(

        request.session_id,

        user,

        request.message,

        reply,

        duration

    )

    score = evaluate_response(

        chat_id,

        request.message,

        reply

    )

    return ChatResponse(

        session_id=request.session_id,

        user_message=request.message,

        ai_response=reply,

        model_used=MODEL,

        duration_ms=round(duration, 2),

        eval_score=score

    )