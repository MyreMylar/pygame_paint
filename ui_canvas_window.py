import pygame
import pygame_gui

from ui_editable_canvas import EditableCanvas
from pygame_gui.elements.ui_scrolling_container import UIScrollingContainer


class CanvasWindow(pygame_gui.elements.UIWindow):
    def __init__(self, rect,
                 manager,
                 image_file_name,
                 image):
        super().__init__(rect, manager,
                         window_display_title=image_file_name,
                         object_id='#canvas_window',
                         resizable=True)

        container_rect = pygame.Rect((0, 0),
                                     self.get_container().get_size())
        self.scrolling_container = UIScrollingContainer(relative_rect=container_rect,
                                                        manager=self.ui_manager,
                                                        container=self,
                                                        anchors={'left': 'left',
                                                                 'right': 'right',
                                                                 'top': 'top',
                                                                 'bottom': 'bottom'})

        self.scrolling_container.set_scrollable_area_dimensions((image.get_width() + 20,
                                                                 image.get_height() + 20))

        self.canvas_ui = EditableCanvas(relative_rect=pygame.Rect((10, 10),
                                                                  (image.get_width(),
                                                                   image.get_height())),
                                        image_surface=image,
                                        manager=manager,
                                        container=self.scrolling_container,
                                        anchors={'left': 'left',
                                                 'right': 'left',
                                                 'top': 'top',
                                                 'bottom': 'top'})
