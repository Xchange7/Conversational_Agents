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
        使用预训练模型对文本情感进行分类/分析。
        这里是一个简单的示例，将文本情感分为1-5星评价，可自行映射到更细的情绪标签。
        """
        inputs = self.tokenizer.encode_plus(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        scores = outputs.logits.detach().numpy()[0]
        # 找到得分最高的情感标签(1到5)
        predicted_label = scores.argmax() + 1  # argmax得到0-4
        return f"{predicted_label}-star sentiment"  # 你可以改成更细致的分类结果

def extract_audio_features(audio_path: str):
    """
    使用 pyAudioAnalysis 提取音频特征的示例
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"{audio_path} not found.")

    # 读取音频并提取特征
    [Fs, x] = audioFeatureExtraction.read_audio_file(audio_path)
    # 提取短期特征
    features, feature_names = ShortTermFeatures.feature_extraction(x, Fs, 0.05 * Fs, 0.025 * Fs)
    # 这里简单返回均值作为示例
    features_mean = np.mean(features, axis=1)
    return features_mean, feature_names


def predict_audio_emotion(features_mean):
    """
    仅做示例：根据提取的特征进行情感预测
    实际使用时需要训练或使用预训练模型对特征进行分类
    """
    # 这里只是示例，返回一个假设结果
    # 你可以把 features_mean 输入到自己的分类模型中，得到实际情绪标签
    # e.g. emotion_classifier.predict(features_mean.reshape(1, -1))
    # 这里先简单写死
    return "happy"
