from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.social import Social, SQLAlchemyConnectionDatastore, \
	 login_failed
from mongokit import *
from models import *

app = Flask(__name__)

# TODO: move all configs into external file.
app.config['SOCIAL_FACEBOOK'] = {
    'consumer_key': '804807199563793',
    'consumer_secret': 'e7d68bbbd3b828743dc3d6fff7cc9406'
}

app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '967982158206-146hbl8954b0oa45e71ii9efuuaj4fj0.apps.googleusercontent.com',
    'consumer_secret': 'JFYgnNsq8FR6qfjSC-uDHFEl'
}

app.config['SECURITY_POST_LOGIN'] = '/profile'

##
# STAGE FOR DELETE
#################################################
app.config.update(
    SECRET_KEY='Tieng3us3Xie5meiyae6iKKHVUIUDF',
    GOOGLE_LOGIN_CLIENT_ID='1002179078501-mdq5hvm940d0hbuhqltr0o1qhsr7sduc.apps.googleusercontent.com',
    GOOGLE_LOGIN_CLIENT_SECRET='O1kpQ8Is9s2pD3eOpxRfh-7x',
    GOOGLE_LOGIN_REDIRECT_URI='http://127.0.0.1:5000/oauth2callback',
)
#################################################

db = SQLAlchemy(app)

connection = Connection()
connection.register([StudySession])
mongo_db = connection.succor

print "Running app..."

from . import views, models

# security_ds = SQLAlchemyUserDatastore(db, models.User, models.Role)
# social_ds = SQLAlchemyConnectionDatastore(db, models.Connection)

# app.security = Security(app, security_ds)
# app.social = Social(app, social_ds)

# class SocialLoginError(Exception):
#     def __init__(self, provider):
#         self.provider = provider

# @app.before_first_request
# def before_first_request():
#     try:
#         models.db.create_all()
#     except Exception, e:
#         app.logger.error(str(e))

# @login_failed.connect_via(app)
# def on_login_failed(sender, provider, oauth_response):
#     app.logger.debug('Social Login Failed via %s; '
#                      '&oauth_response=%s' % (provider.name, oauth_response))

#     # Save the oauth response in the session so we can make the connection
#     # later after the user possibly registers
#     session['failed_login_connection'] = \
#         get_connection_values_from_oauth_response(provider, oauth_response)

#     raise SocialLoginError(provider)