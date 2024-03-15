import pytesseract
from PIL import Image
import sys

img_path = sys.argv[1]

# 读取图片
im = Image.open(img_path)

# 识别文字，并指定语言为中文
string = pytesseract.image_to_string(im, lang='eng')

# 打印识别结果
print(string)