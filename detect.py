import os 
import sys
import show

if __name__ == '__main__':
    if len(sys.argv) !=4:
        raise NotImplementedError('参数错误')
    folder_path = sys.argv[1]
    save_path = sys.argv[2]
    pro_num = int(sys.argv[3])
    img_names = [f for f in os.listdir(folder_path) if f.endswith(('.png','jpg'))]

    print(f'共载入{len(img_names)}张图片')
    for id, name in enumerate(img_names):
        if id > pro_num:
            break
        print(f'处理第{id}张...')
        # print(f'{folder_path}/{name}')

        show.process(f'{folder_path}/{name}',f'{save_path}/{name}',False)