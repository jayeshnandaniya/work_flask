from unittest.mock import patch
import json

# Patch jwt_required decorator before doing anything
# Look Patching decorator section here
# http://alexmarandon.com/articles/python_mock_gotchas/
patch('flask_jwt_extended.jwt_required', lambda x: x).start()


"""
This functions test listing of users
"""
@patch('src.resources.users.models')
@patch('src.resources.users.request')
@patch('src.resources.users.db_session')
def test_users_list_get(
        mock_db_session, mock_request, mock_model,
        model_user, app, users):

    mock_request.args = {
        'single_user': True,
        'id': 42
    }

    mock_model.User.return_value = model_user

    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value

    # Return our user from filter.all
    mock_filter.all.return_value = [model_user]

    user_list = users.UserList()

    with app.test_request_context():
        users_list = user_list.get()

    assert len(users_list) == 1
    assert users_list[0]['id'] == 42


"""
This functions test user creation
"""
@patch('src.resources.users.save_jpeg_file')
@patch('src.resources.users.models')
@patch('src.resources.users.request')
@patch('src.resources.users.db_session')
def test_users_list_post(
        mock_db_session, mock_request, mock_model,
        mock_save_jpeg_file, app, users, model_user):

    mock_request.data.decode.return_value = json.dumps({
        'email': 'some@mail.com',
        'password': '12345',
        'handle': 'queenb',
        'image_is_local': True,
        'image_url': 'http://someimage.jpg'
    })

    mock_model.User.return_value = model_user
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.one_or_none.return_value = None
    mock_save_jpeg_file.return_value = 'http://savedimage.jpg'

    user_list = users.UserList()
    with app.test_request_context():
        new_user_dict = user_list.post()
        print(new_user_dict)

    assert isinstance(new_user_dict, dict)
    assert 'access_token' in new_user_dict
    # verify access_token

    assert 'user' in new_user_dict
    # check that email, handle, and image_url are correct
    assert new_user_dict['user']['handle'] == "JorgeTheBoy"
    assert new_user_dict['user']['email'] == "gg@mail.com"
    assert new_user_dict['user']['image_url'] == ''
    # check that user was created

"""
This functions test user update
"""
@patch('src.resources.users.save_jpeg_file')
@patch('src.resources.users.models')
@patch('src.resources.users.request')
@patch('src.resources.users.db_session')
def test_users_list_put(
        mock_db_session, mock_request, mock_model,
        mock_save_jpeg_file, app, users, model_user,
        request_json):

    mock_request.get_json.return_value = request_json

    mock_model.User.return_value = model_user
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.one.return_value = model_user
    mock_filter.one_or_none.return_value = None
    mock_save_jpeg_file.return_value = 'http://savedimage.jpg'

    user_list = users.UserList()
    with app.test_request_context():
        new_user_dict = user_list.put()

    assert isinstance(new_user_dict, dict)
    assert new_user_dict['id'] == 42
