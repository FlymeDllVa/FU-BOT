from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Flask_Config

app = Flask(__name__)
app.config.from_object(Flask_Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
from app.models import Users, Groups, Schedule, ScheduleObject
