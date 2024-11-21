"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from flask_jwt_extended import JWTManager
from api.models import db, ExerciseInterests
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from api.blacklist import blacklist

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# Add CORS configuration right after Flask app initialization
CORS(app)

# database configuration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# Initialize database and seed exercise interests
def initialize_database():
    with app.app_context():
        db.create_all()
        try:
            ExerciseInterests.seed_default_interests()
            print("Successfully seeded exercise interests")
        except Exception as e:
            print(f"Error seeding exercise interests: {str(e)}")

# Call the initialization function
initialize_database()

jwt = JWTManager(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")  # Change in production
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints from the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

@jwt.token_in_blocklist_loader # Runs every time a private request is made
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)


# """
# This module takes care of starting the API Server, Loading the DB and Adding the endpoints
# """
# import os
# from flask import Flask, jsonify, send_from_directory
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_cors import CORS
# from api.utils import APIException, generate_sitemap
# from flask_jwt_extended import JWTManager
# from api.models import db, ExerciseInterests
# from api.routes import api
# from api.admin import setup_admin
# from api.commands import setup_commands
# from api.blacklist import blacklist


# # from models import Person

# ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
# static_file_dir = os.path.join(os.path.dirname(
#     os.path.realpath(__file__)), '../public/')
# app = Flask(__name__)
# app.url_map.strict_slashes = False

# # Add CORS configuration right after Flask app initialization
# CORS(app)

# # database condiguration
# db_url = os.getenv("DATABASE_URL")
# if db_url is not None:
#     app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
#         "postgres://", "postgresql://")
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# MIGRATE = Migrate(app, db, compare_type=True)
# db.init_app(app)

# #initialize datavase and seed data 
# def initialize_database():
#     with app.app_context():
#         db.create_all()
#         ExerciseInterests.seed_default_interests()


# jwt = JWTManager(app)

# # add the admin
# setup_admin(app)

# # add the admin
# setup_commands(app)

# # Add all endpoints form the API with a "api" prefix
# app.register_blueprint(api, url_prefix='/api')

# # Setup the Flask-JWT-Extended extension
# app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")  # Change in production
# app.config["JWT_BLACKLIST_ENABLED"] = True
# app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

# jwt = JWTManager(app)

# @jwt.token_in_blocklist_loader # Runs every time a private request is made
# def check_if_token_in_blacklist(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     return jti in blacklist

# # Handle/serialize errors like a JSON object
# @app.errorhandler(APIException)
# def handle_invalid_usage(error):
#     return jsonify(error.to_dict()), error.status_code

# # generate sitemap with all your endpoints
# @app.route('/')
# def sitemap():
#     if ENV == "development":
#         return generate_sitemap(app)
#     return send_from_directory(static_file_dir, 'index.html')

# # any other endpoint will try to serve it like a static file

# @app.route('/<path:path>', methods=['GET'])
# def serve_any_other_file(path):
#     if not os.path.isfile(os.path.join(static_file_dir, path)):
#         path = 'index.html'
#     response = send_from_directory(static_file_dir, path)
#     response.cache_control.max_age = 0  # avoid cache memory
#     return response


# # this only runs if `$ python src/main.py` is executed
# if __name__ == '__main__':
#     PORT = int(os.environ.get('PORT', 3001))
#     app.run(host='0.0.0.0', port=PORT, debug=True)