from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QLinearGradient, QRadialGradient, QPen
from PyQt5.QtCore import Qt, QPoint, QRect


class DrawingElements:
    @staticmethod
    def draw_fret(painter, fret):
        """Рисование лада с различными стилями"""
        x, y, size, symbol = fret['x'], fret['y'], fret['size'], fret['symbol']
        style = fret.get('style', 'default')
        font_family = fret.get('font_family', 'Arial')
        color = fret.get('color', (0, 0, 0))

        # Применяем выбранный стиль
        DrawingElements._apply_fret_style(painter, x, y, size, style, color)

        # Настраиваем шрифт
        font = QFont(font_family, size, QFont.Bold)
        painter.setFont(font)

        font_metrics = QFontMetrics(painter.font())
        text_width = font_metrics.width(symbol)
        text_height = font_metrics.height()

        text_x = x - text_width // 2
        text_y = y + text_height // 3

        painter.drawText(text_x, text_y, symbol)

    @staticmethod
    def _apply_fret_style(painter, x, y, size, style, color):
        """Применение различных стилей к ладу"""
        if style == 'default':
            painter.setPen(QColor(*color))

        elif style == 'gradient_text':
            gradient = QLinearGradient(x - size, y - size, x + size, y + size)
            gradient.setColorAt(0, QColor(255, 100, 100))
            gradient.setColorAt(0.5, QColor(*color))
            gradient.setColorAt(1, QColor(100, 100, 255))
            painter.setPen(QPen(gradient, 2))

        elif style == 'shadow':
            shadow_color = QColor(0, 0, 0, 100)
            painter.setPen(QPen(shadow_color, 3))

        elif style == 'glow':
            glow_color = QColor(255, 255, 255, 80)
            painter.setPen(QPen(glow_color, 4))

        elif style == 'outline':
            outline_color = QColor(255, 255, 255)
            painter.setPen(QPen(outline_color, 4))

        elif style == 'metallic':
            gradient = QLinearGradient(x - size, y - size, x + size, y + size)
            gradient.setColorAt(0, QColor(255, 255, 255))
            gradient.setColorAt(0.3, QColor(200, 200, 200))
            gradient.setColorAt(0.7, QColor(100, 100, 100))
            gradient.setColorAt(1, QColor(150, 150, 150))
            painter.setPen(QPen(gradient, 2))

        elif style == 'gold_embossed':
            gradient = QLinearGradient(x - size, y - size, x + size, y + size)
            gradient.setColorAt(0, QColor(255, 215, 0))
            gradient.setColorAt(0.5, QColor(218, 165, 32))
            gradient.setColorAt(1, QColor(184, 134, 11))
            painter.setPen(QPen(gradient, 3))

        elif style == 'silver_embossed':
            gradient = QLinearGradient(x - size, y - size, x + size, y + size)
            gradient.setColorAt(0, QColor(255, 255, 255))
            gradient.setColorAt(0.5, QColor(192, 192, 192))
            gradient.setColorAt(1, QColor(150, 150, 150))
            painter.setPen(QPen(gradient, 3))

        elif style == 'neon':
            neon_color = QColor(*color)
            neon_color.setAlpha(200)
            painter.setPen(QPen(neon_color, 2))

        elif style == 'stamped':
            stamp_color = QColor(*color)
            stamp_color.setAlpha(180)
            painter.setPen(QPen(stamp_color, 2))

    @staticmethod
    def draw_note(painter, note):
        """Рисование ноты с различными стилями и оформлением"""
        x, y, radius, style = note['x'], note['y'], note['radius'], note.get('style', 'default')
        finger, note_name = note['finger'], note['note_name']
        decoration = note.get('decoration', 'none')
        text_color = note.get('text_color', (255, 255, 255))
        font_style = note.get('font_style', 'normal')
        display_text = note.get('display_text', 'finger')  # 'finger' или 'note_name'

        # Применяем выбранный стиль
        DrawingElements._apply_note_style(painter, x, y, radius, style)

        # Рисуем основной круг
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Применяем дополнительное оформление
        DrawingElements._apply_decoration(painter, x, y, radius, decoration, style)

        # Рисуем текст
        text_to_display = finger if display_text == 'finger' else note_name
        DrawingElements._draw_note_text(painter, x, y, radius, text_to_display, text_color, font_style)

    @staticmethod
    def draw_open_note(painter, open_note):
        """Рисование открытой ноты с различными стилями и оформлением"""
        x, y, radius, style = open_note['x'], open_note['y'], open_note['radius'], open_note.get('style', 'default')
        symbol, note_name = open_note['symbol'], open_note['note_name']
        decoration = open_note.get('decoration', 'none')
        text_color = open_note.get('text_color', (255, 255, 255))
        font_style = open_note.get('font_style', 'normal')
        display_text = open_note.get('display_text', 'symbol')  # 'symbol' или 'note_name'

        # Применяем выбранный стиль
        DrawingElements._apply_note_style(painter, x, y, radius, style)

        # Рисуем основной круг
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Применяем дополнительное оформление
        DrawingElements._apply_decoration(painter, x, y, radius, decoration, style)

        # Рисуем текст
        text_to_display = symbol if display_text == 'symbol' else note_name
        DrawingElements._draw_note_text(painter, x, y, radius, text_to_display, text_color, font_style)

    @staticmethod
    def _apply_note_style(painter, x, y, radius, style):
        """Применение различных стилей к ноте"""
        painter.setPen(QColor(0, 0, 0))  # Черная обводка по умолчанию

        if style == 'default':
            painter.setBrush(QColor(255, 0, 0))

        elif style == 'blue_gradient':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(100, 150, 255))
            gradient.setColorAt(1, QColor(50, 100, 200))
            painter.setBrush(gradient)

        elif style == 'red_3d':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 150, 150))
            gradient.setColorAt(0.7, QColor(220, 50, 50))
            gradient.setColorAt(1, QColor(180, 0, 0))
            painter.setBrush(gradient)

        elif style == 'green_3d':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 180))
            gradient.setColorAt(0.7, QColor(80, 200, 80))
            gradient.setColorAt(1, QColor(40, 160, 40))
            painter.setBrush(gradient)

        elif style == 'purple_3d':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 200, 255))
            gradient.setColorAt(0.7, QColor(180, 100, 230))
            gradient.setColorAt(1, QColor(140, 60, 200))
            painter.setBrush(gradient)

        elif style == 'gold_3d':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 230, 100))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(230, 170, 30))
            painter.setBrush(gradient)

        elif style == 'glass':
            painter.setBrush(QColor(255, 255, 255, 180))
            painter.setPen(QColor(200, 200, 255, 200))

        elif style == 'metal':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(220, 220, 220))
            gradient.setColorAt(0.5, QColor(180, 180, 180))
            gradient.setColorAt(1, QColor(150, 150, 150))
            painter.setBrush(gradient)

        elif style == 'fire':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 255, 150))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(255, 100, 0))
            painter.setBrush(gradient)

        elif style == 'ice':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 230, 255))
            gradient.setColorAt(0.5, QColor(150, 200, 255))
            gradient.setColorAt(1, QColor(100, 170, 255))
            painter.setBrush(gradient)

        elif style == 'soft_pink':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 240))
            gradient.setColorAt(0.7, QColor(255, 200, 220))
            gradient.setColorAt(1, QColor(240, 160, 200))
            painter.setBrush(gradient)

        elif style == 'mint_green':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 255, 220))
            gradient.setColorAt(0.7, QColor(180, 230, 180))
            gradient.setColorAt(1, QColor(140, 200, 140))
            painter.setBrush(gradient)

        elif style == 'lavender':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 230, 255))
            gradient.setColorAt(0.7, QColor(210, 200, 240))
            gradient.setColorAt(1, QColor(180, 160, 220))
            painter.setBrush(gradient)

        elif style == 'peach':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 240, 220))
            gradient.setColorAt(0.7, QColor(255, 210, 170))
            gradient.setColorAt(1, QColor(240, 180, 140))
            painter.setBrush(gradient)

        elif style == 'sky_blue':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 230, 255))
            gradient.setColorAt(0.7, QColor(150, 200, 240))
            gradient.setColorAt(1, QColor(100, 170, 220))
            painter.setBrush(gradient)

        elif style == 'lemon_yellow':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 255, 200))
            gradient.setColorAt(0.7, QColor(255, 240, 120))
            gradient.setColorAt(1, QColor(240, 220, 80))
            painter.setBrush(gradient)

        elif style == 'coral':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 200))
            gradient.setColorAt(0.7, QColor(255, 180, 140))
            gradient.setColorAt(1, QColor(240, 140, 100))
            painter.setBrush(gradient)

        elif style == 'aqua_marine':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 255, 240))
            gradient.setColorAt(0.7, QColor(160, 230, 220))
            gradient.setColorAt(1, QColor(120, 200, 190))
            painter.setBrush(gradient)

        elif style == 'rose_quartz':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 235))
            gradient.setColorAt(0.7, QColor(240, 200, 210))
            gradient.setColorAt(1, QColor(220, 170, 190))
            painter.setBrush(gradient)

        elif style == 'seafoam':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 255, 230))
            gradient.setColorAt(0.7, QColor(190, 230, 200))
            gradient.setColorAt(1, QColor(160, 200, 170))
            painter.setBrush(gradient)

        elif style == 'buttercup':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 245, 180))
            gradient.setColorAt(0.7, QColor(255, 225, 100))
            gradient.setColorAt(1, QColor(240, 200, 60))
            painter.setBrush(gradient)

        elif style == 'lilac':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(245, 230, 255))
            gradient.setColorAt(0.7, QColor(225, 200, 240))
            gradient.setColorAt(1, QColor(200, 170, 220))
            painter.setBrush(gradient)

        elif style == 'honey':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 240, 180))
            gradient.setColorAt(0.7, QColor(255, 220, 120))
            gradient.setColorAt(1, QColor(240, 190, 80))
            painter.setBrush(gradient)

        elif style == 'turquoise':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 240, 230))
            gradient.setColorAt(0.7, QColor(160, 220, 210))
            gradient.setColorAt(1, QColor(120, 190, 180))
            painter.setBrush(gradient)

        elif style == 'apricot':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 200))
            gradient.setColorAt(0.7, QColor(255, 200, 150))
            gradient.setColorAt(1, QColor(240, 170, 120))
            painter.setBrush(gradient)

        elif style == 'periwinkle':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 230, 255))
            gradient.setColorAt(0.7, QColor(200, 200, 240))
            gradient.setColorAt(1, QColor(170, 170, 220))
            painter.setBrush(gradient)

        elif style == 'sage':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 240, 220))
            gradient.setColorAt(0.7, QColor(200, 220, 180))
            gradient.setColorAt(1, QColor(170, 190, 150))
            painter.setBrush(gradient)

        elif style == 'melon':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 190))
            gradient.setColorAt(0.7, QColor(255, 180, 140))
            gradient.setColorAt(1, QColor(240, 150, 110))
            painter.setBrush(gradient)

        elif style == 'powder_blue':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 230, 255))
            gradient.setColorAt(0.7, QColor(190, 210, 240))
            gradient.setColorAt(1, QColor(160, 180, 220))
            painter.setBrush(gradient)

        elif style == 'pistachio':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 255, 220))
            gradient.setColorAt(0.7, QColor(200, 230, 180))
            gradient.setColorAt(1, QColor(170, 200, 150))
            painter.setBrush(gradient)

        elif style == 'blush':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 225))
            gradient.setColorAt(0.7, QColor(240, 190, 200))
            gradient.setColorAt(1, QColor(220, 160, 180))
            painter.setBrush(gradient)

        elif style == 'mauve':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 220, 230))
            gradient.setColorAt(0.7, QColor(220, 190, 210))
            gradient.setColorAt(1, QColor(190, 160, 180))
            painter.setBrush(gradient)

        elif style == 'cream':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 250, 240))
            gradient.setColorAt(0.7, QColor(255, 240, 220))
            gradient.setColorAt(1, QColor(240, 220, 200))
            painter.setBrush(gradient)

        elif style == 'teal':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 230, 230))
            gradient.setColorAt(0.7, QColor(160, 200, 200))
            gradient.setColorAt(1, QColor(120, 170, 170))
            painter.setBrush(gradient)

        elif style == 'salmon':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 190))
            gradient.setColorAt(0.7, QColor(255, 170, 150))
            gradient.setColorAt(1, QColor(240, 140, 120))
            painter.setBrush(gradient)

        elif style == 'orchid':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(245, 210, 240))
            gradient.setColorAt(0.7, QColor(225, 180, 220))
            gradient.setColorAt(1, QColor(200, 150, 190))
            painter.setBrush(gradient)

        elif style == 'mint_blue':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(210, 240, 255))
            gradient.setColorAt(0.7, QColor(180, 220, 240))
            gradient.setColorAt(1, QColor(150, 190, 220))
            painter.setBrush(gradient)

        elif style == 'pear':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 255, 200))
            gradient.setColorAt(0.7, QColor(200, 230, 160))
            gradient.setColorAt(1, QColor(170, 200, 130))
            painter.setBrush(gradient)

        elif style == 'rose_gold':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 210))
            gradient.setColorAt(0.7, QColor(240, 200, 170))
            gradient.setColorAt(1, QColor(220, 170, 140))
            painter.setBrush(gradient)

        elif style == 'lavender_gray':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 230, 240))
            gradient.setColorAt(0.7, QColor(220, 210, 220))
            gradient.setColorAt(1, QColor(190, 180, 190))
            painter.setBrush(gradient)

        elif style == 'honeydew':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 255, 240))
            gradient.setColorAt(0.7, QColor(220, 240, 220))
            gradient.setColorAt(1, QColor(200, 220, 200))
            painter.setBrush(gradient)

        elif style == 'peach_puff':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 210))
            gradient.setColorAt(0.7, QColor(255, 210, 180))
            gradient.setColorAt(1, QColor(240, 180, 150))
            painter.setBrush(gradient)

        elif style == 'azure':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 240, 255))
            gradient.setColorAt(0.7, QColor(200, 220, 240))
            gradient.setColorAt(1, QColor(170, 190, 220))
            painter.setBrush(gradient)

        elif style == 'pale_green':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 255, 230))
            gradient.setColorAt(0.7, QColor(200, 240, 200))
            gradient.setColorAt(1, QColor(170, 210, 170))
            painter.setBrush(gradient)

        elif style == 'light_coral':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 210, 210))
            gradient.setColorAt(0.7, QColor(240, 180, 180))
            gradient.setColorAt(1, QColor(220, 150, 150))
            painter.setBrush(gradient)

        elif style == 'thistle':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(245, 230, 245))
            gradient.setColorAt(0.7, QColor(225, 200, 225))
            gradient.setColorAt(1, QColor(200, 170, 200))
            painter.setBrush(gradient)

        elif style == 'wheat':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 240, 220))
            gradient.setColorAt(0.7, QColor(240, 220, 190))
            gradient.setColorAt(1, QColor(220, 190, 160))
            painter.setBrush(gradient)

        elif style == 'light_cyan':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 255, 255))
            gradient.setColorAt(0.7, QColor(200, 240, 240))
            gradient.setColorAt(1, QColor(170, 210, 210))
            painter.setBrush(gradient)

        elif style == 'pale_turquoise':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(210, 240, 240))
            gradient.setColorAt(0.7, QColor(180, 220, 220))
            gradient.setColorAt(1, QColor(150, 190, 190))
            painter.setBrush(gradient)

        elif style == 'light_pink':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 230, 235))
            gradient.setColorAt(0.7, QColor(240, 200, 210))
            gradient.setColorAt(1, QColor(220, 170, 190))
            painter.setBrush(gradient)

        elif style == 'light_salmon':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 210, 190))
            gradient.setColorAt(0.7, QColor(255, 180, 150))
            gradient.setColorAt(1, QColor(240, 150, 120))
            painter.setBrush(gradient)

        elif style == 'light_skyblue':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(210, 230, 255))
            gradient.setColorAt(0.7, QColor(180, 210, 240))
            gradient.setColorAt(1, QColor(150, 180, 220))
            painter.setBrush(gradient)

        elif style == 'light_green':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(210, 255, 210))
            gradient.setColorAt(0.7, QColor(180, 230, 180))
            gradient.setColorAt(1, QColor(150, 200, 150))
            painter.setBrush(gradient)

        elif style == 'plum':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(245, 210, 245))
            gradient.setColorAt(0.7, QColor(225, 180, 225))
            gradient.setColorAt(1, QColor(200, 150, 200))
            painter.setBrush(gradient)

        elif style == 'bisque':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 240, 220))
            gradient.setColorAt(0.7, QColor(240, 220, 190))
            gradient.setColorAt(1, QColor(220, 190, 160))
            painter.setBrush(gradient)

        else:
            # Стиль по умолчанию
            painter.setBrush(QColor(255, 0, 0))

    @staticmethod
    def _apply_decoration(painter, x, y, radius, decoration, style):
        """Применение дополнительного оформления"""
        if decoration == 'none':
            return
        elif decoration == 'double_border':
            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
            DrawingElements._apply_note_style(painter, x, y, radius, style)
        elif decoration == 'glow':
            pen = QPen(QColor(255, 255, 255, 100))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius - 2, y - radius - 2, (radius + 2) * 2, (radius + 2) * 2)
            DrawingElements._apply_note_style(painter, x, y, radius, style)
        elif decoration == 'shadow':
            pen = QPen(QColor(0, 0, 0, 80))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
            DrawingElements._apply_note_style(painter, x, y, radius, style)
        elif decoration == 'sparkle':
            sparkle_color = QColor(255, 255, 255, 200)
            painter.setBrush(sparkle_color)
            painter.setPen(Qt.NoPen)
            sparkle_radius = max(2, radius // 8)
            positions = [
                (x - radius + sparkle_radius, y - radius + sparkle_radius),
                (x + radius - sparkle_radius, y - radius + sparkle_radius),
                (x - radius + sparkle_radius, y + radius - sparkle_radius),
                (x + radius - sparkle_radius, y + radius - sparkle_radius)
            ]
            for pos_x, pos_y in positions:
                painter.drawEllipse(pos_x, pos_y, sparkle_radius * 2, sparkle_radius * 2)
            DrawingElements._apply_note_style(painter, x, y, radius, style)
        elif decoration == 'dotted_border':
            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 1, y - radius + 1, (radius - 1) * 2, (radius - 1) * 2)
            DrawingElements._apply_note_style(painter, x, y, radius, style)

    @staticmethod
    def _draw_note_text(painter, x, y, radius, text, text_color, font_style):
        """Рисование текста на ноте с идеальным центрированием"""
        if not text:
            return

        # Настраиваем шрифт - увеличиваем размер для лучшего заполнения круга
        font_size = max(10, radius)  # Увеличиваем размер шрифта
        font = QFont("Arial", font_size)

        if font_style == 'bold':
            font.setWeight(QFont.Bold)
        elif font_style == 'light':
            font.setWeight(QFont.Light)
        elif font_style == 'italic':
            font.setItalic(True)
        elif font_style == 'bold_italic':
            font.setWeight(QFont.Bold)
            font.setItalic(True)

        painter.setFont(font)

        # Устанавливаем цвет текста
        painter.setPen(QColor(*text_color))

        # Идеальное центрирование текста
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.width(text)
        text_height = font_metrics.height()

        # Центрируем по горизонтали и вертикали
        text_x = x - text_width // 2
        text_y = y + text_height // 4  # Более точное вертикальное центрирование

        # Если текст слишком большой для круга, уменьшаем шрифт
        if text_width > radius * 1.8 or text_height > radius * 1.8:
            font_size = max(8, radius * 3 // 4)
            font.setPointSize(font_size)
            painter.setFont(font)
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.width(text)
            text_height = font_metrics.height()
            text_x = x - text_width // 2
            text_y = y + text_height // 4

        painter.drawText(text_x, text_y, text)

    @staticmethod
    def draw_barre(painter, barre):
        """Рисование баре с различными стилями"""
        x, y, width, height, radius, style = (
            barre['x'], barre['y'], barre['width'],
            barre['height'], barre['radius'], barre.get('style', 'default')
        )
        color = barre.get('color', (189, 183, 107))
        decoration = barre.get('decoration', 'none')

        # Применяем выбранный стиль
        DrawingElements._apply_barre_style(painter, x, y, width, height, radius, style, color)

        # Рисуем основной прямоугольник
        painter.drawRoundedRect(
            x - width // 2,
            y - height // 2,
            width,
            height,
            radius,
            radius
        )

        # Применяем дополнительное оформление
        DrawingElements._apply_barre_decoration(painter, x, y, width, height, radius, decoration, style, color)

    @staticmethod
    def _apply_barre_style(painter, x, y, width, height, radius, style, color):
        """Применение различных стилей к баре"""
        painter.setPen(QColor(0, 0, 0))  # Черная обводка по умолчанию

        if style == 'default':
            painter.setBrush(QColor(*color))
        elif style == 'wood':
            gradient = QLinearGradient(x - width // 2, y - height // 2, x + width // 2, y + height // 2)
            gradient.setColorAt(0, QColor(210, 180, 140))
            gradient.setColorAt(0.5, QColor(160, 120, 80))
            gradient.setColorAt(1, QColor(210, 180, 140))
            painter.setBrush(gradient)
        elif style == 'metal':
            gradient = QLinearGradient(x - width // 2, y - height // 2, x + width // 2, y + height // 2)
            gradient.setColorAt(0, QColor(200, 200, 200))
            gradient.setColorAt(0.5, QColor(100, 100, 100))
            gradient.setColorAt(1, QColor(200, 200, 200))
            painter.setBrush(gradient)
        elif style == 'rubber':
            gradient = QRadialGradient(x, y, max(width, height))
            gradient.setColorAt(0, QColor(80, 80, 80))
            gradient.setColorAt(1, QColor(40, 40, 40))
            painter.setBrush(gradient)
        elif style == 'gradient':
            gradient = QLinearGradient(x - width // 2, y - height // 2, x + width // 2, y + height // 2)
            gradient.setColorAt(0, QColor(*color))
            lighter = QColor(*color).lighter(150)
            gradient.setColorAt(1, QColor(lighter.red(), lighter.green(), lighter.blue()))
            painter.setBrush(gradient)
        elif style == 'striped':
            painter.setBrush(QColor(*color))
        else:
            painter.setBrush(QColor(*color))

    @staticmethod
    def _apply_barre_decoration(painter, x, y, width, height, radius, decoration, style, color):
        """Применение дополнительного оформления к баре"""
        if decoration == 'none':
            return
        elif decoration == 'shadow':
            pen = QPen(QColor(0, 0, 0, 80))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                x - width // 2 + 2,
                y - height // 2 + 2,
                width,
                height,
                radius,
                radius
            )
        elif decoration == 'glow':
            pen = QPen(QColor(255, 255, 255, 60))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                x - width // 2 - 1,
                y - height // 2 - 1,
                width + 2,
                height + 2,
                radius,
                radius
            )
        elif decoration == 'double_border':
            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                x - width // 2 + 1,
                y - height // 2 + 1,
                width - 2,
                height - 2,
                radius,
                radius
            )
        elif decoration == 'stripes' and style == 'striped':
            stripe_color = QColor(*color).darker(120)
            painter.setPen(QPen(stripe_color, 1))
            stripe_spacing = height // 4
            for i in range(1, 4):
                stripe_y = y - height // 2 + i * stripe_spacing
                painter.drawLine(
                    x - width // 2 + 2,
                    stripe_y,
                    x + width // 2 - 2,
                    stripe_y
                )

    @staticmethod
    def draw_crop_rect(painter, crop_rect):
        """Рисование рамки обрезки с улучшенной видимостью"""
        x, y, width, height = crop_rect['x'], crop_rect['y'], crop_rect['width'], crop_rect['height']
        color = crop_rect.get('color', (255, 0, 0))
        style = crop_rect.get('style', 'dashed')

        # Основная рамка - более толстая и заметная
        pen = QPen(QColor(*color))
        pen.setWidth(3)  # Увеличиваем толщину

        if style == 'dashed':
            pen.setStyle(Qt.DashLine)
        elif style == 'dotted':
            pen.setStyle(Qt.DotLine)
        elif style == 'solid':
            pen.setStyle(Qt.SolidLine)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(x, y, width, height)

        # Добавляем полупрозрачную заливку для лучшей видимости области
        fill_color = QColor(*color)
        fill_color.setAlpha(30)  # Полупрозрачная заливка
        painter.setBrush(fill_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y, width, height)

        # Угловые маркеры - более заметные
        marker_size = 12
        marker_color = QColor(*color)
        marker_color.setAlpha(200)
        painter.setPen(QPen(marker_color, 3))
        painter.setBrush(QColor(255, 255, 255, 180))

        # Угловые точки
        points = [
            (x, y),  # левый верхний
            (x + width, y),  # правый верхний
            (x, y + height),  # левый нижний
            (x + width, y + height)  # правый нижний
        ]

        for point_x, point_y in points:
            painter.drawRect(point_x - marker_size // 2, point_y - marker_size // 2, marker_size, marker_size)

        # Добавляем текст с размерами
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(*color))

        # Размеры области
        size_text = f"{width} x {height}"
        text_width = QFontMetrics(font).width(size_text)

        # Рисуем текст в центре верхней границы
        text_x = x + (width - text_width) // 2
        text_y = y - 10
        painter.drawText(text_x, text_y, size_text)