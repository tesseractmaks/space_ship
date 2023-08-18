import asyncio
from os import path
from itertools import cycle
import curses
from physics import update_speed

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


def read_frame(filename):
    with open(filename, 'r') as frame1:
        file = frame1.read()
    return file


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows, columns

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, polys, coroutines):
    rows, columns = canvas.getmaxyx()

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

    row_speed, column_speed = 0, 0

    while True:
        for _ in range(2):
            direction_y, direction_x, shot = read_controls(canvas)

            file_name_1 = path.realpath('frames/rocket_frame_1.txt')
            frame_1 = read_frame(file_name_1)
            correct_for_fire = 2


            spaceship_rows_for_fire, spaceship_columns_for_fire = get_frame_size(frame_1)

            frame_pos_x = current_column - spaceship_columns_for_fire / 2 + correct_for_fire
            frame_pos_y = current_row - spaceship_rows_for_fire / 2

            if shot:
                shot_pos_x = frame_pos_x + spaceship_columns_for_fire / 2
                shot_pos_y = frame_pos_y + correct_for_fire * 2

                coroutine_fire = fire(canvas, shot_pos_y, shot_pos_x, rows_speed=-0.3, columns_speed=0)

                coroutines.append(coroutine_fire)

            row_speed, column_speed = update_speed(
                row_speed,
                column_speed,
                direction_y,
                direction_x
            )

            current_column += column_speed
            current_row += row_speed


            frame_column_max = current_column + frame_size_column
            frame_row_max = current_row + frame_size_row

            field_column_max = width - border_size
            field_row_max = height - border_size

            start_column = max(min(frame_column_max, field_column_max) - frame_size_column, border_size)
            start_row = max(min(frame_row_max, field_row_max) - frame_size_row, border_size)

            draw_frame(canvas, start_row, start_column, current_frame)
            await asyncio.sleep(0)

            draw_frame(canvas, start_row, start_column, current_frame, negative=True)
            current_frame = next(iterator)
