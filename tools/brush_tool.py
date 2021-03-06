import pygame

from tools.undo_record import UndoRecord


class BrushTool:

    def __init__(self, palette_colour, opacity, brush_size):
        self.option_data = {'palette_colour': pygame.Color(palette_colour.r,
                                                           palette_colour.g,
                                                           palette_colour.b, 255),
                            'opacity': opacity,
                            'brush_size': brush_size}

        self.brush_aa_amount = 4
        self.center_position = (0, 0)
        self.start_painting = False
        self.painting = False
        self.painted_area = None
        self.relative_painted_area = None
        self.new_rects_to_blit = []

        self.temp_painting_surface = None
        self.pre_painting_surface = None
        self.opacity_surface = None

        self.image = None

        self.active_canvas = None

        self._redraw_brush()

    def process_canvas_event(self, event, canvas, mouse_pos):
        consumed_event = False
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if canvas.hover_point(mouse_x, mouse_y):
                if not self.painting:
                    self.start_painting = True
                    consumed_event = True
        return consumed_event

    def process_event(self, event):
        consumed_event = False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.painting:
                self.painting = False

                if self.active_canvas is not None:
                    undo_surf = pygame.Surface(self.relative_painted_area.size,
                                               flags=pygame.SRCALPHA)
                    undo_surf.blit(self.pre_painting_surface,
                                   (0, 0), self.relative_painted_area)
                    self.active_canvas.undo_stack.append(UndoRecord(undo_surf,
                                                                    self.relative_painted_area))
                    self.active_canvas.redo_stack.clear()
                    if len(self.active_canvas.undo_stack) > 25:
                        self.active_canvas.undo_stack.pop(0)

                self.temp_painting_surface = None
                self.opacity_surface = None
                self.pre_painting_surface = None
                self.painted_area = None
                self.relative_painted_area = None

        return consumed_event

    def update(self, time_delta, canvas_surface, canvas_position, canvas):
        new_position = pygame.mouse.get_pos()

        if self.start_painting:
            self.start_painting = False
            self.center_position = new_position
            self.pre_painting_surface = canvas_surface.copy()

            self.painted_area = pygame.Rect((0, 0), self.image.get_size())
            self.painted_area.center = new_position

            self.new_rects_to_blit.append(self.painted_area.copy())
            self.painting = True

        if self.painting:
            # use line algorithm to generate series of points between the two
            # turn the points into rects and store them

            point_set = BrushTool._plot_line(self.center_position, new_position)
            point_set.add(new_position)
            if len(point_set) > 0:
                if self.center_position in point_set:
                    point_set.remove(self.center_position)
                for point in point_set:
                    if canvas.hover_point(point[0], point[1]):
                        new_rect = pygame.Rect((0, 0), self.image.get_size())
                        new_rect.center = point
                        self.new_rects_to_blit.append(new_rect)

                new_painted_area_rect = self.painted_area.unionall(self.new_rects_to_blit)
            else:
                new_painted_area_rect = self.painted_area

            new_temp_painting_surface = pygame.Surface(new_painted_area_rect.size,
                                                       flags=pygame.SRCALPHA,
                                                       depth=32)
            new_temp_painting_surface.fill(pygame.Color(self.option_data['palette_colour'].r,
                                                        self.option_data['palette_colour'].g,
                                                        self.option_data['palette_colour'].b,
                                                        0))
            if self.temp_painting_surface is not None:
                new_temp_painting_surface.blit(self.temp_painting_surface,
                                               (self.painted_area.left - new_painted_area_rect.left,
                                                self.painted_area.top - new_painted_area_rect.top))

            self.painted_area = new_painted_area_rect
            self.temp_painting_surface = new_temp_painting_surface

            self.opacity_surface = pygame.Surface(self.painted_area.size,
                                                  flags=pygame.SRCALPHA,
                                                  depth=32)
            self.opacity_surface.fill(pygame.Color(255, 255, 255, self.option_data['opacity']))

            for blit_rect in self.new_rects_to_blit:
                blit_rect.left -= self.painted_area.left
                blit_rect.top -= self.painted_area.top
                self.temp_painting_surface.blit(self.image, blit_rect)

            self.new_rects_to_blit = []

            canvas_surface.blit(self.pre_painting_surface, (0, 0))
            pre_blend = self.temp_painting_surface.copy()
            pre_blend.blit(self.opacity_surface, (0, 0),
                           special_flags=pygame.BLEND_RGBA_MULT)

            self.relative_painted_area = self.painted_area.copy()
            self.relative_painted_area.topleft = (self.painted_area.left - canvas_position[0],
                                                  self.painted_area.top - canvas_position[1])

            canvas_surface.blit(pre_blend, self.relative_painted_area)
            canvas.set_image(canvas_surface)

        self.center_position = new_position

    def set_option(self, option_id, value):
        if option_id in self.option_data:
            self.option_data[option_id] = value
            self._redraw_brush()

    def _redraw_brush(self):
        padding = 8
        self.image = pygame.Surface((self.option_data['brush_size']+padding,
                                     self.option_data['brush_size']+padding),
                                    flags=pygame.SRCALPHA,
                                    depth=32)

        aa_brush_size = self.option_data['brush_size'] * self.brush_aa_amount
        aa_padding = padding * self.brush_aa_amount
        aa_surface = pygame.Surface((aa_brush_size+aa_padding,
                                     aa_brush_size+aa_padding),
                                    flags=pygame.SRCALPHA, depth=32)
        aa_surface.fill(pygame.Color(self.option_data['palette_colour'].r,
                                     self.option_data['palette_colour'].g,
                                     self.option_data['palette_colour'].b, 0))
        pygame.draw.circle(aa_surface,
                           pygame.Color(self.option_data['palette_colour'].r,
                                        self.option_data['palette_colour'].g,
                                        self.option_data['palette_colour'].b, 85),
                           (int((aa_brush_size + aa_padding) / 2),
                            int((aa_brush_size + aa_padding) / 2)),
                           int(aa_brush_size / 2) + int(self.brush_aa_amount * 0.5))
        pygame.draw.circle(aa_surface,
                           pygame.Color(self.option_data['palette_colour'].r,
                                        self.option_data['palette_colour'].g,
                                        self.option_data['palette_colour'].b, 175),
                           (int((aa_brush_size + aa_padding) / 2),
                            int((aa_brush_size + aa_padding) / 2)),
                           int(aa_brush_size / 2))
        pygame.draw.circle(aa_surface,
                           pygame.Color(self.option_data['palette_colour'].r,
                                        self.option_data['palette_colour'].g,
                                        self.option_data['palette_colour'].b, 255),
                           (int((aa_brush_size + aa_padding) / 2),
                            int((aa_brush_size + aa_padding) / 2)),
                           int(aa_brush_size / 2) - int(self.brush_aa_amount * 0.5))
        pygame.transform.smoothscale(aa_surface,
                                     (self.option_data['brush_size']+padding,
                                      self.option_data['brush_size']+padding),
                                     self.image)

    @staticmethod
    def _plot_line(point_1, point_2):
        x0 = point_1[0]
        x1 = point_2[0]
        y0 = point_1[1]
        y1 = point_2[1]
        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                plot_points = BrushTool._plot_line_low(x1, y1, x0, y0)
            else:
                plot_points = BrushTool._plot_line_low(x0, y0, x1, y1)
        else:
            if y0 > y1:
                plot_points = BrushTool._plot_line_high(x1, y1, x0, y0)
            else:
                plot_points = BrushTool._plot_line_high(x0, y0, x1, y1)
        return plot_points

    @staticmethod
    def _plot_line_low(x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy

        d = 2 * dy - dx
        y = y0

        plot_points = set()
        for x in range(x0, x1):
            plot_points.add((x, y))
            if d > 0:
                y = y + yi
                d = d - 2 * dx
            d = d + 2 * dy

        return plot_points

    @staticmethod
    def _plot_line_high(x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        d = 2 * dx - dy
        x = x0

        plot_points = set()
        for y in range(y0, y1):
            plot_points.add((x, y))
            if d > 0:
                x = x + xi
                d = d - 2 * dy

            d = d + 2 * dx

        return plot_points
