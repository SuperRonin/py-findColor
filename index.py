import cv2
import numpy as np
import pyautogui
import mss
import time
import random
import win32api
from colorama import Fore, Style

# Settings
# 范围
X_FOV = 100
Y_FOV = 100
# x、Y移动速度
X_SPEED = 30
Y_SPEED = 30
# Y轴上的额外偏移
AIMING_PRECISION = 7
# 定义了触发点击动作的目标区域的大小，即当目标在这个区域内时触发点击动作
TRIGGERBOT_X_SIZE = 3
TRIGGERBOT_Y_SIZE = 25
AIM_KEYS = [0x02, 0x06]
TRIGGER_KEYS = [0x12, 0x05, 0x10]


#Advanced settings
LOWER_COLOR = [11, 100, 100]
UPPER_COLOR = [25, 255, 255]
# 用于控制脚本主循环中的等待时间，以减缓脚本的执行速度，防止过度占用CPU
ENHANCE_CPU_USAGE = 0.005
# 用于图像处理的核的大小
KERNEL_SIZE = (3, 3)
# 图像膨胀的迭代次数
DILATING = 5
DEBUGGING = False  # TO DO

class Prozac:
    def __init__(self):
        self.mouse = Mouse()
        self.capture = Capture()

    def listen(self):
        while True:
            for aim_key in AIM_KEYS:
                if win32api.GetAsyncKeyState(aim_key) < 0:
                    self.run("aim")
            for trigger_key in TRIGGER_KEYS:
                if win32api.GetAsyncKeyState(trigger_key) < 0:
                    self.run("click")
            time.sleep(ENHANCE_CPU_USAGE)

    def run(self, task):
        print(f"running {task} task")
        hsv = cv2.cvtColor(self.capture.get_screen(), cv2.COLOR_BGR2HSV)
        # mask = cv2.inRange(hsv, np.array([140, 120, 180]), np.array([160, 200, 255]))
        mask = cv2.inRange(hsv, np.array(LOWER_COLOR), np.array(UPPER_COLOR))
        kernel = np.ones(KERNEL_SIZE, np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=DILATING)
        thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        
        if contours:
            print(f"=====检测到目标=======")
            screen_center = (X_FOV // 2, Y_FOV // 2)
            min_distance = float('inf')
            closest_contour = None

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                center = (x + w // 2, y + h // 2)
                distance = ((center[0] - screen_center[0]) ** 2 + (center[1] - screen_center[1]) ** 2) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    closest_contour = contour

            x, y, w, h = cv2.boundingRect(closest_contour)
            cX = x + w // 2
            cY = y + h // 2
            top_most_y = y + AIMING_PRECISION

            x_offset = cX - screen_center[0]
            y_offset = top_most_y - screen_center[1]
            trigger_y_offset = cY - screen_center[1]

            if task == "aim":
                self.mouse.move(x_offset * (X_SPEED * 0.1), y_offset * (Y_SPEED * 0.1))
                print(f"Simulating mouse movement: x={x_offset * (X_SPEED * 0.1)}, y={y_offset * (Y_SPEED * 0.1)}")

            if task == "click":
                if abs(x_offset) <= TRIGGERBOT_X_SIZE and abs(trigger_y_offset) <= TRIGGERBOT_Y_SIZE:
                    self.mouse.click()
                    print("Simulating mouse click")

class Mouse:
    def __init__(self):
        pass

    def move(self, x, y):
        # Replace with actual mouse movement code
        monitor_size = pyautogui.size()
        x_center = monitor_size.width // 2
        y_center = monitor_size.height // 2
        target_x = x_center + X_FOV // 2 + x
        target_y = y_center + Y_FOV // 2 + y
        print(f"🚀 ~ file: index.py:88 ~ target_x:", target_x)
        print(f"🚀 ~ file: index.py:90 ~ target_y:", target_y)

        current_x, current_y = pyautogui.position()

        # Number of steps for the random trajectory
        num_steps = 3
        for step in range(num_steps + 1):
            # Calculate the intermediate position
            intermediate_x = int(current_x + (target_x - current_x) * step / num_steps)
            intermediate_y = int(current_y + (target_y - current_y) * step / num_steps)

            # Add random offsets to simulate natural movement
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)

            # Move the mouse to the intermediate position with random offsets
            pyautogui.moveTo(intermediate_x + offset_x, intermediate_y + offset_y, 0.1)

        # Move the mouse to the final position
        pyautogui.moveTo(target_x, target_y, 0.1)

       

    def click(self):
        # Replace with actual mouse click code
        pyautogui.click()
        print("Mouse clicked")

class Capture:
    def __init__(self):
        monitor_size = pyautogui.size()
        self.region = self.calculate_region(monitor_size)

    def calculate_region(self, monitor_size):
        x_center = monitor_size.width // 2
        y_center = monitor_size.height // 2
        left = x_center - X_FOV // 2
        top = y_center - Y_FOV // 2
        width = X_FOV
        height = Y_FOV
        # left = 1000
        # top = 1000
        # width = 1000
        # height = 1000
        print(f"位置信息为：{left, top, width, height}")
        return {'left': left, 'top': top, 'width': width, 'height': height}

    def get_screen(self):
        with mss.mss() as sct:
            screenshot = sct.grab(self.region)
            return np.array(screenshot)

if __name__ == '__main__':
    prozac_instance = Prozac()
    prozac_instance.listen()



# if __name__ == '__main__':
#     prozac_instance = Prozac()
    
#     print("Automatically triggering mouse movement and click every 5 seconds.")
#     try:
#         while True:
#             prozac_instance.run("aim")
#             time.sleep(ENHANCE_CPU_USAGE)
#             prozac_instance.run("click")
#             time.sleep(100)  # 等待5秒后再次触发
#     except KeyboardInterrupt:
#         print("Manual interruption detected. Exiting...")
#         sys.exit(0)