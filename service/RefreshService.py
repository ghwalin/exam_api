import jwt
from flask import make_response, jsonify, current_app, request
from flask_restful import Resource

from util.authorization import make_access_token, read_keys


class RefreshService(Resource):
    """
    service to refresh the access token

    author: Marcel Suter
    """

    def get(self, email):
        """
        get a new access token using the refresh token
        :param email  the email address
        :return: access token
        """
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            jwt.decode(token[7:], current_app.config['REFRESH_TOKEN_KEY'], algorithms=["HS256"])
            access, role = make_access_token(email)
            return jsonify({
                'access': access,
                'email': email,
                'role': role
            })
        except Exception:
            pass

        return make_response(jsonify({"message": "Invalid token!"}), 401)


def decode_idtoken(token):
    """
    decodes the token
    :param token:
    :return:
    """
    try:
        [rsa_pem_key_bytes, token_alg] = read_keys(token)

        jwt.decode(
            token,
            key=rsa_pem_key_bytes,
            verify=True,
            algorithms=[token_alg],
            audience='8b113aa0-1d94-4f7b-a5e7-c7157e1c7b90',
            issuer="https://login.microsoftonline.com/12ea5aa9-906c-4d84-86d2-4713c6ae66d3/v2.0"
        )
    except Exception:
        raise


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
