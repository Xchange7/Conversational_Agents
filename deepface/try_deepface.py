import cv2
from deepface import DeepFace


def main():
    # 打开摄像头（0 表示默认摄像头，如果有多个摄像头可以尝试 1,2,...）
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧")
            break

        # 每隔若干帧进行一次识别，可以减少计算量
        # 本例中简化，假设每帧都做分析，实际可加个计数器控制

        # analyze 方法返回一个列表或字典，包含检测到的人脸的分析信息
        # 如果帧中检测不到人脸，可能会抛出异常，需要 try/except 捕获处理
        try:
            # 为避免分辨率过大导致速度太慢，可在此对 frame 进行适当缩放
            # 例如： frame = cv2.resize(frame, (640, 480))

            results = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],  # 只检测情绪
                detector_backend='opencv'  # 使用opencv作为人脸检测后端
            )

            # 可能同时检测到多张人脸，这里只演示第一张
            if isinstance(results, list):
                # DeepFace.analyze 有时返回列表，每个元素代表一张人脸
                for res in results:
                    draw_face_box(frame, res)
            else:
                # 只检测到一张人脸，results就是一个字典
                draw_face_box(frame, results)

        except Exception as e:
            # 未检测到人脸等其他错误时，可以选择跳过或者打印错误
            pass

        cv2.imshow("Real-time Face Emotion", frame)

        # 按下q键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# def draw_face_box(frame, analysis):
#     """
#     根据 DeepFace 返回的分析数据，在图像上绘制人脸框和情绪信息
#     """
#     region = analysis['region']  # 字典，包含(x,y,w,h)
#     emotion = analysis['dominant_emotion']  # 字符串，如 'happy', 'sad', 'neutral' 等
#
#     x, y, w, h = region['x'], region['y'], region['w'], region['h']
#     # 绘制矩形框
#     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
#
#     # 在方框上方写上检测到的情绪
#     cv2.putText(
#         frame,
#         emotion,
#         (x, y - 10),  # 字会显示在方框的上方
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.9,  # 字体大小
#         (0, 255, 0),  # 字体颜色
#         2  # 线宽
#     )

def draw_face_box(frame, analysis):
    """
    根据 DeepFace 返回的分析数据，在图像上绘制人脸框和情绪信息
    """
    region = analysis['region']  # 人脸区域信息
    emotions = analysis['emotion']  # 各情绪置信度

    x, y, w, h = region['x'], region['y'], region['w'], region['h']

    # 绘制矩形框
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 将情绪置信度转换成文本，只保留前三种最可能的情绪
    top_emotions = sorted(emotions.items(), key=lambda item: item[1], reverse=True)[:3]
    emotion_text = ", ".join([f"{e}: {round(p, 1)}%" for e, p in top_emotions])

    # 在方框上方写上检测到的情绪
    cv2.putText(
        frame,
        emotion_text,
        (x, y - 10),  # 文字位置（框的上方）
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,  # 字体大小
        (0, 255, 0),  # 字体颜色（绿色）
        1  # 线宽
    )

if __name__ == "__main__":
    main()
