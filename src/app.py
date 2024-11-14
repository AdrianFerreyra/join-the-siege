import requests

from flask import Flask, request, jsonify
from werkzeug.datastructures import FileStorage

from src import logging
from config import settings


logger = logging.get_logger(__name__)

app = Flask(__name__)

CLASSIFIER_CLASSIFY_FILE_URL = (
    "{host}:{port}/{endpoint}".format(  # pylint: disable=consider-using-f-string
        host=settings.CLASSIFIER_SERVICE_HOST,
        port=settings.CLASSIFIER_SERVICE_PORT,
        endpoint=settings.CLASSIFIER_SERVICE_ENDPOINT,
    )
)
CLASSIFIER_CALL_TIMEOUT = 5


class ClassificationError(Exception):
    def __init__(self, message, error_code):
        new_message = f"File Classification failed: {message}"
        super().__init__(new_message)
        self.error_code = error_code


def _validate_request_args(request_param):
    if "file" not in request_param.files:
        return {"error": "No file part in the request"}, 400

    file = request_param.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    return None


@app.route("/classify_file", methods=["POST"])
def classify_file_route():
    validations = _validate_request_args(request)
    if validations is not None:
        return jsonify(validations[0]), validations[1]

    file = request.files["file"]

    try:
        file_class = _classify_file(file)
        return jsonify({"file_class": file_class}), 200
    except ClassificationError as e:
        return jsonify({"error": str(e)}), e.error_code


def _classify_file(file: FileStorage):
    files = {"file": (file.filename, file.read())}
    try:
        response = requests.post(
            url=CLASSIFIER_CLASSIFY_FILE_URL,
            files=files,
            timeout=CLASSIFIER_CALL_TIMEOUT,
        )
        if response.ok:
            return response.json()
        raise ClassificationError(response.reason, response.status_code)
    except requests.RequestException as exc:
        raise ClassificationError("Connection Error", 500) from exc


if __name__ == "__main__":
    app.run(debug=True)
