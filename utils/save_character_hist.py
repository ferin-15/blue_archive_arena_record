import sys
sys.path.append('C:\\Python312\\Lib\\site-packages')
import joblib # type: ignore

import cv2
import glob
import numpy as np

from PIL import Image

histgram_list = []
for path in glob.glob('character/*/*.png', recursive=True):
    # パスに日本語が含まれるので通常のopencv2とは異なる読み込み方を使用
    pil_img = Image.open(path)
    character_image = np.array(pil_img)
    character_image = cv2.cvtColor(character_image, cv2.COLOR_RGB2BGR)

    # 生徒とアイコンのヒストグラムのペアを用意
    hist = cv2.calcHist([character_image], [0], None, [256], [0, 256])
    character = path.split('\\')[1]
    histgram_list.append((character, hist))

# histgram_list を pickle で保存
with open('data/histgram_list.pkl', 'wb') as f:
    # pickle ではファイルサイズが大きくなるため、joblib で圧縮して保存
    joblib.dump(histgram_list, f, compress=3)