from datetime import datetime, timedelta

import jwt
from flask import make_response, jsonify, current_app as app, request
from flask_restful import Resource, reqparse

from util.authorization import make_access_token, read_keys

parser = reqparse.RequestParser()
parser.add_argument('email', location='form', help='email')
parser.add_argument('password', location='form', help='password')


class AuthenticationService(Resource):
    """
    services for Authentication

    author: Marcel Suter
    """

    def __init__(self):
        """
        constructor

        Parameters:

        """
        pass

    def get(self):
        """
        get a jwt access and refresh token based on the MSAL idToken
        :return:
        """
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            app.logger.info("A valid token is missing!")
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            decoded_token = decode_id_token(token[7:])
            email = decoded_token['email']
            access, role = make_access_token(email)

            if access is not None:
                refresh = jwt.encode({
                    'exp': datetime.utcnow() + timedelta(minutes=app.config['TOKEN_DURATION'])
                },
                    app.config['REFRESH_TOKEN_KEY'], "HS256"
                )

                return jsonify({
                    'access': access,
                    'refresh': refresh,
                    'email': email,
                    'role': role
                })

            return make_response('could not verify', 404, {'Authentication': '"login failed"'})

        except Exception as ex:
            app.logger.info("Invalid token!")
            return make_response(jsonify({"message": "EXAM/login: Invalid token!"}), 401)


def decode_id_token(token):
    """
    decodes the id token from MSAL
    :param token:
    :return:
    """
    try:
        [rsa_pem_key_bytes, token_alg] = read_keys(token)

        decoded_token = jwt.decode(
            token,
            key=rsa_pem_key_bytes,
            verify=True,
            algorithms=[token_alg],
            audience=app.config['MSAL_AUDIENCE'],
            issuer=app.config['MSAL_ISSUER']
        )
        return decoded_token
    except Exception:
        app.logger.info("Error in jwt.decode")
        raise


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
