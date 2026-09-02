import cv2

class Camera:
    def __init__(self, config):
        self.config = config
        self.cap = None

    def open(self):
        index = int(self.config.get("index", 0))
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.config.get("width", 1280)))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.config.get("height", 720)))
        self.cap.set(cv2.CAP_PROP_FPS, int(self.config.get("fps", 30)))
        if not self.cap.isOpened():
            raise RuntimeError("Webcam tidak dapat dibuka")
        return self

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return False, None
        if self.config.get("mirror", True):
            frame = cv2.flip(frame, 1)
        return True, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
