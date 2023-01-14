import logging
from datetime import timedelta
from fastapi import FastAPI, Request
from pysubs.utils.settings import PySubsSettings
from pysubs.utils.models import GeneralResponse, VideoMetadataResponse, User
from pysubs.utils.pysubs_manager import start_transcribe_worker

logging.basicConfig(level=logging.INFO)

PySubsSettings.instance()

app = FastAPI()


@app.get("/health")
async def root():
    return {"status": "OK"}


@app.get("/upload")
async def upload_video() -> GeneralResponse:
    return GeneralResponse(status="OK")


@app.get("/yt/info")
async def get_yt_video_metadata(request: Request) -> GeneralResponse:
    json_data = await request.json()
    video_url = json_data.get("video_url")
    return VideoMetadataResponse(
        status="OK",
        video_url=video_url,
        title="",
        video_length=timedelta(hours=1),
        thumbnail=b"",
    )


@app.post("/subtitles/yt/generate")
async def generate_subtitles_for_youtube(request: Request) -> GeneralResponse:
    json_data = await request.json()
    video_url = json_data.get("video_url")
    user = User(id=None)
    start_transcribe_worker(video_url=video_url, user=user)
    return GeneralResponse(status="OK")
