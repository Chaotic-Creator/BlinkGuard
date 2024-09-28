import threading
import time
from math import ceil
from pynput import keyboard, mouse

class Tracker:
    
    def __init__(self):
        # Define a global variable to track the last activity time
        self.last_activity_time = time.time()
        self.start_inactive_time = None
        self.inactive_time = 0
        self.total_inactive_time = 0
        # Define the inactivity threshold (in seconds)
        self.inactivity_threshold = 5
        self.timer_started = False
        self.__is_listening = False
        # print(self.userID) ### What is this for?
        # Collect events until released
        self.mouse_listener = mouse.Listener(
            on_move=self.__on_move,
            on_click=self.__on_click,
            on_scroll=self.__on_scroll)
        # Collect events until released
        self.keyboard_listener = keyboard.Listener(
            on_press=self.__on_press,
            on_release=self.__on_release)

    def set_listening(self, option):
        self.__is_listening = option

    # Define a callback function for mouse events
    def __on_move(self, x, y):
        # Update the last activity time
        self.last_activity_time = time.time()

        # If the timer is not started, start it
        if not self.timer_started:
            print("Timer started.")
            self.timer_started = True
            if self.inactive_time != 0:
                print(self.total_inactive_time)
                self.total_inactive_time += self.inactive_time

    # Define a callback function for mouse events
    def __on_click(self, x, y, button, pressed):
        # Update the last activity time
        self.last_activity_time = time.time()

        # If the timer is not started, start it
        if not self.timer_started:
            print("Timer started.")
            self.timer_started = True
            if self.inactive_time != 0:
                print(self.inactive_time)
                self.total_inactive_time += self.inactive_time

    # Define a callback function for mouse events
    def __on_scroll(self, x, y, dx, dy):
        # Update the last activity time
        self.last_activity_time = time.time()

        # If the timer is not started, start it
        if not self.timer_started:
            print("Timer started.")
            self.timer_started = True
            if self.inactive_time != 0:
                print(self.inactive_time)
                self.total_inactive_time += self.inactive_time

    # Define a callback function for keyboard events
    def __on_press(self, key):
        # 更新最后活动时间
        self.last_activity_time = time.time()

        # 如果定时器尚未启动，则启动它
        if not self.timer_started:
            print("Timer started due to key press.")
            self.timer_started = True
            if self.inactive_time != 0:
                self.total_inactive_time += self.inactive_time
                self.inactive_time = 0  # 重置非活动时间

    # Define a callback function for keyboard events
    def __on_release(self, key):
        # Update the last activity time
        self.last_activity_time = time.time()

        # If the timer is not started, start it
        if not self.timer_started:
            print("Timer started.")
            self.timer_started = True
            if self.inactive_time != 0:
                print(self.inactive_time)
                self.total_inactive_time += self.inactive_time

    #
    def track_user_activity(self):
        # Start listening for events
        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.timer_started = True

        # Listen for events
        try:
            while self.__is_listening:
                # Check for inactivity
                if time.time() - self.last_activity_time >= self.inactivity_threshold:
                    # Inactivity detected, stop the timer if it's running
                    if self.timer_started:
                        print("Timer stopped. User is inactive.")
                        self.timer_started = False
                        self.start_inactive_time = time.time()
                    self.inactive_time = self.inactivity_threshold + ceil(time.time() - self.start_inactive_time)
            else:
                self.keyboard_listener.stop()
                self.mouse_listener.stop()
        except KeyboardInterrupt:
            # Stop the listeners when the script is interrupted
            self.keyboard_listener.stop()
            self.mouse_listener.stop()

    # 
    def run_tracker(self):
        # Start monitoring tasks in parallel
        monitor_thread = threading.Thread(target=self.track_user_activity)
        monitor_thread.start()

    # 
    def test_tracker(self):
        # Set up and run the tracker
        self.set_listening(True)
        self.run_tracker()
        time.sleep(10)
        self.set_listening(False)

# 运行测试
tkr = Tracker()
tkr.test_tracker()

"""
import unittest

class TestTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = Tracker()  # 假设你的 Tracker 类已经导入
        self.tracker.set_listening(True)
        self.tracker.run_tracker()  # 运行追踪器

    def test_inactivity(self):
        # 模拟用户一段时间没有活动
        time.sleep(self.tracker.inactivity_threshold + 1)
        self.tracker.track_user_activity()  # 这可能需要调整以适应实际逻辑
        self.assertTrue(self.tracker.total_inactive_time > 0)

    def tearDown(self):
        self.tracker.set_listening(False)

# 运行测试
if __name__ == '__main__':
    unittest.main()
"""
