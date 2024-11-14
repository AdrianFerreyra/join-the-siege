import pickle
import csv
import argparse

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from src import logging
from config import settings


logger = logging.get_logger(__name__)


def main(filename: str):
    logger.info("🏋️‍♀️ Starting Model training...")
    training_data = _get_training_data(filename)

    df = pd.DataFrame(training_data, columns=["text", "label"])

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)

    x_set = vectorizer.fit_transform(df["text"])
    y_set = df["label"]

    classifier = MultinomialNB()
    classifier.fit(x_set, y_set)

    logger.info("Saving classifier and vectorizer...")
    with open(settings.CLASSIFIER_SERVICE_MODEL_FILENAME, "wb") as model_file:
        pickle.dump(classifier, model_file)

    with open(settings.CLASSIFIER_SERVICE_VECTORIZER_FILENAME, "wb") as vectorizer_file:
        pickle.dump(vectorizer, vectorizer_file)


def _get_training_data(training_file_path):
    data = []
    with open(training_file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            category = row[0]
            text = row[1]
            data.append((text, category))

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser("python -m src.trainer")
    parser.add_argument(
        "filepath",
        help="Path to the training dataset file. This file should be in CSV format, where each row represents the target label, and the last column is the training text.",
        type=str,
    )
    args = parser.parse_args()
    main(args.filepath)
