import os
from datetime import timedelta

import jinja2
from flask import Flask
from flask_mongoengine import MongoEngine

from .config import MONGODB_SETTINGS
from .api_routes import bp
from .admin_routes import admin_bp


app = Flask(__name__)

# 配置 MongoDB
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS

# 初始化 MongoEngine
db = MongoEngine(app)

app.register_blueprint(bp)
app.register_blueprint(admin_bp)
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=2)


def render_template_string(self, context):
    env = jinja2.Environment()
    template = env.from_string(self)
    return template.render(**context)


app.jinja_env.filters['render_template'] = render_template_string
