from database import get_connection


def get_request_logs(

        limit,

        offset

):

    conn = get_connection()

    rows = conn.execute(

        """

        SELECT *

        FROM request_logs

        ORDER BY id DESC

        LIMIT ?

        OFFSET ?

        """,

        (

            limit,

            offset

        )

    ).fetchall()

    total = conn.execute(

        """

        SELECT COUNT(*)

        FROM request_logs

        """

    ).fetchone()[0]

    conn.close()

    return {

        "total": total,

        "items": [

            dict(row)

            for row in rows

        ]

    }


def get_chat_logs(

        limit,

        offset

):

    conn = get_connection()

    rows = conn.execute(

        """

        SELECT

            c.id,

            c.session_id,

            c.user_key,

            c.user_message,

            c.ai_response,

            c.duration_ms,

            c.created_at,

            e.overall_score,

            e.eval_feedback

        FROM chat_logs c

        LEFT JOIN eval_logs e

        ON e.chat_log_id = c.id

        ORDER BY c.id DESC

        LIMIT ?

        OFFSET ?

        """,

        (

            limit,

            offset

        )

    ).fetchall()

    total = conn.execute(

        """

        SELECT COUNT(*)

        FROM chat_logs

        """

    ).fetchone()[0]

    conn.close()

    return {

        "total": total,

        "items": [

            dict(row)

            for row in rows

        ]

    }