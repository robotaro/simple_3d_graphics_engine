import pygame
import pygame_gui
import tkinter as tk
from tkinter import filedialog
import os

# Initialize pygame
pygame.init()

# Set up the screen dimensions and create a screen object
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption("Pygame GUI Example with Image Loader")

# Create a UIManager
ui_manager = pygame_gui.UIManager((screen_width, screen_height))

# Create a button to load an image
load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                           text='Load Image',
                                           manager=ui_manager)

# Clock to control the frame rate
clock = pygame.time.Clock()

# Image surface
image_surface = None

# Main loop flag
is_running = True


def load_image():
    global image_surface
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename()
    if file_path:
        image_surface = pygame.image.load(file_path).convert()
        # Optionally, resize the image to fit the screen or a specific area
        image_surface = pygame.transform.scale(image_surface, (200, 200))


while is_running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == load_button:
                load_image()

        ui_manager.process_events(event)

    screen.fill((0, 0, 0))

    # Display the image if it has been loaded
    if image_surface:
        screen.blit(image_surface, (300, 200))

    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
