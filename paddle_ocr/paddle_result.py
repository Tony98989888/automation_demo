class PaddleResult(object):
    def __init__(self, **kwargs):
        self._paddle_result = kwargs.get("paddle_result")

    @property
    def paddle_result(self):
        ocr_result = {}

        for i in self._paddle_result:
            for j in range(len(i["rec_texts"])):
                ocr_result[i["rec_texts"][j]] = [
                    i["rec_polys"][j][0],
                    i["rec_polys"][j][-1],
                ]

                pos_x = (i["rec_polys"][j][0][0] + i["rec_polys"][j][-1][0]) / 2
                pos_y = (i["rec_polys"][j][0][1] + i["rec_polys"][j][-1][1]) / 2

                ocr_result[i["rec_texts"][j]].append((int(pos_x), int(pos_y)))

        return ocr_result

    def try_get_text_coord(self, text):
        if not self.paddle_result:
            return None

        for k, v in self.paddle_result.items():
            if text in k:
                return v[-1]
