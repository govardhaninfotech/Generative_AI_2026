from fastapi import (

    APIRouter,

    Depends

)

from auth import verify_api_key

from services.log_service import (

    get_request_logs,

    get_chat_logs

)


router = APIRouter(

    tags=["Logs"]

)


@router.get(

    "/logs"

)

def logs(

    limit: int = 20,

    offset: int = 0,

    user=Depends(

        verify_api_key

    )

):

    return get_request_logs(

        limit,

        offset

    )


@router.get(

    "/logs/chat"

)

def chat_logs(

    limit: int = 20,

    offset: int = 0,

    user=Depends(

        verify_api_key

    )

):

    return get_chat_logs(

        limit,

        offset

    )