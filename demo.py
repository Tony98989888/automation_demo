import os

from paddleocr import PaddleOCR

from utils.adb_manager import ADBManager
from paddle_ocr.paddle_result import PaddleResult

if __name__ == "__main__":
    adb = ADBManager(default_port=16384)
    if not adb.connect_device():
        raise RuntimeError("无法连接到设备")

    os.environ["PATH"] = (
        r"C:\Users\Tony\Downloads\ccache-4.11.3-windows-x86_64\ccache-4.11.3-windows-x86_64\ccache.exe"
        + os.environ["PATH"]
    )
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    while True:
        save_path = r"resources/screenshot.png"
        img = adb.screenshot(save_path)
        paddle_result = ocr.predict(save_path)

        result = PaddleResult(paddle_result=paddle_result)

        for k, v in result.paddle_result.items():
            print(k, v)

        # coord = result.try_get_text_coord('大陆地图')
        # adb.tap(coord[0], coord[1])

        break
