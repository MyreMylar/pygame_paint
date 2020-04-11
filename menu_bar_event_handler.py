from typing import Union
from pathlib import Path

import pygame

from pygame_gui.windows import UIFileDialog, UIMessageWindow
from pygame_gui import UI_BUTTON_START_PRESS, UI_WINDOW_MOVED_TO_FRONT, UI_WINDOW_CLOSE
from pygame_gui import UI_FILE_DIALOG_PATH_PICKED

from ui_canvas_window import CanvasWindow


class MenuBarEventHandler:
    def __init__(self, window_surface, ui_manger):

        self.window_surface = window_surface
        self.ui_manager = ui_manger

        self.last_used_file_path = str(Path('.').absolute())

        self.active_canvas_window = None  # type: Union[CanvasWindow, None]

    def process_event(self, event):
        if (event.type == pygame.USEREVENT
                and event.user_type == UI_WINDOW_MOVED_TO_FRONT
                and event.ui_object_id == '#canvas_window'):
            self.active_canvas_window = event.ui_element
        if (event.type == pygame.USEREVENT
                and event.user_type == UI_WINDOW_CLOSE
                and event.ui_object_id == '#canvas_window'
                and self.active_canvas_window == event.ui_element):
            self.active_canvas_window = None

        if (event.type == pygame.USEREVENT
                and event.user_type == UI_BUTTON_START_PRESS
                and event.ui_object_id == 'menu_bar.#file_menu_items.#open'):
            file_dialog_rect = pygame.Rect(0, 0, 400, 500)
            file_dialog_rect.center = self.window_surface.get_rect().center
            UIFileDialog(rect=file_dialog_rect,
                         manager=self.ui_manager,
                         window_title="Open...",
                         initial_file_path=self.last_used_file_path,
                         object_id='#open_file_dialog',
                         allow_existing_files_only=True)

        if (event.type == pygame.USEREVENT
                and event.user_type == UI_BUTTON_START_PRESS
                and event.ui_object_id == 'menu_bar.#file_menu_items.#save'
                and self.active_canvas_window is not None
                and self.active_canvas_window.canvas_ui.save_file_path is not None):

            try:
                print("Saving to: " + str(self.active_canvas_window.canvas_ui.save_file_path))
                pygame.image.save(self.active_canvas_window.canvas_ui.get_image(),
                                  str(self.active_canvas_window.canvas_ui.save_file_path))
            except pygame.error:
                message_rect = pygame.Rect(0, 0, 250, 160)
                message_rect.center = self.window_surface.get_rect().center
                message_window = UIMessageWindow(rect=message_rect,
                                                 html_message='Unable to save image.',
                                                 manager=self.ui_manager,
                                                 window_title='Saving error')
                message_window.set_blocking(True)

        if (event.type == pygame.USEREVENT
                and event.user_type == UI_BUTTON_START_PRESS
                and event.ui_object_id == 'menu_bar.#file_menu_items.#save_as'
                and self.active_canvas_window is not None):
            file_dialog_rect = pygame.Rect(0, 0, 400, 500)
            file_dialog_rect.center = self.window_surface.get_rect().center
            if self.active_canvas_window.canvas_ui.save_file_path is not None:
                file_path = self.active_canvas_window.canvas_ui.save_file_path
            else:
                file_path = Path(self.last_used_file_path) / self.active_canvas_window.window_display_title
            save_dialog = UIFileDialog(rect=file_dialog_rect,
                                       manager=self.ui_manager,
                                       window_title="Save As...",
                                       initial_file_path=str(file_path),
                                       object_id='#save_file_dialog')
            save_dialog.set_blocking(True)

        if (event.type == pygame.USEREVENT
                and event.user_type == UI_BUTTON_START_PRESS
                and event.ui_object_id == 'menu_bar.#view_menu_items.#info'
                and self.active_canvas_window is not None):
            info_window_rect = pygame.Rect(0, 0, 400, 250)
            info_window_rect.center = self.window_surface.get_rect().center

            file_name = self.active_canvas_window.window_display_title
            pixel_size = (str(self.active_canvas_window.canvas_ui.rect.width) +
                          ' x ' +
                          str(self.active_canvas_window.canvas_ui.rect.height) +
                          ' pixels.')

            UIMessageWindow(rect=info_window_rect,
                            html_message='<br><b>Image Info</b><br>'
                                         '---------------<br><br>'
                                         '<b>File Name: </b>' + file_name + '<br>'
                                         '<b>Pixel size: ' + pixel_size + '<br>',
                            manager=self.ui_manager,
                            window_title='Image info')

        if (event.type == pygame.USEREVENT
                and event.user_type == UI_BUTTON_START_PRESS
                and event.ui_object_id == 'menu_bar.#help_menu_items.#about'):
            about_window_rect = pygame.Rect(0, 0, 400, 250)
            about_window_rect.center = self.window_surface.get_rect().center
            UIMessageWindow(rect=about_window_rect,
                            html_message='<br><b>Pygame Paint</b><br>'
                                         '---------------<br><br>'
                                         '<b>Version: </b>1.0.0<br>'
                                         '<b>Created by: </b>Dan Lawrence<br>'
                                         '<b>Copyright: </b>© 2020, Robotic Shed<br>',
                            manager=self.ui_manager,
                            window_title='About')

        if (event.type == pygame.USEREVENT and
                event.user_type == UI_FILE_DIALOG_PATH_PICKED and
                event.ui_object_id == '#save_file_dialog'):
            path = Path(event.text)
            self.last_used_file_path = path.parent
            try:
                print("Saving to: " + str(path))
                pygame.image.save(self.active_canvas_window.canvas_ui.get_image(),
                                  str(path))
                self.active_canvas_window.set_display_title(path.name)
                self.active_canvas_window.canvas_ui.save_file_path = path
            except pygame.error:
                message_rect = pygame.Rect(0, 0, 250, 160)
                message_rect.center = self.window_surface.get_rect().center
                message_window = UIMessageWindow(rect=message_rect,
                                                 html_message='Unable to save image to path: '
                                                              '<br>' + str(path) + '<br><br>'
                                                              'pygame can only save to .bmp, .png,'
                                                              '.jpg & .tga. TGA is the default '
                                                              'format.',
                                                 manager=self.ui_manager,
                                                 window_title='Saving error')
                message_window.set_blocking(True)
