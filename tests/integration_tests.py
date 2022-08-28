import os
import sys
from inspect import getsourcefile

import pytest
import tempfile
import json
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import unittest

# put src into our path so we can import app, database, etc
current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
grandparent_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
sys.path.append(os.pardir)

from src.models import User
from src.resources.users import UserList

def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

def init_db():
    engine = create_engine('sqlite:///:memory:', echo=True)
    db_session = scoped_session(sessionmaker(bind=engine))
    base = declarative_base()
    base.query = db_session.query_property()
    base.metadata.create_all(bind=engine)
    return db_session

class TestIntegrations(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config['DATABASE'] = 'sqlite:///:memory:'#tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            session = init_db()
        api = Api(app)
        api.add_resource(UserList, '/api/v1/users')

    #def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(app.config['DATABASE'])

    def test_signup(self):
        """
            create user
            make sure jwt isn't required
        """

        data = {
            'email':'test1@test.com',
            'password':'password',
            'handle':'test1',
            'image_url':'https://avatars0.githubusercontent.com/u/5882512?s=460&v=4',
            'image_is_local': False
        }
        response = self.app.post('/api/v1/users',
                            data=json.dumps(data),
                            content_type='application/json')
        print(response.data)
        print(response.status_code)
        assert response.status_code == 200
        res = json.loads(response.data.decode('utf-8'))
        assert res['email'] == data['email']
'''
    def dont_test_user_list(self):
        """
            list users
            make sure jwt required
        """
        data = {
            id_list: [],
            email: "",
            handle: "",
            name: "",
            single_user: True,
        }
        response = self.app.get('/api/v1/users',
                            data=json.dumps(data),
                            content_type='application/json')
        assert response.status_code == 200

    def dont_test_user_edit(self):
        """
            edit user
            make sure jwt required
        """
        data = {
            email: "",
            handle: "",
            password: "",
            name: "",
            image_is_local: False
        }
        response = self.app.put('/api/v1/users',
                            data=json.dumps(data),
                            content_type='application/json')
        assert response.status_code == 200

    def dont_test_login(self):
        # get is not allowed
        response = self.app.get('/api/v1/auth')
        assert response.status_code == 405
        assert json.loads(response.data.decode('utf-8')) == {'message': 'The method is not allowed for the requested URL.'}

        # post without any data
        response = self.app.post('/api/v1/auth')
        assert response.status_code == 400
        assert json.loads(response.data.decode('utf-8')) == {'message': 'There was no json data provided.'}

        # post with just password
        response = self.app.post("/api/v1/auth",
                                 data=json.dumps({'password':'password'}),
                                 content_type='application/json')
        assert response.status_code == 400
        assert json.loads(response.data.decode('utf-8')) == {'message': "email: ['Missing data for required field.']"}

        # post with valid email and password
        response = self.app.post("/api/v1/auth",
                                 data=json.dumps({"email": "test@test.com", "password":"password"}),
                                 content_type='application/json')
        print(response.data)
        assert response.status_code == 200
        assert json.loads(response.data.decode('utf-8')) == {'message': "..."}

    def dont_test_facebook_login(self):
        # TODO: test user access_token
        # pass to view
        # make sure you get right stuff back
        pass

    def dont_test_google_login(self):
        # TODO: test user access_token
        # pass to view
        # make sure you get right stuff back
        pass
'''
#if __name__ == '__main__':
    #unittest.main()
