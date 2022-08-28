"""
Controller for user API endpoints
"""

import datetime

from argon2 import PasswordHasher
from flask import request
import flask_jwt_extended
import flask_restful
import marshmallow
import requests
import json

import src.models as models
from src.database import db_session
from src.utils import must_not_be_blank, \
    must_be_comma_joined_ints, \
    save_jpeg_to_s3, \
    ImageTypes

ph = PasswordHasher(hash_len=64, salt_len=32)


class UserSchema(marshmallow.Schema):
    """
    Schema to be used for single user endpoints.
    This would be where you select a single user by a unique identifier
    """
    pass


class User(flask_restful.Resource):
    """
    TODO (Kirill): What is it?
    """

    def get(self, user_id):
        """ GET request """
        pass

    def put(self, user_id):
        """ PUT request """
        pass

    def delete(self, user_id):
        """ DELETE request """
        pass


class UserPostListSchema(marshmallow.Schema):
    """
    Serialization schema for user post list
    """
    id = marshmallow.fields.Int()
    email = marshmallow.fields.Str(required=True, validate=must_not_be_blank)
    handle = marshmallow.fields.Str(required=True, validate=must_not_be_blank)
    password = marshmallow.fields.Str(required=True, validate=must_not_be_blank)
    name = marshmallow.fields.Str()
    image_url = marshmallow.fields.Str()
    image_is_local = marshmallow.fields.Bool()
    expo_push_token = marshmallow.fields.Str()
    created_at = marshmallow.fields.DateTime()
    recaptcha = marshmallow.fields.Str()


user_post_list_schema = UserPostListSchema()


class UserPutListSchema(marshmallow.Schema):
    """
    Serialization schema for user put list
    """
    email = marshmallow.fields.Str()
    handle = marshmallow.fields.Str()
    password = marshmallow.fields.Str()
    name = marshmallow.fields.Str()
    image_url = marshmallow.fields.Str()
    image_is_local = marshmallow.fields.Bool()
    expo_push_token = marshmallow.fields.Str()


user_put_list_schema = UserPutListSchema()


class UserGetListSchema(marshmallow.Schema):
    """
    Serialization schema for user get list
    """
    id = marshmallow.fields.Int()
    id_list = marshmallow.fields.Str(validate=must_be_comma_joined_ints)
    email = marshmallow.fields.Str()
    handle = marshmallow.fields.Str()
    name = marshmallow.fields.Str()
    single_user = marshmallow.fields.Bool(required=True)


user_get_list_schema = UserGetListSchema()


