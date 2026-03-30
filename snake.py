import curses
import random
import time

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # snake
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # food
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # score
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # border

    sh, sw = stdscr.getmaxyx()
    game_h = sh - 2  # leave room for score bar
    game_w = sw

    # Initial snake: 3 segments in the middle
    mid_y, mid_x = game_h // 2 + 1, sw // 2
    snake = [(mid_y, mid_x - i) for i in range(3)]
    direction = curses.KEY_RIGHT

    def spawn_food(snake):
        while True:
            y = random.randint(1, game_h - 1)
            x = random.randint(1, game_w - 2)
            if (y, x) not in snake:
                return (y, x)

    food = spawn_food(snake)
    score = 0
    base_delay = 0.15
    min_delay = 0.04

    def draw_border():
        stdscr.attron(curses.color_pair(4))
        # Top border (row 1) and bottom border (row game_h)
        for x in range(sw):
            try:
                stdscr.addch(1, x, curses.ACS_HLINE)
                stdscr.addch(game_h, x, curses.ACS_HLINE)
            except curses.error:
                pass
        for y in range(1, game_h + 1):
            try:
                stdscr.addch(y, 0, curses.ACS_VLINE)
                stdscr.addch(y, sw - 1, curses.ACS_VLINE)
            except curses.error:
                pass
        try:
            stdscr.addch(1, 0, curses.ACS_ULCORNER)
            stdscr.addch(1, sw - 1, curses.ACS_URCORNER)
            stdscr.addch(game_h, 0, curses.ACS_LLCORNER)
            stdscr.addch(game_h, sw - 1, curses.ACS_LRCORNER)
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(4))

    def draw_score(score):
        stdscr.attron(curses.color_pair(3))
        score_str = f" SNAKE  |  Score: {score}  |  Use arrow keys to move  |  Q to quit "
        try:
            stdscr.addstr(0, 0, score_str[:sw - 1].ljust(sw - 1))
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(3))

    def draw_food(food):
        try:
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addch(food[0], food[1], '@')
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

    def draw_snake(snake):
        for i, seg in enumerate(snake):
            try:
                if i == 0:
                    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                    stdscr.addch(seg[0], seg[1], 'O')
                    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addch(seg[0], seg[1], 'o')
                    stdscr.attroff(curses.color_pair(1))
            except curses.error:
                pass

    last_time = time.time()

    while True:
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        # Update direction — prevent reversing
        if key == curses.KEY_UP and direction != curses.KEY_DOWN:
            direction = curses.KEY_UP
        elif key == curses.KEY_DOWN and direction != curses.KEY_UP:
            direction = curses.KEY_DOWN
        elif key == curses.KEY_LEFT and direction != curses.KEY_RIGHT:
            direction = curses.KEY_LEFT
        elif key == curses.KEY_RIGHT and direction != curses.KEY_LEFT:
            direction = curses.KEY_RIGHT

        delay = max(min_delay, base_delay - score * 0.003)
        now = time.time()
        if now - last_time < delay:
            time.sleep(0.01)
            continue
        last_time = now

        # Compute new head
        head_y, head_x = snake[0]
        if direction == curses.KEY_UP:
            head_y -= 1
        elif direction == curses.KEY_DOWN:
            head_y += 1
        elif direction == curses.KEY_LEFT:
            head_x -= 1
        elif direction == curses.KEY_RIGHT:
            head_x += 1

        new_head = (head_y, head_x)

        # Wall collision
        if head_y <= 1 or head_y >= game_h or head_x <= 0 or head_x >= sw - 1:
            break

        # Self collision
        if new_head in snake:
            break

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            food = spawn_food(snake)
        else:
            # Erase tail
            tail = snake.pop()
            try:
                stdscr.addch(tail[0], tail[1], ' ')
            except curses.error:
                pass

        stdscr.clear()
        draw_border()
        draw_score(score)
        draw_food(food)
        draw_snake(snake)
        stdscr.refresh()

    # Game over screen
    stdscr.clear()
    stdscr.nodelay(False)
    msg1 = "GAME OVER"
    msg2 = f"Final Score: {score}"
    msg3 = "Press any key to exit"
    cy = sh // 2
    cx = sw // 2

    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    try:
        stdscr.addstr(cy - 2, cx - len(msg1) // 2, msg1)
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    try:
        stdscr.addstr(cy, cx - len(msg2) // 2, msg2)
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    stdscr.attron(curses.color_pair(4))
    try:
        stdscr.addstr(cy + 2, cx - len(msg3) // 2, msg3)
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(4))

    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
