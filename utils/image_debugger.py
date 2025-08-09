from typing import List, Tuple

import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RectangleSelector

from core.adb_manager import ADBManager


def draw_bounding_boxes(image_path: str, boxes: List[Tuple[int, int, int, int]], output_path: str = None,
                        color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法读取图片: {image_path}")

    for box in boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

    if output_path:
        cv2.imwrite(output_path, image)

    return image


def display_image(image: np.ndarray):
    cv2.imshow('Image with Bounding Boxes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# # 打开图片
# img = mpimg.imread(r"C:\Users\Tony\Desktop\automation_demo-main\resources\test.png")
#
# # 显示图片
# fig, ax = plt.subplots()
# ax.imshow(img)
#
# # 回调函数：获取选择的区域
# def onselect(eclick, erelease):
#     # 获取选择的矩形区域的坐标 (左上角到右下角)
#     x1, y1 = eclick.xdata, eclick.ydata
#     x2, y2 = erelease.xdata, erelease.ydata
#     print(f"选定区域: ({x1}, {y1}) 到 ({x2}, {y2})")
#
#     # 截取图片的选定区域
#     cropped_img = img[int(y1):int(y2), int(x1):int(x2)]
#
#     # 保存截取后的图片
#     plt.imsave('cropped_image.jpg', cropped_img)
#     print("截图已保存为 'cropped_image.jpg'")
#
# # 设置矩形选择工具，移除 drawtype 参数
# rect_selector = RectangleSelector(ax, onselect, useblit=True)
#
# # 显示图像并启动交互
# plt.show()


if __name__ == '__main__':
    adb = ADBManager(default_port=16384)
    adb.connect_device()

    save_path = r"D:\automation_demo\resources\test.png"
    adb.screenshot(save_path)

    img = mpimg.imread(save_path)

    fig, ax = plt.subplots()
    ax.imshow(img)


    def onselect(eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print(f"选定区域: ({x1}, {y1}) 到 ({x2}, {y2})")

        cropped_img = img[int(y1):int(y2), int(x1):int(x2)]

        plt.imsave(r'D:\automation_demo\resources\cropped_image.jpg', cropped_img)
        print("截图已保存为 'cropped_image.jpg'")


    rect_selector = RectangleSelector(ax, onselect, useblit=True)

    plt.show()

# if __name__ == "__main__":
#     image_path = r"D:\automation_demo\resources\test.png"
#     boxes = [(1814, 1026, 1880, 1059), ]

#     result_image = draw_bounding_boxes(image_path=image_path, boxes=boxes,
#                                        output_path=r"C:\Users\Tony\Desktop\automation_demo-main\resources\debug_result.png",
#                                        color=(0, 0, 255),  # 红色 (BGR)
#                                        thickness=2)

#     display_image(result_image)
