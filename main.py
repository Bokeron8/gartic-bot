import time
import datetime
from math import sqrt
from gif import getFrames
from Keys import released, press, VK_CODE
import cv2
import win32api, win32con

OFFSET_X = 380
OFFSET_Y = 250
SIZE_W = 400
SIZE_H = 300

class Counter:
    click_counter = 0
    drawn = 0
counter = Counter()

COLORS = [
    {
        #BLACK
        'COLOR': (0, 0, 0, 255), 'POS': (270, 310)
    },
    {
        #WHITE
        'COLOR': (255, 255, 255, 255), 'POS': (270, 345)
    },
    {
        #GREEN
        'COLOR': (17,176,60,255), 'POS': (270, 400)
    },
    {
        #DARK GREEN
        'COLOR': (1,116,32,255), 'POS': (270, 370)
    },
    {
        #BLUE
        'COLOR': (70,75,177,255), 'POS': (330, 300)
    },
    {
        #LIGHT BLUE
        'COLOR': (38,201,255,255), 'POS': (330, 340)
    },
    {
        #RED
        'COLOR': (148, 39, 30, 255), 'POS': (300, 400)
    },
    {
        #ORANGE
        'COLOR': (255,120,41,255), 'POS': (330, 400)
    },
    {
        #YELLOW
        'COLOR': (243,242,28,255), 'POS': (270, 470)
    },
    {
        #PINK
        'COLOR': (254,174,201,255), 'POS': (330, 470)
    },
    {
        #DARKER PINK
        'COLOR': (203,90,87,255), 'POS': (330, 440)
    },
    {
        #GRAY
        'COLOR': (102,102,102,255), 'POS': (300, 300)
    },
    {
        #BROWN
        'COLOR': (150,65,18,255), 'POS': (330, 370)    
    },
    {
        #BORDO
        'COLOR': (105,21,6,255), 'POS': (300, 370)    
    },
    {
        #GOLD
        'COLOR': (176,112,28,255), 'POS': (280, 440)    
    }
]
def closest_color(rgb):
    r, g, b = rgb
    color_diffs = []
    for color in COLORS:
        cr, cg, cb, a = color['COLOR']
        color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
        color_diffs.append((color_diff, color['COLOR']))
    return min(color_diffs)[1]

def change_color(color):
    if counter.drawn > 0:
        y_offset = 40
        x, y = color
        click(x, y+y_offset)
    else:
        x, y = color
        click(x, y)

def click(x,y):
    counter.click_counter += 1
    if counter.click_counter >= 3000:
        time.sleep(10)
        counter.click_counter = 0
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def pixelMatchesColor(rgb, expectedRGBColor, tolerance=0):
    pix = rgb
    if len(pix) == 3 or len(expectedRGBColor) == 3: #RGB mode
        r, g, b = pix[0], pix[1], pix[2]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
    elif len(pix) == 4 and len(expectedRGBColor) == 4: #RGBA mode
        r, g, b, a = pix
        exR, exG, exB, exA = expectedRGBColor
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance) and (abs(a - exA) <= tolerance)
    else:
        assert False, 'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s' % (len(pix), len(expectedRGBColor))

def change_image(img, w, h):
    img = cv2.imread(img, cv2.IMREAD_UNCHANGED)

    height, width, channels = img.shape

    if channels > 3:
        trans_mask = img[:,:,3] == 0
        #replace areas of transparency with white and not transparent
        img[trans_mask] = [255, 255, 255, 255]

    #new image without alpha channel...
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    img = cv2.resize(img, (w, h), interpolation = cv2.INTER_AREA)
    return img

def click_done():
    counter.drawn += 1
    click(890, 650)

def change_color_rgb(rgb):
    click(300, 500)
    time.sleep(0.01)
    keys2press = []
    for i in range(3):
        keys2press.append('tab')
    for value in rgb:
        for i in str(value):
            keys2press.append(i)
        keys2press.append('tab')
    press(keys2press)
    click(300, 600)

def draw(img, sleep=0):
    img = change_image(img, SIZE_W, SIZE_H)
    time.sleep(sleep)
    #while True:
    #    if released(ord('S')):
    #        break
    print(datetime.datetime.fromtimestamp(time.time()).strftime('%c'))
    old_color = COLORS[0]['COLOR']
    for i in range(len(img)):
        for j in range(len(img[i])):
            if win32api.GetAsyncKeyState(win32con.VK_CAPITAL):
                break
            if pixelMatchesColor(closest_color(img[i, j]), old_color, 20):
                #check if is the same color
                click(j+OFFSET_X, i+OFFSET_Y)
            elif pixelMatchesColor(img[i, j], (255, 255, 255), 1):
                pass
            else: 
                #if is not and old color and is note white then change the color
                old_color = closest_color(img[i, j])
                color = next(item for item in COLORS if item["COLOR"] == old_color)
                change_color(color['POS'])
                #change_color_rgb(img[i, j])
                click(j+OFFSET_X, i+OFFSET_Y)
    #click_done()
    print(datetime.datetime.fromtimestamp(time.time()).strftime('%c'))

def draw_gif(gif):
    path = gif[:-4]
    frames = getFrames(gif, path)
    turns = 20
    steps = round(frames/turns)
    for frame in range(0, frames, steps):
        draw(f'{path}/{frame}.jpg', 9)
        if counter.drawn >= turns:
            return

if __name__ == '__main__':
    mp4 = 'franco.mp4'
    gif = 'gifs/jujutsu-kaisen.gif'
    image = 'img/jojoBoquita.jpg'

    draw(image)
    #draw_gif(gif)

