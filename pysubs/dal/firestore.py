import threading
from datetime import datetime
from typing import Optional

import firebase_admin
from google.cloud import firestore
from pysubs.dal.datastore_models import MediaModel, SubtitleModel, MediaSubtitlesModel, UserModel
from pysubs.exceptions.firestore import UserNotFoundError
from pysubs.interfaces.datastore import Datastore


class FirestoreDatastore(Datastore):
    """
    Firestore app can be initialized once, so this class is made into a singleton
    All should access this class using the FirestoreDatastore.instance() method
    rather than using the default initializing method
    """
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
        """
        Initializing the app and creating the client
        """
        firebase_admin.initialize_app()
        self.db = firestore.Client()

    def upsert_media(self, media: MediaModel) -> MediaModel:
        """
        Upserts media data to the media collection and returns the upserted media model
        :param media:
        :return:
        """
        media_ref = self.db.collection('media').document(media.id)
        media_ref.set(media.dict())
        return media

    def upsert_user(self, user: UserModel) -> UserModel:
        """
        upserts the user data to the users collection and returns the upserted user model
        this is mainly used to update the credits of a user
        :param user:
        :return:
        """
        user_ref = self.db.collection('users').document(user.id)
        user_ref.set(user.dict(), merge=True)
        return user

    def upsert_subtitle(self, subtitle: SubtitleModel) -> SubtitleModel:
        """
        upserts the user data to the subtitles collection and returns the upserted subtitles model
        :param subtitle:
        :return:
        """
        subtitle_ref = self.db.collection('subtitles').document(subtitle.id)
        subtitle_ref.set(subtitle.dict())
        return subtitle

    def get_user(self, user_id: str) -> Optional[UserModel]:
        """
        queries the datastore for the user with the specified user id and returns user model if such a user exists.
        :param user_id:
        :return:
        """
        user_ref = self.db.collection('users').document(user_id)
        user = user_ref.get()
        if user.exists:
            return UserModel(**user.to_dict())
        else:
            raise UserNotFoundError(f"User with id: {user_id} was not found in firestore.")

    def get_subtitle_for_media(self, media_id: str) -> SubtitleModel:
        """
        queries the datastore for the subtitles for the given media.
        TODO: a media can have multiple subtitles, this method has to be updated to provision that later.
        :param media_id:
        :return:
        """
        subtitles = self.db.collection('subtitles').where("media_id", "==", media_id).stream()
        for s in subtitles:
            return SubtitleModel(**s.to_dict())

    def get_media(self, media_id: str) -> MediaModel:
        """
        queries the datastore for media with the given media id
        :param media_id:
        :return:
        """
        media = self.db.collection('media').document(media_id).get()
        if media.exists:
            return MediaModel(**media.to_dict())

    def get_history_for_user(
            self,
            user_id: str,
            last_created_at: Optional[datetime] = None,
            count: int = 100
    ) -> list[MediaSubtitlesModel]:
        """
        Gets the media entities with subtitles for a given user
        :param user_id:
        :param last_created_at:
        :param count:
        :return:
        """
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
