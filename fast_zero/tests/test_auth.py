from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_password_exception(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'invalid_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_token_user_exception(client, user):
    response = client.post(
        '/auth/token',
        data={'username': '', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
