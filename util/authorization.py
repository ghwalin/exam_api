import json
from functools import wraps
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from flask import jsonify, request, make_response, g, current_app
from data.PersonDAO import PersonDAO
from datetime import datetime, timedelta


def token_required(func):
    """
    checks if the authorization token is valid
    :param func: callback function
    :return:
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            data = jwt.decode(token[7:], current_app.config['ACCESS_TOKEN_KEY'], algorithms=["HS256"])
            email = data['email']
            person_dao = PersonDAO()
            g.user = person_dao.read_person(email)
        except Exception:
            return make_response(jsonify({"message": "EXAM/auth: Invalid token!"}), 401)

        return func(*args, **kwargs)

    return decorator


def teacher_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if not g.user.role == 'teacher':
            return make_response(jsonify({"message": "not allowed for students"}), 401)
        return func(*args, **kwargs)

    return wrap


def make_access_token(email):
    """
    creates an access token
    :param email: the email address of the user
    :return: token
    """
    person_dao = PersonDAO()
    person = person_dao.read_person(email)
    if person is not None:
        access = jwt.encode({
            'email': email,
            'role': person.role,
            'exp': datetime.utcnow() + timedelta(minutes=current_app.config['TOKEN_DURATION'])
        },
            current_app.config['ACCESS_TOKEN_KEY'], "HS256"
        )
        return access, person.role
    else:
        return None, "guest"


def read_keys(token):
    """
    reads the ms keys for the token
    :param token: the token
    :return:
    """
    response = requests.get("https://login.microsoftonline.com/common/discovery/keys")
    keys = response.json()['keys']

    token_headers = jwt.get_unverified_header(token)
    token_alg = token_headers['alg']
    token_kid = token_headers['kid']
    public_key = None
    for key in keys:
        if key['kid'] == token_kid:
            public_key = key

    rsa_pem_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(public_key))
    rsa_pem_key_bytes = rsa_pem_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return rsa_pem_key_bytes, token_alg


if __name__ == '__main__':
    ''' Check if started directly '''
    pass
