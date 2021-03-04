"""Main Tetris module"""
from os.path import join, realpath, dirname
from game_files.game import CLOCK, give_random_structure, MyException, init_game
from game_files.menu import init_menu
import pygame

pygame.init()

pygame.mixer.music.load(join(dirname(realpath(__file__)), 'game_files', 'data', 'soundtrack.mp3'))

GAME_CYCLE = 800
GAME_EVENT_TYPE = pygame.USEREVENT
GAME_EVENT = pygame.event.Event(GAME_EVENT_TYPE)

pygame.event.set_allowed(None)
pygame.event.set_allowed([GAME_EVENT_TYPE, pygame.QUIT, pygame.KEYDOWN])

def main():
    """Start the game"""
    init_game()
    pygame.event.clear()
    pygame.time.set_timer(GAME_EVENT_TYPE, GAME_CYCLE)
    current_structure = give_random_structure()
    while True:
        CLOCK.tick(120)
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == GAME_EVENT_TYPE:
                    raise MyException
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        pygame.time.set_timer(GAME_EVENT_TYPE, GAME_CYCLE)
                        raise MyException
                    elif event.key == pygame.K_LEFT:
                        current_structure.move('left')
                    elif event.key == pygame.K_RIGHT:
                        current_structure.move('right')
                    elif event.key == pygame.K_UP:
                        current_structure.rotate()
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_SPACE:
                        CLOCK.tick(0.1)
        except MyException:
            if current_structure.move('down'):
                current_structure = give_random_structure()
                if not current_structure:
                    return

while not init_menu():
    # If the player doesn't press on QUIT GAME, start the game over
    pygame.mixer.music.play(loops=-1)
    main()
    pygame.mixer.music.stop()

pygame.quit()
