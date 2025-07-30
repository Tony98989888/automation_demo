import os
import subprocess
import time
import tempfile
from PIL import Image
import cv2
import numpy as np


class ADBManager:
    def __init__(self, adb_path="adb", default_port=5555):
        """
        初始化ADB管理器
        :param adb_path: adb可执行文件路径
        :param default_port: 默认连接端口
        """
        self.adb_path = adb_path
        self.default_port = default_port
        self.device_serial = None

    def check_adb_available(self):
        """检查ADB是否可用"""
        result = subprocess.run([self.adb_path, "version"],
                                capture_output=True, text=True)
        return "Android Debug Bridge" in result.stdout

    def connect_device(self, ip="127.0.0.1", port=None):
        """
        连接模拟器设备
        :param ip: 设备IP地址
        :param port: 设备端口号
        :return: 是否连接成功
        """
        if port is None:
            port = self.default_port

        # 先断开已有连接
        self.disconnect_device()

        # 连接新设备
        result = subprocess.run([self.adb_path, "connect", f"{ip}:{port}"],
                                capture_output=True, text=True)

        if "connected" in result.stdout:
            self.device_serial = f"{ip}:{port}"
            return True
        return False

    def disconnect_device(self):
        """断开当前连接的设备"""
        if self.device_serial:
            subprocess.run([self.adb_path, "disconnect", self.device_serial])
            self.device_serial = None

    def execute_command(self, command, with_device=True):
        """
        执行ADB命令
        :param command: 命令字符串或列表
        :param with_device: 是否包含设备序列号
        :return: 命令执行结果
        """
        if isinstance(command, str):
            command = command.split()

        full_command = [self.adb_path]
        if with_device and self.device_serial:
            full_command.extend(["-s", self.device_serial])
        full_command.extend(command)

        result = subprocess.run(full_command,
                                capture_output=True,
                                text=True)
        return result.stdout.strip()

    # 基本操作功能
    def tap(self, x, y):
        """点击屏幕指定位置"""
        self.execute_command(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1, y1, x2, y2, duration=300):
        """滑动/拖拽操作"""
        self.execute_command([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2),
            str(duration)
        ])

    def long_press(self, x, y, duration=1000):
        """长按操作"""
        self.swipe(x, y, x, y, duration)

    def press_key(self, keycode):
        """按键操作"""
        self.execute_command(["shell", "input", "keyevent", str(keycode)])

    def input_text(self, text):
        """输入文本"""
        self.execute_command(["shell", "input", "text", text])

    # 屏幕相关功能
    def screenshot(self, save_path=None):
        """
        截取屏幕
        :param save_path: 保存路径，如果为None则返回PIL.Image对象
        :return: 如果save_path为None则返回Image对象，否则返回保存路径
        """
        # 使用临时文件保存截图
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            remote_path = f"/sdcard/screencap_{int(time.time())}.png"

            # 截屏并拉取到本地
            self.execute_command(["shell", "screencap", "-p", remote_path])
            self.execute_command(["pull", remote_path, tmp.name])
            self.execute_command(["shell", "rm", remote_path])

            # 读取图片
            img = Image.open(tmp.name)

            if save_path:
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                img.save(save_path)
                return save_path
            return img

    def get_screen_resolution(self):
        """获取屏幕分辨率"""
        output = self.execute_command(["shell", "wm", "size"])
        # 输出格式通常是: "Physical size: 1080x1920"
        size_str = output.split()[-1]
        return tuple(map(int, size_str.split("x")))

    # 高级功能
    def find_image_on_screen(self, template_path, threshold=0.8):
        """
        在屏幕上查找指定图片
        :param template_path: 模板图片路径
        :param threshold: 匹配阈值(0-1)
        :return: 匹配位置的坐标(x,y)，未找到返回None
        """
        # 获取屏幕截图
        screen_img = self.screenshot()
        screen_cv = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)

        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            raise ValueError(f"无法读取模板图片: {template_path}")

        # 模板匹配
        result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # 返回中心点坐标
            h, w = template.shape[:2]
            return (max_loc[0] + w // 2, max_loc[1] + h // 2)
        return None

    def tap_image(self, template_path, threshold=0.8):
        """
        点击屏幕上匹配的图片
        :param template_path: 模板图片路径
        :param threshold: 匹配阈值(0-1)
        :return: 是否点击成功
        """
        pos = self.find_image_on_screen(template_path, threshold)
        if pos:
            self.tap(*pos)
            return True
        return False

    # 设备信息
    def get_device_info(self):
        """获取设备基本信息"""
        info = {
            "model": self.execute_command(["shell", "getprop", "ro.product.model"]),
            "manufacturer": self.execute_command(["shell", "getprop", "ro.product.manufacturer"]),
            "android_version": self.execute_command(["shell", "getprop", "ro.build.version.release"]),
            "sdk_version": self.execute_command(["shell", "getprop", "ro.build.version.sdk"]),
            "resolution": self.get_screen_resolution(),
            "serial": self.execute_command(["get-serialno"], with_device=False)
        }
        return info


if __name__ == '__main__':
    adb = ADBManager(default_port=16384)
    adb.connect_device()
    adb.screenshot(r'../resources/test.png')
