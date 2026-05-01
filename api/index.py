import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

from flask import Flask, request, redirect, abort
from flask_babel import Babel, get_locale as babel_get_locale
from flask_mongoengine import MongoEngine

from .config import MONGODB_SETTINGS
from .api_routes import bp
from .admin_routes import admin_bp


app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'zh_Hans']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(__file__), 'translations')

db = MongoEngine(app)


def get_locale():
    locale = request.cookies.get('locale')
    if locale in app.config['BABEL_SUPPORTED_LOCALES']:
        return locale
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES']) or 'en'


babel = Babel(app, locale_selector=get_locale)

app.register_blueprint(bp)
app.register_blueprint(admin_bp)
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=2)


@app.route('/locale/<locale_code>')
def set_locale(locale_code):
    if locale_code not in app.config['BABEL_SUPPORTED_LOCALES']:
        abort(404)
    referrer = request.referrer
    if referrer:
        parsed = urlparse(referrer)
        if parsed.netloc != request.host:
            referrer = None
    response = redirect(referrer or '/')
    response.set_cookie('locale', locale_code, max_age=365 * 24 * 60 * 60, samesite='Lax')
    return response


@app.context_processor
def inject_now():
    return {'now': datetime.now(), 'get_locale': babel_get_locale}
