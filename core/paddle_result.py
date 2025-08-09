from dataclasses import dataclass


@dataclass
class PaddleResultItemData:
    text: str
    predict_rect: tuple
    pos: tuple


class PaddleResult(object):
    def __init__(self, **kwargs):
        self._paddle_result = kwargs.get("paddle_result")

    @property
    def paddle_result(self) -> list[PaddleResultItemData]:
        res = []
        for i in self._paddle_result:
            for j in range(len(i["rec_texts"])):
                text = i["rec_texts"][j]
                # ocr_result = {text: [i["rec_polys"][j][0], i["rec_polys"][j][-1]]}

                y_start = min(i["rec_polys"][j][0][1], i["rec_polys"][j][-1][1])
                y_end = max(i["rec_polys"][j][0][1], i["rec_polys"][j][-1][1])

                pixel_per_character = abs(y_end - y_start)

                x_start = min(i["rec_polys"][j][0][0], i["rec_polys"][j][-1][0])
                x_end = pixel_per_character * len(text) + x_start

                # ocr_result[text].append({"predict_rect": (x_start, y_start, x_end, y_end)})

                pos_x = (x_start + x_end) / 2
                pos_y = (y_start + y_end) / 2

                # ocr_result[text].append((int(pos_x), int(pos_y)))

                item_data = PaddleResultItemData(
                    text=text,
                    predict_rect=(x_start, y_start, x_end, y_end),
                    pos=(int(pos_x), int(pos_y))
                )
                res.append(item_data)

        return res

    def try_get_text_coord(self, text) -> list[PaddleResultItemData]:
        if not self.paddle_result:
            return None
        res = []
        for item in self.paddle_result:
            if text in item.text:
                res.append(item)

        return res

    def try_get_text_coord_in_range(self, text, x1, y1, x2, y2) -> list[PaddleResultItemData]:

        if not self.paddle_result:
            return []

        res: list[PaddleResultItemData] = []
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        for item in self.paddle_result:
            if text in item.text:
                pos_x, pos_y = item.pos
                if min_x <= pos_x <= max_x and min_y <= pos_y <= max_y:
                    res.append(item)

        return res
