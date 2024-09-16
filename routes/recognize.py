from fastapi import APIRouter, File, UploadFile, Body
from pydantic import BaseModel
import os
import random
import string
from libs.mongo import jobs, songs
from libs.rabbitmq import RabbitMQ
from bson import ObjectId

router = APIRouter(prefix="/recognize", tags=["recognize"])


@router.post("/upload")
async def recognize(file: UploadFile = File(...)):
    contents = await file.read()
    job_id = jobs.insert_one({"status": "new"}).inserted_id
    file_path = os.path.join("tmp", f"{str(job_id)}.wav")
    file_path = os.path.abspath(file_path)
    with open(file_path, "wb") as f:
        f.write(contents)
    secret_token = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    jobs.update_one(
        {"_id": job_id}, {"$set": {"status": "waiting", "token": secret_token}}
    )
    rabbitmq = RabbitMQ()
    rabbitmq.connect()
    rabbitmq.publish({"job_id": str(job_id)})
    rabbitmq.close()
    return {
        "job_id": str(job_id),
        "token": secret_token,
    }


class ResultRequest(BaseModel):
    job_id: str
    token: str


@router.post("/result")
async def result(request_data: ResultRequest = Body(...)):
    job_id = request_data.job_id
    token = request_data.token
    job = jobs.find_one({"_id": ObjectId(job_id), "token": token})
    if job is None:
        return {
            "err": 1,
            "msg": "Job not found",
        }

    if job["status"] != "completed":
        return {
            "err": 2,
            "msg": "Job is not completed",
        }

    list_result = []
    for result in job["result"]:
        this_song = songs.find_one({"idn": int(result["song_idn"])})
        song_info = {
            "score": result["score"],
        }
        if this_song is not None:
            song_info["_id"] = str(this_song["_id"])
            song_info["idn"] = this_song["idn"]
            song_info["encodeId"] = this_song["encodeId"]
            song_info["title"] = this_song["title"]
            song_info["artistsNames"] = this_song["artistsNames"]
            song_info["category"] = this_song["category"]
            song_info["duration"] = int(this_song["duration"])
            song_info["link"] = "https://zingmp3.vn" + this_song["link"]
            song_info["releaseDate"] = this_song["releaseDate"]
            song_info["thumbnailM"] = this_song["thumbnailM"]
            song_info["mp3url"] = (
                "https://msee-api.mse19hn.com/static/music/"
                + str(this_song["_id"])
                + ".mp3"
            )
            list_result.append(song_info)

    return {
        "list_result": list_result,
        "processing_time": job["processing_time"],
    }
