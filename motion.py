import cv2

class MotionDetector:
    def __init__(self):
        self.previous_frame = None
        self.motion_detected = False
    
    def detect_motion(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (160,120))
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        if self.previous_frame is None:
            self.previous_frame = gray
            return False

        frame_diff = cv2.absdiff(self.previous_frame, gray)
        self.previous_frame = gray
        motion_score = frame_diff.mean()
        return motion_score > 8
        

        motion = any(cv2.contourArea(c) > 1500 for c in contours)
        self.previous_frame = gray
        self.motion_detected = motion
        return motion