"""
Controller for notifications API and points
"""

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
import flask_restful #import Resource, abort
import marshmallow
from sqlalchemy.exc import SQLAlchemyError

import src.models as models
from src.database import db_session


class NotificationPutSchema(marshmallow.Schema):
    """
    Serialization schema for PUT notification
    """
    is_read = marshmallow.fields.Bool(required=True)


notification_put_schema = NotificationPutSchema()


class NotificationGetListSchema(marshmallow.Schema):
    """
    Serialization schema for GET notification
    """
    only_read = marshmallow.fields.Bool()
    only_unread = marshmallow.fields.Bool()
    before = marshmallow.fields.DateTime()
    after = marshmallow.fields.DateTime()


notification_get_list_schema = NotificationGetListSchema()


class Notification(flask_restful.Resource):
    """
    Notification controller for /api/v1/notifications/<notification_id> rout
    """
    @staticmethod
    @jwt_required
    def put(notification_id):
        """put request, changes is_read of notification.

        header
        jwt token

        request arguments:
        is_read -- if the notification has been viewed

        returns Notification
        """
        user_id = get_jwt_identity()
        json_data = request.get_json()
        if not json_data:
            flask_restful.abort(400, message='You must at least supply the boolean is_read as a request parameter.')
        data, errors = notification_put_schema.load(json_data)
        if errors:
            error_str = '\n'.join([f'{key}: {value}' for key, value in errors.items()])
            flask_restful.abort(400, message=error_str)
        notification_object = db_session.query(models.Notification).\
            filter(models.Notification.id == notification_id, models.Notification.user_id == user_id).one_or_none()
        if notification_object is None:
            flask_restful.abort(404, message='Notification not found for this user.')
        else:
            notification_object.is_read = data['is_read']

        try:
            db_session.commit()
            return {
                'id': notification_object.id,
                'user_id': notification_object.user_id,
                'created_at': notification_object.created_at.isoformat(),
                'category': notification_object.category,
                'text': notification_object.text,
                'data': notification_object.data,
                'is_read': notification_object.is_read
                }

        except SQLAlchemyError as ex:
            print(ex)
            db_session.rollback()
            flask_restful.abort(400, message="Database error for that data.")


class NotificationList(flask_restful.Resource):
    """
    Notification list controller for /api/v1/notifications rout
    """
    @staticmethod
    @jwt_required
    def get():
        """get request returns list of notifications.

        header
        jwt token

        request arguments:
        only_read = return only read
        only_unread = return only unread
        before = before date
        after = after date

        returns Notifications list
        """
        user_id = get_jwt_identity()
        json_data = request.args
        data, errors = notification_get_list_schema.load(json_data)
        if errors:
            error_str = '\n'.join([f'{key}: {value}' for key, value in errors.items()])
            flask_restful.abort(400, message=error_str)

        query = db_session.query(models.Notification).filter(models.Notification.user_id == user_id)
        if 'only_read' in data.keys():
            if data['only_read']:
                query = query.filter(models.Notification.is_read)
        if 'only_unread' in data.keys():
            if data['only_unread']:
                query = query.filter(models.Notification.is_read)
        if 'before' in data.keys():
            query = query.filter(models.Notification.created_at < data['before'])
        if 'after' in data.keys():
            query = query.filter(models.Notification.created_at > data['after'])

        return [{'id': notification.id,
                 'user_id': notification.user_id,
                 'created_at': notification.created_at.isoformat(),
                 'category': notification.category,
                 'text': notification.text,
                 'data': notification.data,
                 'is_read': notification.is_read}
                for notification in query.all()]
