from unittest.mock import patch
import json

@patch('src.resources.auth.models')
@patch('src.resources.auth.request')
@patch('src.resources.auth.db_session')
def test_jwt_distributor_post(
        mock_db_session, mock_request,
        mock_model, app, auth,
        model_user, request_json):

    mock_request.data.decode.return_value = json.dumps({
        'email': 'gg@mail.com',
        'password': 'password',
    })
    mock_model.User.return_value = model_user

    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value

    mock_filter.one_or_none.return_value = model_user

    jwt_distributor = auth.JWTDistributor()
    with app.test_request_context():
        response = jwt_distributor.post()

    assert isinstance(response, dict)

    assert 'user' in response
    assert 'handle' in response['user']
    assert response['user']['handle'] == "JorgeTheBoy"

    assert 'access_token' in response
    assert len(response['access_token']) != 0
    assert len(response['access_token'].split('.')) == 3

@patch('src.resources.auth.models')
@patch('src.resources.auth.request')
@patch('src.resources.auth.db_session')
def test_facebook_login_post(
        mock_db_session, mock_request,
        mock_model, app, auth,
        model_user, request_json):

    mock_request.data.decode.return_value = json.dumps({
        'access_token': 'EAAKi7uygkrQBAJbuQAxRDtQoYalm0t9omLGdrHWKLrdr5uXlaygEYoW80THcAkoOgf7zZCPLP32yQ2KMOWZAZAZApXpBupgUhTIVkx9VUo0dQRjtualRrUV0tjVGZClAlrvwZC9L50LWn41QvjmZAZBxxNtSmOKmXTKMZCre1ZASa3XS9CpDPjGLuTTE8mWyZCsMLHZCbVszC5gZA7QlENFLVRZCsQiWQqD0WcnJqiCN7lEvTzDqFdwOzAYc1q'
    })
    mock_model.User.return_value = model_user
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.one_or_none.return_value = model_user

    facebook_login = auth.FacebookLogin()
    with app.test_request_context():
        response = facebook_login.post()

    assert isinstance(response, dict)

    assert 'access_token' in response
    assert len(response['access_token']) != 0
    assert len(response['access_token'].split('.')) == 3
