# emotion_analyzer.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import numpy as np
# from pyAudioAnalysis import audioFeatureExtraction, ShortTermFeatures
from pyAudioAnalysis import ShortTermFeatures

import torch

class EmotionAnalyzer:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def analyze_emotion(self, text: str) -> str:
        """
        Use a pretrained model to classify/analyze text sentiment.
        This is a simple example that classifies text sentiment into 1-5 star ratings,
        which can be mapped to more detailed emotion labels if needed.
        """
        inputs = self.tokenizer.encode_plus(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        scores = outputs.logits.detach().numpy()[0]
        # Find the highest scoring emotion label (1 to 5)
        predicted_label = scores.argmax() + 1  # argmax returns 0-4
        return f"{predicted_label}-star sentiment"  # You can change this to a more detailed classification

def extract_audio_features(audio_path: str):
    """
    Example of using pyAudioAnalysis to extract audio features
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"{audio_path} not found.")

    # Read audio and extract features
    [Fs, x] = audioFeatureExtraction.read_audio_file(audio_path)
    # Extract short-term features
    features, feature_names = ShortTermFeatures.feature_extraction(x, Fs, 0.05 * Fs, 0.025 * Fs)
    # Return the mean as an example
    features_mean = np.mean(features, axis=1)
    return features_mean, feature_names


def predict_audio_emotion(features_mean):
    """
    Example only: Predict emotion based on extracted features
    In actual use, you would need to train or use a pretrained model to classify the features
    """
    # This is just an example, returning a hypothetical result
    # You can input features_mean into your own classification model to get actual emotion labels
    # e.g. emotion_classifier.predict(features_mean.reshape(1, -1))
    # Here we simply return a hardcoded value
    return "happy"
