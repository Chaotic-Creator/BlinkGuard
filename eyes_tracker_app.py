import tkinter as tk
from PIL import Image, ImageTk

from eyes_tracker import EyeTracker

class EyeTrackerAPP:
    def __init__(self, master):
        # Initialize the tkinter window
        self.master = master
        self.master.title("PauseForSight")
        self.master.geometry("400x250")  # Set the window size

        # Load the logo and resize it
        self.logo_image = Image.open("logo.png")
        self.logo_image = self.logo_image.resize((100, 100), )
        self.logo_image = ImageTk.PhotoImage(self.logo_image)

        # Display the logo image
        logo_label = tk.Label(root, image=self.logo_image)
        logo_label.pack()

        # Display the application title
        app_title = tk.Label(root, text="PauseForSight", font=("Arial", 20))
        app_title.pack()

        # Create and display the "Start Tracker" button
        self.start_button = tk.Button(master, text="Start Tracker", command=self.start_eye_tracker)
        self.start_button.pack(pady=10)  # Add padding between the button and the label

        # Create and display the label for the message
        self.message_label = tk.Label(root, text="Press 'ESC' to stop the tracker.", font=("Arial", 12))
        self.message_label.pack()

    def start_eye_tracker(self):
        # Start the EyeTracker when the button is clicked
        app = EyeTracker()
        self.master.iconify()  # Minimize the window

# Create the main Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    gui = EyeTrackerAPP(root)
    root.mainloop()
