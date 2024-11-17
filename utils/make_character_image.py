
import datetime
import glob
import cv2

from PIL import Image
import numpy as np


def cv2pil(image):
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
def icon_image_preprocessing(img):
    # 背景色を透過
    mask = cv2.imread('data/mask.png', cv2.IMREAD_GRAYSCALE)
    img[mask > 0] = [255, 255, 255]

    # グレースケール化
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    return img


# 生徒画像をcrop
def make_character_image(path):
    img = cv2.imread(path)

    # 解像度1600x900の場合の生徒画像をcrop
    # shape = (60, 73, 3)
    l1 = icon_image_preprocessing(img[663 : 723, 127 : 200])
    l2 = icon_image_preprocessing(img[663 : 723, 221 : 294])
    l3 = icon_image_preprocessing(img[663 : 723, 315 : 388])
    l4 = icon_image_preprocessing(img[663 : 723, 409 : 482])
    l5 = icon_image_preprocessing(img[663 : 723, 503 : 576])
    l6 = icon_image_preprocessing(img[663 : 723, 597 : 670])

    dt = datetime.datetime.now()
    ts = dt.timestamp()

    cv2.imwrite(f'character/l1_{ts}.png', l1)
    cv2.imwrite(f'character/l2_{ts}.png', l2)
    cv2.imwrite(f'character/l3_{ts}.png', l3)
    cv2.imwrite(f'character/l4_{ts}.png', l4)
    cv2.imwrite(f'character/l5_{ts}.png', l5)
    cv2.imwrite(f'character/l6_{ts}.png', l6)

    r1 = icon_image_preprocessing(img[663 : 723, 923 : 996])
    r2 = icon_image_preprocessing(img[663 : 723, 1017 : 1090])
    r3 = icon_image_preprocessing(img[663 : 723, 1111 : 1184])
    r4 = icon_image_preprocessing(img[663 : 723, 1205 : 1278])
    r5 = icon_image_preprocessing(img[663 : 723, 1300 : 1373])
    r6 = icon_image_preprocessing(img[663 : 723, 1394 : 1467])

    cv2.imwrite(f'character/r1_{ts}.png', r1)
    cv2.imwrite(f'character/r2_{ts}.png', r2)
    cv2.imwrite(f'character/r3_{ts}.png', r3)
    cv2.imwrite(f'character/r4_{ts}.png', r4)
    cv2.imwrite(f'character/r5_{ts}.png', r5)
    cv2.imwrite(f'character/r6_{ts}.png', r6)


if __name__ == '__main__':
    for path in glob.glob('input_image/*.png'):
        make_character_image(path)

    # 既存の画像を修正したい場合
    # for path in glob.glob('character/*/.png', recursive=True):
    #     pil_img = Image.open(path)
    #     img = np.array(pil_img)
    #     img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    #     img = icon_image_preprocessing(img)
    #     cv2pil(img).save(path)

        






# 座標の計算を以下のコードで行い、目視で微調整でcropする場所を決定
# 2値化した画像で黒が連続している部分を生徒画像の範囲として取得
def calc_character_image_area(image, threshold, offset=0):
    # 2値化
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('gray.png', gray)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    cv2.imwrite('binary.png', binary)

    character_area_list = [
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
    ]
    num = 0
    is_range = False
    x, y = False, False
    for i in range(image.shape[1]):
        z = cv2.countNonZero(binary[:, i]) < 65
        
        if not is_range and x and y and z:
            is_range = True
            character_area_list[num][0] = i-2 + offset
        elif is_range and not x and not y and not z:
            is_range = False
            character_area_list[num][1] = i-2 + offset
            num += 1
        
        x = y
        y = z

    print(character_area_list)

# image = cv2.imread('input_image/screenshot.png')
# left_img = image[661 : 726, 100 : 700]
# calc_character_image_area(left_img, 245, 100)

# right_img = img[661 : 726, 900 : 1500]
# calc_character_image_area(right_img, 230, 900)