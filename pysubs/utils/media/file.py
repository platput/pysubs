import os.path
import tempfile
from datetime import timedelta, datetime
from typing import Optional

from fastapi import UploadFile
from pysubs.exceptions.media import UnsupportedMediaConversionError
from pysubs.interfaces.media import MediaManager
from pysubs.utils import file_helper
from pysubs.utils import conversion
from pysubs.utils import ffmpeg_utils
from pysubs.utils.models import MediaType, Media, ConvertedFile, MediaSource


class FileMediaManager(MediaManager):
    """
    Class to handle file uploads and subtitle generation for uploaded video files.
    """
    def upload(self, media: Media) -> Media:
        pass

    def get_media_info(self, video_url: Optional[str] = None, video_file: Optional[UploadFile] = None) -> Media:
        """
        Gets the media info.
        TODO: Use this function to get information about the video and raise exception
        if the uploaded file is unsupported
        :param video_url:
        :param video_file:
        :return:
        """
        file = video_file.file
        content = file.read()
        file.close()
        temp_dir = tempfile.gettempdir()
        uploaded_filename = os.path.splitext(video_file.filename)
        current_timestamp = int(round(datetime.now().timestamp()))
        # Sanitizing the user inputted filename
        # TODO: To be improved later using regex
        sanitized_filename = uploaded_filename[0].replace("&", "").replace(" ", "_").replace("|", "").replace(";", "").replace("-", "_")
        sanitized_ext = uploaded_filename[1].replace("&", "").replace(" ", "_").replace("|", "").replace(";", "").replace("-", "_")
        video_filename = f"{sanitized_filename}-{current_timestamp}{sanitized_ext}"
        local_storage_path = os.path.join(temp_dir, video_filename)
        file_helper.write_content_to_file(local_storage_path=local_storage_path, file_content=content)
        duration = ffmpeg_utils.get_media_duration(media_file_path=local_storage_path)
        thumbnail_path = ffmpeg_utils.create_thumbnail(media_file_path=local_storage_path)
        base64_url = conversion.get_base64_src_for_image(image_filepath=thumbnail_path)
        return Media(
            id=None,
            title=os.path.basename(local_storage_path),
            thumbnail_url=base64_url,
            duration=timedelta(seconds=duration),
            content=None,
            source=MediaSource.RAW_FILE,
            file_type=MediaType.MP4,
            local_storage_path=local_storage_path,
            source_url=local_storage_path,
        )

    def download(self, media: Media) -> Media:
        """
        Nothing to do as the file has been uploaded to the server
        :param media:
        :return:
        """
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        """
        Converts the video to mo3 file for further processing
        :param media:
        :param to_type:
        :return:
        """
        if to_type != MediaType.MP3:
            raise UnsupportedMediaConversionError(f"Converting to {to_type} is not supported at this moment.")
        converted: ConvertedFile = conversion.convert_to_mp3(media=media)
        converted_media = Media(
            id=media.id,
            title=media.title,
            content=None,
            duration=media.duration,
            source=media.source,
            file_type=to_type,
            local_storage_path=converted.local_storage_path,
            source_url=media.source_url,
            thumbnail_url=media.thumbnail_url
        )
        return converted_media
