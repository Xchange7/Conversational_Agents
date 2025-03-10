import cv2
from deepface import DeepFace


def main():
    # Open the camera (0 represents the default camera, if you have multiple cameras you can try 1,2,...)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Unable to open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Unable to read camera frame")
            break

        # Process only every few frames to reduce computation
        # This example is simplified, assuming every frame is analyzed; in practice, you could add a counter

        # The analyze method returns a list or dictionary containing analysis information of detected faces
        # If no face is detected in the frame, an exception may be thrown, so we need try/except to handle it
        try:
            # To avoid slowness due to high resolution, you can resize the frame here
            # For example: frame = cv2.resize(frame, (640, 480))

            results = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],  # Only detect emotion
                detector_backend='opencv'  # Use opencv as face detection backend
            )

            # Multiple faces may be detected simultaneously, here we only demonstrate the first one
            if isinstance(results, list):
                # DeepFace.analyze sometimes returns a list, with each element representing a face
                for res in results:
                    draw_face_box(frame, res)
            else:
                # Only one face detected, results is a dictionary
                draw_face_box(frame, results)

        except Exception as e:
            # When no face is detected or other errors occur, you can choose to skip or print the error
            pass

        cv2.imshow("Real-time Face Emotion", frame)

        # Press q to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# def draw_face_box(frame, analysis):
#     """
#     Draw face box and emotion information on the image based on the analysis data returned by DeepFace
#     """
#     region = analysis['region']  # Dictionary containing (x,y,w,h)
#     emotion = analysis['dominant_emotion']  # String, such as 'happy', 'sad', 'neutral', etc.
#
#     x, y, w, h = region['x'], region['y'], region['w'], region['h']
#     # Draw rectangle
#     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
#
#     # Write detected emotions above the frame
#     cv2.putText(
#         frame,
#         emotion,
#         (x, y - 10),  # Text will be displayed above the frame
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.9,  # Font size
#         (0, 255, 0),  # Font color
#         2  # Line width
#     )

def draw_face_box(frame, analysis):
    """
    Draw face box and emotion information on the image based on the analysis data returned by DeepFace
    """
    region = analysis['region']  # Face region information
    emotions = analysis['emotion']  # Emotion confidence scores

    x, y, w, h = region['x'], region['y'], region['w'], region['h']

    # Draw rectangle
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Convert emotion confidence to text, keep only the top three most likely emotions
    top_emotions = sorted(emotions.items(), key=lambda item: item[1], reverse=True)[:3]
    emotion_text = ", ".join([f"{e}: {round(p, 1)}%" for e, p in top_emotions])

    # Write detected emotions above the frame
    cv2.putText(
        frame,
        emotion_text,
        (x, y - 10),  # Text position (above the frame)
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,  # Font size
        (0, 255, 0),  # Font color (green)
        1  # Line width
    )

if __name__ == "__main__":
    main()
