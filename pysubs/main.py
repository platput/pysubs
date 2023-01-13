from fastapi import FastAPI

from pysubs.utils.models import GeneralResponse

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


@app.get("/subtitles/yt/generate")
async def generate_subtitles_for_youtube(video_url: str) -> GeneralResponse:
    return GeneralResponse(status="OK", id="")
