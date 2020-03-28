import pygame
import pygame_gui


class EditableCanvas(pygame_gui.core.ui_element.UIElement):
    def __init__(self, relative_rect,
                 image_surface,
                 manager,
                 container=None,
                 parent=None,
                 object_id=None,
                 anchors=None):

        element_ids, object_ids = self.create_valid_ids(container=container,
                                                        parent_element=parent,
                                                        object_id=object_id,
                                                        element_id='editable_canvas')
        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         container=container,
                         starting_height=1,
                         layer_thickness=1,
                         object_ids=object_ids,
                         element_ids=element_ids,
                         anchors=anchors)

        self.image = image_surface

        self.active_tool = None

    def set_active_tool(self, tool):
        self.active_tool = tool

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False

        if (self.active_tool is not None and
                self.active_tool.process_event(event,
                                               self,
                                               self.ui_manager.get_mouse_position())):
            consumed_event = True

        return consumed_event

    def update(self, time_delta: float):
        super().update(time_delta)
        self.active_tool.update(time_delta=time_delta,
                                canvas_surface=self.image,
                                canvas_position=self.rect.topleft)
        #self.active_tool.draw(self.image, self.rect.topleft)