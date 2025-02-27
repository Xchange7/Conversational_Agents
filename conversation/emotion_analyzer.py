# emotion_analyzer.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
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
