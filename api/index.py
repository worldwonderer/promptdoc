from flask import Flask
from flask_mongoengine import MongoEngine

from .config import MONGODB_SETTINGS
from .routes import bp


app = Flask(__name__)

# 配置 MongoDB
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS

# 初始化 MongoEngine
db = MongoEngine(app)

app.register_blueprint(bp)
