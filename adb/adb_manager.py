import os
import subprocess
import time
from typing import Optional, Union

import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog


class ADBManager:
    def __init__(
        self, adb_path: str = "adb", host: str = "127.0.0.1", port: int = 7555
    ):
        self.adb_path = adb_path
        self.host = host
        self.port = port
        self.device_serial = None
        self.connected = False

    def connect(self) -> bool:
        try:
            self.disconnect()
            connect_cmd = f"{self.adb_path} connect {self.host}:{self.port}"
            result = subprocess.run(
                connect_cmd, shell=True, capture_output=True, text=True
            )

            if "connected" in result.stdout:
                self.device_serial = f"{self.host}:{self.port}"
                self.connected = True
                return True
            else:
                print(f"连接失败: {result.stdout.strip()}")
                return False
        except Exception as e:
            print(f"连接过程中发生错误: {str(e)}")
            return False

    def disconnect(self) -> None:
        if self.connected:
            disconnect_cmd = f"{self.adb_path} disconnect {self.host}:{self.port}"
            subprocess.run(
                disconnect_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.connected = False
            self.device_serial = None

    def execute_command(self, command: str, with_device: bool = True) -> str:
        try:
            full_command = self.adb_path
            if with_device and self.device_serial:
                full_command += f" -s {self.device_serial}"
            full_command += f" {command}"

            result = subprocess.run(
                full_command, shell=True, capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"执行命令 {command} 时出错: {str(e)}")
            return ""

    def screenshot(
        self, save_path: Optional[str] = None, return_array: bool = False
    ) -> Union[None, np.ndarray]:
        try:
            temp_path = "/sdcard/screencap_temp.png"
            result = self.execute_command(f"shell screencap -p {temp_path}")
            print(f"Screenshot command result: {result}")

            local_temp = "temp_screencap.png"
            pull_result = self.execute_command(f"pull {temp_path} {local_temp}")
            print(f"Pull command result: {pull_result}")

            self.execute_command(f"shell rm {temp_path}")

            img = cv2.imread(local_temp)

            if os.path.exists(local_temp):
                os.remove(local_temp)

            if img is None:
                raise ValueError("截图读取失败")

            if save_path:
                cv2.imwrite(save_path, img)

            if return_array:
                return img

            return None
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return None if not return_array else np.array([])

    def tap(self, x: int, y: int, duration: Optional[int] = None) -> bool:
        try:
            if duration:
                self.execute_command(f"shell input swipe {x} {y} {x} {y} {duration}")
            else:
                self.execute_command(f"shell input tap {x} {y}")
            return True
        except Exception as e:
            print(f"点击操作失败: {str(e)}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        try:
            self.execute_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
            return True
        except Exception as e:
            print(f"滑动操作失败: {str(e)}")
            return False

    def key_event(self, key_code: int) -> bool:
        try:
            self.execute_command(f"shell input keyevent {key_code}")
            return True
        except Exception as e:
            print(f"按键事件发送失败: {str(e)}")
            return False

    def text(self, text: str) -> bool:
        try:
            escaped_text = text.replace(" ", "%s").replace("'", "'\\''")
            self.execute_command(f"shell input text '{escaped_text}'")
            return True
        except Exception as e:
            print(f"文本输入失败: {str(e)}")
            return False

    def get_device_resolution(self) -> Optional[tuple]:
        try:
            output = self.execute_command("shell wm size")
            if "Physical size:" in output:
                resolution = output.split(":")[1].strip()
                width, height = map(int, resolution.split("x"))
                return width, height
            return None
        except Exception as e:
            print(f"获取分辨率失败: {str(e)}")
            return None

    def is_screen_on(self) -> bool:
        try:
            output = self.execute_command("shell dumpsys power")
            return "mHoldingDisplaySuspendBlocker=true" in output
        except Exception as e:
            print(f"检查屏幕状态失败: {str(e)}")
            return False

    def wake_up(self) -> bool:
        try:
            self.execute_command("shell input keyevent 26")  # POWER 键
            time.sleep(0.5)
            self.execute_command("shell input keyevent 82")  # MENU 键（解锁）
            return True
        except Exception as e:
            print(f"唤醒设备失败: {str(e)}")
            return False

    def list_devices(self) -> list:
        try:
            output = self.execute_command("devices", with_device=False)
            devices = []
            for line in output.splitlines()[1:]:  # 跳过第一行标题
                if line.strip():
                    devices.append(line.split("\t")[0])
            return devices
        except Exception as e:
            print(f"列出设备失败: {str(e)}")
            return []

    def install_app(self, apk_path: str) -> bool:
        try:
            output = self.execute_command(f"install -r {apk_path}")
            return "Success" in output
        except Exception as e:
            print(f"安装应用失败: {str(e)}")
            return False

    def uninstall_app(self, package_name: str) -> bool:
        try:
            output = self.execute_command(f"uninstall {package_name}")
            return "Success" in output
        except Exception as e:
            print(f"卸载应用失败: {str(e)}")
            return False

    def start_activity(self, package_name: str, activity_name: str) -> bool:
        try:
            self.execute_command(f"shell am start -n {package_name}/{activity_name}")
            return True
        except Exception as e:
            print(f"启动 Activity 失败: {str(e)}")
            return False

    def stop_app(self, package_name: str) -> bool:
        try:
            self.execute_command(f"shell am force-stop {package_name}")
            return True
        except Exception as e:
            print(f"停止应用失败: {str(e)}")
            return False

    def get_current_activity(self) -> Optional[str]:
        try:
            output = self.execute_command(
                "shell dumpsys window windows | grep mCurrentFocus"
            )
            if "mCurrentFocus" in output:
                return output.split(" ")[-1].rstrip("}")
            return None
        except Exception as e:
            print(f"获取当前 Activity 失败: {str(e)}")
            return None

    def push_file(self, local_path: str, device_path: str) -> bool:
        try:
            output = self.execute_command(f"push {local_path} {device_path}")
            return "pushed" in output
        except Exception as e:
            print(f"推送文件失败: {str(e)}")
            return False

    def pull_file(self, device_path: str, local_path: str) -> bool:
        try:
            output = self.execute_command(f"pull {device_path} {local_path}")
            return "pulled" in output
        except Exception as e:
            print(f"拉取文件失败: {str(e)}")
            return False

    def screenshot_and_edit(
        self, save_path: Optional[str] = None, return_array: bool = False
    ):
        try:
            temp_path = "/sdcard/screencap_temp.png"
            result = self.execute_command(f"shell screencap -p {temp_path}")
            print(f"Screenshot command result: {result}")

            local_temp = "temp_screencap.png"
            pull_result = self.execute_command(f"pull {temp_path} {local_temp}")
            print(f"Pull command result: {pull_result}")

            self.execute_command(f"shell rm {temp_path}")

            img = cv2.imread(local_temp)

            if os.path.exists(local_temp):
                os.remove(local_temp)

            if img is None:
                raise ValueError("截图读取失败")

            if save_path:
                cv2.imwrite(save_path, img)

            if return_array:
                return img

            # Open Image Editor for cropping
            self.open_image_editor(img)

        except Exception as e:
            print(f"截图失败: {str(e)}")
            return None if not return_array else np.array([])

    def open_image_editor(self, img: np.ndarray):
        from utils import ImageEditor

        root = tk.Tk()
        root.title("图片裁剪工具")
        editor = ImageEditor(root, img)
        root.mainloop()


if __name__ == "__main__":
    adb = ADBManager(port=16384)
    adb.screenshot_and_edit()
