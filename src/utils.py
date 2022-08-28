"""
General utilities
"""

import base64
import datetime
from enum import Enum, auto
import os

import boto3
from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
import marshmallow
import requests.exceptions

from src import models
from src.database import db_session
from src.loggers import error_logger


class ImageTypes(Enum):
    """ Image type """

    user = auto()


def must_be_time_dict(data):
    """checks that data is days of the week"""
    try:
        if not sorted([key.lower() for key in data.keys()]) == sorted(
            [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
        ):
            raise marshmallow.ValidationError(
                "Must be an object with the days of the week as keys."
            )
    except Exception as error:
        print(error)
        raise marshmallow.ValidationError(
            "Must be an object with the days of the week as keys."
        )


def must_not_be_blank(data):
    """check of the data blank"""
    if not data:
        raise marshmallow.ValidationError("Data not provided.")


def must_be_comma_joined_ints(data):
    """checks for commas"""
    try:
        [int(object_id) for object_id in data.split(",")]
    except Exception as error:
        print(error)
        raise marshmallow.ValidationError("Data must be integers separated by commas.")


def datetime_number_str():
    """replaces '.' with '' in datetime """
    return str(datetime.datetime.utcnow().timestamp()).replace(".", "")


def save_jpeg_to_s3(item_type, item_id, input_str):
    """saves image to s3"""
    item_type_name = item_type.name
    base64_str = input_str.split(",", maxsplit=1)[1]

    project = os.environ["PROJECT"]  # e.g. 'boilerplate'
    environment = os.environ["ENVIRONMENT"]  # e.g. 'staging'
    aws_bucket_name = f"{project}-{environment}-user-data-files"

    path = f"{item_type_name}_images/{item_type_name}_{item_id}_image_{datetime_number_str()}.jpeg"
    s3_instance = boto3.client("s3")
    s3_instance.put_object(
        Bucket=aws_bucket_name,
        Key=path,
        Body=base64.b64decode(base64_str),
        ContentType="image/jpeg",
        ACL="public-read",
    )
    return f"{aws_bucket_name}.s3.amazonaws.com/{path}"


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, message, extra=None):
    """
    sends push notification

    requires:
    token
    message
    """
    response = None
    try:
        response = PushClient().publish(PushMessage(to=token, body=message, data=extra))
    except PushServerError as error:
        # Encountered some likely formatting/validation error.
        error_logger.exception(
            f"""
            error: {error}
            token: {token}
            message: {message}
            extra: {extra}
            errors: {error.errors}
            response_data: {error.response_data}
        """
        )
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
    ) as error:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        error_logger.exception("Connection error: Retrying")
        response = PushClient().publish(PushMessage(to=token, body=message, data=extra))

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        if response is not None:
            response.validate_response()
    except DeviceNotRegisteredError:
        # Get rid of the token
        user = (
            db_session.query(models.User)
            .filter(models.User.expo_push_token == token)
            .one()
        )
        user.expo_push_token = ""
        db_session.commit()
    except PushResponseError as error:
        # Encountered some other per-notification error.
        error_logger.exception(
            f"""
            token: {token}
            message: {message}
            extra: {extra}
            push_response: {error.push_response._asdict()}
        """
        )
