import numpy as np
import matplotlib.pyplot as plt
import cv2


def fill_rec(bin, x, y, original_color, new_color):

    # print(f'visit {x}/{bin.shape[0]} {y}/{bin.shape[1]}')
    
    # 出界判断
    if x  < 0 or y < 0 or x == bin.shape[0] or y == bin.shape[1]:
        # print('Out of Filed')
        return
    
    # 碰壁判断
    if bin[x,y] !=original_color:
        # print('On edge')
        return
    bin[x,y] = new_color
    fill_rec(bin,x-1,y,original_color,new_color) 
    fill_rec(bin,x+1,y,original_color,new_color)
    fill_rec(bin,x,y-1,original_color,new_color)
    fill_rec(bin,x,y+1,original_color,new_color)

def fill(bin, x, y, original_color, new_color):

    visited = set()
    visited.add((x,y))
    while len(visited) !=0:
        x, y = visited.pop()
        
        print(f'visit {x}/{bin.shape[0]} {y}/{bin.shape[1]}')
        
        # 出界判断
        if x  < 0 or y < 0 or x == bin.shape[0] or y == bin.shape[1]:
            print('Out of Filed')
            continue
        
        # 碰壁判断
        if bin[x,y] !=original_color:
            print('On edge')
            continue
        
        bin[x,y] = new_color

        # 入队相连通的块
        visited.add((x-1,y))
        visited.add((x+1,y))
        visited.add((x,y-1))
        visited.add((x,y+1))


matrix = np.array([
    [255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
    [255, 0, 0, 0, 0, 0, 0, 0, 0, 255],
    [255, 0, 255, 255, 255, 255, 255, 255, 0, 255],
    [255, 0, 255, 0, 255, 0, 0, 255, 0, 255],
    [255, 0, 255, 0, 255, 255, 0, 255, 0, 255],
    [255, 0, 255, 0, 255, 255, 0, 255, 0, 255],
    [255, 0, 255, 0, 0, 0, 0, 255, 0, 255],
    [255, 0, 255, 255, 255, 255, 255, 255, 0, 255],
    [255, 0, 0, 0, 0, 0, 0, 0, 0, 255],
    [255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
    [255, 0, 0, 0, 0, 0, 0, 0, 0, 255], 
    [255, 255, 255, 255, 255, 255, 255, 255, 255, 255]              
])
fig, [ax0,ax1] = plt.subplots(1,2)
ax0.imshow(matrix,cmap='gray')
ax0.set_title('ORIGIANL')

x,y = 0,0
fill(matrix, x, y, matrix[x,y], 100)

ax1.imshow(matrix,cmap='gray')
ax1.set_title('RESULTS')
plt.show()