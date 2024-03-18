import pytesseract
from PIL import Image
import cv2
import sys

def ocrDis(im):
    
    string = pytesseract.image_to_string(im, lang= 'eng')

    # 打印识别结果
    print(string)

if __name__ == '__main__':
    img_path = sys.argv[1]
    im = cv2.imread(img_path)
    ocrDis(im)

