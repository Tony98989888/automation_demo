import time
from typing import Tuple, Optional, List

import cv2
import numpy as np


class ImageDetector:
    def __init__(self):
        pass

    def find_template(self, screenshot_path: str, template_path: str, threshold: float = 0.8,
                      method: int = cv2.TM_CCOEFF_NORMED) -> Optional[Tuple[int, int, float]]:
        try:
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)

            if screenshot is None or template is None:
                raise ValueError("无法读取图像文件")

            result = cv2.matchTemplate(screenshot, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                best_loc = min_loc
                confidence = 1 - min_val
            else:
                best_loc = max_loc
                confidence = max_val

            if confidence >= threshold:
                template_h, template_w = template.shape[:2]
                center_x = best_loc[0] + template_w // 2
                center_y = best_loc[1] + template_h // 2
                return (center_x, center_y, confidence)

            return None

        except Exception as e:
            print(f"图像匹配出错: {e}")
            return None

    def find_all_templates(self, screenshot_path: str, template_path: str, threshold: float = 0.8,
                           method: int = cv2.TM_CCOEFF_NORMED) -> List[Tuple[int, int, float]]:
        try:
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)

            if screenshot is None or template is None:
                raise ValueError("无法读取图像文件")

            template_h, template_w = template.shape[:2]
            result = cv2.matchTemplate(screenshot, template, method)
            locations = np.where(result >= threshold)
            matches = []

            for pt in zip(*locations[::-1]):
                confidence = result[pt[1], pt[0]]
                center_x = pt[0] + template_w // 2
                center_y = pt[1] + template_h // 2
                matches.append((center_x, center_y, confidence))

            return sorted(matches, key=lambda x: x[2], reverse=True)

        except Exception as e:
            print(f"多目标匹配出错: {e}")
            return []

    def find_template_with_scale(self, screenshot_path: str, template_path: str, threshold: float = 0.8,
                                 scale_range: Tuple[float, float] = (0.8, 1.2), scale_steps: int = 5) -> Optional[
        Tuple[int, int, float, float]]:
        try:
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)

            if screenshot is None or template is None:
                raise ValueError("无法读取图像文件")

            best_match = None
            best_confidence = 0
            scales = np.linspace(scale_range[0], scale_range[1], scale_steps)

            for scale in scales:
                scaled_w = int(template.shape[1] * scale)
                scaled_h = int(template.shape[0] * scale)
                scaled_template = cv2.resize(template, (scaled_w, scaled_h))

                if scaled_w >= screenshot.shape[1] or scaled_h >= screenshot.shape[0]:
                    continue

                result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_confidence and max_val >= threshold:
                    best_confidence = max_val
                    center_x = max_loc[0] + scaled_w // 2
                    center_y = max_loc[1] + scaled_h // 2
                    best_match = (center_x, center_y, best_confidence, scale)

            return best_match

        except Exception as e:
            print(f"多尺度匹配出错: {e}")
            return None

    def find_template_in_region(self, screenshot_path: str, template_path: str, region: Tuple[int, int, int, int],
                                threshold: float = 0.8) -> Optional[Tuple[int, int, float]]:
        try:
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)

            if screenshot is None or template is None:
                raise ValueError("无法读取图像文件")

            x, y, w, h = region
            roi = screenshot[y:y + h, x:x + w]

            result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                template_h, template_w = template.shape[:2]
                global_x = x + max_loc[0] + template_w // 2
                global_y = y + max_loc[1] + template_h // 2
                return (global_x, global_y, max_val)

            return None

        except Exception as e:
            print(f"区域匹配出错: {e}")
            return None

    def save_matched_result(self, screenshot_path: str, template_path: str, output_path: str,
                            match_result: Tuple[int, int, float]) -> bool:
        try:
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)

            if screenshot is None or template is None:
                return False

            x, y, confidence = match_result
            template_h, template_w = template.shape[:2]

            top_left = (x - template_w // 2, y - template_h // 2)
            bottom_right = (x + template_w // 2, y + template_h // 2)

            cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
            cv2.circle(screenshot, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(screenshot, f'Conf: {confidence:.3f}', (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            return cv2.imwrite(output_path, screenshot)

        except Exception as e:
            print(f"保存匹配结果出错: {e}")
            return False