class UserList(flask_restful.Resource):
    """
    User list controller that handles /api/v1/users route
    """

    @staticmethod
    def post():
        """
        post json data, creates user

        required arguments:
        email -- the users email
        handle -- username
        password -- the users password
        name -- users name
        image_url -- url of profile? image
        image_is_local -- boolean, I'm guessing use a default image on server


        returns valid user information,
        :return user data
        :rtype: dict
        """
        # load json
        json_data = json.loads(request.data.decode('utf-8'))  # type: dict
        if not json_data:
            flask_restful.abort(400, message='There was no json data provided.')

        # pass to UserPostListSchema serializer instance
        user_post_list_schema = UserPostListSchema()
        data, errors = user_post_list_schema.load(json_data)

        # check for errors
        if errors:
            error_str = '\n'.join([f"{key}: {value}" for key, value in errors.items()])
            flask_restful.abort(400, message=error_str)

        # check to see if email already exists
        if db_session.query(models.User).filter(models.User.email == data['email']).one_or_none():
            flask_restful.abort(400, message="That email is already in use")

        google_verification_request = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                                    data={
                                                        'secret': "6Ld9GVcUAAAAAPmo5NhMWzra3oIkwBBvfZSWzMyD",
                                                        'response': data.get('recaptcha', ''),
                                                        'remoteip': request.remote_addr
                                                    },
                                                    allow_redirects=True)

        if not bool(google_verification_request.json()["success"]):
            flask_restful.abort(400, message="You're probably a bot.")

        # TODO check if handle exists?

        new_user = models.User(name=data.get('name', ''),
                               email=data.get('email'),
                               handle=data.get('handle', ''),
                               password_hash=ph.hash(data['password']),
                               image_url=data.get('image_url', ''),
                               # expo_push_token=data.get('expo_push_token', ''),
                               created_at=datetime.datetime.utcnow())

        db_session.add(new_user)
        db_session.flush()  # Flushing here because we need the id

        # new_user.image_url = save_jpeg_file(ImageTypes['user'], new_user.id, data['image_url'])

        try:
            db_session.commit()
        # TODO (Kirill): Not quite sure what type of exceptions are we trying to catch here.
        # Can we be more specific about it?
        except Exception as ex:
            print(ex)
            db_session.rollback()
            flask_restful.abort(400, message="Database Error")

        # if all goes to plan lets make an access token
        access_token = flask_jwt_extended.create_access_token(identity=new_user.id)  # type: str

        return {
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'handle': new_user.handle,
                'email': new_user.email,
                'name': new_user.name,
                'image_url': new_user.image_url,
                # 'expo_push_token': new_user.expo_push_token, TODO fix
                'created_at': new_user.created_at.isoformat()
            }
        }

    @staticmethod
    @flask_jwt_extended.jwt_required
    def put():
        """put edits user information.
        load json, pass to UserPutListSchema serializer instance

        header
        jwt token

        arguments:
        email -- the users email, checks for duplicates if True returns 404
        handle -- username
        password -- the users password
        name -- users name
        image_is_local -- boolean


        returns valid user information,
        """
        json_data = json.loads(request.data.decode('utf-8'))  # type: dict
        if not json_data:
            flask_restful.abort(400, message='There was no json data provided.')
        data, errors = user_put_list_schema.load(json_data)

        # check for errors
        if errors:
            error_str = '\n'.join([f"{key}: {value}" for key, value in errors.items()])
            flask_restful.abort(400, message=error_str)

        # make sure user exists
        user = db_session.query(models.User).filter(models.User.id == flask_jwt_extended.get_jwt_identity()).one()
        if 'email' in data.keys():
            email = data['email']
            # email_check_result = db_session.query(models.User).filter(models.User.email == email).one_or_none()
            # if email_check_result is not None:
            #    flask_restful.abort(400, message='That email is already in use.')
            user.email = email

        if 'handle' in data.keys():
            user.handle = data['handle']

        if 'image_is_local' in data.keys() and 'image_url' in data.keys():
            local = data['image_is_local']
            if not local:
                flask_restful.abort(400, message="For now I'm only handling uploads.")
            user.image_url = save_jpeg_to_s3(ImageTypes['user'], user.id, data['image_url'])

        if 'name' in data.keys():
            user.name = data['name']

        if 'password' in data.keys():
            password_hash = ph.hash(json_data['password'])
            user.password_hash = password_hash

        if 'handle' in data.keys():
            user.handle = data['handle']

        if 'expo_push_token' in data.keys():
            user.expo_push_token = data['expo_push_token']

        try:
            db_session.commit()

            # if all goes to plan lets make an access token
            access_token = flask_jwt_extended.create_access_token(identity=user.id)  # type: str

            return {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'handle': user.handle,
                    'name': user.name,
                    'image_url': user.image_url,
                    # 'availability': user.availability,
                    # 'expo_push_token': user.expo_push_token,  # TODO: Fix
                    "created_at": user.created_at.isoformat()
                }
            }

        # TODO (Kirill): Not quite sure what type of exceptions are we trying to catch here.
        # Can we be more specific about it?
        except Exception as ex:
            print(ex)
            db_session.rollback()
            flask_restful.abort(400, message="Database error")

    @staticmethod
    @flask_jwt_extended.jwt_required
    def get():
        users = db_session.query(models.User).all()
        user_get_list_schema = UserGetListSchema()
        return user_get_list_schema.dump(users, many=True)
        """get returns list of users

        header
        jwt token

        arguments
        id_list -- list of user.id's
        email -- email to search
        handle -- handle to search
        name -- name to search
        single_user -- bool if you want one user (required)

        returns list of users
        """
        '''
        # load json
        json_data = request.args
        if not json_data:
            flask_restful.abort(400, message='You must at least supply the boolean single_user as a request parameter.')

        # pass data to serializer
        user_get_list_schema = UserGetListSchema()
        data, errors = user_get_list_schema.load(json_data)

        # check for errors
        if errors:
            error_str = '\n'.join([f'{key}: {value}' for key, value in errors.items()])
            flask_restful.abort(400, message=error_str)

        requesting_user_id = flask_jwt_extended.get_jwt_identity()  # user id or None
        user_query = db_session.query(models.User)

        if data['single_user']:
            if 'id' in data.keys() or 'email' in data.keys() or 'handle' in data.keys():
                if 'id' in data.keys():
                    user_query = user_query.filter(models.User.id == data['id'])
                if 'email' in data.keys():
                    user_query = user_query.filter(models.User.email == data['email'])
                if 'handle' in data.keys():
                    user_query = user_query.filter(models.User.handle == data['handle'])
            else:
                user_query = user_query.filter(models.User.id == requesting_user_id)
        else:
            if 'id_list' in data.keys():
                id_list = [int(object_id) for object_id in data['id_list'].split(',')]
                user_query = user_query.filter(models.User.id.in_(id_list))
            else:
                flask_restful.abort(400, message='You cant have all the users. Use a string of comma separated IDs for the id_list.')

        user_query_result = user_query.all()

        return [{'id': user.id,
                 'email': user.email,
                 'handle': user.handle,
                 'name': user.name,
                 'image_url': user.image_url,
                #  'expo_push_token': user.expo_push_token,  # TODO: Fix
                 'created_at': user.created_at.isoformat()}
                for user in user_query_result]
        '''
