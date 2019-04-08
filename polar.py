from PIL import Image

import sys
import math

im = Image.open(sys.argv[1])
mat_size = int(sys.argv[2])
th_res = int(sys.argv[3])

im.resize((mat_size, mat_size), resample=Image.BICUBIC)
c_x = im.size[0] // 2
c_y = im.size[1] // 2
th_mul = 360 // th_res

matrix = [ ]
for i in range(th_res):
    radial = [ ]
    for j in range(mat_size // 2):
        x = round(c_x + (j * math.cos(th_mul * i * math.pi / 180)))
        y = round(c_y + (j * math.sin(th_mul * i * math.pi / 180)))

        rgb = im.getpixel((x,y))
        radial.append(hex((rgb[1] << 16) + (rgb[0] << 8) + rgb[2]))
    matrix.append(radial)

mat_file = open('matrix.py', 'w')
mat_file.write('matrix = [\n')
for i in range(th_res):
    mat_file.write('    [ ')
    for j in range(mat_size // 2):
        mat_file.write(matrix[i][j] + ', ')
    mat_file.write('],\n')
mat_file.write(']')

