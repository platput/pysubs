import threading
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from pysubs.dal.datastore_models import MediaModel, SubtitleModel
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

    def upsert_subtitle(self, subtitle: SubtitleModel) -> SubtitleModel:
        subtitle_ref = self.db.collection('subtitles').document(subtitle.id)
        subtitle_ref.set(subtitle.dict())
        return subtitle

    def get_subtitle_for_media(self, media_id: str) -> SubtitleModel:
        subtitles = self.db.collection('subtitles').where("media_id", "==", media_id).stream()
        for s in subtitles:
            return SubtitleModel(**s.to_dict())

    def get_media(self, media_id: str) -> MediaModel:
        media = self.db.collection('media').document(media_id).get()
        if media.exists:
            return MediaModel(**media.to_dict())
