"""Game handling module for Tetris"""
from os.path import join, realpath, dirname
from random import randrange
import pygame
from cfg import (COLORS, BACKGROUND_COLOR, SQUARE_OUTLINE_COLOR, BORDER_COLOR,
                 SCREEN_DIMENSIONS, BOARD_DIMENSIONS, OFFSET, BORDER_DISTANCE, SQUARE_OFFSET,
                 NUM_COLUMNS, NUM_ROWS, COLUMN_STEP, ROW_STEP, SQUARE_WIDTH, SQUARE_HEIGHT)

pygame.init()

CLOCK = pygame.time.Clock()

class MyException(Exception):
    """Exception for custom use"""
    pass

class Square:
    """Wrapper for Squares on the board"""
    def __init__(self, rectangle, position):
        self.rect = rectangle
        self.pos = position
        self.full = False

# BOARD outline rectangle and list of containing rectangles
BOARD_RECT = pygame.rect.Rect(OFFSET, BOARD_DIMENSIONS)
BOARD = tuple(
    tuple(
        Square(
            pygame.rect.Rect(
                j * COLUMN_STEP + SQUARE_OFFSET[0],
                i * ROW_STEP + SQUARE_OFFSET[1],
                SQUARE_WIDTH,
                SQUARE_HEIGHT,
            ),
            (i, j),
        )
        for j in range(NUM_COLUMNS)
    )
    for i in range(NUM_ROWS)
)

SCREEN = pygame.display.set_mode(SCREEN_DIMENSIONS)
pygame.mouse.set_visible(False)
pygame.display.set_caption("Tetris")

BACKGROUND = pygame.Surface(SCREEN_DIMENSIONS).convert()

def load_image(name, alpha_value=None):
    """Load an image using its name and optionally set its alpha value"""
    fullname = join(dirname(realpath(__file__)), 'data', name)
    image = pygame.image.load(fullname).convert()
    if alpha_value:
        image.set_alpha(alpha_value)
    return image

def init_background():
    """Initialize the background surface"""
    BACKGROUND.blit(load_image('shapes.jpg', 130), (0, 0))
    pygame.draw.rect(BACKGROUND, BACKGROUND_COLOR, BOARD_RECT)
    for squares_line in BOARD:
        for square in squares_line:
            pygame.draw.rect(BACKGROUND,
                             SQUARE_OUTLINE_COLOR,
                             square.rect.inflate(2 * BORDER_DISTANCE, 2 * BORDER_DISTANCE),
                             1)
    pygame.draw.rect(BACKGROUND, BORDER_COLOR, BOARD_RECT, 2)

init_background()

def init_game():
    """Initialize the game"""
    for squares_line in BOARD:
        for square in squares_line:
            square.full = False
    SCREEN.blit(BACKGROUND, (0, 0))
    pygame.display.update()

class Structure:
    """Wrapper for Tetris structures"""
    def __init__(self, squares, color):
        self.squares = squares
        self.color = color

    def copy(self):
        """Return a shallow copy of the structure"""
        return Structure(self.squares, self.color)

    def draw_structure(self, surface, erase=False, display_on_screen=False):
        """Draw structure to a surface (or erase it)"""
        if not erase:
            for square in self.squares:
                pygame.draw.rect(surface, self.color, square.rect)
        else:
            for square in self.squares:
                pygame.draw.rect(surface, BACKGROUND_COLOR, square.rect)
        if display_on_screen:
            pygame.display.update([square.rect for square in self.squares])

    def move_by_squares(self, surface, new_squares):
        """Move a structure on a surface using square sequences and update the display"""
        update_squares = set(self.squares + new_squares)
        self.draw_structure(surface, erase=True)
        self.squares = new_squares
        self.draw_structure(surface)
        pygame.display.update([square.rect for square in update_squares])

    def move(self, direction, surface=SCREEN):
        """Move structure, draw it on a surface and update the display"""
        temp_squares = []
        if direction == 'down':
            offset = (1, 0)
            boundary = NUM_ROWS - 1
            index = 0
        elif direction == 'left':
            offset = (0, -1)
            boundary = 0
            index = 1
        elif direction == 'right':
            offset = (0, 1)
            boundary = NUM_COLUMNS - 1
            index = 1
        try:
            for square in self.squares:
                if square.pos[index] != boundary:
                    after_square = BOARD[square.pos[0] + offset[0]][square.pos[1] + offset[1]]
                    if after_square.full:
                        raise MyException
                    temp_squares.append(after_square)
                else:
                    raise MyException
            self.move_by_squares(surface, temp_squares)
        except MyException:
            if direction == 'down':
                for square in self.squares:
                    square.full = True
                break_rows(set(square.pos[0] for square in self.squares))
                return True

    def rotate(self, surface=SCREEN):
        """Rotate the structure, draw it on a surface and update the display"""
        ref_square = self.squares.pop(1)
        temp_squares = []
        try:
            for square in self.squares:
                dist = tuple(square.pos[i] - ref_square.pos[i] for i in range(2))
                after_square_pos = (ref_square.pos[0] + dist[1], ref_square.pos[1] - dist[0])
                if (after_square_pos[0] >= 0 and after_square_pos[0] <= NUM_ROWS - 1 and
                        after_square_pos[1] >= 0 and after_square_pos[1] <= NUM_COLUMNS - 1):
                    after_square = BOARD[after_square_pos[0]][after_square_pos[1]]
                    if after_square.full:
                        raise MyException
                    temp_squares.append(after_square)
                else:
                    raise MyException
            self.move_by_squares(surface, temp_squares)
        except MyException:
            pass
        self.squares.insert(1, ref_square)

