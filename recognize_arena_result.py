import glob
import cv2
import os
import joblib

from PIL import Image
from dotenv import load_dotenv

if os.getenv('ENV') == 'private':
    import pyocr


class RecognizeArenaResult:
    def __init__(self):
        load_dotenv()

        self.histgram_list = []
        with open('data/histgram_list.pkl', 'rb') as f:
            self.histgram_list = joblib.load(f)


    def cv2pil(self, image):
        ''' OpenCV型 -> PIL型 '''
        new_image = image.copy()
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        new_image = Image.fromarray(new_image)
        return new_image
    

    # 生徒画像のアイコンの前処理
    def icon_image_preprocessing(self, img):
        # 背景色を透過
        mask = cv2.imread('data/mask.png', cv2.IMREAD_GRAYSCALE)
        img[mask > 0] = [255, 255, 255]

        # グレースケール化
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return img
    
    
    # 文字認識
    def recognize_text(self, img, binary_threshold=200):
        pyocr.tesseract.TESSERACT_CMD = os.getenv('TESSERACT_PATH')
        engines = pyocr.get_available_tools()
        engine = engines[0]
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY)

        # 周囲の余白を削除
        h, w = binary.shape
        non_zero_num_rows = [cv2.countNonZero(binary[i, :]) for i in range(h)]
        non_zero_num_columns = [cv2.countNonZero(binary[:, i]) for i in range(w)]

        u, b, l, r = 1, h-2, 1, w-2
        for y in range(h):
            if non_zero_num_rows[y] < w:
                u = y
                break
        for y in range(h-1, -1, -1):
            if non_zero_num_rows[y] < w:
                b = y
                break
        for x in range(w):
            if non_zero_num_columns[x] < h:
                l = x
                break
        for x in range(w-1, -1, -1):
            if non_zero_num_columns[x] < h:
                r = x
                break

        binary = binary[u-1 : b+2, l-1 : r+2]
        
        name = engine.image_to_string(
            self.cv2pil(binary),
            lang='jpn',
            builder=pyocr.builders.TextBuilder(tesseract_layout=8)
        )

        return name


    # 画像から結果を認識する, 解像度1600x900のみ対応
    def recognize_image(self, path):
        img = cv2.imread(path)
        img_height, img_width = img.shape[:2]

        # 自分が攻撃か防御か判定
        atk_icon_img = cv2.imread('image/atk_icon.png')
        res = cv2.matchTemplate(img, atk_icon_img, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        is_atk =  max_loc[0] < img_width / 2

        # 勝者を判定
        win_icon_img = cv2.imread('image/win_icon.png')
        res = cv2.matchTemplate(img, win_icon_img, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        is_win = max_loc[0] < img_width / 2        

        # 生徒名を判定
        character_area = [
            (663, 723, 127, 200),
            (663, 723, 221, 294),
            (663, 723, 315, 388),
            (663, 723, 409, 482),
            (663, 723, 503, 576),
            (663, 723, 597, 670),
            (663, 723, 923, 996),
            (663, 723, 1017, 1090),
            (663, 723, 1111, 1184),
            (663, 723, 1205, 1278),
            (663, 723, 1300, 1373),
            (663, 723, 1394, 1467),
        ]

        character_list = []
        for i, (upper, bottom, left, right) in enumerate(character_area):
            character_image = self.icon_image_preprocessing(
                img[upper : bottom, left : right]
            )
            character_hist = cv2.calcHist(
                [character_image],
                [0],
                None,
                [256],
                [0, 256]
            )

            max_similarity = -100
            max_similarity_character = ''
            for character, hist in self.histgram_list:
                similarity = cv2.compareHist(character_hist, hist, cv2.HISTCMP_CORREL)
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_similarity_character = character
            character_list.append(max_similarity_character)

            if max_similarity < 0.5:
                raise Exception(f'{i+1} 番目の生徒の認識に失敗')

        # 相手の名前を読む
        if os.get_environ('ENV') == 'private':
            name_img = img[210 : 250, 1305 : 1550]
            enemy_name = self.recognize_text(name_img, binary_threshold=200)
        else:
            enemy_name = ''

        return dict(
            is_atk=is_atk,
            is_win=is_win,
            character_list=character_list,
            enemy_name=enemy_name
        )


if __name__ == '__main__':
    recognize_arena_result = RecognizeArenaResult()

    for path in glob.glob('input_image/*.png'):
        try:
            result = recognize_arena_result.recognize_image(path)
            print(result)
        except Exception as e:
            print(e)
            continue
