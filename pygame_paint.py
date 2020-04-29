from pathlib import Path

import pygame
import pygame_gui

from pygame_gui import UIManager
from pygame_gui.windows import UIMessageWindow

from ui.ui_canvas_window import CanvasWindow
from ui.ui_tool_bar_window import ToolBarWindow
from ui.ui_menu_bar import UIMenuBar

from menu_bar_event_handler import MenuBarEventHandler


class PygamePaintApp:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Pygame Paint")
        window_dimensions = (1024, 576)
        self.window_surface = pygame.display.set_mode(window_dimensions)
        title_bar_icon = pygame.image.load('data/paint_icon.png')
        pygame.display.set_icon(title_bar_icon)

        self.window_background = pygame.Surface(window_dimensions, depth=32)
        self.window_background.fill(pygame.Color(50, 50, 50))

        self.ui_manager = UIManager(window_dimensions, theme_path='data/ui_theme.json')

        menu_data = {'#file_menu': {'display_name': 'File',
                                    'items':
                                        {
                                            '#new': {'display_name': 'New...'},
                                            '#open': {'display_name': 'Open...'},
                                            '#save': {'display_name': 'Save'},
                                            '#save_as': {'display_name': 'Save As...'}
                                        }
                                    },
                     '#edit_menu': {'display_name': 'Edit',
                                    'items':
                                        {
                                            '#undo': {'display_name': 'Undo'},
                                            '#redo': {'display_name': 'Redo'}
                                        }
                                    },
                     '#view_menu': {'display_name': 'View',
                                    'items':
                                        {
                                            '#info': {'display_name': 'Image info'}
                                        }
                                    },
                     '#help_menu': {'display_name': 'Help',
                                    'items':
                                        {
                                            '#about': {'display_name': 'About'}
                                        }
                                    }
                     }
        self.menu_bar = UIMenuBar(relative_rect=pygame.Rect(0, 0, 1280, 25),
                                  menu_item_data=menu_data,
                                  manager=self.ui_manager)

        self.menu_bar_event_handler = MenuBarEventHandler(self.window_surface, self.ui_manager)

        self.tool_bar_window = ToolBarWindow(pygame.Rect(0, 25, 200, 695),
                                             manager=self.ui_manager)

        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.menu_bar_event_handler.process_event(event)

                if (event.type == pygame.USEREVENT and
                        event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED and
                        event.ui_object_id == '#open_file_dialog'):
                    path = Path(event.text)
                    self.menu_bar_event_handler.last_used_file_path = path.parent
                    try:
                        loaded_image = pygame.image.load(str(path)).convert_alpha()

                        canvas_window_rect = pygame.Rect(200, 25,
                                                         min(loaded_image.get_width() + 52,
                                                             self.window_surface.get_width() - 200),
                                                         min(loaded_image.get_height() + 82,
                                                             self.window_surface.get_height() - 25))

                        window = CanvasWindow(rect=canvas_window_rect,
                                              manager=self.ui_manager,
                                              image_file_name=path.name,
                                              image=loaded_image)

                        window.canvas_ui.set_active_tool(self.tool_bar_window.get_active_tool())
                        window.canvas_ui.set_save_file_path(path)

                    except pygame.error:
                        message_rect = pygame.Rect(0, 0, 250, 160)
                        message_rect.center = self.window_surface.get_rect().center
                        message_window = UIMessageWindow(rect=message_rect,
                                                         html_message='Unable to load image.',
                                                         manager=self.ui_manager,
                                                         window_title='Loading error')
                        message_window.set_blocking(True)

                if event.type == pygame.USEREVENT and event.user_type == 'create_new_canvas':

                    new_canvas = pygame.Surface(event.size, flags=pygame.SRCALPHA, depth=32)
                    new_canvas.fill(event.colour)
                    canvas_window_rect = pygame.Rect(200, 25,
                                                     min(new_canvas.get_width() + 52,
                                                         self.window_surface.get_width() - 200),
                                                     min(new_canvas.get_height() + 82,
                                                         self.window_surface.get_height() - 25))
                    canvas_window = CanvasWindow(rect=canvas_window_rect,
                                                 manager=self.ui_manager,
                                                 image_file_name='untitled.png',
                                                 image=new_canvas)

                    canvas_window.canvas_ui.set_active_tool(self.tool_bar_window.get_active_tool())



                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta=time_delta)

            self.window_surface.blit(self.window_background, (0, 0))

            self.ui_manager.draw_ui(self.window_surface)

            pygame.display.update()


if __name__ == "__main__":
    app = PygamePaintApp()
    app.run()
