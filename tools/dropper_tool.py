import pygame

from ui.event_types import UI_PAINT_COLOUR_DROPPER_CHANGED


class DropperTool:

    def __init__(self):

        self.option_data = {}

        self.start_dropper_position = None
        self.time_to_grab_colour = False

        self.active_canvas = None

    def process_canvas_event(self, event, canvas, mouse_pos):
        consumed_event = False
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if canvas.hover_point(mouse_x, mouse_y):
                self.start_dropper_position = mouse_pos
                self.time_to_grab_colour = True
                consumed_event = True

        return consumed_event

    def process_event(self, event):
        return False

    def update(self, time_delta, canvas_surface, canvas_position, canvas):

        if self.time_to_grab_colour:
            self.time_to_grab_colour = False
            self.start_dropper_position = (self.start_dropper_position[0] - canvas_position[0],
                                           self.start_dropper_position[1] - canvas_position[1])

            new_colour = canvas_surface.get_at(self.start_dropper_position)

            pygame.event.post(pygame.event.Event(UI_PAINT_COLOUR_DROPPER_CHANGED,
                                                 {'ui_object_id': '#dropper_tool',
                                                  'ui_element': self,
                                                  'colour': new_colour}))

    def set_option(self, option_id, value):
        if option_id in self.option_data:
            self.option_data[option_id] = value
