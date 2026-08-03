import time

from fastapi.responses import StreamingResponse

from llm import chain

from services.chat_service import (

    save_conversation

)

from services.eval_service import (

    evaluate_response

)


async def process_stream_chat(

        request,

        user

):

    async def generate():

        history = []

        from database import load_history

        history = load_history(

            request.session_id

        )

        start = time.time()

        full_response = ""

        async for chunk in chain.astream(

            {

                "input": request.message,

                "history": history

            }

        ):

            full_response += chunk

            yield f"data: {chunk}\n\n"

        duration = (

            time.time() - start

        ) * 1000

        chat_id = save_conversation(

            request.session_id,

            user,

            request.message,

            full_response,

            duration

        )

        evaluate_response(

            chat_id,

            request.message,

            full_response

        )

        yield "data: [DONE]\n\n"

    return StreamingResponse(

        generate(),

        media_type="text/event-stream"

    )