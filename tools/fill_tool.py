import pygame

from tools.undo_record import UndoRecord


class FillTool:

    def __init__(self, palette_colour, opacity, threshold):

        self.option_data = {'palette_colour': pygame.Color(palette_colour.r,
                                                           palette_colour.g,
                                                           palette_colour.b, 255),
                            'opacity': opacity,
                            'threshold': threshold}

        self.start_fill_position = None
        self.start_fill_colour = None

        self.start_filling = False
        self.stop_filling = False
        self.filling = False

        self.filling_edge_pixels = set()

        self.temp_painting_surface = None
        self.pre_painting_surface = None
        self.opacity_surface = None

        self.pre_painting_surf_blank_int_col = None

        self.active_canvas = None

        self.clock = pygame.time.Clock()

    def process_canvas_event(self, event, canvas, mouse_pos):
        consumed_event = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x = mouse_pos[0]
            mouse_y = mouse_pos[1]

            if canvas.hover_point(mouse_x, mouse_y) and not self.filling:
                self.start_filling = True
                consumed_event = True

                undo_surf = canvas.get_image().copy()

                canvas.undo_stack.append(UndoRecord(undo_surf, undo_surf.get_rect()))
                canvas.redo_stack.clear()
                if len(canvas.undo_stack) > 25:
                    canvas.undo_stack.pop(0)

        return consumed_event

    def process_event(self, event):
        return False

    def update(self, time_delta, canvas_surface, canvas_position, canvas):
        if self.start_filling:
            self.start_filling = False
            self.start_fill_position = pygame.mouse.get_pos()
            self.start_fill_position = (self.start_fill_position[0] - canvas_position[0],
                                        self.start_fill_position[1] - canvas_position[1])
            self.start_fill_colour = canvas_surface.get_at(self.start_fill_position)

            self.pre_painting_surface = canvas_surface.copy()
            self.temp_painting_surface = pygame.Surface(canvas_surface.get_size(),
                                                        flags=pygame.SRCALPHA,
                                                        depth=32)
            self.temp_painting_surface.fill(pygame.Color(self.option_data['palette_colour'].r,
                                                         self.option_data['palette_colour'].g,
                                                         self.option_data['palette_colour'].b,
                                                         0))
            self.opacity_surface = pygame.Surface(canvas_surface.get_size(),
                                                  flags=pygame.SRCALPHA,
                                                  depth=32)
            self.opacity_surface.fill(pygame.Color(255, 255, 255, self.option_data['opacity']))
            self.filling_edge_pixels = {self.start_fill_position}
            self.filling = True

        if self.stop_filling:
            self.stop_filling = False
            self.filling = False
            canvas_surface.blit(self.pre_painting_surface, (0, 0))
            self.temp_painting_surface.blit(self.opacity_surface, (0, 0),
                                            special_flags=pygame.BLEND_RGBA_MULT)
            canvas_surface.blit(self.temp_painting_surface, (0, 0))

            canvas.set_image(canvas_surface)
            self.temp_painting_surface = None
            self.opacity_surface = None
            self.pre_painting_surface = None

        if self.filling:
            self._rect_fill_start(canvas_surface, self.start_fill_position[0],
                                  self.start_fill_position[1])

            canvas_surface.blit(self.pre_painting_surface, (0, 0))
            pre_blend = self.temp_painting_surface.copy()
            pre_blend.blit(self.opacity_surface, (0, 0),
                           special_flags=pygame.BLEND_RGBA_MULT)
            canvas_surface.blit(pre_blend, (0, 0))

            self.stop_filling = True

    def set_option(self, option_id, value):
        if option_id in self.option_data:
            self.option_data[option_id] = value

    def _rect_fill_start(self, canvas_surface, x: int, y: int):
        pixel_array = pygame.PixelArray(self.temp_painting_surface)
        self._fill_colour = self.option_data['palette_colour']
        self._fill_threshold = self.option_data['threshold'] * 195075
        self.pre_painting_surf_blank_int_col = pixel_array[0, 0]
        self._rect_fill(pixel_array, x, y, pixel_array.shape[0],
                        pixel_array.shape[1], canvas_surface)
        try:
            pixel_array.close()
        except AttributeError:
            pass

    def _rect_fill(self, array, x: int, y: int, width: int, height: int, canvas_surface):
        while True:
            ox = x
            oy = y
            while y != 0 and self._test_fill_pixel(array, x, y - 1, canvas_surface):
                y -= 1
            while x != 0 and self._test_fill_pixel(array, x-1, y, canvas_surface):
                x -= 1
            if x == ox and y == oy:
                break
        self._rect_fill_core(array, x, y, width, height, canvas_surface)

    def _rect_fill_core(self, array, x: int, y: int, width: int, height: int, canvas_surface):

        last_row_length = 0

        while True:
            row_length = 0
            sx = x

            if last_row_length == 0 or self._test_fill_pixel(
                array, x, y, canvas_surface
            ):
                while x != 0 and self._test_fill_pixel(array, x-1, y, canvas_surface):
                    x -= 1
                    array[x, y] = self._fill_colour
                    if y != 0 and self._test_fill_pixel(array, x, y-1, canvas_surface):
                        self._rect_fill(array, x, y - 1, width, height, canvas_surface)
                    row_length += 1
                    last_row_length += 1

            else:
                while True:
                    last_row_length -= 1
                    if last_row_length == 0:
                        return
                    x += 1
                    if self._test_fill_pixel(array, x, y, canvas_surface):
                        break

                sx = x
            while sx < width and self._test_fill_pixel(array, sx, y, canvas_surface):
                array[sx, y] = self._fill_colour
                row_length += 1
                sx += 1

            if row_length < last_row_length:
                end = x + last_row_length
                while sx + 1 < end:
                    if self._test_fill_pixel(array, sx, y, canvas_surface):
                        self._rect_fill_core(array, sx, y, width, height, canvas_surface)
                    sx += 1
            elif row_length > last_row_length and y != 0:
                ux = x + last_row_length
                while ux + 1 < sx:
                    if self._test_fill_pixel(array, ux, y - 1, canvas_surface):
                        self._rect_fill(array, ux, y - 1, width, height, canvas_surface)
                    ux += 1
            last_row_length = row_length
            if last_row_length == 0 or y + 1 >= height:
                break
            else:
                y += 1

    def _test_fill_pixel(self, array, x, y, canvas_surface):
        if array[x, y] != self.pre_painting_surf_blank_int_col:
            return False
        pixel_colour = canvas_surface.get_at((x, y))
        return (self.calc_cheap_distance_between_colours(pixel_colour, self.start_fill_colour) <
                self._fill_threshold)

    @staticmethod
    def calc_distance_between_colours(colour_1, colour_2):
        red_param = (colour_1.r + colour_2.r)/2.0

        sq_red_diff = (colour_2.r - colour_1.r) ** 2
        sq_green_diff = (colour_2.g - colour_1.g) ** 2
        sq_blue_diff = (colour_2.b - colour_1.b) ** 2

        return (((2 + (red_param/256)) * sq_red_diff +
                (4 * sq_green_diff) +
                (2 + ((255 - red_param)/256)) * sq_blue_diff) ** 0.5) / 765.0

    @staticmethod
    def calc_cheap_distance_between_colours(colour_1, colour_2):
        sq_red_diff = (colour_2.r - colour_1.r) ** 2
        sq_green_diff = (colour_2.g - colour_1.g) ** 2
        sq_blue_diff = (colour_2.b - colour_1.b) ** 2
        return sq_red_diff + sq_green_diff + sq_blue_diff
