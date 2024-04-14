from typing import List, Optional
from pathlib import Path

import pygame
import pygame_gui

from tools.undo_record import UndoRecord
from ui.event_types import UI_PAINT_PAINTING_TOOL_CHANGED


class EditableCanvas(pygame_gui.core.ui_element.UIElement):
    def __init__(self, relative_rect,
                 image_surface,
                 manager,
                 container=None,
                 parent=None,
                 object_id=None,
                 anchors=None):

        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         container=container,
                         starting_height=1,
                         layer_thickness=1,
                         anchors=anchors)

        self._create_valid_ids(container=container,
                               parent_element=parent,
                               object_id=object_id,
                               element_id='editable_canvas')

        self.set_image(image_surface)

        self.active_tool = None
        self.save_file_path: Optional[Path] = None

        self.undo_stack: List[Optional[UndoRecord]] = []
        self.redo_stack: List[Optional[UndoRecord]] = []

    def set_save_file_path(self, path):
        self.save_file_path = path

    def set_active_tool(self, tool):
        self.active_tool = tool

    def get_colour_at(self, pos):
        return self.image.get_at(pos)

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False

        if event.type == UI_PAINT_PAINTING_TOOL_CHANGED:
            self.set_active_tool(event.tool)

        if (self.active_tool is not None and
                self.active_tool.process_canvas_event(event,
                                                      self,
                                                      self.ui_manager.get_mouse_position())):
            self.active_tool.active_canvas = self
            consumed_event = True

        return consumed_event

    def update(self, time_delta: float):
        super().update(time_delta)

    def get_image(self) -> pygame.Surface:
        """
        :return: The complete image Surface without any clipping.
        """
        if self.get_image_clipping_rect() is not None:
            return self._pre_clipped_image
        else:
            return self.image

    def set_image(self, new_image: Optional[pygame.surface.Surface]) -> None:
        """

        :param new_image: the new image surface to use in the UIImage element.
        """
        self._set_image(new_image)
