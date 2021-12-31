import pygame

from pygame_gui.elements import UIWindow, UILabel, UITextEntryLine, UIButton
from pygame_gui import UI_BUTTON_PRESSED, UI_TEXT_ENTRY_FINISHED, UI_TEXT_ENTRY_CHANGED

from ui.event_types import UI_PAINT_CREATE_NEW_CANVAS


class UINewCanvasDialog(UIWindow):
    def __init__(self, rect,
                 manager):
        super().__init__(rect, manager,
                         window_display_title='Create a New Image',
                         object_id='#new_canvas_dialog',
                         resizable=False)

        UILabel(relative_rect=pygame.Rect(10, 20, 80, 30),
                text='Image Size',
                manager=self.ui_manager,
                container=self,
                object_id='#small_header_label')

        UILabel(relative_rect=pygame.Rect(20, 60, 56, 30),
                text='Width:',
                manager=self.ui_manager,
                container=self)

        UILabel(relative_rect=pygame.Rect(20, 100, 56, 30),
                text='Height:',
                manager=self.ui_manager,
                container=self)

        initial_width = 640
        initial_height = 400

        self.current_colour = pygame.Color(255, 255, 255)
        self.max_width = 4096
        self.max_height = 4096

        self.width_entry = UITextEntryLine(relative_rect=pygame.Rect(86, 60, 50, 30),
                                           manager=self.ui_manager,
                                           container=self)

        self.width_entry.set_allowed_characters('numbers')
        self.width_entry.set_text(str(initial_width))
        self.width_entry.set_text_length_limit(4)

        self.height_entry = UITextEntryLine(relative_rect=pygame.Rect(86, 100, 50, 30),
                                            manager=self.ui_manager,
                                            container=self)

        self.height_entry.set_allowed_characters('numbers')
        self.height_entry.set_text(str(initial_height))
        self.height_entry.set_text_length_limit(4)

        self.ok_button = UIButton(relative_rect=pygame.Rect(-220, -40, 100, 30),
                                  text='OK',
                                  manager=self.ui_manager,
                                  container=self,
                                  object_id='#ok_button',
                                  anchors={'left': 'right',
                                           'right': 'right',
                                           'top': 'bottom',
                                           'bottom': 'bottom'})

        self.cancel_button = UIButton(relative_rect=pygame.Rect(-110, -40, 100, 30),
                                      text='Cancel',
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id='#cancel_button',
                                      anchors={'left': 'right',
                                               'right': 'right',
                                               'top': 'bottom',
                                               'bottom': 'bottom'})

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = super().process_event(event)
        if (event.type == UI_BUTTON_PRESSED and
                event.ui_element == self.cancel_button):
            self.kill()

        if (event.type == UI_BUTTON_PRESSED and
                event.ui_element == self.ok_button):
            event_data = {'colour': self.current_colour,
                          'size': (min(int(self.width_entry.get_text()), self.max_width),
                                   min(int(self.height_entry.get_text()), self.max_height)),
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            new_canvas_event = pygame.event.Event(UI_PAINT_CREATE_NEW_CANVAS, event_data)
            pygame.event.post(new_canvas_event)
            self.kill()

        if event.type == UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.width_entry:
                try:
                    int_value = int(self.width_entry.get_text())
                except ValueError:
                    int_value = 0
                    self.width_entry.set_text(str(int_value))

                if int_value > self.max_width:
                    self.width_entry.set_text(str(self.max_width))

            elif event.ui_element == self.height_entry:
                try:
                    int_value = int(self.height_entry.get_text())
                except ValueError:
                    int_value = 0
                    self.height_entry.set_text(str(int_value))

                if int_value > self.max_height:
                    self.height_entry.set_text(str(self.max_height))

        if event.type == UI_TEXT_ENTRY_CHANGED:
            try:
                int(event.ui_element.get_text())
            except ValueError:
                event.ui_element.set_text(str(0))

        return consumed_event
