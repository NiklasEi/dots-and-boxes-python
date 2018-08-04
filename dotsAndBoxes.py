import pygame
import numpy as np
import sys


class Game:
    def __init__(self):
        self.grid_size = 10  # default
        if len(sys.argv) > 1:
            self.grid_size = int(sys.argv[1])

        # It turns out that there are nice structures when setting ~0.75 walls per slot
        self.start_walls = int(0.75 * self.grid_size ** 2)

        self.accept_clicks = True

        # variables for the boxes for each player (x would be computer)
        self.a_boxes = 0
        self.b_boxes = 0
        self.x_boxes = 0

        self.turn = "X"
        self.caption = "'s turn    "

        # 0 empty 1 is A 2 is B and 3 is X
        self.grid_status = np.zeros((self.grid_size, self.grid_size), np.int)
        self.upper_walls_set_flags = np.zeros((self.grid_size, self.grid_size), np.dtype(bool))
        self.left_walls_set_flags = np.zeros((self.grid_size, self.grid_size), np.dtype(bool))

        # set the outer walls
        for column in range(self.grid_size):
            for row in range(self.grid_size):
                if column == 0:
                    self.left_walls_set_flags[column][row] = True
                if row == 0:
                    self.upper_walls_set_flags[column][row] = True

        # initialize pygame
        pygame.init()

        # set the display size (one slot has 30x30 pixels; Walls: 4x26 Box: 26x26)
        self.screen = pygame.display.set_mode([30 * self.grid_size + 4, 30 * self.grid_size + 4])

        # load all images
        self.empty = pygame.image.load("pics/empty.png")
        self.A = pygame.image.load("pics/A.png")
        self.B = pygame.image.load("pics/B.png")
        self.X = pygame.image.load("pics/X.png")
        self.block = pygame.image.load("pics/block.png")
        self.lineX = pygame.image.load("pics/lineX.png")
        self.lineXempty = pygame.image.load("pics/lineXempty.png")
        self.lineY = pygame.image.load("pics/lineY.png")
        self.lineYempty = pygame.image.load("pics/lineYempty.png")

        tries = 0
        # set the start walls randomly but do not create any opportunity to directly close boxes
        while self.start_walls > 0 and tries < 4*self.grid_size**2:
            x = np.random.randint(self.grid_size)
            y = np.random.randint(self.grid_size)
            up = np.random.randint(2)

            if up:
                if not self.upper_walls_set_flags[x][y] \
                        and self.get_number_of_walls(x, y) < 2 \
                        and self.get_number_of_walls(x, y - 1) < 2:
                    self.upper_walls_set_flags[x][y] = True
                    self.start_walls -= 1
            else:
                if not self.left_walls_set_flags[x][y] \
                        and self.get_number_of_walls(x, y) < 2 \
                        and self.get_number_of_walls(x - 1, y) < 2:
                    self.left_walls_set_flags[x][y] = True
                    self.start_walls -= 1

            tries += 1

        # now it's the first players turn
        self.turn = "A"
        self.show()

        while True:
            # go through all events and check the types
            for event in pygame.event.get():
                # quit the game when the player closes it
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)

                # left click
                elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                    if not self.accept_clicks:
                        continue

                    # get the current position of the cursor
                    x = pygame.mouse.get_pos()[0]
                    y = pygame.mouse.get_pos()[1]

                    # check whether it was a not set wall that was clicked
                    wall_x, wall_y = self.get_wall(x, y)

                    if not (wall_x >= 0 and wall_y >= 0):
                        continue

                    upper_wall = wall_y % 30 == 0

                    if upper_wall:
                        if not self.upper_walls_set_flags[wall_x//30][wall_y//30]:
                            self.upper_walls_set_flags[wall_x//30][wall_y//30] = True
                            self.screen.blit(self.lineX, (wall_x, wall_y))
                        else:
                            continue
                    else:
                        if not self.left_walls_set_flags[wall_x//30][wall_y//30]:
                            self.left_walls_set_flags[wall_x//30][wall_y//30] = True
                            self.screen.blit(self.lineY, (wall_x, wall_y))
                        else:
                            continue

                    if not self.set_all_slots() > 0:
                        if self.turn == "A":
                            self.turn = "B"
                        elif self.turn == "B":
                            self.turn = "A"

                    if self.won():
                        self.accept_clicks = False

                    else:

                        # set the display caption
                        pygame.display.set_caption(self.turn + self.caption + "     A:" + str(
                            self.a_boxes) + "   B:" + str(self.b_boxes))

                        # update the players screen
                        pygame.display.flip()

    def get_number_of_walls(self, slot_column, slot_row):
        """
        Get the number of set walls around the passed slot
        :param slot_column: x of the slot
        :param slot_row: y of the slot
        :return: number of set walls
        """
        number_of_walls = 0

        if slot_column == self.grid_size - 1:
            number_of_walls += 1
        elif self.left_walls_set_flags[slot_column + 1][slot_row]:
            number_of_walls += 1

        if slot_row == self.grid_size - 1:
            number_of_walls += 1
        elif self.upper_walls_set_flags[slot_column][slot_row + 1]:
            number_of_walls += 1

        if self.left_walls_set_flags[slot_column][slot_row]:
            number_of_walls += 1

        if self.upper_walls_set_flags[slot_column][slot_row]:
            number_of_walls += 1

        return number_of_walls

    @staticmethod
    def get_wall(pos_x, pos_y):
        rest_x = pos_x % 30
        rest_y = pos_y % 30

        wall_slot_x = pos_x//30
        wall_slot_y = pos_y//30

        # in a corner
        if rest_x < 4 and rest_y < 4:
            return -1, -1

        if rest_x < 4:
            # is left wall of the slot
            return wall_slot_x*30, wall_slot_y*30 + 4

        if rest_y < 4:
            # is upper wall of the slot
            return wall_slot_x*30 + 4, wall_slot_y*30

        # inside the box => not a wall
        return -1, -1

    def set_all_slots(self):
        """
        Find all newly closed boxes and close them for the current player
        :return: number of closed boxes
        """
        to_return = 0

        for column_ in range(self.grid_size):
            for row_ in range(self.grid_size):
                if self.grid_status[column_][row_] != 0 or self.get_number_of_walls(column_, row_) < 4:
                    continue

                if self.turn == "A":
                    self.grid_status[column_][row_] = 1
                    self.screen.blit(self.A, (column_ * 30 + 4, row_ * 30 + 4))
                    self.a_boxes += 1
                elif self.turn == "B":
                    self.grid_status[column_][row_] = 2
                    self.screen.blit(self.B, (column_ * 30 + 4, row_ * 30 + 4))
                    self.b_boxes += 1
                elif self.turn == "X":
                    self.grid_status[column_][row_] = 3
                    self.screen.blit(self.X, (column_ * 30 + 4, row_ * 30 + 4))
                    self.x_boxes += 1

                to_return += 1

        return to_return

    def won(self):
        """
        Check whether the game was finished
        If so change the caption to display the winner
        :return: won or not
        """
        if self.a_boxes + self.b_boxes + self.x_boxes == self.grid_size ** 2:
            if self.a_boxes < self.b_boxes:
                won_caption = "Player B won!   Congrats"
            elif self.b_boxes < self.a_boxes:
                won_caption = "Player A won!   Congrats"
            else:
                won_caption = "It's a tie!"

            # set the display caption
            pygame.display.set_caption(won_caption)

            # update the players screen
            pygame.display.flip()

            return True
        else:
            return False

    def show(self):
        """
        Reload the screen
        Use the current grid and wall information to
        update the players screen
        """
        self.screen.fill(0)

        # loop over all slots
        for column in range(self.grid_size):
            for row in range(self.grid_size):
                x, y = column * 30, row * 30
                self.screen.blit(self.block, (x, y))
                x += 4
                if not self.upper_walls_set_flags[column][row]:
                    self.screen.blit(self.lineXempty, (x, y))
                else:
                    self.screen.blit(self.lineX, (x, y))
                x -= 4
                y += 4
                if not self.left_walls_set_flags[column][row]:
                    self.screen.blit(self.lineYempty, (x, y))
                else:
                    self.screen.blit(self.lineY, (x, y))

                # calculate x and y in pixels
                x, y = column * 30 + 4, row * 30 + 4

                if self.grid_status[column][row] == 0:
                    self.screen.blit(self.empty, (x, y))
                elif self.grid_status[column][row] == 1:
                    self.screen.blit(self.A, (x, y))
                elif self.grid_status[column][row] == 2:
                    self.screen.blit(self.B, (x, y))
                elif self.grid_status[column][row] == 3:
                    self.screen.blit(self.X, (x, y))

        pygame.display.set_caption(self.turn + self.caption + "     A:" + str(self.a_boxes) + "   B:" + str(
            self.b_boxes))
        pygame.display.flip()


game = Game()  # start a game
