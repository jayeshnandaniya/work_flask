import json

def test_root_get(test_client):
    res = test_client.get('/')
    assert res.status_code == 200


def test_auth_post(test_client):
    res = test_client.post('/api/v1/auth', data=json.dumps({
	    "email": "kk@mail.com",
	    "password": "12345"
    }), content_type='application/json')

    assert res.status_code == 200


def test_users_get(test_client):
    jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MjQ3MTc0NTMsIm5iZiI6MTUyNDcxNzQ1MywianRpIjoiZjhiMzQ1ZGEtNDg4NC00ZmZjLTg4MDYtMDE5YjUyOTA1MTkyIiwiZXhwIjoxNTU2MjUzNDUzLCJpZGVudGl0eSI6NTksImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.SSPB8IPuc7tSb64aCOueIyhZwqS-Y0pL8HXAcW3mkCQ'
    res = test_client.get('/api/v1/users?single_user=true', headers={'Authorization': f'Bearer {jwt_token}'})

    assert res.status_code == 200
