import logging

from fastapi import FastAPI, Request

from pysubs.utils.constants import LogConstants
from pysubs.utils.models import GeneralResponse, Transcription
from pysubs.utils.pysubs_manager import process_yt_video_url_and_generate_subtitles

app = FastAPI()


@app.get("/health")
async def root():
    return {"status": "OK"}


@app.get("/upload")
async def upload_video() -> GeneralResponse:
    return GeneralResponse(status="OK", id="")


@app.get("/upload/yt")
async def upload_video_from_youtube() -> GeneralResponse:
    return GeneralResponse(status="OK", id="")


@app.post("/subtitles/yt/generate")
async def generate_subtitles_for_youtube(request: Request) -> GeneralResponse:
    json_data = await request.json()
    video_url = json_data.get("video_url")
    transcription: Transcription = process_yt_video_url_and_generate_subtitles(video_url=video_url)
    logging.getLogger(LogConstants.LOGGER_NAME).info(
        f"Transcribed Audio: \n{transcription.content}"
    )
    return GeneralResponse(status="OK", id=transcription.id)
