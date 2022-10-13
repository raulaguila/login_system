from fastapi import APIRouter, Response, status
router = APIRouter()


@router.get('/', response_model=None)
async def root():

    return Response(status_code=status.HTTP_200_OK)
