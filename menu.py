"""Menu handling module for Tetris"""
from os.path import join, realpath, dirname
import pygame
import pygame.freetype
from cfg import SCREEN_DIMENSIONS, COLORS
from game import SCREEN, CLOCK, BACKGROUND

pygame.init()

def init_menu():
    """Initialize the menu screen

        Return True if the player chooses to quit the game
    """
    background = BACKGROUND.copy()
    dark_surface = pygame.Surface(SCREEN_DIMENSIONS).convert()
    dark_surface.fill((0, 0, 0))
    dark_surface.set_alpha(210)
    background.blit(dark_surface, (0, 0))
    SCREEN.blit(background, (0, 0))
    font = pygame.freetype.Font(join(dirname(realpath(__file__)), 'data', 'FreeSans.ttf'), 85)

    def move_center(rectangle, surface, top):
        """Center a rectangle in a surface with a height adjustment"""
        rectangle.topleft = ((surface.get_width() - rectangle.width) // 2, top)

    def rect_sides(surface, source, rectangle):
        """Return a rectangle's sides in a surface based on a source surface's size"""
        offset = surface.get_width() // 50
        top = rectangle.top + (rectangle.height - source.get_height()) // 2
        left_rect = pygame.Rect((rectangle.left - source.get_width() - offset, top),
                                (source.get_width(), source.get_height()))
        right_rect = pygame.Rect((rectangle.right + 1 + offset, top),
                                 (source.get_width(), source.get_height()))
        # rectangle.right + 1 because pygame rectangles do not include right- and bottom-most edges
        return (left_rect, right_rect)

    title = font.render('TETRIS', fgcolor=COLORS['RED'])
    move_center(title[1], SCREEN, SCREEN_DIMENSIONS[1] // 4)
    SCREEN.blit(title[0], title[1])

    font.size = 20
    offset = SCREEN_DIMENSIONS[1] // 30

    start_button = font.render('START GAME', fgcolor=(150, 150, 150))
    move_center(start_button[1], SCREEN, SCREEN_DIMENSIONS[1] // 2 + offset)
    SCREEN.blit(start_button[0], start_button[1])

    quit_button = font.render('QUIT GAME', fgcolor=(150, 150, 150))
    move_center(quit_button[1], SCREEN, start_button[1].top + start_button[1].height + offset)
    SCREEN.blit(quit_button[0], quit_button[1])

    selection = font.render('.', fgcolor=(150, 150, 150))
    start_sides = rect_sides(SCREEN, selection[0], start_button[1])
    quit_sides = rect_sides(SCREEN, selection[0], quit_button[1])
    sides = (start_sides, quit_sides)

    del dark_surface, font, move_center, rect_sides, title, start_button, quit_button

    selected = False
    for rect in start_sides:
        SCREEN.blit(selection[0], rect)

    pygame.display.update()

    def change_selection():
        """Change currently selected menu option"""
        nonlocal selected
        for rect in sides[selected]:
            SCREEN.blit(background, rect, area=rect)
        selected = not selected
        for rect in sides[selected]:
            SCREEN.blit(selection[0], rect)
        for rect_list in sides:
            pygame.display.update(rect_list)

    while True:
        CLOCK.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    change_selection()
                elif event.key == pygame.K_RETURN:
                    return selected
