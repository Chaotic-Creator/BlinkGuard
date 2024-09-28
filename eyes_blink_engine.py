import math
import time

import cv2
import mediapipe as mp
import numpy as np

import utils

class EyeBlinkDetector:
    
    def __init__(self):
        self.CLOSED_EYES_FRAME = 3
        self.FONTS = cv2.FONT_HERSHEY_COMPLEX
        self.BLINK_RATIO = 3.8
        # Left eyes indices
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        # right eyes indices
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.MAX_BLINKS_PER_MINUTE = 25
        self.BLINK_RATIO_UPPER_LIMIT = 5.0  # BLINK_RATIO 的最大值
        self.BLINK_RATIO_LOWER_LIMIT = 2.5  # BLINK_RATIO 的最小值
        self.map_face_mesh = mp.solutions.face_mesh
        self.color = [utils.GRAY, utils.YELLOW]
        self.start_time_blink = None
        self.start_time = None
        self.CEF_counter = 0
        self.total_blinks = 0
        self.text = 'no break needed'
        self.is_listening = False
        self.is_face_detected = False

        self.last_warning_time = 0
        self.warning_interval = 10  # 警告消息的最小时间间隔（秒）

    def reset_values(self):
        self.start_time_blink = None
        self.CEF_counter = 0
        self.total_blinks = 0
        self.text = 'no break needed'
        self.start_time = None
        self.is_face_detected = False

    def landmarks_detection(self, img, results, draw=False):
        img_height, img_width = img.shape[:2]
        mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in
                      results.multi_face_landmarks[0].landmark]
        if draw:
            [cv2.circle(img, p, 2, (0, 255, 0), -1) for p in mesh_coord]

        return mesh_coord

    def euclidean_distance(self, point, point1):
        x, y = point
        x1, y1 = point1
        distance = math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)

        return distance

    def blink_ratio(self, landmarks, right_indices, left_indices):
        rh_right = landmarks[right_indices[0]]
        rh_left = landmarks[right_indices[8]]
        rv_top = landmarks[right_indices[12]]
        rv_bottom = landmarks[right_indices[4]]

        lh_right = landmarks[left_indices[0]]
        lh_left = landmarks[left_indices[8]]

        lv_top = landmarks[left_indices[12]]
        lv_bottom = landmarks[left_indices[4]]

        rh_distance = self.euclidean_distance(rh_right, rh_left)
        rv_distance = self.euclidean_distance(rv_top, rv_bottom)

        lv_distance = self.euclidean_distance(lv_top, lv_bottom)
        lh_distance = self.euclidean_distance(lh_right, lh_left)

        re_ratio = rh_distance / rv_distance
        le_ratio = lh_distance / lv_distance

        ratio = (re_ratio + le_ratio) / 2

        return ratio

    def process_image(self, frame, frame_counter):
        try:
            face_mesh = self.map_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
            frame, frame_height, results = self.fetch_face_data(face_mesh, frame)

            if results.multi_face_landmarks:

                if not self.is_face_detected:
                    self.is_face_detected = True
                    self.start_time_blink = time.time()
                    self.start_time = time.time()

                mesh_coords = self.landmarks_detection(frame, results, False)
                self.update_blink_data(frame, frame_height, mesh_coords)
                self.draw_eyes(frame, mesh_coords)
                self.total_blinks, self.text, self.start_time_blink = self.check_blink_rate(
                    self.total_blinks, self.start_time_blink, self.text)
                utils.colorBackgroundText(frame, f'Eyes: {self.text}', self.FONTS, 1.0, (30, 300), 2, self.color[0],
                                          self.color[1], 8,
                                          8)
                frame = self.show_activity_timer(frame, self.start_time)
                frame = self.calculate_frame_per_sec(frame, frame_counter, self.start_time)
            else:
                self.reset_values()

        except Exception as e:
            print(f"An error occurred: {e}")
            self.reset_values()  # 重置值以避免部分处理的状态

        self.advanced_visual_feedback(frame, self.total_blinks, self.CEF_counter)

        return frame

    def fetch_face_data(self, face_mesh, frame):
        frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        frame_height, frame_width = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        results = face_mesh.process(rgb_frame)

        return frame, frame_height, results

    """
    def fetch_face_data(self, face_mesh, frame):
        # 调整图像大小以提高处理速度
        frame_small = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        frame_height, frame_width = frame_small.shape[:2]
        rgb_frame = cv2.cvtColor(frame_small, cv2.COLOR_RGB2BGR)
        results = face_mesh.process(rgb_frame)

        return frame_small, frame_height, results
    """

    def update_blink_data(self, frame, frame_height, mesh_coords):
        ratio = self.blink_ratio(mesh_coords, self.RIGHT_EYE, self.LEFT_EYE)
        utils.colorBackgroundText(frame, f'Ratio : {round(ratio, 2)}', self.FONTS, 0.7, (30, 100), 2, utils.PINK,
                                  utils.YELLOW)
        if ratio > self.BLINK_RATIO:
            self.CEF_counter += 1
            utils.colorBackgroundText(frame, f'Blink', self.FONTS, 1.7, (int(frame_height / 2), 100), 2,
                                      utils.YELLOW, pad_x=6, pad_y=6)

        if self.CEF_counter > self.CLOSED_EYES_FRAME:
            # print(self.BLINK_RATIO)
            self.total_blinks += 1
            self.CEF_counter = 0
        utils.colorBackgroundText(frame, f'Total Blinks: {self.total_blinks}', self.FONTS, 0.7, (30, 150), 2)

    def draw_eyes(self, frame, mesh_coords):
        cv2.polylines(frame, [np.array([mesh_coords[p] for p in self.LEFT_EYE], dtype=np.int32)], True, utils.GREEN,
                      1, cv2.LINE_AA)
        cv2.polylines(frame, [np.array([mesh_coords[p] for p in self.RIGHT_EYE], dtype=np.int32)], True, utils.GREEN,
                      1, cv2.LINE_AA)

    def show_activity_timer(self, frame, start_time):
        end_time = time.time() - start_time
        frame = utils.textWithBackground(frame, f'Time on Screen: {int(end_time)} sec', self.FONTS, 1.0, (30, 220),
                                         bgOpacity=0.9, textThickness=2)

        return frame

    def calculate_frame_per_sec(self, frame, frame_counter, start_time):
        end_time = time.time() - start_time
        fps = frame_counter / end_time
        frame = utils.textWithBackground(frame, f'FPS: {round(fps, 1)}', self.FONTS, 1.0, (30, 50), bgOpacity=0.9,
                                         textThickness=2)

        return frame

    """
    def check_blink_rate(self, total_blinks, start_time_blink, text):
        elapsed_time = time.time() - start_time_blink
        if elapsed_time >= 60:
            blink_rate = total_blinks / (elapsed_time / 60)
            print(f"Blinks per minute: {blink_rate}")

            if blink_rate > self.MAX_BLINKS_PER_MINUTE:
                print("Eye fatigue")
                text = 'break needed'

            total_blinks = 0
            start_time_blink = time.time()

        return total_blinks, text, start_time_blink
    """

    def check_blink_rate(self, total_blinks, start_time_blink, text):
        elapsed_time = time.time() - start_time_blink
        if elapsed_time >= 60:
            blink_rate = total_blinks / (elapsed_time / 60)
            print(f"Blinks per minute: {blink_rate}")

            # 动态调整闭眼阈值
            if blink_rate > self.MAX_BLINKS_PER_MINUTE:
                self.BLINK_RATIO = max(self.BLINK_RATIO * 0.9, self.BLINK_RATIO_LOWER_LIMIT) # 如果眨眼过于频繁，降低阈值
            else:
                self.BLINK_RATIO = min(self.BLINK_RATIO * 1.1, self.BLINK_RATIO_UPPER_LIMIT) # 如果眨眼不频繁，提高阈值

            # 重置计数器
            total_blinks = 0
            start_time_blink = time.time()

        return total_blinks, text, start_time_blink

    def advanced_visual_feedback(self, frame, total_blinks, CEF_counter):
        current_time = time.time()

        # 如果检测到眼睛持续闭合
        if CEF_counter > self.CLOSED_EYES_FRAME and (current_time - self.last_warning_time) > self.warning_interval:
            self.show_warning_message(frame, "您可能需要休息一下！")
            self.last_warning_time = current_time

        # 根据眨眼次数显示不同的信息（根据需要调整）
        if total_blinks < 10:
            self.show_info_message(frame, "眨眼次数正常")
        elif total_blinks < 20:
            self.show_info_message(frame, "眨眼次数偏多")
        else:
            if (current_time - self.last_warning_time) > self.warning_interval:
                self.show_warning_message(frame, "频繁眨眼，注意休息！")
                self.last_warning_time = current_time

    """
    def show_warning_message(self, frame, message):
        # 显示警告信息
        cv2.putText(frame, message, (50, 50), self.FONTS, 1, (0, 0, 255), 2, cv2.LINE_AA)
    """

    def show_warning_message(self, frame, message):
        # 使用简单的文本显示，避免复杂的图形渲染
        cv2.putText(frame, message, (50, 50), self.FONTS, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    def show_info_message(self, frame, message):
        # 显示一般信息
        cv2.putText(frame, message, (50, 100), self.FONTS, 1, (0, 255, 0), 2, cv2.LINE_AA)

    def calculate_closed_eyes_frame(self, frame_rate):
        # 假设正常眨眼持续时间为100到400毫秒
        min_blink_duration = 0.1  # 最短眨眼时间，以秒为单位
        max_blink_duration = 0.4  # 最长眨眼时间，以秒为单位

        # 计算每秒帧数在这个时间范围内可能的帧数
        min_frames = int(math.ceil(min_blink_duration * frame_rate))
        max_frames = int(math.floor(max_blink_duration * frame_rate))

        # 返回一个合理的阈值
        return (min_frames + max_frames) // 2  # 取平均值作为初始阈值



"""
import pprint
pp = pprint.PrettyPrinter()
"""
