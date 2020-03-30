import pygame
import pygame_gui

from pygame_gui.elements import UIHorizontalSlider, UIButton, UILabel

from tools.brush_tool import BrushTool
from tools.fill_tool import FillTool
from tools.dropper_tool import DropperTool


class ToolBarWindow(pygame_gui.elements.UIWindow):
    def __init__(self, rect,
                 manager
                 ):
        super().__init__(rect, manager,
                         window_display_title="Tools",
                         object_id='#tool_bar_window',
                         resizable=True)

        # tool picking buttons
        spacing = 10
        brush_button_rect = pygame.Rect(15, 15, 64, 64)
        self.brush_button = UIButton(brush_button_rect,
                                     text='',
                                     manager=self.ui_manager,
                                     container=self,
                                     object_id='#brush_button',
                                     anchors={'left': 'left',
                                              'right': 'left',
                                              'top': 'top',
                                              'bottom': 'top'})
        fill_button_rect = pygame.Rect(0, 0, 64, 64)
        fill_button_rect.topright = (-15, 15)
        self.fill_button = UIButton(fill_button_rect,
                                    text='',
                                    manager=self.ui_manager,
                                    container=self,
                                    object_id='#fill_button',
                                    anchors={'left': 'right',
                                             'right': 'right',
                                             'top': 'top',
                                             'bottom': 'top'})

        dropper_button_rect = pygame.Rect(15, brush_button_rect.bottom + spacing, 64, 64)
        self.dropper_button = UIButton(dropper_button_rect,
                                       text='',
                                       manager=self.ui_manager,
                                       container=self,
                                       object_id='#dropper_button',
                                       anchors={'left': 'left',
                                                'right': 'left',
                                                'top': 'top',
                                                'bottom': 'top'})

        self.tool_options_ui_dict = {}

        # tool options params
        self.palette_colour = pygame.Color(255,255,255,255)
        self.brush_size = 16
        self.opacity = 255
        self.threshold = 0.3

        # starting tool
        self.active_tool = BrushTool(self.palette_colour, self.opacity, self.brush_size)

        self.palette_button = UIButton(pygame.Rect(52, -264, 64, 64),
                                       text='',
                                       manager=self.ui_manager,
                                       container=self,
                                       anchors={'left': 'left',
                                                'right': 'left',
                                                'top': 'bottom',
                                                'bottom': 'bottom'}
                                       )

        self.palette_button.normal_image = pygame.Surface((58, 58),
                                                          flags=pygame.SRCALPHA,
                                                          depth=32)
        self.palette_button.normal_image.fill(self.palette_colour)
        self.palette_button.hovered_image = self.palette_button.normal_image
        self.palette_button.selected_image = self.palette_button.normal_image
        self.palette_button.rebuild()

        self.refresh_tool_options_ui()

    def set_active_tool(self, tool_name):
        if tool_name == 'brush':
            self.active_tool = BrushTool(self.palette_colour, self.opacity, self.brush_size)
        elif tool_name == 'dropper':
            self.active_tool = DropperTool()
        elif tool_name == 'fill':
            self.active_tool = FillTool(self.palette_colour, self.opacity, self.threshold)

        self.refresh_tool_options_ui()

        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                             {'user_type': 'paint_tool_changed',
                                              'ui_object_id': self.most_specific_combined_id,
                                              'ui_element': self,
                                              'tool': self.active_tool}))

    def refresh_tool_options_ui(self):
        for key, widget in self.tool_options_ui_dict.items():
            widget.kill()
        self.tool_options_ui_dict.clear()

        if self.active_tool is not None:
            current_y = -166
            self.tool_options_ui_dict['opacity_label'] = UILabel(
                pygame.Rect(10, current_y, 148, 20),
                text="Tool Options",
                manager=self.ui_manager,
                container=self,
                object_id='#tool_options_header_label',
                anchors={'left': 'left',
                         'right': 'left',
                         'top': 'bottom',
                         'bottom': 'bottom'})
            current_y += 30
            for option_data in self.active_tool.option_data:
                if option_data == 'opacity':
                    self.tool_options_ui_dict['opacity_label'] = UILabel(pygame.Rect(10, current_y,
                                                                                     148, 20),
                                                                         "Opacity:",
                                                                         manager=self.ui_manager,
                                                                         container=self,
                                                                         anchors={'left': 'left',
                                                                                  'right': 'left',
                                                                                  'top': 'bottom',
                                                                                  'bottom': 'bottom'})
                    current_y += 20
                    self.tool_options_ui_dict['opacity_slider'] = UIHorizontalSlider(
                                                                    pygame.Rect(10, current_y, 148, 20),
                                                                    value_range=(0, 255),
                                                                    start_value=self.opacity,
                                                                    manager=self.ui_manager,
                                                                    container=self,
                                                                    object_id='#opacity_slider',
                                                                    anchors={'left': 'left',
                                                                             'right': 'left',
                                                                             'top': 'bottom',
                                                                             'bottom': 'bottom'})
                    current_y += 25

                elif option_data == 'brush_size':
                    self.tool_options_ui_dict['brush_size_label'] = UILabel(pygame.Rect(10, current_y,
                                                                                     148, 20),
                                                                         "Brush size:",
                                                                         manager=self.ui_manager,
                                                                         container=self,
                                                                         anchors={'left': 'left',
                                                                                  'right': 'left',
                                                                                  'top': 'bottom',
                                                                                  'bottom': 'bottom'})
                    current_y += 20
                    self.tool_options_ui_dict['brush_size'] = UIHorizontalSlider(
                                                                    pygame.Rect(10, current_y, 148, 20),
                                                                    value_range=(1, 100),
                                                                    start_value=self.brush_size,
                                                                    manager=self.ui_manager,
                                                                    container=self,
                                                                    object_id='#brush_size_slider',
                                                                    anchors={'left': 'left',
                                                                             'right': 'left',
                                                                             'top': 'bottom',
                                                                             'bottom': 'bottom'})
                    current_y += 25
                elif option_data == 'threshold':
                    self.tool_options_ui_dict['threshold_label'] = UILabel(
                        pygame.Rect(10, current_y,
                                    148, 20),
                        "Threshold:",
                        manager=self.ui_manager,
                        container=self,
                        anchors={'left': 'left',
                                 'right': 'left',
                                 'top': 'bottom',
                                 'bottom': 'bottom'})
                    current_y += 20
                    self.tool_options_ui_dict['threshold'] = UIHorizontalSlider(
                                                                    pygame.Rect(10, current_y, 148, 20),
                                                                    value_range=(0.0, 1.0),
                                                                    start_value=self.threshold,
                                                                    manager=self.ui_manager,
                                                                    container=self,
                                                                    object_id='#threshold_slider',
                                                                    anchors={'left': 'left',
                                                                             'right': 'left',
                                                                             'top': 'bottom',
                                                                             'bottom': 'bottom'})
                    current_y += 25

    def get_active_tool(self):
        return self.active_tool

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            distance = FillTool.calc_distance_between_colours(pygame.Color(0, 0, 0, 255),
                                                              pygame.Color(255,255,255,255))
            print(distance)

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_object_id == "#tool_bar_window.#brush_button"):
            self.set_active_tool('brush')
        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_object_id == "#tool_bar_window.#fill_button"):
            self.set_active_tool('fill')
        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_object_id == "#tool_bar_window.#dropper_button"):
            self.set_active_tool('dropper')

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element == self.palette_button):
            pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect(100, 300, 390, 390),
                                                    manager=self.ui_manager,
                                                    initial_colour=self.palette_colour)

        if (event.type == pygame.USEREVENT and
                event.user_type == 'colour_dropper_changed'):
            self.palette_colour = event.colour
            self.active_tool.set_option('palette_colour', self.palette_colour)
            self.palette_button.normal_image = pygame.Surface((58, 58),
                                                              flags=pygame.SRCALPHA,
                                                              depth=32)
            self.palette_button.normal_image.fill(self.palette_colour)
            self.palette_button.hovered_image = self.palette_button.normal_image
            self.palette_button.selected_image = self.palette_button.normal_image
            self.palette_button.rebuild()
        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED):
            self.palette_colour = event.colour
            self.active_tool.set_option('palette_colour', self.palette_colour)
            self.palette_button.normal_image = pygame.Surface((58, 58),
                                                              flags=pygame.SRCALPHA,
                                                              depth=32)
            self.palette_button.normal_image.fill(self.palette_colour)
            self.palette_button.hovered_image = self.palette_button.normal_image
            self.palette_button.selected_image = self.palette_button.normal_image
            self.palette_button.rebuild()

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_object_id == '#tool_bar_window.#brush_size_slider'):
            self.brush_size = int(event.value)
            self.active_tool.set_option('brush_size', self.brush_size)

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_object_id == '#tool_bar_window.#opacity_slider'):
            self.opacity = int(event.value)
            self.active_tool.set_option('opacity', self.opacity)

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and
                event.ui_object_id == '#tool_bar_window.#threshold_slider'):
            self.threshold = float(event.value)
            self.active_tool.set_option('threshold', self.threshold)
            print(self.threshold)

        return False  # consumes nothing
