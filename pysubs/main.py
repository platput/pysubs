import logging
import re
from datetime import timedelta
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from pysubs.dal.firestore import FirestoreDatastore
from pysubs.utils.auth import decode_token, get_current_user
from pysubs.utils.constants import LogConstants
from pysubs.utils.settings import PySubsSettings
from pysubs.utils.models import GeneralResponse, VideoMetadataResponse, User, SubtitleResponse, HistoryResponse
from pysubs.utils.pysubs_manager import start_transcribe_worker, get_subtitle_generation_status, get_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(LogConstants.LOGGER_NAME)
PySubsSettings.instance()
FirestoreDatastore.instance()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def root():
    return {"status": "OK"}


@app.get("/upload")
async def upload_video() -> GeneralResponse:
    return GeneralResponse(status="OK")


@app.get("/yt/info")
async def get_yt_video_metadata(request: Request, user: User = Depends(decode_token)) -> GeneralResponse:
    json_data = await request.json()
    video_url = json_data.get("video_url")
    return VideoMetadataResponse(
        status="OK",
        video_url=video_url,
        title="",
        video_length=timedelta(hours=1).seconds,
        thumbnail="https://yt.be/test.jpg",
    )


@app.post("/subtitle/status")
async def get_status(
        request: Request,
        user: User = Depends(get_current_user)
) -> SubtitleResponse:
    logger.info(f"User found in token: {user}")
    json_data = await request.json()
    video_url = json_data.get("video_url")
    if verify_url(video_url):
        media, subtitle = get_subtitle_generation_status(video_url=video_url, user=user)
        if media and subtitle:
            return SubtitleResponse(
                status="OK",
                subtitle_id=subtitle.id,
                video_id=media.id,
                video_url=media.media_url,
                title=media.title,
                video_length=media.duration,
                thumbnail=media.thumbnail_url,
                subtitle=subtitle.content,
                created_at=subtitle.created_at
            )
        else:
            return SubtitleResponse(status="pending")
    else:
        raise HTTPException(status_code=403, detail="Invalid URL")


@app.post("/subtitles/yt/generate")
async def generate_subtitles_for_youtube(
        request: Request,
        user: User = Depends(get_current_user)
) -> GeneralResponse:
    json_data = await request.json()
    video_url = json_data.get("video_url")
    if verify_url(video_url):
        start_transcribe_worker(video_url=video_url, user=user)
        return GeneralResponse(status="OK")
    else:
        raise HTTPException(status_code=403, detail="Invalid URL")


@app.post("/history")
async def generate_subtitles_for_youtube(
        request: Request,
        user: User = Depends(get_current_user)
) -> HistoryResponse:
    json_data = await request.json()
    last_created_at = json_data.get("last_created_at")
    if count := json_data.get("count"):
        count = int(count)
    subtitles = get_history(last_created_at=last_created_at, count=count, user=user)
    return HistoryResponse(status="OK", subtitles=subtitles)


def verify_url(url: str):
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")
    p = re.compile(regex)
    return re.search(p, url)
