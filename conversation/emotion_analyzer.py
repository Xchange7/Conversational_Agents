# emotion_analyzer.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import numpy as np
# from pyAudioAnalysis import audioFeatureExtraction, ShortTermFeatures
from pyAudioAnalysis import ShortTermFeatures
from scipy.io import wavfile

import requests
import torch

from logger import Logger

class EmotionAnalyzer:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.logger = Logger()  # Use the logger `singleton instance`

    def analyze_text_emotion(self, text: str) -> str:
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

    def analyze_speech_emotion(self, audio_path: str) -> str:
        """
        Analyze emotion from speech audio file.
        
        Parameters:
            audio_path: Path to the audio file to analyze
            
        Returns:
            String representing the detected emotion from speech
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_path):
                self.logger.log_error(f"Audio file not found: {audio_path}")
                return "neutral"

            self.logger.log(f"Analyzing speech emotion from: {audio_path}")
            
            # Read audio file using scipy (used by pyAudioAnalysis)
            sampling_rate, signal = wavfile.read(audio_path)
            
            # Make sure we have mono audio
            if len(signal.shape) > 1:
                signal = signal[:, 0]  # Take only the first channel
            
            # Extract features using pyAudioAnalysis
            window_size = int(0.05 * sampling_rate)  # 50ms window
            step_size = int(0.025 * sampling_rate)   # 25ms step
            features, feature_names = ShortTermFeatures.feature_extraction(signal, 
                                                                          sampling_rate, 
                                                                          window_size, 
                                                                          step_size)
            
            # Calculate mean values for each feature
            features_mean = np.mean(features, axis=1)
            
            # Simple emotion classification based on audio features
            # This is a simplified approach - in production, use a trained model
            emotion = self.classify_emotion_from_features(features_mean, feature_names)
            
            self.logger.log(f"Speech Emotion Analysis Result: {emotion}")
            return emotion
            
        except Exception as e:
            self.logger.log_error(f"Error in speech emotion analysis: {e}")
            return "neutral"  # Default fallback emotion
    
    def classify_emotion_from_features(self, features_mean, feature_names):
        """
        Simple classification of emotions based on audio features.
        This is a simplified approach and should be replaced with a proper
        trained model in production.
        
        Parameters:
            features_mean: Mean values of extracted audio features
            feature_names: Names of the features
            
        Returns:
            String representing the detected emotion
        """
        # Find indices for relevant features
        energy_idx = feature_names.index('energy') if 'energy' in feature_names else 0
        zcr_idx = feature_names.index('zero_crossing_rate') if 'zero_crossing_rate' in feature_names else 1
        
        # Simple rule-based classification
        energy = features_mean[energy_idx]
        zcr = features_mean[zcr_idx]
        
        # Very simple rules (would need to be calibrated for real applications)
        if energy > 0.7:  # High energy
            if zcr > 0.5:
                return "angry"  # High energy, high zero-crossing rate
            else:
                return "happy"  # High energy, lower zero-crossing rate
        elif energy > 0.4:  # Medium energy
            if zcr > 0.6:
                return "fearful"
            else:
                return "surprised"
        else:  # Low energy
            if zcr > 0.4:
                return "sad"
            else:
                return "neutral"

    def analyze_face_emotion(self, docker_service_url: str = "http://localhost:5005") -> str:
        """
        调用另外一个 Docker 服务中的 deepface 模块，
        从 /emotion 接口获取当前用户的表情信息

        参数:
            docker_service_url: Docker 服务的基础 URL，例如 "http://127.0.0.1:5005"

        返回:
            用户当前表情（例如 "happy", "sad" 等），如果调用失败则返回 "unknown"
        """
        try:
            # 构造接口完整 URL
            docker_service_url = "http://host.docker.internal:5005" # Map
            url = f"{docker_service_url}/emotion"
            response = requests.get(url, timeout=5)
            # 如果返回状态码正常，则解析 JSON 数据
            if response.status_code == 200:
                data = response.json()
                self.logger.log("Facial Emotion Result: " + data["emotion"])
                return data.get("emotion", "unknown")
            else:
                self.logger.log(f"请求失败，状态码: {response.status_code}")
                return "unknown"
        except Exception as e:
            self.logger.log(f"请求异常: {e}")
            return "unknown"

# def extract_audio_features(audio_path: str):
#     """
#     Example of using pyAudioAnalysis to extract audio features
#     """
#     if not os.path.exists(audio_path):
#         raise FileNotFoundError(f"{audio_path} not found.")

#     # Read audio and extract features
#     [Fs, x] = audioFeatureExtraction.read_audio_file(audio_path)
#     # Extract short-term features
#     features, feature_names = ShortTermFeatures.feature_extraction(x, Fs, 0.05 * Fs, 0.025 * Fs)
#     # Return the mean as an example
#     features_mean = np.mean(features, axis=1)
#     return features_mean, feature_names


# def predict_audio_emotion(features_mean):
#     """
#     Example only: Predict emotion based on extracted features
#     In actual use, you would need to train or use a pretrained model to classify the features
#     """
#     # This is just an example, returning a hypothetical result
#     # You can input features_mean into your own classification model to get actual emotion labels
#     # e.g. emotion_classifier.predict(features_mean.reshape(1, -1))
#     # Here we simply return a hardcoded value
#     return "happy"

