import pygame
import numpy as np


gridSize = 10
startWalls = 75

turn = "X"
caption = "Kaese           Player: "

#   0 empty 1 is A 2 is B and 3 is X
grid = np.zeros((gridSize, gridSize), np.int)

# boolean array to save covered/uncovered info about every slot
upperSet = np.zeros((gridSize, gridSize), np.dtype(bool))
leftSet = np.zeros((gridSize, gridSize), np.dtype(bool))

for column in range(gridSize):
    for row in range(gridSize):
        if column ==0:
            leftSet[column][row] = True

        if row == 0:
            upperSet[column][row] = True


# initialize pygame
pygame.init()
# set the display size (our pictures are 15*15)
screen = pygame.display.set_mode((30 * gridSize + 4, 30 * gridSize + 4))

# load all images
empty = pygame.image.load("pics/empty.png")
A = pygame.image.load("pics/A.png")
B = pygame.image.load("pics/B.png")
X = pygame.image.load("pics/X.png")

block = pygame.image.load("pics/block.png")

lineX = pygame.image.load("pics/lineX.png")
lineXempty = pygame.image.load("pics/lineXempty.png")

lineY = pygame.image.load("pics/lineY.png")
lineYempty = pygame.image.load("pics/lineYempty.png")


def get_number_of_walls(slot_column, slot_row):
    """
    Get the number of set walls arround the passed slot
    :param slot_column: x of the slot
    :param slot_row: y of the slot
    :return: number of set walls
    """
    number_of_walls = 0

    if slot_column == gridSize - 1:
        number_of_walls += 1
    elif leftSet[slot_column + 1][slot_row]:
        number_of_walls += 1

    if slot_row == gridSize - 1:
        number_of_walls += 1
    elif upperSet[slot_column][slot_row + 1]:
        number_of_walls += 1

    if leftSet[slot_column][slot_row]:
        number_of_walls += 1

    if upperSet[slot_column][slot_row]:
        number_of_walls += 1

    return number_of_walls


def get_wall(pos_x, pos_y):
    rest_x = pos_x % 30
    rest_y = pos_y % 30

    wall_slot_x = pos_x / 30
    wall_slot_y = pos_y / 30

    if rest_x < 4 and rest_y < 4:
        return -1, -1

    if rest_x < 4:
        # is left wall of the slot
        return wall_slot_x*30, wall_slot_y*30 + 4

    if rest_y < 4:
        # is upper wall of the slot
        return wall_slot_x*30 + 4, wall_slot_y*30

    return -1, -1


tries = 0

while startWalls > 0 and tries < 4*gridSize**2:
    x = np.random.random_integers(0, gridSize-1)
    y = np.random.random_integers(0, gridSize-1)
    up = np.random.random_integers(0,1)

    if up:
        if not upperSet[x][y] and get_number_of_walls(x, y) < 2 and get_number_of_walls(x, y - 1) < 2:
            upperSet[x][y] = True
            startWalls -= 1
    else:
        if not leftSet[x][y] and get_number_of_walls(x, y) < 2 and get_number_of_walls(x - 1, y) < 2:
            leftSet[x][y] = True
            startWalls -= 1

    tries += 1


def set_all_slots():
    to_return = 0

    for column_ in range(gridSize):
        for row_ in range(gridSize):
            if grid[column_][row_] != 0 or get_number_of_walls(column_, row_) < 4:
                continue

            if turn == "A":
                grid[column_][row_] = 1
                screen.blit(A, (column_ * 30 + 4, row_ * 30 + 4))
            elif turn == "B":
                grid[column_][row_] = 2
                screen.blit(B, (column_ * 30 + 4, row_ * 30 + 4))
            elif turn == "X":
                grid[column_][row_] = 3
                screen.blit(X, (column_ * 30 + 4, row_ * 30 + 4))

            to_return += 1

    return to_return


def show():
    """
    Reload the screen
    Use the current grid and cover/flag information to
    update the players screen
    """

    # empty the screen
    screen.fill(0)

    # loop over all slots
    for column in range(gridSize):
        for row in range(gridSize):
            x, y = column * 30, row * 30
            screen.blit(block, (x, y))
            x += 4
            if not upperSet[column][row]:
                screen.blit(lineXempty, (x, y))
            else:
                screen.blit(lineX, (x, y))
            x -= 4
            y += 4
            if not leftSet[column][row]:
                screen.blit(lineYempty, (x, y))
            else:
                screen.blit(lineY, (x, y))

            # calculate x and y in pixels
            x, y = column * 30 + 4, row * 30 + 4

            if grid[column][row] == 0:
                screen.blit(empty, (x, y))
            elif grid[column][row] == 1:
                screen.blit(A, (x,y))
            elif grid[column][row] == 2:
                screen.blit(B, (x,y))
            elif grid[column][row] == 3:
                screen.blit(X, (x,y))

    # set the display caption
    pygame.display.set_caption(caption + turn)

    # update the players screen
    pygame.display.flip()

set_all_slots()
turn = "A"
show()

while True:
    # go through all events and check the types
    for event in pygame.event.get():
        # quit the game when the player closes it
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        # now check for left and right click

        # left click
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:

            # get the current position of the cursor
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]

            # check weather it was an unset wall that was clicked
            wall_x, wall_y = get_wall(x,y)

            if not (wall_x >= 0 and wall_y >= 0):
                continue

            upperWall = wall_y % 30 == 0

            if upperWall:
                if not upperSet[wall_x/30][wall_y/30]:
                    upperSet[wall_x / 30][wall_y / 30] = True
                    screen.blit(lineX, (wall_x, wall_y))
                else:
                    continue
            else:
                if not leftSet[wall_x/30][wall_y/30]:
                    leftSet[wall_x/30][wall_y/30] = True
                    screen.blit(lineY, (wall_x, wall_y))
                else:
                    continue

            if not set_all_slots() > 0:
                if turn == "A":
                    turn = "B"
                elif turn == "B":
                    turn = "A"

            # set the display caption
            pygame.display.set_caption(caption + turn)

            # update the players screen
            pygame.display.flip()


