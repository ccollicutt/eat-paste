# a flask rest api for pasting text

from flask import Flask, request, make_response
from coolname import generate_slug
import pymongo
from pymongo import MongoClient
import os
import logging
import re
import bleach

#
# Take a small amount of plain text as a paste and return a coolname slug where
# it can be retrieved later.
#


# setting mongo_client to None to allow passing in mock client for testing
class PasteApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mongo_client = None

    def set_mongo_client(self, client):
        self.mongo_client = client


app = PasteApp(__name__)


class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


@app.errorhandler(APIError)
def handle_api_error(error):
    app.logger.error("APIError: %s", error)
    return make_response(str(error), error.status_code)


def is_valid_slug(slug):
    # only allow word-word format slugs
    pattern = re.compile(r"^[a-z]+-[a-z]+$")
    return bool(pattern.match(slug))


def get_collection():
    db_name = "paste"
    collection_name = "entries"

    if not app.mongo_client:
        app.logger.error("client is none")
        mongo_connection = os.environ.get("MONGODB_CONNECTION")
        if not mongo_connection:
            app.logger.error("MONGODB_CONNECTION environment variable is not set")
            raise APIError("Internal configuration error", 500)

        try:
            app.mongo_client = MongoClient(mongo_connection)
        except pymongo.errors.ConnectionFailure as e:
            raise APIError("Could not connect to database server", 500)

    collection = app.mongo_client[db_name][collection_name]
    return collection


@app.route("/paste", methods=["POST"])
def paste():
    content_length = request.content_length
    mimetype = request.mimetype

    if content_length is None or content_length == 0:
        raise APIError("Paste empty", 400)
    if content_length > 10000:
        raise APIError("Paste too large", 413)
    if mimetype != "text/plain":
        raise APIError("Paste must be text/plain", 400)

    data = request.get_data(as_text=True)
    # sanitize input
    cleaned_data = bleach.clean(data)
    if data != cleaned_data:
        raise APIError("HTML content not allowed", 400)

    slug = generate_slug(2)
    collection = get_collection()

    try:
        collection.insert_one({"slug": slug, "data": data})
    except Exception as e:
        app.logger.error("Could not insert paste: %s", e)
        raise APIError("Could not insert paste", 500)

    response = make_response(slug, 200)
    response.mimetype = "text/plain"
    return response


@app.route("/paste/<string:slug>", methods=["GET"])
def get_paste(slug):
    if not is_valid_slug(slug):
        raise APIError("Invalid slug format", 500)

    mongo_query = {"slug": slug}
    collection = get_collection()

    try:
        result = collection.find_one(mongo_query)
    except Exception as e:
        app.logger.error("Could not retrieve paste: %s", e)
        raise APIError("Paste not found", 404)

    if result:
        response = make_response(result["data"], 200)
        response.mimetype = "text/plain"
        return response

    raise APIError("Paste not found", 404)


# if running out of gunicorn, use the gunicorn logger
# https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
