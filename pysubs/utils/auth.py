import logging
from typing import Optional

import firebase_admin.auth
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from pysubs.utils.constants import LogConstants
from pysubs.utils.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(LogConstants.LOGGER_NAME)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    return user


def decode_token(token: str) -> Optional[User]:
    try:
        user = firebase_admin.auth.verify_id_token(token)
        return User(
            id=user.get("user_id"),
            email=user.get("email")
        )
    except (ValueError, firebase_admin.auth.InvalidIdTokenError) as e:
        logger.error(f"Invalid token received as part of the request. Error: {e}")
    except firebase_admin.auth.ExpiredIdTokenError as e:
        logger.error(f"Expired token received as part of the request. Error: {e}")
    except firebase_admin.auth.RevokedIdTokenError as e:
        logger.error(f"Revoked token received as part of the request. Error: {e}")
    except firebase_admin.auth.UserDisabledError as e:
        logger.error(f"User is disabled. Error: {e}")
