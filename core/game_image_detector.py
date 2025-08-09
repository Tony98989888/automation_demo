import time
from typing import Tuple, Optional, List

import cv2

from core.image_detector import ImageDetector


class GameImageDetector:
    def __init__(self):
        self.matcher = ImageDetector()
        self.template_cache = {}

    def load_template(self, template_name: str, template_path: str):
        try:
            template = cv2.imread(template_path)
            if template is not None:
                self.template_cache[template_name] = template_path
                print(f"模板 '{template_name}' 加载成功")
            else:
                print(f"模板 '{template_name}' 加载失败")
        except Exception as e:
            print(f"加载模板出错: {e}")

    def find_element(self, screenshot_path: str, template_name: str, threshold: float = 0.8,
                     region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        if template_name not in self.template_cache:
            print(f"模板 '{template_name}' 未找到，请先加载")
            return None

        template_path = self.template_cache[template_name]

        if region:
            result = self.matcher.find_template_in_region(screenshot_path, template_path, region, threshold)
        else:
            result = self.matcher.find_template(screenshot_path, template_path, threshold)

        if result:
            x, y, confidence = result
            print(f"找到 '{template_name}': 坐标({x}, {y}), 置信度: {confidence:.3f}")
            return (x, y)
        else:
            print(f"未找到 '{template_name}'")
            return None

    def find_multiple_elements(self, screenshot_path: str, template_name: str, threshold: float = 0.8) -> List[
        Tuple[int, int]]:
        if template_name not in self.template_cache:
            print(f"模板 '{template_name}' 未找到，请先加载")
            return []

        template_path = self.template_cache[template_name]
        results = self.matcher.find_all_templates(screenshot_path, template_path, threshold)

        coordinates = [(x, y) for x, y, _ in results]
        print(f"找到 {len(coordinates)} 个 '{template_name}'")

        return coordinates

    def wait_for_element(self, screenshot_func, template_name: str, timeout: int = 10, interval: float = 1.0,
                         threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        start_time = time.time()

        while time.time() - start_time < timeout:
            screenshot_path = screenshot_func()
            result = self.find_element(screenshot_path, template_name, threshold)
            if result:
                return result
            time.sleep(interval)

        print(f"等待 '{template_name}' 超时")
        return None


if __name__ == "__main__":
    game_vision = GameImageDetector()

    game_vision.load_template("skip_cinematic_button", r"../resources/skip_cinematic_button.png")

    screenshot_path = r"../resources/test.png"

    start_pos = game_vision.find_element(screenshot_path, "skip_cinematic_button")
    if start_pos:
        print(f"可以点击开始按钮，坐标: {start_pos}")
