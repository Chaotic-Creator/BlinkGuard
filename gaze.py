import cv2
import dlib
import numpy as np

# 加载Dlib的面部特征检测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# 定义瞳孔位置检测函数
def detect_pupil(frame, landmarks, eye_points, contour_area_threshold):
    # 将Landmarks转换为坐标数组
    region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in eye_points], np.int32)

    # 计算眼睛区域的边界框
    min_x = np.min(region[:, 0])
    max_x = np.max(region[:, 0])
    min_y = np.min(region[:, 1])
    max_y = np.max(region[:, 1])

    # 确保坐标不超出frame的边界
    min_x = max(min_x, 0)
    max_x = min(max_x, frame.shape[1])
    min_y = max(min_y, 0)
    max_y = min(max_y, frame.shape[0])

    # 裁剪出眼睛区域
    eye_region = frame[min_y:max_y, min_x:max_x]

    # 将眼睛区域转换为灰度图像
    gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)

    # 应用阈值处理
    _, threshold_eye = cv2.threshold(gray_eye, 90, 255, cv2.THRESH_BINARY)

    # 使用腐蚀和膨胀处理图像
    kernel = np.ones((3, 3), np.uint8)
    threshold_eye = cv2.erode(threshold_eye, kernel, iterations=2)
    threshold_eye = cv2.dilate(threshold_eye, kernel, iterations=4)
    threshold_eye = cv2.medianBlur(threshold_eye, 5)

    # 寻找轮廓以定位瞳孔
    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 假设最大的轮廓是瞳孔
        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) > contour_area_threshold:
            # 基于轮廓计算瞳孔中心
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                return True, cx, cy

    return False, 0, 0



# 初始化眨眼次数和帧计数
blink_count = 0
frame_count = 0
closed_eyes_frame_threshold = 3  # 眼睛连续闭合的帧数阈值



# 启动视频流
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        # 设置瞳孔检测的轮廓面积阈值
        contour_area_threshold = 100  # 可根据实际情况调整这个值

        left_eye_closed, _, _ = detect_pupil(frame, landmarks, range(36, 42), contour_area_threshold)
        right_eye_closed, _, _ = detect_pupil(frame, landmarks, range(42, 48), contour_area_threshold)

        if left_eye_closed and right_eye_closed:
            frame_count += 1
            if frame_count <= closed_eyes_frame_threshold:
                blink_count += 1
                frame_count = 0  # 重置帧计数器
        else:
            frame_count = 0

        # 显示眨眼次数
        cv2.putText(frame, "Blinks: {}".format(blink_count), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # 显示处理后的帧
    cv2.imshow("Blink Detection", frame)

    # 处理退出
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 释放视频捕获对象并关闭所有窗口
cap.release()
cv2.destroyAllWindows()
