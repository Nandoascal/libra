import os
from os import environ
###########################
# Flask config
###########################

DEBUG = True
IP = environ.get('IP', '')
PORT = environ.get('PORT', '')
SECRET_KEY = environ.get('SECRET_KEY', '')
SERVER_NAME = environ.get('SERVER_NAME, '')

###########################
# DB info
###########################

SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI', '')

###########################
# OIDC config
###########################

OIDC_ISSUER = os.environ.get('OIDC_ISSUER', '')
OIDC_CLIENT_CONFIG = {
    'client_id': environ.get('OIDC_CLIENT_ID', ''),
    'client_secret': environ.get('OIDC_CLIENT_SECRET', ''),
    'post_logout_redirect_uris': [environ.get('LIBRA_OIDC_LOGOUT_REDIRECT_URI', 'https://libra.csh.rit.edu/logout')]
}
