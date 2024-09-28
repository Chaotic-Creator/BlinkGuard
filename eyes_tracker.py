import queue
import threading
import time
from tkinter import messagebox  # Import messagebox for notifications

import cv2

import utils
from activity_inactivity_engine import predict
from eyes_blink_engine import EyeBlinkDetector
from mouse_keyboard_tracker import Tracker

class EyeTracker:
    def __init__(self):
        self.prediction = 'no break needed'
        self.frame_queue = queue.Queue()
        self.eye_blink_detector = EyeBlinkDetector()
        self.tracker = Tracker()
        self.is_listening = False
        self.is_running = True
        self.show_message = False
        # Start the engine in a separate thread
        threading.Thread(target=self.run_engine).start()

    def reset_values(self):
        # Reset values when needed
        self.is_listening = False
        self.tracker.set_listening(option=False)
        self.tracker = Tracker()
        self.prediction = 'no break needed'
        self.show_message = False

    def process_image_thread(self, frame, frame_counter):
        # Process each frame in a separate thread
        frame = self.eye_blink_detector.process_image(frame, frame_counter)
        self.break_prediction()
        utils.colorBackgroundText(frame, f'AI Prediction: {self.prediction}', self.eye_blink_detector.FONTS, 1.0,
                                  (30, 370), 2, self.eye_blink_detector.color[0], self.eye_blink_detector.color[1], 8,
                                  8)
        self.frame_queue.put(frame)
        if not self.show_message and \
                (self.prediction != 'no break needed' or self.eye_blink_detector.text != 'no break needed'):
            self.show_message = True
            # Show a Tkinter notification
            messagebox.showinfo("Take a Break! \nLook away and relax.")

        if not self.eye_blink_detector.is_face_detected:
            self.reset_values()

    def __init__(self):
        self.frame_queue = queue.Queue()
        self.eye_blink_detector = EyeBlinkDetector()
        self.tracker = Tracker()
        self.is_listening = False
        self.is_running = True
        self.show_message = False
        threading.Thread(target=self.run_engine).start()

    def reset_values(self):
        self.is_listening = False
        self.tracker.set_listening(option=False)
        self.tracker = Tracker()
        self.show_message = False

    def process_image_thread(self, frame, frame_counter):
        frame = self.eye_blink_detector.process_image(frame, frame_counter)
        # Add any additional processing here
        self.frame_queue.put(frame)
        if not self.eye_blink_detector.is_face_detected:
            self.reset_values()

    def run_engine(self):
        frame_counter = 0
        cap = cv2.VideoCapture(0)
        while self.is_running:
            frame_counter += 1
            ret, frame = cap.read()
            if not ret:
                break
            # Process each frame in a separate thread
            thread = threading.Thread(target=self.process_image_thread, args=(frame, frame_counter))
            thread.start()
            try:
                frame_to_display = self.frame_queue.get_nowait()
                cv2.imshow('frame', frame_to_display)
            except queue.Empty:
                pass
            if self.eye_blink_detector.is_face_detected and not self.is_listening:
                # Start the tracker when a face is detected
                self.tracker.set_listening(option=True)
                self.tracker.run_tracker()
                self.is_listening = True
            key = cv2.waitKey(2)
            if key == 27:  # Use the ASCII value for the 'Esc' key
                # Stop the application when 'Esc' key is pressed
                self.is_running = False
                self.tracker.set_listening(False)

        # Clean up
        cv2.destroyAllWindows()
        cap.release()

if __name__ == "__main__":
    app = EyeTracker()
