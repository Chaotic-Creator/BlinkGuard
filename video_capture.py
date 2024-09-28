import sys
import cv2
import platform
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QImage, QPixmap

class VideoThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QImage)

    def detect_blink(self, gray, landmarks, eye_points):
        # 获取眼睛区域坐标
        eye_region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in eye_points], dtype=np.int32)

        # 计算眼睛区域的边界
        min_x = np.min(eye_region[:, 0])
        max_x = np.max(eye_region[:, 0])
        min_y = np.min(eye_region[:, 1])
        max_y = np.max(eye_region[:, 1])

        # 裁剪眼睛区域
        eye = gray[min_y:max_y, min_x:max_x]

        # 应用阈值来区分瞳孔和眼白
        _, threshold_eye = cv2.threshold(eye, 70, 255, cv2.THRESH_BINARY)

        # 计算眼睛区域中白色像素的比例
        height, width = threshold_eye.shape
        white_pixels = cv2.countNonZero(threshold_eye)
        eye_area = height * width
        white_area_ratio = white_pixels / eye_area

        # 如果白色区域比例低于某个阈值，则判定为眨眼
        if white_area_ratio < 0.2:  # 阈值可以根据实际情况调整
            return True
        else:
            return False

    def adjust_brightness_contrast(image, brightness=0, contrast=0):
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow

            buf = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
        else:
            buf = image.copy()

        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)

            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

        return buf

    def run(self):
        # 摄像头捕获
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(0)

        while True:
            ret, cv_img = cap.read()
            if ret:
                # 这里可以添加眨眼检测的代码
                # ...
                
                # 将捕获的视频帧转换为QImage
                qt_img = self.convert_cv_qt(cv_img)
                self.change_pixmap_signal.emit(qt_img)

    @staticmethod
    def convert_cv_qt(cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        return convert_to_Qt_format.scaled(800, 600, QtCore.Qt.KeepAspectRatio)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("眼动追踪与眨眼检测")
        self.setGeometry(100, 100, 800, 600)

        # 创建一个 QLabel 对象来显示摄像头捕获的视频
        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)
        self.image_label.move(80, 60)

        self.blink_label = QLabel("Blinks: 0", self)
        self.blink_label.resize(200, 40)
        self.blink_label.move(640, 10)

        # 启动视频捕获线程
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    @QtCore.pyqtSlot(QImage)
    def update_image(self, qt_img):
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    def update_blink_count(self, count):
        self.blink_label.setText(f"Blinks: {count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