def insert_sorted(item, sorted_list):
    """Inserts an item into a sorted list (descending order)"""
    pos = 0
    for _ in range(len(sorted_list)):
        if item < sorted_list[pos]:
            pos += 1
        else:
            break
    sorted_list.insert(pos, item)

def break_rows(rows):
    """Check and break square rows that are full and update the display"""
    rows_to_break = []
    for i in rows:
        try:
            for j in range(NUM_COLUMNS):
                if not BOARD[i][j].full:
                    raise MyException
        except MyException:
            continue
        insert_sorted(i, rows_to_break)
    if rows_to_break:
        num_rows_to_break = len(rows_to_break)
        rows_to_break.append(0)
        blit_rect = BOARD_RECT.inflate(- BORDER_DISTANCE * 2, - BORDER_DISTANCE * 2)
        blit_rect.move_ip(0, rows_to_break[0] * ROW_STEP)
        for k in range(num_rows_to_break):
            dist = rows_to_break[k] - rows_to_break[k + 1]
            for i in reversed(range(rows_to_break[k + 1] + 2 + k, rows_to_break[k] + 1 + k)):
                for j in range(NUM_COLUMNS):
                    BOARD[i][j].full = BOARD[i - k - 1][j].full
            blit_rect.move_ip(0, - dist * ROW_STEP)
            blit_rect.height = dist * ROW_STEP - BORDER_DISTANCE * 2
            SCREEN.blit(SCREEN, blit_rect.move(0, (k + 1) * ROW_STEP), blit_rect)
        for i in range(num_rows_to_break + 1):
            for j in range(NUM_COLUMNS):
                BOARD[i][j].full = False
        blit_rect.height = num_rows_to_break * ROW_STEP
        blit_rect.top = SQUARE_OFFSET[1]
        SCREEN.blit(BACKGROUND, blit_rect, blit_rect)
        pygame.display.update(BOARD_RECT)

STRUCTURES = (
    Structure(
        [
            BOARD[0][i] for i in range(3, 7)
        ],
        COLORS['BLUE']
    ),
    Structure(
        [
            BOARD[0][3],
            BOARD[0][4],
            BOARD[0][5],
            BOARD[1][3],
        ],
        COLORS['TEAL']
    ),
    Structure(
        [
            BOARD[0][3],
            BOARD[0][4],
            BOARD[0][5],
            BOARD[1][4],
        ],
        COLORS['PURPLE']
    ),
    Structure(
        [
            BOARD[0][3],
            BOARD[0][4],
            BOARD[0][5],
            BOARD[1][5],
        ],
        COLORS['ORANGE']
    ),
    Structure(
        [
            BOARD[0][5],
            BOARD[0][4],
            BOARD[1][4],
            BOARD[1][5],
        ],
        COLORS['YELLOW']
    ),
    Structure(
        [
            BOARD[0][3],
            BOARD[0][4],
            BOARD[1][4],
            BOARD[1][5],
        ],
        COLORS['GREEN']
    ),
    Structure(
        [
            BOARD[0][5],
            BOARD[0][4],
            BOARD[1][3],
            BOARD[1][4],
        ],
        COLORS['RED']
    ),
)

def give_random_structure(surface=SCREEN):
    """Draw a random structure to a surface and return it"""
    structure = STRUCTURES[randrange(len(STRUCTURES))].copy()
    for square in structure.squares:
        if square.full:
            return False
    structure.draw_structure(surface, display_on_screen=True)
    return structure
