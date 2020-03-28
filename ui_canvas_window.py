import pygame
import pygame_gui

from ui_editable_canvas import EditableCanvas


class CanvasWindow(pygame_gui.elements.UIWindow):
    def __init__(self, rect,
                 manager,
                 image_file_name,
                 image):
        super().__init__(rect, manager,
                         window_display_title=image_file_name,
                         resizable=True)

        self.canvas_ui = EditableCanvas(relative_rect=pygame.Rect((10, 10),
                                        image.get_size()),
                                        image_surface=image,
                                        manager=manager,
                                        container=self)
