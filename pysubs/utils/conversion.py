import base64
import os
import tempfile
import uuid

from pysubs.exceptions.media import UnsupportedMediaConversionError
from pysubs.utils.ffmpeg_utils import ffmpeg_convert
from pysubs.utils.models import ConvertedFile, Media, MediaType


def convert_to_mp3(media: Media) -> ConvertedFile:
    """
    Conversion utility function to take the media object and convert the video to mp3 using ffmpeg
    :param media:
    :return:
    """
    if media.file_type != MediaType.MP4:
        raise UnsupportedMediaConversionError(f"Unsupported file type conversion tried. {media.file_type}")
    mp3_filename = f"{str(uuid.uuid4())}.mp3"
    temp_audio_filepath = os.path.join(tempfile.gettempdir(), mp3_filename)
    ffmpeg_convert(source=media.local_storage_path, dest=temp_audio_filepath, codec="mp3")
    return ConvertedFile(local_storage_path=temp_audio_filepath)


def get_base64_src_for_image(image_filepath: str) -> str:
    """
    Get the image file path, encodes to base64, and adds the url scheme
    so that it can directly be used as the thumbnail in the front end
    :param image_filepath:
    :return:
    """
    # Convert image to base 64 format and save it as url
    with open(image_filepath, "rb") as image_file:
        content = image_file.read()
        thumbnail_url = f"data:image/jpeg;base64,{base64.b64encode(content).decode()}"
    return thumbnail_url
