import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-3gd0rhi9.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error: dict['code': int, 'description': str], status_code: int):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
    Attempt to get the header from the request
    and return the token part of the header
'''


def get_token_auth_header():
    auth: str | None = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError(
            {'code': 'auth_missing', 'description': 'Authorization header is required'}, 401)
    bearer_token = auth.split(' ')
    if len(bearer_token) != 2:
        raise AuthError({'code': 'invalid_header',
                        'description': 'Bearer token is invalid'}, 400)
    bearer = bearer_token[0]
    if bearer.lower() != 'bearer':
        raise AuthError({'code': 'invalid_header',
                        'description': 'Authorization header must begin with "Bearer "'}, 400)
    token = bearer_token[1]
    if not token:
        raise AuthError({'code': 'invalid_header',
                        'description': 'An auth token is required'}, 400)
    return token


'''
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
    Check that the permissions specify the desired permission.
'''


def check_permissions(permission: str, payload: str):
    if 'permissions' not in payload:
        raise AuthError(
            {'code': 'malformed_query', 'description': 'Malformed token: permissions not specified'}, 400)
    if permission not in payload['permissions']:
        raise AuthError(
            {'code': 'unauthorized_access', 'description': 'missing permission'}, 401)
    return True


'''Return the decoded jwt payload.

    @INPUTS
        token: a json web token (string)

    It verifies an Auth0 token with a key id (kid).
    It decodes the payload from the token and validates the claims.

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if not rsa_key:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.'
        }, 401)

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f'https://{AUTH0_DOMAIN}/',
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError({
            'code': 'invalid_token',
            'description': 'Token has expired'
        }, 403)
    except jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Claims error: check the audience and issuer.'
        }, 401)
    except Exception:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.'
        }, 400)


'''Return the decorator which passes the decoded payload to the decorated method.

    @INPUTS
        permission: string permission (i.e. 'post:drink')

    This method decodes the JWT, validates the claims and verifies the requested permission.
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
