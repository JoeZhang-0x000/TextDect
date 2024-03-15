import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re
import sys
import subprocess
import cv2

def extract_xy_values(string):
    pattern = r'x=(\d*),y=(\d*),width=(\d*),height=(\d*)'
    matches = re.findall(pattern, string)
    # print(matches)
    recs = [[int(x),int(y),int(w),int(h)] for x, y, w, h in matches]
    return recs

def draw_rectangles(image_path, rectangles, show=True, save_path='.'):
    if len(rectangles) == 0:
        print('no text')
        return
    print(f'处理{image_path}')

    # 加载图片并获取图片名称
    image = cv2.imread(image_path)
    # 去除后缀
    save_path_ = re.findall(r'(\S*).(png|jpg)$', save_path)[0][0]

    rec_list= []

    
    # 绘制文本框
    for id, rect in enumerate(rectangles):
        x, y, width, height = rect
        rect_patch = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='red', facecolor='none')
        rec_list.append(rect_patch)
        text_img = image[y:y+height,x:x+width]
        cv2.imwrite(f'{save_path_}_{id}.png',text_img)
    
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots()
    plt.cla()
    plt.axis('off')
    ax.imshow(img_rgb)
    for rec in rec_list:
        ax.add_patch(rec)

    # 展示或保存
    if show == True:
        plt.show()
    else:
        print(f'save {save_path}')
        plt.savefig(f'{save_path}')

    

# 检测图片中文字，用矩形框标注
def process(img_path, save_path='a.png', show=True):
    # 执行java程序分割定位图片
    cmd = f'java textlocator.Main {img_path}'
    java_output = subprocess.check_output(cmd.split()).decode('utf-8')
    # print(java_output)
    rectangles =  extract_xy_values(java_output) # List of rectangles (x, y, width, height)
    draw_rectangles(img_path, rectangles, save_path=save_path, show=show)

if __name__ == '__main__':
    # 接受参数
    args_list = sys.argv
    flag = True
    num_args = len(args_list)
    if num_args !=2 and num_args !=3:
        raise NotImplementedError('参数错误')
    image_path = args_list[1]

    if len(args_list) == 3:
        flag = args_list[2]=='True'
        print('flag:',flag)
    process(image_path,show=flag)




