import pygame
import pygame_gui

from pygame_gui import UIManager

from ui_canvas_window import CanvasWindow
from ui_tool_bar_window import ToolBarWindow


class PygamePaintApp:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Pygame Paint")
        window_dimensions = (1280, 720)
        self.window_surface = pygame.display.set_mode(window_dimensions)
        title_bar_icon = pygame.image.load('data/paint_icon.png')
        pygame.display.set_icon(title_bar_icon)

        self.window_background = pygame.Surface(window_dimensions, depth=32)
        self.window_background.fill(pygame.Color(50,50,50))

        self.ui_manager = UIManager(window_dimensions)

        self.tool_bar_window = ToolBarWindow(pygame.Rect(10, 10, 200, 700),
                                             manager=self.ui_manager)

        new_canvas = pygame.Surface((500, 400), flags=pygame.SRCALPHA, depth=32)
        new_canvas.fill(pygame.Color(100, 100, 100, 255))
        canvas_window_rect = pygame.Rect(0, 0, 640, 480)
        canvas_window_rect.center = (640, 360)
        self.canvas_window = CanvasWindow(rect=canvas_window_rect,
                                          manager=self.ui_manager,
                                          image_file_name='new_image.png',
                                          image=new_canvas)

        self.canvas_window.canvas_ui.set_active_tool(self.tool_bar_window.get_active_tool())

        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            time_delta = self.clock.tick(120)/1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.ui_manager.process_events(event)

            self.ui_manager.update(time_delta=time_delta)

            self.window_surface.blit(self.window_background, (0, 0))

            self.ui_manager.draw_ui(self.window_surface)

            pygame.display.update()


if __name__ == "__main__":
    app = PygamePaintApp()
    app.run()
