from typing import Union, Dict, Tuple

import pygame
import pygame_gui

from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_selection_list import UISelectionList


class UIMenuBar(UIElement):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 menu_item_data,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent: Union[UIElement, None] = None,
                 object_id: Union[str, None] = None,
                 anchors: Union[Dict[str, str], None] = None):

        element_ids, object_ids = self.create_valid_ids(container=container,
                                                        parent_element=parent,
                                                        object_id=object_id,
                                                        element_id='menu_bar')
        super().__init__(relative_rect=relative_rect,
                         manager=manager,
                         container=container,
                         starting_height=1,
                         layer_thickness=1,
                         object_ids=object_ids,
                         element_ids=element_ids,
                         anchors=anchors)

        self.menu_item_data = menu_item_data

        self.background_colour = None
        self.border_colour = None
        self.shape_type = 'rectangle'

        self.open_menu = None
        self._selected_menu_bar_button = None

        self.rebuild_from_changed_theme_data()

        container_rect = pygame.Rect(self.relative_rect.left +
                                     (self.shadow_width + self.border_width),
                                     self.relative_rect.top +
                                     (self.shadow_width + self.border_width),
                                     self.relative_rect.width -
                                     2 * (self.shadow_width + self.border_width),
                                     self.relative_rect.height -
                                     2 * (self.shadow_width + self.border_width))

        self.menu_bar_container = UIContainer(container_rect, manager,
                                              starting_height=1,
                                              parent_element=self,
                                              object_id='#menu_bar_container')

        top_level_button_x = 0
        for menu_item_key, menu_item_data in self.menu_item_data.items():
            # create top level menu buttons
            default_font = self.ui_manager.get_theme().get_font_dictionary().get_default_font()
            item_text_size = default_font.size(menu_item_data['display_name'])
            UIButton(pygame.Rect(top_level_button_x,
                                 0,
                                 item_text_size[0]+10,
                                 self.menu_bar_container.rect.height),
                     text=menu_item_data['display_name'],
                     manager=self.ui_manager,
                     container=self.menu_bar_container,
                     object_id=menu_item_key,
                     parent_element=self)
            top_level_button_x += item_text_size[0]+10

    def unfocus(self):
        if self.open_menu is not None:
            self.open_menu.kill()
            self.open_menu = None
        if self._selected_menu_bar_button is not None:
            self._selected_menu_bar_button.unselect()
            self._selected_menu_bar_button = None

    def update(self, time_delta: float):
        """
        A method called every update cycle of our application. Designed to be overridden by derived
        classes but also has a little functionality to make sure the menu's layer 'thickness' is
        accurate and to handle window resizing.

        :param time_delta: time passed in seconds between one call to this method and the next.

        """
        super().update(time_delta)
        if self.menu_bar_container.layer_thickness != self.layer_thickness:
            self.layer_thickness = self.menu_bar_container.layer_thickness

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Can be overridden, also handle resizing windows. Gives UI Windows access to pygame events.
        Currently just blocks mouse click down events from passing through the menu.

        :param event: The event to process.

        :return: Should return True if this element consumes this event.

        """
        consumed_event = False
        if (self is not None and
                event.type == pygame.MOUSEBUTTONDOWN and
                event.button in [pygame.BUTTON_LEFT,
                                 pygame.BUTTON_RIGHT,
                                 pygame.BUTTON_MIDDLE]):
            scaled_mouse_pos = (int(event.pos[0] * self.ui_manager.mouse_pos_scale_factor[0]),
                                int(event.pos[1] * self.ui_manager.mouse_pos_scale_factor[1]))

            if self.hover_point(scaled_mouse_pos[0], scaled_mouse_pos[1]):
                consumed_event = True
            # else:
            #     self.unfocus()

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_element in self.menu_bar_container.elements):
            if self._selected_menu_bar_button is not None:
                self._selected_menu_bar_button.unselect()
            self._selected_menu_bar_button = event.ui_element
            self._selected_menu_bar_button.select()
            self._open_top_level_menu(event)

        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED and
                self.open_menu is not None and
                event.ui_element in self.menu_bar_container.elements):
            if self._selected_menu_bar_button is not None:
                self._selected_menu_bar_button.unselect()
            self._selected_menu_bar_button = event.ui_element
            self._selected_menu_bar_button.select()
            self._open_top_level_menu(event)

        return consumed_event

    def _open_top_level_menu(self, event):
        # kill any open menus
        if self.open_menu is not None:
            self.open_menu.kill()
        # open this menu
        menu_key = event.ui_object_id.split('.')[-1]
        menu_size = ((len(self.menu_item_data[menu_key]['items']) * 20) +
                     (2 * (0 + 1)))
        item_data = [
            (item_data['display_name'], item_key)
            for item_key, item_data in self.menu_item_data[menu_key][
                'items'
            ].items()
        ]
        menu_rect = pygame.Rect(0, 0, 200, menu_size)
        menu_rect.topleft = event.ui_element.rect.bottomleft
        top_ui_layer = self.ui_manager.get_sprite_group().get_top_layer()
        self.open_menu = UISelectionList(relative_rect=menu_rect,
                                         item_list=item_data,
                                         manager=self.ui_manager,
                                         starting_height=top_ui_layer,
                                         parent_element=self,
                                         object_id='#menu_bar_selection_list')
        self.ui_manager.set_focus_element(self)

    def kill(self):
        """
        Overrides the basic kill() method of a pygame sprite so that we also kill all the UI
        elements in this menu.

        """
        self.menu_bar_container.kill()
        super().kill()

    def set_dimensions(self, dimensions: Union[pygame.math.Vector2,
                                               Tuple[int, int],
                                               Tuple[float, float]]):
        """
        Set the size of this menu and then re-sizes and shifts the contents of the menu container
        to fit the new size.

        :param dimensions: The new dimensions to set.

        """
        # Don't use a basic gate on this set dimensions method because the container may be a
        # different size to the window
        super().set_dimensions(dimensions)

        new_container_dimensions = (self.relative_rect.width -
                                    2 * (self.shadow_width + self.border_width),
                                    self.relative_rect.height -
                                    2 * (self.shadow_width + self.border_width))
        if new_container_dimensions != self.menu_bar_container.relative_rect.size:
            container_rel_pos = (self.relative_rect.x + (self.shadow_width + self.border_width),
                                 self.relative_rect.y + (self.shadow_width + self.border_width))
            self.menu_bar_container.set_dimensions(new_container_dimensions)
            self.menu_bar_container.set_relative_position(container_rel_pos)

    def set_relative_position(self, position: Union[pygame.math.Vector2,
                                                    Tuple[int, int],
                                                    Tuple[float, float]]):
        """
        Method to directly set the relative rect position of an element.

        :param position: The new position to set.

        """
        super().set_relative_position(position)
        container_rel_pos = (self.relative_rect.x + (self.shadow_width + self.border_width),
                             self.relative_rect.y + (self.shadow_width + self.border_width))
        self.menu_bar_container.set_relative_position(container_rel_pos)

    def set_position(self, position: Union[pygame.math.Vector2,
                                           Tuple[int, int],
                                           Tuple[float, float]]):
        """
        Method to directly set the absolute screen rect position of an element.

        :param position: The new position to set.

        """
        super().set_position(position)
        container_rel_pos = (self.relative_rect.x + (self.shadow_width + self.border_width),
                             self.relative_rect.y + (self.shadow_width + self.border_width))
        self.menu_bar_container.set_relative_position(container_rel_pos)

    def rebuild_from_changed_theme_data(self):
        """
        Checks if any theming parameters have changed, and if so triggers a full rebuild of the
        button's drawable shape.
        """
        has_any_changed = False

        background_colour = self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                                 self.element_ids,
                                                                 'normal_bg')
        if background_colour != self.background_colour:
            self.background_colour = background_colour
            has_any_changed = True

        border_colour = self.ui_theme.get_colour_or_gradient(self.object_ids,
                                                             self.element_ids,
                                                             'normal_border')
        if border_colour != self.border_colour:
            self.border_colour = border_colour
            has_any_changed = True

        # misc
        shape_type_string = self.ui_theme.get_misc_data(self.object_ids, self.element_ids, 'shape')
        if (shape_type_string is not None and shape_type_string in ['rectangle'] and
                shape_type_string != self.shape_type):
            self.shape_type = shape_type_string
            has_any_changed = True

        if self._check_shape_theming_changed(defaults={'border_width': 1,
                                                       'shadow_width': 0,
                                                       'shape_corner_radius': 0}):
            has_any_changed = True

        if has_any_changed:
            self.rebuild()

    def rebuild(self):
        """
        A complete rebuild of the drawable shape used by this button.

        """
        theming_parameters = {'normal_bg': self.background_colour,
                              'normal_border': self.border_colour,
                              'border_width': self.border_width,
                              'shadow_width': self.shadow_width}

        if self.shape_type == 'rectangle':
            self.drawable_shape = RectDrawableShape(self.rect, theming_parameters,
                                                    ['normal'], self.ui_manager)

        self.on_fresh_drawable_shape_ready()
