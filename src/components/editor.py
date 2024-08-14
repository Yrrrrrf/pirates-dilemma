import math
import numpy as np
from pygame.math import Vector2 as vector


import sys
import pygame
from dataclasses import dataclass

@dataclass
class Editor:
    """Editor class. This class contains the logic for the GUI"""
    pan_active: bool = False  # if the user is panning
    display_surface: pygame.Surface = pygame.display.get_surface()

    def __init__(self):
        """Initialize the app"""
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.pan_active: bool = False  # if the user is panning
        self.origin: vector = vector(self.display_surface.get_width() // 2, self.display_surface.get_height() // 2)

        # * Editor Grid
        self.grid_size = 72  # size of the grid
        self.support_line_surface = pygame.Surface(self.display_surface.get_size())  # create a surface for the grid
        self.support_line_surface.set_colorkey("green")  # set the colorkey of the surface (the colorkey is the color that is considered transparent)
        self.support_line_surface.set_alpha(32)  # set the transparency of the surface (0 is transparent and 255 is opaque)

    def event_loop(self):
        for event in pygame.event.get():  # get all events
            if event.type == pygame.QUIT:  # if the user closes the window
                pygame.quit()  # quit pygame
                sys.exit()  # exit the program
            self.print_pixel_data(event)  # print the pixel data of the pixel that the user clicked on

    def draw_grid(self):
        """
        Draw the grid on the screen

        The grid moves with the origin of the coordinate system, so it is always centered on the screen
        """
        # update the size of the surface
        columns: int = self.display_surface.get_width() // self.grid_size  # calculate the number of columns
        rows: int = self.display_surface.get_height() // self.grid_size  # calculate the number of rows
        self.support_line_surface.fill("green")  # fill the surface with transparent black

        # draw grid lines (vertical and horizontal)
        origin_offset: vector = vector(self.origin.x % self.grid_size, self.origin.y % self.grid_size)  # calculate the offset between the origin and the top left corner of the screen
        [pygame.draw.line(self.support_line_surface, (0, 0, 0), (self.grid_size * column + origin_offset.x, 0), (self.grid_size * column + origin_offset.x, self.display_surface.get_height())) for column in range(columns + 1)]
        [pygame.draw.line(self.support_line_surface, (0, 0, 0), (0, self.grid_size * row + origin_offset.y), (self.display_surface.get_width(), self.grid_size * row + origin_offset.y)) for row in range(rows + 1)]
        self.display_surface.blit(self.support_line_surface, (0, 0))  # draw the grid on the screen

    def draw_axes_lines(self, colored: bool = False):
        """Draw the axes of the coordinate system"""
        pygame.draw.line(self.support_line_surface, (0, 0, 255 if colored else 0), (self.origin.x, 0), (self.origin.x, self.display_surface.get_height()), 2)
        pygame.draw.line(self.support_line_surface, (255 if colored else 0, 0, 0), (0, self.origin.y), (self.display_surface.get_width(), self.origin.y), 2)

        self.display_surface.blit(self.support_line_surface, (0, 0))  # draw the grid on the screen

    def draw_numbers_on_grid(self):
        """Draw the numbers on the grid"""
        columns: int = self.display_surface.get_width() // self.grid_size  # calculate the number of columns
        rows: int = self.display_surface.get_height() // self.grid_size  # calculate the number of rows
        origin_offset: vector = vector(self.origin.x % self.grid_size, self.origin.y % self.grid_size)  # calculate the offset between the origin and the top left corner of the screen

        x_align = self.origin.x - 20
        y_align = self.origin.y + 4

        # * draw X axis coordinates (red)
        [self.support_line_surface.blit(pygame.font.SysFont("Consolas", 16).render(
            str(int((self.grid_size * column + origin_offset.x - self.origin.x) // self.grid_size)), True, (255, 0, 0)),
            (self.grid_size * column + origin_offset.x - 20, y_align)
        ) for column in range(columns + 1)]

        # * draw Y axis coordinates (blue)
        [self.support_line_surface.blit(pygame.font.SysFont("Consolas", 16).render(
            str(int((self.grid_size * row + origin_offset.y - self.origin.y) // self.grid_size * -1)), True, (0, 0, 255)),
            (x_align, self.grid_size * row + origin_offset.y + 4)
        ) for row in range(rows + 1, -1, -1)]

        self.support_line_surface.blit(pygame.font.SysFont("Consolas", 16).render("0",True, (0, 0, 0)), (x_align, y_align))  # draw the origin
        self.display_surface.blit(self.support_line_surface, (0, 0))  # draw the grid on the screen

    def print_pixel_data(self, event: pygame.event.Event):
        """
        Get the pixel data of the pixel that the user clicked on only when the user clicks the left mouse button
        """
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:  # check if the left mouse button is pressed
            colors = self.display_surface.get_at(pygame.mouse.get_pos())
            print(f"{pygame.mouse.get_pos()[0] - self.origin.x:4.0f}x, {pygame.mouse.get_pos()[1] - self.origin.y:4.0f}y = RGBA: (\033[91m{colors[0]:3}\033[0m, \033[92m{colors[1]:3}\033[0m, \033[94m{colors[2]:3}\033[0m, \033[97m{colors[3]:3}\033[0m)")

    def run(self, dt: float) -> None:
        """
        Initialize the Editor (GUI)

        ### Parameters:
            dt (float): time in seconds since the last tick
        """
        self.event_loop()  # handle events

        # self.display_surface.fill('white')  # fill the screen with white
        self.display_surface.fill((220, 220, 220))  # fill the screen with white
        self.draw_grid()  # draw grid
        self.draw_axes_lines(colored=True)  # draw axes
        self.draw_numbers_on_grid()  # draw numbers on grid
