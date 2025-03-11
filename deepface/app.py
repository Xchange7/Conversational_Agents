from flask import Flask, jsonify
from threading import Thread
import cv2
import time
from deepface import DeepFace

app = Flask(__name__)

# Global Variable
current_emotion = "unknown"
running = True

def capture_emotion():
    global current_emotion, running
    # Init Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot Open Camera")
        running = False
        return
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Cannot Read Frame from Camera")
            break
        try:
            # Analysis
            # enforce_detection=False to prevent no facial exception
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            if isinstance(result, list):
                result = result[0]
            current_emotion = result['dominant_emotion']
            # current_emotion = result.get('dominant_emotion', 'unknown')

        except Exception as e:
            print("Exception:", e)
            current_emotion = "error"
        # Detect per second
        time.sleep(1)
    cap.release()

@app.route('/emotion', methods=['GET'])
def get_emotion():
    """return emotion detected"""
    print("emotion detected:", current_emotion)
    return jsonify({"emotion": current_emotion})

if __name__ == '__main__':
    # Capture emotion by another thread
    t = Thread(target=capture_emotion)
    t.daemon = True
    t.start()
    # Use Flask service，Listen to 0.0.0.0:5005
    app.run(host='0.0.0.0', port=5005)



# from flask import Flask, request, jsonify
# import os
# import cv2
# import numpy as np
# from deepface import DeepFace
# from io import BytesIO
# from PIL import Image
#
# app = Flask(__name__)
#
# # ============== 1. 全局配置 ==============
# MODEL_NAME = "Facenet"      # 可换成 "ArcFace", "Facenet512", "SFace" 等
# DIST_THRESHOLD = 0.7        # 不同模型不同阈值，可根据实验调整
# DB_PATH = "faces_db"        # 已知人脸库路径
# face_db = []                # 用于存储数据库的人脸 embedding
#
# # ============== 2. 启动时构建数据库 ==============
# @app.on_request_startup
# def build_database():
#     global face_db
#     face_db = build_face_database(DB_PATH, model_name=MODEL_NAME)
#     app.logger.info(f"Face DB loaded. Total: {len(face_db)} entries")
#
# def build_face_database(db_path, model_name='Facenet'):
#     db = []
#     if not os.path.exists(db_path):
#         print(f"[WARNING] faces_db folder {db_path} does not exist.")
#         return db
#
#     for file_name in os.listdir(db_path):
#         if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
#             name = os.path.splitext(file_name)[0]  # 用文件名(去后缀)当作人的标签
#             img_path = os.path.join(db_path, file_name)
#             try:
#                 reps = DeepFace.represent(
#                     img_path=img_path,
#                     model_name=model_name,
#                     enforce_detection=False
#                 )
#                 if len(reps) > 0:
#                     db.append({
#                         'embedding': reps[0]['embedding'],
#                         'name': name
#                     })
#             except Exception as e:
#                 print(f"[ERROR] Cannot process {img_path}: {e}")
#     return db
#
# # ============== 3. 人脸识别函数 ==============
# def recognize_face(face_img_rgb, face_db, model_name='Facenet', threshold=0.7):
#     """
#     比对数据库，返回识别的姓名和最小距离
#     """
#     reps = DeepFace.represent(
#         img_path=face_img_rgb,
#         model_name=model_name,
#         enforce_detection=False
#     )
#     if len(reps) == 0:
#         return ("Unknown", None)
#
#     face_embed = reps[0]['embedding']
#     best_dist = float('inf')
#     best_name = "Unknown"
#
#     for item in face_db:
#         db_embed = item['embedding']
#         dist = np.linalg.norm(face_embed - db_embed)
#         if dist < best_dist:
#             best_dist = dist
#             best_name = item['name']
#
#     if best_dist > threshold:
#         best_name = "Unknown"
#
#     return best_name, best_dist
#
# # ============== 4. 对外暴露 API ==============
# @app.route("/analyze", methods=["POST"])
# def analyze_face():
#     """
#     接收图像，进行人脸检测、情绪分析和人脸识别，返回 JSON。
#     """
#     if "file" not in request.files:
#         return jsonify({"error": "No file part in request."}), 400
#
#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file."}), 400
#
#     try:
#         # 1) 读取为 numpy 数组(RGB)
#         pil_img = Image.open(BytesIO(file.read())).convert("RGB")
#         img_rgb = np.array(pil_img)
#
#         # 2) 人脸检测 + 情绪分析
#         results = DeepFace.analyze(
#             img_path=img_rgb,
#             actions=['emotion'],
#             detector_backend='opencv',  # 可换 'mtcnn' / 'ssd' / 'mediapipe' 等
#             enforce_detection=False
#         )
#         if not isinstance(results, list):
#             results = [results]
#
#         # 3) 遍历结果，做识别
#         output_data = []
#         for res in results:
#             region = res['region']  # x, y, w, h
#             emotion = res['dominant_emotion']
#
#             x, y, w, h = region['x'], region['y'], region['w'], region['h']
#             # 裁剪人脸
#             face_crop = img_rgb[y:y+h, x:x+w]  # RGB
#
#             # 人脸识别
#             name, dist = recognize_face(
#                 face_crop, face_db,
#                 model_name=MODEL_NAME,
#                 threshold=DIST_THRESHOLD
#             )
#
#             item = {
#                 "region": region,
#                 "dominant_emotion": emotion,
#                 "recognized_name": name
#             }
#             if dist is not None:
#                 item["distance"] = round(float(dist), 4)
#
#             output_data.append(item)
#
#         return jsonify({"faces": output_data})
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
# # ============== 5. 启动应用 ==============
# if __name__ == "__main__":
#     # 本地调试： python app.py
#     # 默认监听5000端口，可改你喜欢的
#     app.run(host="0.0.0.0", port=5000, debug=True)


