import base64
import os
import tempfile
import uuid

import ffmpeg

from pysubs.exceptions.media import DecodingMediaDurationError


def ffmpeg_convert(source: str, dest: str, codec: str):
    """
    converts source file using the codec and saves in the given destination path
    :param source:
    :param dest:
    :param codec:
    :return:
    """
    ffmpeg.input(source).output(dest, acodec=codec).run()


def get_media_duration(media_file_path: str) -> float:
    """
    gets the media file path and gets the media duration using ffmpeg
    :param media_file_path:
    :return:
    """
    media_details = ffmpeg.probe(media_file_path)
    try:
        duration = float(media_details["format"]["duration"])
    except (KeyError, ValueError, TypeError):
        raise DecodingMediaDurationError(f"Unknown error in decoding media duration: {media_details}")
    return duration


def create_thumbnail(media_file_path: str) -> str:
    """
    Creates the thumbnail from the video file using ffmpeg
    :param media_file_path:
    :return:
    """
    # Get thumbnail
    # https://github.com/kkroening/ffmpeg-python/blob/master/examples/README.md
    thumbnail_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    ffmpeg.input(
        thumbnail_path, ss=1
    ).filter(
        'scale', 300, -1
    ).output(
        "abc.jpg", vframes=1
    ).overwrite_output().run(quiet=True)
    return thumbnail_path
