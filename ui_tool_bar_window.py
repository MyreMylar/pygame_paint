import pygame
import pygame_gui

from pygame_gui.elements import UIHorizontalSlider, UIButton

from tools.brush_tool import BrushTool


class ToolBarWindow(pygame_gui.elements.UIWindow):
    def __init__(self, rect,
                 manager
                 ):
        super().__init__(rect, manager,
                         window_display_title="Tools",
                         resizable=True)

        self.active_tool = BrushTool()

        # tool bar window stuff
        self.palette_button = UIButton(pygame.Rect(52, -96, 64, 64),
                                       text='',
                                       manager=self.ui_manager,
                                       container=self,
                                       anchors={'left': 'left',
                                                'right': 'left',
                                                'top': 'bottom',
                                                'bottom': 'bottom'}
                                       )

        self.palette_button.normal_image = pygame.Surface((58, 58), flags=pygame.SRCALPHA, depth=32)
        self.palette_button.normal_image.fill(self.active_tool.colour)
        self.palette_button.hovered_image = self.palette_button.normal_image
        self.palette_button.selected_image = self.palette_button.normal_image
        self.palette_button.rebuild()

        # brush size slider
        self.brush_size_slider = UIHorizontalSlider(
            pygame.Rect(10, -136, 148, 20),
            value_range=(1, 100),
            start_value=16,
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left',
                     'right': 'left',
                     'top': 'bottom',
                     'bottom': 'bottom'})

        # brush opacity slider
        self.brush_opacity_slider = UIHorizontalSlider(
            pygame.Rect(10, -166, 148, 20),
            value_range=(0, 255),
            start_value=255,
            manager=self.ui_manager,
            container=self,
            anchors={'left': 'left',
                     'right': 'left',
                     'top': 'bottom',
                     'bottom': 'bottom'}
        )

    def get_active_tool(self):
        return self.active_tool

    def process_event(self, event: pygame.event.Event) -> bool:
        consumed_event = False

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == self.palette_button):
            pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect(100, 300, 390, 390),
                                                    manager=self.ui_manager,
                                                    initial_colour=self.active_tool.colour)

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED):
            self.active_tool.set_colour(event.colour)
            self.palette_button.normal_image = pygame.Surface((58, 58),
                                                              flags=pygame.SRCALPHA,
                                                              depth=32)
            self.palette_button.normal_image.fill(self.active_tool.colour)
            self.palette_button.hovered_image = self.palette_button.normal_image
            self.palette_button.selected_image = self.palette_button.normal_image
            self.palette_button.rebuild()

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_element == self.brush_size_slider):
            self.active_tool.set_size(int(event.value))

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_element == self.brush_opacity_slider):
            self.active_tool.set_opacity(int(event.value))

        return consumed_event
