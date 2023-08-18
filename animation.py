import asyncio

from itertools import cycle

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


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def animate_spaceship(canvas, polys):
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
            direction_y, direction_x, _ = read_controls(canvas)

            row_speed, column_speed = update_speed(
                row_speed,
                column_speed,
                direction_y,
                direction_x
            )

            current_column += column_speed
            current_row += row_speed

            # current_column += direction_x
            # current_row += direction_y

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
