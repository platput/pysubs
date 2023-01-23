import hashlib
import json
import os.path
import tempfile
import uuid
from collections import OrderedDict
from datetime import timedelta
from typing import Optional

from fastapi import UploadFile

from pysubs.dal.datastore_models import UserModel
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
    @staticmethod
    def create_media(video_source: Optional[str | UploadFile], user: UserModel) -> Media:
        """
        Creates the media object which can be passed around until the subtitle is generated
        :param video_source:
        :param user:
        :return:
        """
        media = Media(
            id=None,
            source=MediaSource.RAW_FILE,
            file_type=MediaType.MP4,
            source_file=video_source
        )
        media.id = FileMediaManager.generate_media_id(media=media, user=user)
        return media

    @staticmethod
    def generate_media_id(media: Media, user: UserModel) -> str:
        """
        Generates the media id using the user and the video url
        :param media:
        :param user:
        :return:
        """
        unique_file_id = FileMediaManager.make_filename_unique(media.source_file.filename)
        key_helper_dict = OrderedDict({
            "unique_file_id": unique_file_id,
            "user_id": user.id
        })
        key_helper = json.dumps(key_helper_dict).encode("utf-8")
        return hashlib.sha256(key_helper).hexdigest()

    def upload(self, media: Media) -> Media:
        pass

    def get_media_info(
            self,
            media: Media,
            user: UserModel
    ) -> Media:
        """
        Gets the media info.
        TODO: Use this function to get information about the video and raise exception
        if the uploaded file is unsupported
        :param media:
        :param user:
        :return:
        """
        file = media.source_file.file
        content = file.read()
        temp_dir = tempfile.gettempdir()
        video_filename = FileMediaManager.make_filename_unique(filename=media.source_file.filename)
        local_storage_path = os.path.join(temp_dir, video_filename)
        file_helper.write_content_to_file(local_storage_path=local_storage_path, file_content=content)
        file.close()
        duration = ffmpeg_utils.get_media_duration(media_file_path=local_storage_path)
        thumbnail_path = ffmpeg_utils.create_thumbnail(media_file_path=local_storage_path)
        base64_url = conversion.get_base64_src_for_image(image_filepath=thumbnail_path)
        return Media(
            id=FileMediaManager.generate_media_id(media=media, user=user),
            title=os.path.basename(local_storage_path),
            thumbnail_url=base64_url,
            duration=timedelta(seconds=duration),
            content=None,
            source=MediaSource.RAW_FILE,
            file_type=MediaType.MP4,
            local_storage_path=local_storage_path,
            source_url=local_storage_path,
        )

    @staticmethod
    def make_filename_unique(filename: str) -> str:
        # TODO: To be improved later using regex
        uploaded_filename = os.path.splitext(filename)
        # Sanitizing the user inputted filename
        sanitized_filename = uploaded_filename[0].replace(
            "&", ""
        ).replace(
            " ", "_"
        ).replace("|", "").replace(";", "").replace("-", "_")
        sanitized_ext = uploaded_filename[1].replace(
            "&", ""
        ).replace(" ", "_").replace("|", "").replace(";", "").replace("-", "_")
        unique_filename = f"{sanitized_filename}-{uuid.uuid4().hex}{sanitized_ext}"
        return unique_filename

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
