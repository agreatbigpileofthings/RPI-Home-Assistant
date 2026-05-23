import cv2

class MotionDetector:
    def __init__(self):
        self.previous_frame = None
        self.motion_detected = False
    
    def detect_motion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.previous_frame is None:
            self.previous_frame = gray
            return False

        frame_diff = cv2.absdiff(self.previous_frame, gray)
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.motion_detected = any(
            cv2.contourArea(c) > 1500
            for c in contours
        )
        self.previous_frame = gray

        return self.motion_detected