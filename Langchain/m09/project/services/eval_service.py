from llm import eval_chain

from database import save_eval


def evaluate_response(
    chat_id: int,
    question: str,
    answer: str
):

    try:

        score = eval_chain.invoke(

            {

                "question": question,

                "answer": answer

            }

        )

        overall = round(

            (

                score.get("relevance", 0)

                + score.get("coherence", 0)

                + score.get("conciseness", 0)

            )

            / 3,

            2

        )

        score["overall"] = overall

        save_eval(chat_id, score)

        return overall

    except Exception as e:

        print("Evaluation Error :", e)

        return None