import os
import threading
from dotenv import load_dotenv, find_dotenv
from pysubs.utils.constants import EnvConstants


class PySubsSettings:
    __singleton_instance = None
    __singleton_lock = threading.Lock()
    defaults = {
        EnvConstants.VIDEO_MANAGER: EnvConstants.YOUTUBE
    }

    def __init__(self):
        load_dotenv(find_dotenv())

    @classmethod
    def instance(cls) -> "PySubsSettings":
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    @staticmethod
    def get_config(key):
        return os.getenv(key) if os.getenv(key) else PySubsSettings.defaults.get(key)
