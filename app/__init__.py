from flask import Flask


# from app.modules.logger import setup_logging
from settings import SECRET_KEY

__version__ = "0.1.0"
__version_date__ = "2023-05-26"
__author__ = "Gridnev Anton"
__description__ = "Helper for ECSS 10"
__license__ = "MIT"
__url__ = "https://github.com/Sivolen/"


# Init logging
# valid log levels ("DEBUG", "INFO", "WARNING", "ERROR")
# logger = setup_logging(log_level="INFO")

# Init flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
# app = Flask(__name__)
# Compress(app)
# Add config parameters in flask app and chose release
# app.config.from_object(f"app.configuration.{release_options}")

# Init DB on Flask app
# db = SQLAlchemy(app)
# Add migrate DB
# migrate = Migrate(app, db)
# db.init_app(app)

# import routes
from app import views
