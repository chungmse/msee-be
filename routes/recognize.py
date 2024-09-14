from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/recognize", tags=["subject"])


@router.post("")
async def recognize(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "msg": "File uploaded successfully",
    }
