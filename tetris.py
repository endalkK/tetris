import random
import time
import board
import displayio
import terminalio
import gc
import adafruit_displayio_sh1107
from adafruit_display_text import label
from digitalio import DigitalInOut, Direction, Pull
from adafruit_displayio_sh1107 import SH1107, DISPLAY_OFFSET_ADAFRUIT_FEATHERWING_OLED_4650
from adafruit_display_shapes.rect import Rect

i2c = board.I2C()
rotation_angle = 90
w = 64
h = 128
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SH1107(display_bus, width=w, height=h, display_offset=DISPLAY_OFFSET_ADAFRUIT_FEATHERWING_OLED_4650, rotation=int(rotation_angle))

#button A, right
btn_a = DigitalInOut(board.D9)
btn_a.direction = Direction.INPUT
btn_a.pull = Pull.UP

#button B, switch
btn_b = DigitalInOut(board.D6)
btn_b.direction = Direction.INPUT
btn_b.pull = Pull.UP


#button C, left
btn_c = DigitalInOut(board.D5)
btn_c.direction = Direction.INPUT
btn_c.pull = Pull.UP

group = displayio.Group()
grid_width = 12
grid_height = 25
grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

tetrominoes = {
    'L': [ [(0, 0), (0, 1), (0, 2), (1, 2)], [(1, 0), (1, 1), (1, 2), (0, 2)], [(0, 0), (0, 1), (0, 2), (-1, 0)], [(-1, 2), (0, 2), (1, 2), (1, 0)] ],
    'J': [ [(0, 0), (0, 1), (0, 2), (-1, 2)], [(0, 0), (1, 0), (2, 0), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 0)], [(-1, 0), (0, 0), (1, 0), (-1, 1)] ],
    'O': [ [(0, 0), (1, 0), (0, 1), (1, 1)] ],
    'S': [ [(0, 0), (1, 0), (-1, 1), (0, 1)], [(0, 0), (0, 1), (1, 1), (1, 2)] ],
    'T': [ [(0, 0), (-1, 1), (0, 1), (1, 1)], [(0, 0), (0, 1), (1, 1), (0, 2)], [(0, 1), (-1, 1), (1, 1), (0, 0)], [(0, 0), (0, 1), (-1, 1), (0, 2)] ],
    'Z': [ [(0, 0), (1, 0), (1, 1), (2, 1)], [(0, 0), (0, 1), (1, 1), (1, 2)]]
}
def draw_block(x, y, color, block_size=5):
    block_size = 5
    block = Rect(x * block_size, y * block_size, block_size, block_size, fill=color)
    group.append(block)
def draw_tetromino(tetromino_type, rotation, pos_x, pos_y, color=0xFFFFFF):
    shape_coordinates = tetrominoes[tetromino_type][rotation]
    for coord in shape_coordinates:
        x, y = coord
        draw_block(pos_x + x, pos_y + y, color)
    time.sleep(0.3)
    for coord in shape_coordinates:
        group.pop()
def generate_tetromino():
    shape = random.choice(list(tetrominoes.keys()))
    return {'shape': shape, 'rotation': 0, 'position': [grid_width // 2 - 1, 0]}
def valid_position(obj):
    shape_coords = tetrominoes[obj['shape']][obj['rotation']]
    for dx, dy in shape_coords:
        nx, ny = obj['position'][0] + dx, obj['position'][1] + dy
        if nx < 0 or nx >= grid_width or ny < 0 or ny >= grid_height:
            return False
        if grid[ny][nx] != ' ':
            return False
    return True
def rotate_tetromino(obj):
    obj['rotation'] = (obj['rotation'] + 1) % len(tetrominoes[obj['shape']])
    if not valid_position(obj):
        obj['rotation'] = (obj['rotation'] - 1) % len(tetrominoes[obj['shape']])

def check_completed_lines():
    global grid
    new_grid = [row for row in grid if ' ' in row]
    lines_cleared = len(grid) - len(new_grid)
    while len(new_grid) < grid_height:
        new_grid.insert(0, [' ' for _ in range(grid_width)])
    grid = new_grid
    return lines_cleared

def place_tetromino(obj):
    shape_coords = tetrominoes[obj['shape']][obj['rotation']]
    for dx, dy in shape_coords:
        nx, ny = obj['position'][0] + dx, obj['position'][1] + dy
        grid[ny][nx] = obj['shape']
    check_completed_lines()
    
def move_tetromino_down(obj):
    obj['position'][1] += 1
    if not valid_position(obj):
        obj['position'][1] -= 1
        place_tetromino(obj)
        return False
    return True

# Move tetromino left
def move_tetromino_left(obj):
    obj['position'][0] -= 1
    if not valid_position(obj):
        obj['position'][0] += 1

# Move tetromino right
def move_tetromino_right(obj):
    obj['position'][0] += 1
    if not valid_position(obj):
        obj['position'][0] -= 1

def refresh_display():
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] != ' ':
                draw_block(x, y, 0xFFFFFF)  
    display.show(group)  
        
termino = generate_tetromino()   
while True:
    pos_x, pos_y = termino['position'][0], termino['position'][1]
    if not move_tetromino_down(termino):
        termino = generate_tetromino()
        pos_x, pos_y = grid_width//2, 0
    if not btn_a.value: 
        move_tetromino_left(termino)
        print("moving to the left")
        time.sleep(0.2)  
    
    if not btn_b.value:
        rotate_tetromino(termino)
        print("rotate")
        time.sleep(0.2)  
    
    if not btn_c.value:
        move_tetromino_right(termino)
        print("moving to the right")
    
    draw_tetromino(termino['shape'], termino['rotation'], pos_x, pos_y)
    display.show(group)
    gc.collect()
    refresh_display()

    