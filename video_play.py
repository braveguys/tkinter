import cv2

def Player():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def play(self):
        ret, image = self.cap.read()

        if not ret:
            self.cap.release()
            return
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)