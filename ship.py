import asyncio
from curses import initscr

import time
import curses
import random
from itertools import cycle
from fire_file import fire

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:

        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def frame(filename):
    with open(filename, 'r') as frame1:
        file = frame1.read()
    return file


def draw_frame(canvas, start_row, start_column, text, negative=False):
    rows_number, columns_number = canvas.getmaxyx()
    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue
            if row == rows_number - 1 and column == columns_number - 1:
                continue
            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def animate_spaceship(canvas):
    rows, columns = canvas.getmaxyx()
    start_row, start_column = (rows/2, columns/2)
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    filename1 = 'rocket_frame_1.txt'
    filename2 = 'rocket_frame_2.txt'

    frame11 = frame(filename1)
    frame22 = frame(filename2)

    polys = [frame11, frame22]
    iterator = cycle(polys)
    current_frame = next(iterator)

    height, width = canvas.getmaxyx()
    border_size = 2

    frame_size_y, frame_size_x = get_frame_size(current_frame)
    frame_pos_x = round(start_column) - round(frame_size_x / 2)
    frame_pos_y = round(start_row) - round(frame_size_y / 2)

    while True:
        new_row, new_column, _ = read_controls(canvas)

        frame_pos_x += new_column
        frame_pos_y += new_row

        frame_x_max = frame_pos_x + frame_size_x
        frame_y_max = frame_pos_y + frame_size_y

        field_x_max = width - border_size
        field_y_max = height - border_size

        frame_pos_x = min(frame_x_max, field_x_max) - frame_size_x
        frame_pos_y = min(frame_y_max, field_y_max) - frame_size_y
        start_column = max(frame_pos_x, border_size)
        start_row = max(frame_pos_y, border_size)

        start_row += new_row
        start_column += new_column

        draw_frame(canvas, start_row, start_column, current_frame)
        canvas.refresh()
        await asyncio.sleep(0)
        time.sleep(0.07)
        draw_frame(canvas, start_row, start_column, current_frame, negative=True)
        current_frame = next(iterator)


async def blink(canvas, row, column, symbol='*'):
    TIC_TIMEOUT = 0.01
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)
            time.sleep(TIC_TIMEOUT)
        time.sleep(TIC_TIMEOUT)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
            time.sleep(0.1)
        time.sleep(TIC_TIMEOUT)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)
            time.sleep(TIC_TIMEOUT)
        time.sleep(TIC_TIMEOUT)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
            time.sleep(TIC_TIMEOUT)
        time.sleep(TIC_TIMEOUT)


def main(canvas):
    canvas.border()
    curses.curs_set(False)

    stdscr = initscr()
    rows, cols = stdscr.getmaxyx()
    random.randint(1, rows)
    coroutines = []
    rows, columns = canvas.getmaxyx()
    start_row, start_col = (rows / 2, columns / 2)

    coroutine_fire = fire(canvas, start_row -4, start_col, rows_speed=-0.3, columns_speed=0)
    coroutines.append(coroutine_fire)

    for _ in range(30):
        coroutines.append(
        blink(canvas, random.randint(1, rows - 2), random.randint(1, cols - 2), symbol=random.choice('+*.:')))
    animate_space = animate_spaceship(canvas)
    coroutines.append(animate_space)

    TIC_TIMEOUT = 0
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
                time.sleep(0)
            except StopIteration:
                coroutines.remove(coroutine)

            time.sleep(TIC_TIMEOUT)
            if len(coroutines) == 0:
                break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
