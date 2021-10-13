# -*- coding: utf-8 -*-

import pyautogui
import os
import time
import random
from PIL import Image, ImageDraw
import psutil


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆
VERSION = "1.0.0"
# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

def pull_screenshot():
    pyautogui.screenshot("autojump.png", region=(736, 145, 443, 794)) # This parameter on my computer
    return Image.open('./autojump.png')

def check_screenshot():
    if os.path.isfile('autojump.png'):
        try:
            os.remove('autojump.png')
        except Exception:
            pass

def find_piece_and_board(im):  # Find the location of piece and destination
    w, h = im.size  # width and height of screen shot
    im_pixel = im.load()

    def find_piece(pixel):  # The color of piece
        return ((40 < pixel[0] < 70) and
                (40 < pixel[1] < 65) and
                (75 < pixel[2] < 105))

    # Find Piece ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

    # Rough Check position of the pieces
    piece_found, piece_fx, piece_fy = 0, 0, 0
    scan_piece_unit = w // 20  # Interval
    ny = (h + w) // 2  
    while ny > (h - w) // 2 and not piece_found:
        ny -= scan_piece_unit
        for nx in range(0, w, scan_piece_unit):
            pixel = im_pixel[nx, ny]
            if find_piece(pixel):
                piece_fx, piece_fy = nx, ny
                piece_found = True
                break
    print('%-12s %s,%s' % ('piece_fuzzy:', piece_fx, piece_fy))
    if not piece_fx:
        return 0, 0  # If we don't find the piece

    # Find the exact position of the pieces
    piece_x, piece_x_set = 0, []  
    piece_width = w // 14 +2 
    piece_height = w // 5 
    for ny in range(piece_fy + scan_piece_unit, piece_fy - piece_height, -4):
        for nx in range(max(piece_fx - piece_width, 0),
                        min(piece_fx + piece_width, w)):
            pixel = im_pixel[nx, ny]
            # print(nx,ny,pixel)
            if find_piece(pixel):
                piece_x_set.append(nx)
        if len(piece_x_set) > 10:
            piece_x = sum(piece_x_set) / len(piece_x_set)
            break
    piece_x = round(piece_x, 0)
    print('%-12s %s' % ('p_exact_x:', piece_x))

    # Find Destinatiopn ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆

    board_x = 0

    if piece_x < w / 2:
        board_x_start, board_x_end = w // 2, w 
    else:
        board_x_start, board_x_end = 0, w // 2

    # destination top location
    board_x_set = []
    for by in range((h - w) // 2, (h + w) // 2, 5):
        bg_pixel = im_pixel[0, by]
        for bx in range(board_x_start, board_x_end):
            pixel = im_pixel[bx, by]
            # in case piece is higher than destination
            if abs(bx - piece_x) < piece_width/2:
                continue

            if (abs(pixel[0] - bg_pixel[0]) +
                    abs(pixel[1] - bg_pixel[1]) +
                    abs(pixel[2] - bg_pixel[2]) > 10):
                board_x_set.append(bx)

        if len(board_x_set) > 10:
            board_x = sum(board_x_set) / len(board_x_set)
            board_x = round(board_x, 0)
            print('%-12s %s' % ('target_x:', board_x))
            break  # when we find the destination
    return piece_x, board_x

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def set_button_position(im, gameover):
    w, h = im.size
    if h // 16 > w // 9 + 2:
        uih = int(w / 9 * 16)
    else:
        uih = h
    # uiw = int(uih / 16 * 9)

    # if game over, click play again
    left = 736 + int(w / 1.6)

    top = 145 + int((h - uih) / 2 + uih * 0.825)

    return left, top


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def jump(piece_x, board_x, im, swipe_x1, swipe_y1):
    distanceX = abs(board_x - piece_x)  
    shortEdge = min(im.size) 
    jumpPercent = distanceX / shortEdge  
    jumpFullWidth = 1450     # jumping full width takes 1450 ms
    press_time = round(jumpFullWidth * jumpPercent)  
    press_time = 0 if not press_time else max(press_time, 160)  # press_time ast least 160
    if(press_time<=263 and press_time!=0):
        press_time = 160
    if(press_time == 0):
        pyautogui.mouseDown(swipe_x1, swipe_y1, button="left")
        pyautogui.mouseUp(button="left")
    else:
        print('%-12s %.2f%% (%s/%s) | Press Time: %sms' %
              ('Distance:', jumpPercent * 100, distanceX, shortEdge, press_time))

        # Use pyatuogui to click left mouse button，random click in case the system find cheating 

        x = swipe_x1 + random.randint(-20, 20)
        y = swipe_y1 + random.randint(-10, 10)
        pyautogui.mouseDown(x, y, button="left")
        time.sleep((press_time) / 1000)
        pyautogui.mouseUp(button="left")
        return press_time


# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


def main():
    check_screenshot() 

    count = 0
    while True:
        count += 1
        print('---\n%-12s %s (%s)' % ('Times:', count, int(time.time())))

        # Get screenshot
        im = pull_screenshot()
        w, h = im.size

        # Get locations of piece and destination
        piece_x, board_x = find_piece_and_board(im)
        gameover = 0 if all((piece_x, board_x)) else 1  # if piece_x == 0, board_x == 0，the bot thinks that game over
        swipe_x1, swipe_y1 = set_button_position(im, gameover)  # random click to restart

        # Mark in Screenshot(can be used for debug)

        # draw = ImageDraw.Draw(im)
        # draw.line([piece_x, 0, piece_x, h], fill='blue', width=1)  # start
        # draw.line([board_x, 0, board_x, h], fill='red', width=1)  # end
        # draw.ellipse([swipe_x1 - 16, swipe_y1 - 16,
        #               swipe_x1 + 16, swipe_y1 + 16], fill='red')  # click
        # process_list = []
        # for proc in psutil.process_iter():
        #     process_list.append(proc)
        # im.show()

        jump(piece_x, board_x, im, swipe_x1, swipe_y1)

        wait = random.random()**7*4+3  # In case the system find cheating, stop 3-7 seconds
        print('---\nWait %.3f s...' % wait)
        time.sleep(wait)
        print('Continue!')

# ◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆◆


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        os.system('adb kill-server')
        print('bye')
        exit(0)