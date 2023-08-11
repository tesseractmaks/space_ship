import asyncio

import time
import curses
from itertools import cycle


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


async def animate_spaceship(canvas, polys):
    rows, columns = canvas.getmaxyx()
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    iterator = cycle(polys)
    current_frame = next(iterator)

    borders_size = 1
    max_row, max_column = rows - borders_size, columns - borders_size

    spaceship_rows, spaceship_columns = get_frame_size(current_frame)
    canvas_column_center = max_column // 2

    current_row = max_row - spaceship_rows
    current_column = canvas_column_center - spaceship_columns // 2

    height, width = canvas.getmaxyx()
    border_size = 1
    frame_size_row, frame_size_column = get_frame_size(current_frame)

    while True:
        for _ in range(2):
            direction_y, direction_x, _ = read_controls(canvas)

            current_column += direction_x
            current_row += direction_y

            frame_column_max = current_column + frame_size_column
            frame_row_max = current_row + frame_size_row

            field_column_max = width - border_size
            field_row_max = height - border_size

            start_column = max(min(frame_column_max, field_column_max) - frame_size_column, border_size)
            start_row = max(min(frame_row_max, field_row_max) - frame_size_row, border_size)

            draw_frame(canvas, start_row, start_column, current_frame)
            canvas.refresh()
            await asyncio.sleep(0)
            time.sleep(0.07)

            draw_frame(canvas, start_row, start_column, current_frame, negative=True)
            current_frame = next(iterator)


# async def blink(canvas, row, column, symbol='*'):
#     TIC_TIMEOUT = 0.002
#     while True:
#         time.sleep(TIC_TIMEOUT)
#         canvas.addstr(row, column, symbol, curses.A_DIM)
#         for _ in range(20):
#             await asyncio.sleep(0)
#         time.sleep(TIC_TIMEOUT)
#
#         canvas.addstr(row, column, symbol)
#         for _ in range(30):
#             await asyncio.sleep(0)
#         time.sleep(TIC_TIMEOUT)
#
#         canvas.addstr(row, column, symbol, curses.A_BOLD)
#         for _ in range(50):
#             await asyncio.sleep(0)
#         time.sleep(TIC_TIMEOUT)
#
#         canvas.addstr(row, column, symbol)
#         for _ in range(30):
#             await asyncio.sleep(0)




# def main(canvas):
#     canvas.border()
#     curses.curs_set(False)
#     stdscr = initscr()
#     rows, columns = stdscr.getmaxyx()
#     random.randint(1, rows)
#     coroutines = []
#
#     file_name_1 = path.realpath('frames/rocket_frame_1.txt')
#     file_name_2 = path.realpath('frames/rocket_frame_2.txt')
#
#     frame_1 = frame(file_name_1)
#     frame_2 = frame(file_name_2)
#
#     polys = [frame_1, frame_2]
#
#     borders_size = 1
#     correct_for_fire = 2
#     max_row, max_column = rows - borders_size, columns + correct_for_fire
#
#     spaceship_rows_for_fire, spaceship_columns_for_fire = get_frame_size(frame_1)
#     canvas_column_center = max_column // 2
#
#     start_row_for_fire = max_row - spaceship_rows_for_fire
#     start_col_for_fire = canvas_column_center - spaceship_columns_for_fire // 2
#
#     coroutine_fire = fire(canvas, start_row_for_fire, start_col_for_fire, rows_speed=-0.3, columns_speed=0)
#     coroutines.append(coroutine_fire)
#
#     for _ in range(200):
#         coroutines.append(
#             blink(canvas, random.randint(1, rows - 2), random.randint(1, columns - 2), symbol=random.choice('+*.:')))
#     animate_space = animate_spaceship(canvas, polys)
#     coroutines.append(animate_space)
#
#     TIC_TIMEOUT = 0.1
#     while True:
#         for coroutine in coroutines.copy():
#             try:
#                 coroutine.send(None)
#                 canvas.refresh()
#             except StopIteration:
#                 coroutines.remove(coroutine)
#         time.sleep(TIC_TIMEOUT)
#
#
# if __name__ == '__main__':
#     curses.update_lines_cols()
#     curses.wrapper(main)
