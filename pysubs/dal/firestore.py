import threading
from datetime import datetime
from typing import Optional

import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from pysubs.dal.datastore_models import MediaModel, SubtitleModel, MediaSubtitlesModel, UserModel
from pysubs.exceptions.firestore import UserNotFoundError
from pysubs.interfaces.datastore import Datastore
from pysubs.utils.settings import PySubsSettings


class FirestoreDatastore(Datastore):
    __singleton_instance = None
    __singleton_lock = threading.Lock()

    @classmethod
    def instance(cls) -> "FirestoreDatastore":
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    def __init__(self):
        self.db = firestore.Client()
        cred = credentials.Certificate(PySubsSettings.instance().get_config("GOOGLE_APPLICATION_CREDENTIALS"))
        firebase_admin.initialize_app(cred)

    def upsert_media(self, media: MediaModel) -> MediaModel:
        media_ref = self.db.collection('media').document(media.id)
        media_ref.set(media.dict())
        return media

    def upsert_user(self, user: UserModel) -> UserModel:
        user_ref = self.db.collection('users').document(user.id)
        user_ref.set(user.dict(), merge=True)
        return user

    def upsert_subtitle(self, subtitle: SubtitleModel) -> SubtitleModel:
        subtitle_ref = self.db.collection('subtitles').document(subtitle.id)
        subtitle_ref.set(subtitle.dict())
        return subtitle

    def get_user(self, user_id: str) -> Optional[UserModel]:
        user_ref = self.db.collection('users').document(user_id)
        user = user_ref.get()
        if user.exists:
            return UserModel(**user.to_dict())
        else:
            raise UserNotFoundError(f"User with id: {user_id} was not found in firestore.")

    def get_subtitle_for_media(self, media_id: str) -> SubtitleModel:
        subtitles = self.db.collection('subtitles').where("media_id", "==", media_id).stream()
        for s in subtitles:
            return SubtitleModel(**s.to_dict())

    def get_media(self, media_id: str) -> MediaModel:
        media = self.db.collection('media').document(media_id).get()
        if media.exists:
            return MediaModel(**media.to_dict())

    def get_history_for_user(
            self,
            user_id: str,
            last_created_at: Optional[datetime] = None,
            count: int = 100
    ) -> list[MediaSubtitlesModel]:
        media_subtitles: list[MediaSubtitlesModel] = []
        ordered_medias = self.db.collection(
            'media'
        ).where(
            "user_id", "==", user_id
        ).order_by(
            "created_at", direction=firestore.Query.DESCENDING
        )
        if last_created_at:
            medias = ordered_medias.start_after({
                u'created_at': last_created_at
            }).limit(
                count
            ).stream()
        else:
            medias = ordered_medias.limit(
                count
            ).stream()
        for m in medias:
            media: MediaModel = MediaModel(**m.to_dict())
            subtitles: list[SubtitleModel] = []
            subtitles_ref = self.db.collection('subtitles').where("media_id", "==", m.id).stream()
            for sub in subtitles_ref:
                subtitle: SubtitleModel = SubtitleModel(**sub.to_dict())
                subtitles.append(subtitle)
            media_subtitles.append(MediaSubtitlesModel(media=media, subtitles=subtitles))
        return media_subtitles
