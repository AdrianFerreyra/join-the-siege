import os
from fastapi import FastAPI, File, HTTPException, UploadFile
import joblib

from config import settings
from src import logging
from src.readers import factory as readers_factory
from src.utils import get_filename_extension


logger = logging.get_logger(__name__)

app = FastAPI()

classifier = joblib.load(
    os.path.join(settings.CLASSIFIER_SERVICE_DATA_VOLUME, settings.CLASSIFIER_SERVICE_MODEL_FILENAME)
)
vectorizer = joblib.load(
    os.path.join(settings.CLASSIFIER_SERVICE_DATA_VOLUME, settings.CLASSIFIER_SERVICE_VECTORIZER_FILENAME)
)


class ClassificationError(Exception):
    pass


@app.post("/classify_file")
async def classify_file(file: UploadFile = File(...)):
    logger.info("Starting classification for file '%s'...", file.filename)

    try:
        file_extension, file_bytes = await _extract_extension_and_bytes(file)
        reader = readers_factory.get_reader(file_extension)
        file_text = reader.read(file_bytes)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))

    try:
        new_text_features = vectorizer.transform([file_text])
        predicted_label = classifier.predict(new_text_features)
        file_class = predicted_label[0]
    except Exception:
        return HTTPException(
            status_code=500, detail="Failed evaluating file. Please try again later."
        )

    return {"file_class": file_class}


async def _extract_extension_and_bytes(file: UploadFile):
    try:
        file_extension = get_filename_extension(file.filename)
    except Exception as exc:
        raise ClassificationError("Invalid Filename") from exc

    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise ClassificationError("Unreadable File") from exc

    return file_extension, file_bytes
