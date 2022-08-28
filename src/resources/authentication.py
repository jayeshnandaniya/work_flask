"""
User auth logic
"""

import argon2
import json
import requests
from datetime import datetime

from flask import request
import flask_jwt_extended
import flask_restful
import marshmallow
from sqlalchemy.exc import SQLAlchemyError

import src.models as models
from src.database import db_session
from src.utils import must_not_be_blank
from src.credentials import get_creds


class AuthSchema(marshmallow.Schema):
    """
    Serialization schema for auth fields
    """
    email = marshmallow.fields.Str(required=True, validate=must_not_be_blank)
    password = marshmallow.fields.Str(required=True, validate=must_not_be_blank)


auth_schema = AuthSchema()
ph = argon2.PasswordHasher(hash_len=64, salt_len=32)


class JWTDistributor(flask_restful.Resource):
    """
        Class responsible for giving a JWT in response to a valid email/password combo.
    """
    @staticmethod
    def post():
        """
            post returns valid token.
            recieves email and password through request.get_json(), verifies, and passes an access token

            request arguments:
            email -- the users email
            password -- the users password

            returns valid jwt token
            :return a jwt access token
            :rtype: str
        """
        # load json, pass to AuthSchema serializer instance
        json_data = json.loads(request.data.decode('utf-8'))  # type: dict
        if not json_data:
            flask_restful.abort(400, message='There was no json data provided.')
        data, errors = auth_schema.load(json_data)

        # check for errors
        if errors:
            error_str = '\n'.join([f"{key}: {value}" for key, value in errors.items()])
            flask_restful.abort(400, message=error_str)

        # check to see if a user with this email exists
        user = db_session.query(models.User).filter(models.User.email == data['email']).one_or_none()
        if user is None:
            flask_restful.abort(400, message='There is no such user')

        # check password
        try:
            ph.verify(user.password_hash, data['password'])
        except argon2.exceptions.VerifyMismatchError:
            flask_restful.abort(400, message='Incorrect password.')

        # if all goes to plan lets make an access token
        access_token = flask_jwt_extended.create_access_token(identity=user.id)  # type: str

        return {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'handle': user.handle,
                'email': user.email,
                'name': user.name,
                'image_url': user.image_url,
                # 'expo_push_token': user.expo_push_token,
                'created_at': user.created_at.isoformat()
            }
        }


class ValidationEmailSender(flask_restful.Resource):
    """
        Post requests will handle sending the validation email
        This is likely not the most RESTful thing ever, but we're just rolling with it.
    """

    @staticmethod
    @flask_jwt_extended.jwt_required
    def get():
        """
            Create and store the email validation token.
            Send an email to the user containing the token
        """
        try:
            requesting_user_id = flask_jwt_extended.get_jwt_identity()  # user id or None
            user_query = db_session.query(models.User)
            user_query_result = user_query.filter(models.User.id == requesting_user_id).one()
            for user in user_query_result:
                the_token = ph.hash(str(user.handle))[35:]
                print(the_token)
                tomorrow = datetime.utcnow() + datetime.timedelta(days=1)
                validation_token = models.ValidationToken(token=the_token, created_at=tomorrow, user_id=user.id)
                db_session.add(validation_token)
                db_session.commit()
                # message = f"""Hello, {user.handle} follow this link to validate your email
                # 127.0.0.1/api/v1/validate/{validation_token}"""
                # subject = f"User Account Validation" % handle
                # msg = Message(recipients=[user.email],
                #      body=message,
                #      subject=subject)
                # mail.send(msg)
                # print('this is where we send an email') send an email
        except SQLAlchemyError:
            flask_restful.abort(400, message='user not found')
        return {'message': 'check your email'}


class TokenValidator(flask_restful.Resource):
    """
        Handles validating the token that gets sent out in an email
    """

    # pylint doesn't realize that flask_restful.abort ends the function the same way
    # 'raise' would
    @staticmethod
    @flask_jwt_extended.jwt_required
    def get(token):  # pylint: disable=inconsistent-return-statements
        """
            Set the user's validated state to "true"
        """
        try:
            token = db_session.query(models.ValidationToken).filter(models.ValidationToken.token == token).one()
        except SQLAlchemyError:
            flask_restful.abort(400, message='token not found')
        try:
            if datetime.utcnow() > token.created_at:
                flask_restful.abort(400, message='it has been over a day, try again')
            else:
                user_id = token.user_id
                user_query = db_session.query(models.User).filter(models.User.id == user_id).one()
                user_query.email_validated = True
                db_session(token).delete()
                db_session.commit()
                return {'message': 'email validated'}
        except SQLAlchemyError:
            flask_restful.abort(400, message='problem retrieving user')


