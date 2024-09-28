import time
import threading
import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key
from tkinter import ttk



class EyeTrackingApp:

    FACEMESH_LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
    FACEMESH_RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]

    def __init__(self, window_title):
        self.root = tk.Tk()
        self.root.state('zoomed')
        self.root.title(window_title)
        self.root.configure(bg='#404040')


        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



        self.on_break = False

        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # Create a style object
        style = ttk.Style()
        style.theme_use('clam')  # Use the 'clam' theme as a base for customization

        # Configure style for Button
        style.configure('Custom.TButton', 
                        background='#404040', 
                        foreground='white', 
                        bordercolor='white', 
                        borderwidth=2,
                        font=('Segoe UI', 14))

        # Configure style for Text
        text_bg = '#404040'  # Dark grey background for text
        text_fg = 'white'    # White text color

        # Main Frame
        main_frame = tk.Frame(self.root, bg='#404040')
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Video Frame
        video_frame = tk.Frame(main_frame, bg='#404040')
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right Section Frame
        right_frame = tk.Frame(main_frame, bg='#404040')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_video = tk.Canvas(video_frame, bg='#404040')
        self.canvas_video.pack(fill="both", expand=True)

        # Time Elapsed Frame
        self.total_time_count = 0
        time_frame = tk.Frame(right_frame, bg='#404040')
        time_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.total_time_elapsed = tk.Label(time_frame, text="Total Time Elapsed: 0", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.total_time_elapsed.pack()
        self.change_total_time_count()

        # Strictness Frame
        self.strictness = 10
        strictness_frame = tk.Frame(right_frame, bg='#404040')
        strictness_frame.pack(side=tk.TOP, fill=tk.X)
        strictness_frame.columnconfigure(0, weight=1)
        strictness_frame.columnconfigure(1, weight=1)
        self.strictness_value = tk.Label(strictness_frame, font=("Segoe UI", 20), text='Blink Strictness: ' + str(self.strictness), fg='white', bg='#404040')
        self.strictness_value.grid(row=0, columnspan=2)
        self.strictness_textbox = tk.Text(strictness_frame, font=("Segoe UI", 20), height=1, width=5, bg=text_bg, fg=text_fg)
        self.strictness_textbox.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")
        self.set_strictness_button = ttk.Button(strictness_frame, text="Set Strictness", style='Custom.TButton', command=self.set_strictness)
        self.set_strictness_button.grid(row=1, column=1, pady=(0, 5), padx=5, sticky="ew")
        self.strictness_explanation = tk.Label(strictness_frame, text="Blink Strictness means the maximum blink count per minute", font=("Arial", 15), fg='white', bg='#404040')
        self.strictness_explanation.grid(row=3, columnspan=2)
        self.warning_msg = tk.Label(strictness_frame, text="", font=("Arial", 15), fg='red', bg='#404040')
        self.warning_msg.grid(row=2, columnspan=2)

        # Blink Count Frame
        self.blink_verification_buffer_size = 5  # Number of frames to use for verification
        self.blink_verification_buffer = []
        self.frame_buffer_size = 20  # Size of the frame buffer
        self.frame_buffer = []
        self.blink_detection_buffer = []
        self.blink_detected_frames = 0
        self.blink_count = 0
        self.blink_frames_threshold = 5  # Increase the threshold for confirming a blink
        self.blink_cooldown = 10  # Increase cooldown period
        self.consecutive_frames_without_eyes = 0
        self.cooldown_counter = 0

        self.EAR_THRESHOLD = 0.21
        self.blink_confirmation_frames = 3  # Number of consecutive frames to confirm a blink
        self.eye_closed_counter = 0  # Counter for consecutive frames where eyes are closed
        self.eye_closed = False
        self.blink_count_frame = tk.Frame(right_frame, bg='#404040')
        self.blink_count_frame.pack(side=tk.TOP, fill=tk.X)
        self.total_blink_count = tk.Label(self.blink_count_frame, text="Total Blink Count: 0", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.total_blink_count.pack()

        # Break Label
        self.break_label = tk.Label(right_frame, text="Time for a break!", font=("Segoe UI", 20), fg='red', bg='#404040')
        self.break_label.pack(pady=10)
        self.break_label.pack_forget()

        # Spacer Frame
        spacer_frame = tk.Frame(right_frame, height=20, bg='#404040')
        spacer_frame.pack(side=tk.TOP, fill=tk.X)

        # Clicks and Keystrokes Frame
        self.total_click_amount = 0
        self.total_keystroke_count = 0
        clicks_frame = tk.Frame(right_frame, bg='#404040')
        clicks_frame.pack(side=tk.TOP, fill=tk.X)
        self.total_clicks = tk.Label(clicks_frame, text="Total Clicks: 0", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.total_clicks.pack()
        keystrokes_frame = tk.Frame(right_frame, bg='#404040')
        keystrokes_frame.pack(side=tk.TOP, fill=tk.X)
        self.total_keystrokes_label = tk.Label(keystrokes_frame, text="Total Keystroke Count: 0", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.total_keystrokes_label.pack()

        # Total Inputs Frame
        total_inputs_frame = tk.Frame(right_frame, bg='#404040')
        total_inputs_frame.pack(side=tk.TOP, fill=tk.X)
        self.total_inputs_label = tk.Label(total_inputs_frame, text="Total Inputs: 0", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.total_inputs_label.pack()

        # Input Strictness Frame
        self.input_strictness = 50
        input_strictness_frame = tk.Frame(right_frame, bg='#404040')
        input_strictness_frame.pack(side=tk.TOP, fill=tk.X)
        input_strictness_frame.columnconfigure(0, weight=1)
        input_strictness_frame.columnconfigure(1, weight=1)
        self.input_strictness_value = tk.Label(input_strictness_frame, font=("Segoe UI", 20), text='Input Strictness: ' + str(self.input_strictness), fg='white', bg='#404040')
        self.input_strictness_value.grid(row=0, columnspan=2)
        self.input_strictness_textbox = tk.Text(input_strictness_frame, font=("Segoe UI", 20), height=1, width=5, bg=text_bg, fg=text_fg)
        self.input_strictness_textbox.grid(row=1, column=0, pady=(0, 5), padx=5, sticky="ew")
        self.set_input_strictness_button = ttk.Button(input_strictness_frame, text="Set Input Strictness", style='Custom.TButton', command=self.set_input_strictness)
        self.set_input_strictness_button.grid(row=1, column=1, pady=(0, 5), padx=5, sticky="ew")
        self.input_strictness_warning_msg = tk.Label(input_strictness_frame, text="", font=("Arial", 15), fg='red', bg='#404040')
        self.input_strictness_warning_msg.grid(row=2, columnspan=2)

        # Reset Countdown Label
        self.reset_countdown_label = tk.Label(right_frame, text="Resets in 60 seconds", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.reset_countdown_label.pack(side=tk.TOP, fill=tk.X)


        # Grand counts initialization
        self.grand_blink_count = 0
        self.grand_input_count = 0

        # Grand Blink Count Label
        self.grand_blink_count_label = tk.Label(right_frame, text=f"Grand Blink Count: {self.grand_blink_count}", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.grand_blink_count_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Grand Input Count Label
        self.grand_input_count_label = tk.Label(right_frame, text=f"Grand Input Count: {self.grand_input_count}", font=("Segoe UI", 20), fg='white', bg='#404040')
        self.grand_input_count_label.pack(side=tk.BOTTOM, fill=tk.X)






        # Initialize input listeners in their own threads for keyboard and mouse
        self.input_listener_thread = threading.Thread(target=self.run_input_listeners)
        self.input_listener_thread.daemon = True  # Ensure the thread will close when the main program exits
        self.input_listener_thread.start()

        # Set initial tracking state and video source
        self.is_tracking = False
        self.video_source = 0  # Assuming default webcam
        self.vid = cv2.VideoCapture(self.video_source)  # Setup video capture
        self.delay = 15  # Delay between frames in milliseconds (for video processing)

        # Initialize the video processing in its own thread
        self.video_thread = threading.Thread(target=self.start_updates)
        self.video_thread.daemon = True  # Ensure the thread will close when the main program exits
        self.video_thread.start()

        self.root.mainloop()

    def on_close(self):
        # Create a new top-level window
        dialog = tk.Toplevel(self.root)
        dialog.title("Confirm Exit")
        dialog.configure(bg='#404040')
        dialog.geometry("300x100")  # Width x Height

        # Center the dialog window
        window_width = dialog.winfo_reqwidth()
        window_height = dialog.winfo_reqheight()
        position_right = int(dialog.winfo_screenwidth()/2 - window_width/2)
        position_down = int(dialog.winfo_screenheight()/2 - window_height/2)
        dialog.geometry("+{}+{}".format(position_right, position_down))

        # Message
        tk.Label(dialog, text="Are you sure you want to exit?", bg='#404040', fg='white').pack(pady=10)

        # Yes and No buttons
        yes_button = tk.Button(dialog, text="Yes", command=lambda: [self.root.withdraw(), dialog.destroy(), self.show_summary_dialog()], width=10)
        yes_button.pack(side=tk.LEFT, padx=(50, 10), pady=10)
        no_button = tk.Button(dialog, text="No", command=dialog.destroy, width=10)
        no_button.pack(side=tk.RIGHT, padx=(10, 50), pady=10)

        # Make the dialog modal
        dialog.transient(self.root)  # Set to be on top of the main window
        dialog.grab_set()  # Prevents any other window from interacting until this dialog is closed
        self.root.wait_window(dialog)  # Wait for the dialog to be closed
    def show_summary_dialog(self):
        # Create a new root window for the summary
        summary_root = tk.Tk()
        summary_root.title("Session Summary")
        summary_root.configure(bg='#404040')
        summary_root.geometry("400x200")  # Adjust size as needed

        # Center the window
        window_width = summary_root.winfo_reqwidth()
        window_height = summary_root.winfo_reqheight()
        position_right = int(summary_root.winfo_screenwidth()/2 - window_width/2)
        position_down = int(summary_root.winfo_screenheight()/2 - window_height/2)
        summary_root.geometry("+{}+{}".format(position_right, position_down))

        # Display summary information
        tk.Label(summary_root, text=f"Total Time Elapsed: {divmod(self.total_time_count, 60)[0]} minutes, {divmod(self.total_time_count, 60)[1]} seconds", bg='#404040', fg='white').pack(pady=10)
        tk.Label(summary_root, text=f"Grand Total Blinks: {self.grand_blink_count}", bg='#404040', fg='white').pack(pady=10)
        tk.Label(summary_root, text=f"Grand Total Inputs: {self.grand_input_count}", bg='#404040', fg='white').pack(pady=10)

        # Exit button
        exit_button = tk.Button(summary_root, text="Exit", command=lambda: [summary_root.destroy(), self.root.destroy()], width=10)
        exit_button.pack(pady=20)

        summary_root.mainloop()




    def set_input_strictness(self):
        value = self.input_strictness_textbox.get("1.0", "end").strip()
        try:
            intvalue = int(value)
            if 0 <= intvalue <= 500:
                self.input_strictness = intvalue
                self.input_strictness_value.config(text="Input Strictness: " + str(intvalue))
                self.input_strictness_warning_msg.config(text="")
            else:
                self.input_strictness_warning_msg.config(text="Invalid Input! Please enter a number between 0 and 500!")
        except ValueError:
            self.input_strictness_warning_msg.config(text="Invalid Input! Please enter an integer!")

    def reset_counters(self):
        # Reset all the counters and update their respective labels
        self.blink_count = 0
        self.total_blink_count.config(text="Total Blink Count: 0")
        self.total_click_amount = 0
        self.total_keystroke_count = 0
        self.update_click_count()
        self.update_keystroke_count()
        self.update_total_inputs_label()

    def change_total_time_count(self):
        self.total_time_elapsed.config(text=f"Total Time Elapsed: {self.total_time_count}")
        self.total_time_count += 1
        self.root.after(1000, self.change_total_time_count)

    def update_total_inputs_label(self):
        total_inputs = self.total_click_amount + self.total_keystroke_count
        self.total_inputs_label.config(text=f"Total Inputs: {total_inputs}")
        if total_inputs >= self.input_strictness and not self.on_break:
            self.initiate_break()
    def run_input_listeners(self):
        # Initialize the mouse listener
        mouse_listener = MouseListener(on_click=self.on_click)
        mouse_listener.start()

        # Initialize the keyboard listener
        keyboard_listener = KeyboardListener(on_press=self.on_press)
        keyboard_listener.start()

    def show_break_label(self):
        self.break_label.pack()

    def hide_break_label(self):
        self.break_label.pack_forget()


    def start_eye_tracking(self):
        # Directly start tracking without checking the button state
        self.is_tracking = True
        self.canvas_video.configure(bg='black')

    def handle_reset_countdown(self, countdown=60):
        if hasattr(self, 'after_id'):  # Check if there's an existing after call
            self.root.after_cancel(self.after_id)  # Cancel the previous after call

        if self.on_break:
            if countdown > 0:
                self.reset_countdown_label.config(text=f"Break time! {countdown} seconds remaining")
                self.after_id = self.root.after(1000, self.handle_reset_countdown, countdown - 1)
            else:
                self.on_break = False
                self.reset_countdown_label.config(text="Resets in 60 seconds")
                self.hide_break_label()
                self.reset_counters()  # Call the method to reset the counters
                self.handle_reset_countdown()  # Restart the countdown
        else:
            if countdown > 0:
                self.reset_countdown_label.config(text=f"Resets in {countdown} seconds")
                self.after_id = self.root.after(1000, self.handle_reset_countdown, countdown - 1)
            else:
                self.reset_counters()  # Call the method to reset the counters
                self.handle_reset_countdown()  # Restart the countdown


    

    def clear_video_feed(self):
        self.canvas_video.delete("all")
        self.canvas_video.configure(bg='white')
        self.canvas_video.create_text(
            self.canvas_video.winfo_width() // 2, self.canvas_video.winfo_height() // 2,
            text="Video feed stopped", font=("Arial", 20), fill="black"
        )

    def start_updates(self):
        if not self.is_tracking:
            self.start_eye_tracking()
        self.update()

    def update(self):
        ret, frame = self.vid.read()
        if ret and self.is_tracking:
            frame = cv2.flip(frame, 1)
            canvas_width = self.canvas_video.winfo_width()
            canvas_height = self.canvas_video.winfo_height()

            if canvas_width > 0 and canvas_height > 0:
                frame = self.resize_with_aspect_ratio(frame, width=canvas_width, height=canvas_height)
                if frame is not None:
                    # Use MediaPipe to detect face and eyes
                    frame, eye_regions = self.detect_eyes_with_mediapipe(frame)
                    
                    # Use Haar Cascade within the eye regions detected by MediaPipe
                    frame = self.detect_blinks_with_haar(frame, eye_regions)

                    self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                    self.canvas_video.create_image((canvas_width - self.photo.width()) // 2, (canvas_height - self.photo.height()) // 2, image=self.photo, anchor=tk.NW)
        self.root.after(self.delay, self.update)


    def resize_with_aspect_ratio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        (h, w) = image.shape[:2]

        # Calculate the aspect ratio of the image and the desired aspect ratio
        image_aspect = w / h
        desired_aspect = width / height if width is not None and height is not None else image_aspect

        # Calculate scaling factors for resizing the image while maintaining aspect ratio
        if image_aspect > desired_aspect:
            # Image is wider than the desired aspect ratio
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            # Image is taller or equal to the desired aspect ratio
            r = height / float(h)
            dim = (int(w * r), height)

        # Check that dimensions are valid before attempting to resize
        if dim[0] > 0 and dim[1] > 0:
            resized = cv2.resize(image, dim, interpolation=inter)
            return resized
        return None



    def set_strictness(self):
        value = self.strictness_textbox.get("1.0", "end").strip()
        try:
            intvalue = int(value)
            if 0 <= intvalue <= 75:
                self.strictness = intvalue
                self.strictness_value.config(text=" Blink Strictness: " + str(intvalue))
                self.warning_msg.config(text="")
            else:
                self.warning_msg.config(text="Invalid Input! Please enter a number between 0 and 75!")
        except ValueError:
            self.warning_msg.config(text="Invalid Input! Please enter an integer!")

   
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.total_click_amount += 1
            self.update_click_count()
            self.update_total_inputs_label()
            self.grand_input_count += 1  # Increment grand input count correctly
            self.grand_input_count_label.config(text=f"Grand Input Count: {self.grand_input_count}")  # Update the label




    def on_press(self, key):
        self.total_keystroke_count += 1
        self.update_keystroke_count()
        self.update_total_inputs_label()
        self.grand_input_count += 1  # Increment grand input count correctly
        self.grand_input_count_label.config(text=f"Grand Input Count: {self.grand_input_count}")  # Update the label

    def update_click_count(self):
        self.total_clicks.config(text="Total Clicks: " + str(self.total_click_amount))
        self.update_total_inputs_label()

    def update_keystroke_count(self):
        self.total_keystrokes_label.config(text="Total Keystroke Count: " + str(self.total_keystroke_count))
    def run_mouse_listener(self):
        with MouseListener(on_click=self.on_click) as listener:
            listener.join()

    # Separate method to run the keyboard listener
    def run_keyboard_listener(self):
        with KeyboardListener(on_press=self.on_press) as listener:
            listener.join()

    """
        Eye blink engine time!
    """

    def detect_eyes_with_mediapipe(self, frame):
        # Process the frame with MediaPipe Face Mesh
        results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        eye_regions = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                frame, left_eye = self.extract_eye_region(frame, face_landmarks, self.FACEMESH_LEFT_EYE)
                frame, right_eye = self.extract_eye_region(frame, face_landmarks, self.FACEMESH_RIGHT_EYE)
                eye_regions.extend([left_eye, right_eye])

        return frame, eye_regions

    
    def extract_eye_region(self, frame, landmarks, indices):
        frame_height, frame_width = frame.shape[:2]
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = -float('inf'), -float('inf')

        for index in indices:
            landmark = landmarks.landmark[index]
            x, y = int(landmark.x * frame_width), int(landmark.y * frame_height)
            min_x, min_y, max_x, max_y = min(x, min_x), min(y, min_y), max(x, max_x), max(y, max_y)

        # Increase the expansion margin to create a larger area around the eyes
        expansion_margin = 50  # Adjust this value as needed to make the rectangles bigger
        min_x, min_y = max(0, min_x - expansion_margin), max(0, min_y - expansion_margin)
        max_x, max_y = min(frame_width, max_x + expansion_margin), min(frame_height, max_y + expansion_margin)

        return frame, (min_x, min_y, max_x - min_x, max_y - min_y)


    
    def detect_blinks_with_haar(self, frame, eye_regions):
        eyes_detected_in_frame = 0  # Reset count of eyes detected in the current frame

        for (x, y, w, h) in eye_regions:
            eye_roi = frame[y:y+h, x:x+w]
            gray_eye_roi = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)

            # Adjust detection parameters for more sensitive eye detection
            scaleFactor = 1.1
            minNeighbors = 5  # Lower value may help detect eyes more sensitively
            minSize = (20, 20)  # Smaller size to detect smaller eye openings

            eyes_detected = self.eye_cascade.detectMultiScale(
                gray_eye_roi,
                scaleFactor=scaleFactor,
                minNeighbors=minNeighbors,
                minSize=minSize
            )

            # If eyes are detected, increment the counter
            if len(eyes_detected) > 0:
                eyes_detected_in_frame += 1
                # Optionally draw rectangles around detected eyes
                for (ex, ey, ew, eh) in eyes_detected:
                    cv2.rectangle(eye_roi, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Update the blink detection logic to be less strict
        # A blink is considered if no eyes are detected in the current frame
        self.blink_detection_buffer.append(eyes_detected_in_frame == 0)

        # Reduce the size of the blink detection buffer for quicker response
        self.blink_frames_threshold = 3  # Reduce threshold for faster blink detection

        if len(self.blink_detection_buffer) > self.blink_frames_threshold:
            self.blink_detection_buffer.pop(0)

        # Check for blink pattern with the updated, less strict logic
        if any(self.blink_detection_buffer):
            if self.cooldown_counter == 0:
                self.blink_count += 1

                self.update_blink_count()
                # Reset the buffer after a blink is detected to avoid multiple detections for a single blink
                self.blink_detection_buffer = [False] * self.blink_frames_threshold
                # Set a very short cooldown to allow detecting rapid blinks
                self.cooldown_counter = 2  # Very short cooldown
        else:
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1

        return frame



    def is_blink_pattern(self):
        # Adjust the pattern logic based on testing
        # Considering a simple scenario where a blink is detected when the eyes are not detected
        # in a series of consecutive frames within the blink detection buffer
        if len(self.blink_detection_buffer) < self.blink_frames_threshold:
            return False
        # Check if eyes were not detected in the required number of consecutive frames
        return all(self.blink_detection_buffer)




    def update_blink_count(self):
        if not self.on_break:  # Only update blink count if not on a break
            self.total_blink_count.config(text=f"Total Blink Count: {self.blink_count}")
            self.grand_blink_count += 1  # Correct place to increment grand blink count
            self.grand_blink_count_label.config(text=f"Grand Blink Count: {self.grand_blink_count}")  # Update the label
            
            if self.blink_count >= self.strictness:
                self.initiate_break()


    def initiate_break(self):
        # Set the state to break and update the UI accordingly
        self.on_break = True
        self.show_break_label()
        self.reset_countdown_label.config(text="Timer stopped, take a break!")
        self.handle_reset_countdown(30)  # Start a 30-second break countdown

        # Reset all counts
        self.reset_counters()

    def verify_blink(self):
        # Verify if the pattern in the buffer corresponds to a blink
        # Example: A true blink would have a sequence of False (eyes detected) followed by True (eyes not detected)
        if len(self.blink_verification_buffer) < self.blink_verification_buffer_size:
            return False
        return all(self.blink_verification_buffer[-self.blink_verification_buffer_size:])

    

app = EyeTrackingApp("MediaPipe Eye Tracking with Tkinter")
