import matplotlib.pyplot as plt
import numpy as np
import cv2
import copy
import pytesseract
import sys
import time

MAX_WID, MAX_HEI = 0, 0

def loadImg(img_path):
    global MAX_WID, MAX_HEI
    img = cv2.imread(img_path,cv2.IMREAD_GRAYSCALE)

    MAX_WID, MAX_HEI = img.shape[1], img.shape[0]
    print(f'MAX WIDTH:{MAX_WID}, MAX HEIGHT:{MAX_HEI}')

    plt.axis('off')
    plt.title('ORIGINAL')
    plt.imshow(img,cmap='gray')
    plt.show()
    return img

##############################################################
# 局部阈值法

# OTSU
def otsu(image):
    _, thd = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thd

# 局部OTSU,求在一个滑动窗口内的OTSU阈值
def adOtsu(imgage, x, y, w, h):
    
    # 小于阈值的点被设为黑色
    t_img = imgage[y:y+h, x:x+w]
    black_area = t_img <= otsu(t_img)
    
    # 返回黑色点的位置
    t_1, t_2 = np.where(black_area == 1)
    
    # 相对位置->绝对位置
    t_1 += y
    t_2 += x
    return t_1,t_2

def applyAdOtsu(img,show=False):
    bin_img = np.ones_like(img)*255

    # 水平移动滑动窗口
    w = 8
    for x in np.arange(0,MAX_WID,w):
        black_id = adOtsu(img, x, 0, w, MAX_HEI)
        bin_img[black_id] = 0

    # 竖直移动滑动窗口
    h = 32
    for y in np.arange(0,MAX_HEI, h):
        black_id = adOtsu(img, 0, y, MAX_WID, h)
        bin_img[black_id] = 0

    if show==True:
        plt.title('OTSU BEFORE FLIPPED')
        plt.axis('off')
        plt.imshow(bin_img,cmap='gray')
        plt.show()

    # 认为边界上更多是背景，而不是文字，以此判断文字的颜色是黑色还是白色
    cnt_b = 0
    cnt_w = 0
    xx = np.hstack([
        np.zeros(MAX_WID),
        np.ones(MAX_WID)*(MAX_HEI-1),
        np.arange(MAX_HEI,dtype=int),
        np.arange(MAX_HEI,dtype=int)
    ]).astype(int)
    yy = np.hstack([
        np.arange(MAX_WID,dtype=int),
        np.arange(MAX_WID,dtype=int),
        np.zeros(MAX_HEI),
        np.ones(MAX_HEI)*(MAX_WID-1),
    ]).astype(int)

    t_img = bin_img[(xx,yy)]

    # 若边界上的黑块 < 白块， 说明背景是白色
    cnt_b = np.count_nonzero(t_img == 0)
    cnt_w = np.count_nonzero(t_img == 255)
    print(f'边界黑块数量:{cnt_b}，白块数量:{cnt_w}')
    if cnt_b < cnt_w:
        print('背景偏亮，文字篇暗，翻转明暗度')
        bin_img = 255-bin_img
    if show == True:
        plt.title('OTSU AFTER FLIPPED')
        plt.axis('off')
        plt.imshow(bin_img,cmap='gray')
        plt.show()

    return bin_img

###############################################################
# 坝点标注过程
MIN_W = 1
MAX_W = 10

# 计算V_Len(x,y)
def getVlen(bin_array, x, y):

    # up侧的最大连通像素数
    u_num = 0
    for i in range(x,MAX_HEI):
        if u_num > MAX_W:
            return MAX_W+1
        if bin_array[i,y] == 0:
            break
        u_num += 1
    
    # bottom侧做大连同数
    b_num = 0
    for i in range(x,0,-1):
        if b_num > MAX_W:
            return MAX_W+1
        if bin_array[i,y] == 0:
            break
        b_num += 1
    return u_num+b_num


# 计算H_Len(x,y)
def getHlen(bin_array, x, y):

    # left侧的最大连通像素数
    l_num = 0
    for i in range(y,0,-1):
        if l_num > MAX_W:
            return MAX_W+1
        if bin_array[x,i] == 0:
            break
        l_num += 1
    
    # right侧做大连同数
    r_num = 0
    for i in range(y,MAX_WID):
        if r_num > MAX_W:
            return MAX_W+1
        if bin_array[x,i] == 0:
            break
        r_num += 1
    return r_num + l_num

def findDam(bin_array):
    white_points = np.where(bin_array == 255)
    # print('white:',white_points)
    for i,j in zip(white_points[0], white_points[1]):
        h_len = getHlen(bin_array,i,j)
        v_len = getVlen(bin_array,i,j)
        m_h_v = min(h_len, v_len)
        # print(m_h_v)
        if m_h_v >= MIN_W and m_h_v <= MAX_W:
            bin_array[i,j] = 100
    return bin_array

def applyDamLabel(bin_img,show=True):
    start = time.time()
    bin_img = findDam(bin_img)
    end = time.time()
    print(f'DAM COST:{end-start}')

    if show==True:
        plt.title('DAM')
        plt.axis('off')
        plt.imshow(bin_img,cmap='gray')
        plt.show()
    return bin_img

###########################################################
# 内向填充过程

# 找到连同块，改变颜色
def fill(bin, x, y, original_color, new_color):

    visited = set()
    visited.add((x,y))
    while len(visited) !=0:
        x, y = visited.pop()
        
        # print(f'visit {x}/{bin.shape[0]} {y}/{bin.shape[1]}')
        
        # 出界判断
        if x  < 0 or y < 0 or x == bin.shape[0] or y == bin.shape[1]:
            # print('Out of Filed')
            continue
        
        # 碰壁判断
        if bin[x,y] !=original_color:
            # print('On edge')
            continue
        
        bin[x,y] = new_color

        # 入队相连通的块
        visited.add((x-1,y))
        visited.add((x+1,y))
        visited.add((x,y-1))
        visited.add((x,y+1))

# 从边界开始向内侵蚀，将与边界连通的白色块全部改为黑色
def applyFlood(bin_img,show=True):



    whilte_pos = np.where(bin_img == 255)
    
    if len(whilte_pos) !=1:

        start = time.time()

        for i,j in zip(whilte_pos[0],whilte_pos[1]):
            if i == 0 or j == 0 or i == MAX_HEI-1 or j == MAX_WID-1:
                fill(bin_img,i,j,255,0)

        end = time.time()
        print(f'FLOOD FILL COST:{end-start}')

        # 清除坝点
        bin_img[np.where(bin_img == 100)] = 255

    if show == True:
        plt.title('RESULT')
        plt.axis('off')
        plt.imshow(bin_img,cmap='gray')
        plt.show()

    return bin_img

##########################################################
# 使用OCR识别
def applyOcr(bin_img,show=True):
    text = pytesseract.image_to_string(bin_img,)
    
    if show == True:
        print(f'识别结果:{text}')
    return text


def process(img_path):
    img = loadImg(img_path)
    img = applyAdOtsu(img)
    img = applyDamLabel(img)
    img = applyFlood(img)
    text = applyOcr(img)
    return text

if __name__ == '__main__':
    img_path = sys.argv[1]
    process(img_path)
    
