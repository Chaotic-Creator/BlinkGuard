import queue
import threading

import cv2

from eyes_blink_engine import EyeBlinkDetector
from mouse_keyboard_tracker import Tracker

# Create a queue for passing frames from processing thread to main thread
frame_queue = queue.Queue()
eye_blink_detector = EyeBlinkDetector()
tracker = Tracker()
is_listening = False

def reset_values():
    global is_listening, tracker

    is_listening = False
    tracker.set_listening(option=False)
    tracker = Tracker()

def process_image_thread(frame, frame_counter):
    frame = eye_blink_detector.process_image(frame, frame_counter)
    frame_queue.put(frame)
    if not eye_blink_detector.is_face_detected:
        reset_values()

def run_engine():
    global is_listening
    frame_counter = 0
    cap = cv2.VideoCapture(0)
    while True:
        frame_counter += 1  # frame counter
        ret, frame = cap.read()  # getting frame from camera

        if not ret:
            break  # no more frames break

        thread = threading.Thread(target=process_image_thread, args=(frame, frame_counter))
        thread.start()

        try:
            frame_to_display = frame_queue.get_nowait()
            cv2.imshow('frame', frame_to_display)
        except queue.Empty:
            pass

        if eye_blink_detector.is_face_detected and not is_listening:
            tracker.set_listening(option=True)
            tracker.run_tracker()
            is_listening = True

        key = cv2.waitKey(2)
        if key == ord('q') or key == ord('Q'):
            break

    cv2.destroyAllWindows()
    cap.release()

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading

class MyGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.state('zoomed')
        self.root.title("AI Timetracker")
        self.root.resizable(True, True)

        # ... 其他 Tkinter 部件 ...

        # 添加一个 Canvas 用于显示视频流
        self.video_canvas = tk.Canvas(self.root, width=640, height=480)
        self.video_canvas.pack()

        # 启动一个线程来处理视频流
        threading.Thread(target=self.video_loop, daemon=True).start()

        # ... 其他代码 ...

    def video_loop(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.root.update()

    # ... 其他函数 ...

    def run(self):
        self.root.mainloop()

app = MyGui()
app.run()

    
    # global start_time, start_time_blink, CEF_counter, total_blinks, text, tracker, is_listening, is_face_detected
    # frame_counter = 0
    # cap = cv2.VideoCapture(0)
    # while True:
    #     frame_counter += 1  # frame counter
    #     ret, frame = cap.read()  # getting frame from camera
    #
    #     if not ret:
    #         break  # no more frames break
    #         # Create and start a thread for the process_image function
    #     thread = threading.Thread(target=process_image_thread, args=(frame, frame_counter))
    #     thread.start()
    #
    #     # Get frames from the queue and display them
    #     try:
    #         frame_to_display = frame_queue.get_nowait()
    #         cv2.imshow('frame', frame_to_display)
    #     except queue.Empty:
    #         pass
    #
    #     if is_face_detected and not is_listening:
    #         tracker.set_listening(option=True)
    #         tracker.run_tracker()
    #         is_listening = True
    #
    #     key = cv2.waitKey(2)
    #     if key == ord('q') or key == ord('Q'):
    #         break
    # cv2.destroyAllWindows()
    # cap.release()

# def run_engine():
#     # Start monitoring tasks in parallel
#     blinks_thread = threading.Thread(target=process_video)
#     blinks_thread.start()

# How we would want to handle the commented parts?