class FacebookLogin(flask_restful.Resource):
    """
        Handles the oauth for Facebook
    """
    @staticmethod
    def post() -> str:
        """
            post json data, creates and authenticates a user

            required arguments:
            access_token -- access token provided by the facebook callback

            :return jwt access token
            :rtype: str
        """
        facebook_creds = get_creds('facebook')
        facebook_app_id = facebook_creds['facebook_app_id']
        facebook_app_secret = facebook_creds['facebook_app_secret']
        facebook_app_token = "{}|{}".format(facebook_app_id, facebook_app_secret)

        # load json, pass to userPostListSchema serializer instance
        json_data = json.loads(request.data.decode('utf-8'))
        print("json_data: {}".format(json_data))

        # get debug data from facebook
        debug_token_url = "https://graph.facebook.com/debug_token?input_token={}&access_token={}".format(
            json_data['access_token'], facebook_app_token)
        debug_response = requests.get(debug_token_url).json()

        # check for error from facebook
        if 'error' in debug_response:
            flask_restful.abort(400, message="oauth error")

        debug_token_data = debug_response['data']

        # check if token is expired
        token_expired = datetime.fromtimestamp(int(debug_token_data['expires_at'])) < datetime.now()
        if token_expired:
            flask_restful.abort(400, message="token expired")

        # invalid token
        if not bool(debug_token_data['is_valid']):
            flask_restful.abort(400, message="invalid token")

        # valid token, but wrong app id?
        if not debug_token_data['app_id'] == facebook_app_id:
            flask_restful.abort(400, message="wrong api id")

        # okay grab the profile info
        # requests.get("{}{}?fields=name,email,profile_pic")
        url = "https://graph.facebook.com/v2.12/me?access_token={}&fields=email,name,id,first_name,last_name,picture"
        url = url.format(json_data['access_token'])
        me_response = requests.post(url).json()

        if 'id' not in me_response:
            flask_restful.abort(400, message="error getting user info from facebook")
        if 'email' not in me_response:
            me_response['email'] = "test@test.com"
        # check to see if email already exists
        if db_session.query(models.User).filter(models.User.email == me_response['email']).one_or_none():
            user = db_session.query(models.User).filter(models.User.email == me_response['email']).one()
        else:
            # check to see if handle already exists
            if db_session.query(models.User).filter(models.User.handle == me_response['name']).one_or_none():
                import uuid
                me_response['name'] = "{}{}".format(me_response['name'], str(uuid.uuid4()))
            new_user = models.User(name=me_response['name'],
                                   email=me_response['email'],
                                   handle=me_response['name'],
                                   password_hash=ph.hash("password"),  # hmmm, discuss, this works for now i guess
                                   image_url=me_response['picture']['data']['url'],
                                   created_at=datetime.utcnow())
            db_session.add(new_user)
            db_session.flush()  # Flushing here because we need the id

            try:
                db_session.commit()
                user = new_user
            except SQLAlchemyError as ex:
                print(ex)
                db_session.rollback()
                flask_restful.abort(400, message="Database error")

        # if all goes to plan lets return an access token
        access_token = flask_jwt_extended.create_access_token(identity=user.id)  # type: str

        return {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'handle': user.handle,
                'email': user.email,
                'image_url': user.image_url,
                'created_at': user.created_at.timestamp(),
            }
        }


class GoogleLogin(flask_restful.Resource):
    """
        Handles the oauth for Google
    """
    @staticmethod
    def post() -> str:
        """
            post json data, creates and authenticates a user

            required arguments:
            id_token -- access token provided by the google callback

            :return jwt access token
            :rtype: str
        """
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        google_client_id = "502662800230-9aksdidb6d3eohkdrpj97hfupnr41b4j.apps.googleusercontent.com"

        # load json into a dict
        json_data = json.loads(request.data.decode('utf-8'))  # type: dict
        print("json_data: {}".format(json_data))

        # lets see what google thinks
        idinfo = id_token.verify_oauth2_token(json_data['id_token'], google_requests.Request(), google_client_id)

        # check issuer (i don't know what that actually means)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            flask_restful.abort(400, message='Wrong issuer.')

        # make sure the token isn't expired
        if datetime.fromtimestamp(int(idinfo['exp'])) < datetime.now():
            flask_restful.abort(400, message="Unable to login via Google")

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # userid = idinfo['sub']
        # pylint: disable=fixme
        # TODO: store this userid
        # pylint: enable=fixme

        # check to see if email already exists
        if db_session.query(models.User).filter(models.User.email == idinfo['email']).one_or_none():
            user = db_session.query(models.User).filter(models.User.email == idinfo['email']).one_or_none()
        else:
            # check to see if handle already exists
            if db_session.query(models.User).filter(models.User.handle == idinfo['name']).one_or_none():
                import uuid
                idinfo['name'] = "{}{}".format(idinfo['name'], str(uuid.uuid4()))
            # if it doesn't exist, create a new user
            new_user = models.User(
                email=idinfo['email'],
                handle=idinfo['name'],
                name=idinfo['name'],
                password_hash=ph.hash("password"),  # hmmm, discuss, this works for now i guess
                image_url=idinfo['picture'],
                created_at=datetime.utcnow())
            db_session.add(new_user)
            db_session.flush()  # Flushing here because we need the id

            try:
                db_session.commit()
                user = new_user
            except SQLAlchemyError as ex:
                print(ex)
                db_session.rollback()
                flask_restful.abort(400, message="Database error")

        # if all goes to plan lets make an access token
        access_token = flask_jwt_extended.create_access_token(identity=user.id)  # type: str

        return {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'handle': user.handle,
                'email': user.email,
                'image_url': user.image_url,
                'created_at': user.created_at.timestamp(),
            }
        }
