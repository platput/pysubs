import logging
import firebase_admin.auth
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from pysubs.dal.datastore_models import UserModel
from pysubs.dal.firestore import FirestoreDatastore
from pysubs.utils.constants import LogConstants

"""
Uses the bearer token to authenticate all the requests to the API endpoints
"""


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(LogConstants.LOGGER_NAME)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Gets the token and gets the corresponding user from firebase
    :param token:
    :return:
    """
    user = decode_token(token)
    user_id = user.get("user_id")
    ds_user = FirestoreDatastore.instance().get_user(user_id=user_id)
    return ds_user


def decode_token(token: str) -> dict:
    """
    Takes the token, decodes it and verifies the user account belonging to the token
    :param token:
    :return:
    """
    try:
        user = firebase_admin.auth.verify_id_token(token)
        return user
    except (ValueError, firebase_admin.auth.InvalidIdTokenError) as e:
        logger.error(f"Invalid token received as part of the request. Error: {e}")
    except firebase_admin.auth.ExpiredIdTokenError as e:
        logger.error(f"Expired token received as part of the request. Error: {e}")
    except firebase_admin.auth.RevokedIdTokenError as e:
        logger.error(f"Revoked token received as part of the request. Error: {e}")
    except firebase_admin.auth.UserDisabledError as e:
        logger.error(f"User is disabled. Error: {e}")
