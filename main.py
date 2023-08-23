import asyncio
from curses import initscr

import time
import curses
import random
from os import path
from itertools import cycle

from fire_animation import fire
from physics import update_speed

from curses_tools import draw_frame, read_controls

from space_garbage import fly_garbage, obstacles_actual


TIC_TIMEOUT = 0.1


def read_frame(filename):
    with open(filename, 'r') as frame1:
        file = frame1.read()
    return file


async def sleep(tics=1):
    iteration_count = int(tics * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(30):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(50):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(30):
            await asyncio.sleep(0)


# async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
#     """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
#     rows_number, columns_number = canvas.getmaxyx()
#
#     column = max(column, 0)
#     column = min(column, columns_number - 1)
#
#     row = 0
#
#     while row < rows_number:
#         draw_frame(canvas, row, column, garbage_frame)
#         await asyncio.sleep(0)
#         draw_frame(canvas, row, column, garbage_frame, negative=True)
#         row += speed
#         canvas.border()


# async def fill_orbit_with_garbage(canvas, coroutines, garbage_frames, timeout=1):
#     border_size = 1
#     _, columns_number = canvas.getmaxyx()
#
#     while True:
#         file_name = random.choice(garbage_frames)
#
#         current_trash_frame = read_frame(file_name)
#
#         _, trash_column_size = get_frame_size(current_trash_frame)
#
#         _, columns_number = canvas.getmaxyx()
#
#         random_column = random.randint(
#             border_size,
#             columns_number - trash_column_size - border_size
#         )
#
#         actual_column = min(
#             columns_number - trash_column_size - border_size,
#             random_column + trash_column_size - border_size,
#         )
#
#         garbage_coro = fly_garbage(canvas, actual_column, current_trash_frame)
#         coroutines.append(garbage_coro)
#
#         await sleep(timeout)
def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fill_orbit_with_garbage(canvas, coroutines, garbage_frames):
    border_size = 1
    _, columns_number = canvas.getmaxyx()

    while True:
        file_name = random.choice(garbage_frames)

        current_trash_frame = read_frame(file_name)

        _, trash_column_size = get_frame_size(current_trash_frame)

        _, columns_number = canvas.getmaxyx()


        random_column = random.randint(
            border_size,
            columns_number - trash_column_size - border_size
        )

        actual_column = min(
            columns_number - trash_column_size - border_size,
            random_column + trash_column_size - border_size,
        )

        garbage_coro = fly_garbage(canvas, actual_column, current_trash_frame)
        coroutines.append(garbage_coro)

        await asyncio.sleep(0)
        await asyncio.sleep(0)
        await asyncio.sleep(0)


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


def multiple_frames():
    trash_large = path.realpath('frames/trash_large.txt')
    trash_small = path.realpath('frames/trash_small.txt')
    trash_xl = path.realpath('frames/trash_xl.txt')
    return [trash_large, trash_small, trash_xl]


def run_event_loop(canvas, coroutines):
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
                canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)
    stdscr = initscr()
    rows, columns = stdscr.getmaxyx()

    random.randint(1, rows)
    coroutines = []

    file_name_1 = path.realpath('frames/rocket_frame_1.txt')
    file_name_2 = path.realpath('frames/rocket_frame_2.txt')

    frame_1 = read_frame(file_name_1)
    frame_2 = read_frame(file_name_2)

    polys = [frame_1, frame_2]

    borders_size = 1
    correct_for_fire = 3
    max_row, max_column = rows - borders_size, columns + correct_for_fire

    spaceship_rows_for_fire, spaceship_columns_for_fire = get_frame_size(frame_1)
    canvas_column_center = max_column // 2

    start_row_for_fire = max_row - spaceship_rows_for_fire
    start_col_for_fire = canvas_column_center - spaceship_columns_for_fire // 2

    coroutine_fire = fire(canvas, start_row_for_fire, start_col_for_fire, rows_speed=-0.3, columns_speed=0)
    coroutines.append(coroutine_fire)

    for _ in range(200):
        coroutines.append(
            blink(canvas, random.randint(1, rows - 2), random.randint(1, columns - 2), symbol=random.choice('+*.:')))
    animate_space = animate_spaceship(canvas, polys, coroutines)
    coroutines.append(animate_space)

    garbage_frames = multiple_frames()
    garbage_coro = fill_orbit_with_garbage(canvas, coroutines, garbage_frames)
    coroutines.append(garbage_coro)

    run_event_loop(canvas, coroutines)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)


