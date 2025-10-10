from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QLinearGradient, QRadialGradient, QPen
from PyQt5.QtCore import Qt, QPoint


class DrawingElements:
    @staticmethod
    def draw_fret(painter, fret):
        """Рисование лада (римская цифра)"""
        x, y, size, symbol = fret['x'], fret['y'], fret['size'], fret['symbol']

        font = QFont("Arial", size, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))  # Черный цвет

        font_metrics = QFontMetrics(painter.font())
        text_width = font_metrics.width(symbol)
        text_height = font_metrics.height()

        text_x = x - text_width // 2
        text_y = y + text_height // 3

        painter.drawText(text_x, text_y, symbol)

    @staticmethod
    def draw_note(painter, note):
        """Рисование ноты с различными стилями и оформлением"""
        x, y, radius, style = note['x'], note['y'], note['radius'], note.get('style', 'default')
        finger, note_name = note['finger'], note['note_name']
        decoration = note.get('decoration', 'none')  # Дополнительное оформление

        # Применяем выбранный стиль
        DrawingElements._apply_note_style(painter, x, y, radius, style)

        # Рисуем основной круг
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Применяем дополнительное оформление
        DrawingElements._apply_decoration(painter, x, y, radius, decoration, style)

        # Рисуем текст
        DrawingElements._draw_note_text(painter, x, y, radius, finger, note_name, style)

    @staticmethod
    def draw_open_note(painter, open_note):
        """Рисование открытой ноты с различными стилями и оформлением"""
        x, y, radius, style = open_note['x'], open_note['y'], open_note['radius'], open_note.get('style', 'default')
        symbol, note_name = open_note['symbol'], open_note['note_name']
        decoration = open_note.get('decoration', 'none')  # Дополнительное оформление

        # Применяем выбранный стиль
        DrawingElements._apply_note_style(painter, x, y, radius, style)

        # Рисуем основной круг
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Применяем дополнительное оформление
        DrawingElements._apply_decoration(painter, x, y, radius, decoration, style)

        # Рисуем текст
        DrawingElements._draw_note_text(painter, x, y, radius, symbol, note_name, style)

    @staticmethod
    def _apply_note_style(painter, x, y, radius, style):
        """Применение различных стилей к ноте"""
        painter.setPen(QColor(0, 0, 0))  # Черная обводка по умолчанию

        # Основные цвета и градиенты
        if style == 'default':
            painter.setBrush(QColor(255, 0, 0))  # Красный

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

        # Дополнительные светлые цвета
        elif style == 'soft_pink':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 220))
            gradient.setColorAt(1, QColor(255, 150, 180))
            painter.setBrush(gradient)

        elif style == 'mint_green':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 200))
            gradient.setColorAt(1, QColor(120, 230, 160))
            painter.setBrush(gradient)

        elif style == 'lavender':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(230, 210, 255))
            gradient.setColorAt(1, QColor(200, 180, 240))
            painter.setBrush(gradient)

        elif style == 'peach':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 220, 180))
            gradient.setColorAt(1, QColor(255, 190, 140))
            painter.setBrush(gradient)

        elif style == 'sky_blue':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(180, 230, 255))
            gradient.setColorAt(1, QColor(140, 200, 255))
            painter.setBrush(gradient)

        elif style == 'lemon_yellow':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 255, 150))
            gradient.setColorAt(1, QColor(255, 240, 100))
            painter.setBrush(gradient)

        elif style == 'coral':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 180, 160))
            gradient.setColorAt(1, QColor(255, 140, 120))
            painter.setBrush(gradient)

        elif style == 'aqua_marine':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(150, 255, 230))
            gradient.setColorAt(1, QColor(100, 220, 200))
            painter.setBrush(gradient)

        elif style == 'rose_quartz':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 200, 220))
            gradient.setColorAt(1, QColor(240, 170, 200))
            painter.setBrush(gradient)

        elif style == 'seafoam':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(160, 255, 220))
            gradient.setColorAt(1, QColor(120, 230, 190))
            painter.setBrush(gradient)

        elif style == 'buttercup':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 240, 150))
            gradient.setColorAt(1, QColor(255, 220, 100))
            painter.setBrush(gradient)

        elif style == 'lilac':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 190, 255))
            gradient.setColorAt(1, QColor(210, 160, 240))
            painter.setBrush(gradient)

        elif style == 'honey':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 230, 150))
            gradient.setColorAt(1, QColor(255, 200, 100))
            painter.setBrush(gradient)

        elif style == 'turquoise':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(150, 240, 230))
            gradient.setColorAt(1, QColor(100, 210, 200))
            painter.setBrush(gradient)

        elif style == 'apricot':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 210, 170))
            gradient.setColorAt(1, QColor(255, 180, 140))
            painter.setBrush(gradient)

        elif style == 'periwinkle':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 200, 255))
            gradient.setColorAt(1, QColor(170, 170, 240))
            painter.setBrush(gradient)

        elif style == 'sage':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 230, 200))
            gradient.setColorAt(1, QColor(170, 200, 170))
            painter.setBrush(gradient)

        elif style == 'melon':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 180, 150))
            gradient.setColorAt(1, QColor(255, 140, 110))
            painter.setBrush(gradient)

        elif style == 'powder_blue':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(180, 210, 255))
            gradient.setColorAt(1, QColor(150, 180, 240))
            painter.setBrush(gradient)

        elif style == 'pistachio':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 255, 180))
            gradient.setColorAt(1, QColor(170, 230, 150))
            painter.setBrush(gradient)

        elif style == 'blush':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 190, 200))
            gradient.setColorAt(1, QColor(255, 160, 170))
            painter.setBrush(gradient)

        elif style == 'mauve':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 180, 230))
            gradient.setColorAt(1, QColor(220, 150, 210))
            painter.setBrush(gradient)

        elif style == 'cream':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 250, 220))
            gradient.setColorAt(1, QColor(255, 240, 180))
            painter.setBrush(gradient)

        elif style == 'teal':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(150, 230, 220))
            gradient.setColorAt(1, QColor(100, 200, 190))
            painter.setBrush(gradient)

        elif style == 'salmon':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 180, 170))
            gradient.setColorAt(1, QColor(255, 140, 130))
            painter.setBrush(gradient)

        elif style == 'orchid':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 170, 240))
            gradient.setColorAt(1, QColor(210, 140, 220))
            painter.setBrush(gradient)

        elif style == 'mint_blue':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(170, 240, 240))
            gradient.setColorAt(1, QColor(140, 210, 210))
            painter.setBrush(gradient)

        elif style == 'pear':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 255, 170))
            gradient.setColorAt(1, QColor(190, 230, 140))
            painter.setBrush(gradient)

        elif style == 'rose_gold':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 220, 200))
            gradient.setColorAt(1, QColor(240, 180, 160))
            painter.setBrush(gradient)

        elif style == 'lavender_gray':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 220, 240))
            gradient.setColorAt(1, QColor(210, 200, 220))
            painter.setBrush(gradient)

        elif style == 'honeydew':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(240, 255, 220))
            gradient.setColorAt(1, QColor(220, 240, 190))
            painter.setBrush(gradient)

        elif style == 'peach_puff':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 210, 180))
            gradient.setColorAt(1, QColor(255, 180, 150))
            painter.setBrush(gradient)

        elif style == 'azure':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 230, 255))
            gradient.setColorAt(1, QColor(170, 200, 240))
            painter.setBrush(gradient)

        elif style == 'pale_green':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 255, 220))
            gradient.setColorAt(1, QColor(190, 230, 190))
            painter.setBrush(gradient)

        elif style == 'light_coral':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 200, 200))
            gradient.setColorAt(1, QColor(255, 170, 170))
            painter.setBrush(gradient)

        elif style == 'thistle':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 200, 240))
            gradient.setColorAt(1, QColor(220, 170, 220))
            painter.setBrush(gradient)

        elif style == 'wheat':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 230, 200))
            gradient.setColorAt(1, QColor(240, 210, 170))
            painter.setBrush(gradient)

        elif style == 'light_cyan':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(200, 255, 255))
            gradient.setColorAt(1, QColor(170, 230, 230))
            painter.setBrush(gradient)

        elif style == 'pale_turquoise':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 240, 240))
            gradient.setColorAt(1, QColor(170, 210, 210))
            painter.setBrush(gradient)

        elif style == 'light_pink':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 210, 220))
            gradient.setColorAt(1, QColor(255, 180, 190))
            painter.setBrush(gradient)

        elif style == 'light_salmon':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 200, 180))
            gradient.setColorAt(1, QColor(255, 170, 150))
            painter.setBrush(gradient)

        elif style == 'light_skyblue':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 220, 255))
            gradient.setColorAt(1, QColor(150, 190, 240))
            painter.setBrush(gradient)

        elif style == 'light_green':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 255, 200))
            gradient.setColorAt(1, QColor(170, 230, 170))
            painter.setBrush(gradient)

        elif style == 'plum':
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(240, 180, 240))
            gradient.setColorAt(1, QColor(220, 150, 220))
            painter.setBrush(gradient)

        elif style == 'bisque':
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 220, 190))
            gradient.setColorAt(1, QColor(255, 200, 160))
            painter.setBrush(gradient)

        else:
            # Стандартный красный
            painter.setBrush(QColor(255, 0, 0))

    @staticmethod
    def _apply_decoration(painter, x, y, radius, decoration, style):
        """Применение дополнительного оформления"""
        if decoration == 'none':
            return

        elif decoration == 'double_border':
            # Двойная рамка
            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
            # Возвращаем оригинальную кисть
            DrawingElements._apply_note_style(painter, x, y, radius, style)

        elif decoration == 'glow':
            # Свечение
            pen = QPen(QColor(255, 255, 255, 100))
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius - 2, y - radius - 2, (radius + 2) * 2, (radius + 2) * 2)
            # Возвращаем оригинальную кисть
            DrawingElements._apply_note_style(painter, x, y, radius, style)

        elif decoration == 'shadow':
            # Тень
            pen = QPen(QColor(0, 0, 0, 80))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
            # Возвращаем оригинальную кисть
            DrawingElements._apply_note_style(painter, x, y, radius, style)

        elif decoration == 'sparkle':
            # Блестки (маленькие кружки по краю)
            sparkle_color = QColor(255, 255, 255, 200)
            painter.setBrush(sparkle_color)
            painter.setPen(Qt.NoPen)

            # Рисуем 4 блестки
            sparkle_radius = max(2, radius // 8)
            positions = [
                (x - radius + sparkle_radius, y - radius + sparkle_radius),
                (x + radius - sparkle_radius, y - radius + sparkle_radius),
                (x - radius + sparkle_radius, y + radius - sparkle_radius),
                (x + radius - sparkle_radius, y + radius - sparkle_radius)
            ]

            for pos_x, pos_y in positions:
                painter.drawEllipse(pos_x, pos_y, sparkle_radius * 2, sparkle_radius * 2)

            # Возвращаем оригинальную кисть
            DrawingElements._apply_note_style(painter, x, y, radius, style)

        elif decoration == 'dotted_border':
            # Пунктирная рамка
            pen = QPen(QColor(255, 255, 255))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 1, y - radius + 1, (radius - 1) * 2, (radius - 1) * 2)
            # Возвращаем оригинальную кисть
            DrawingElements._apply_note_style(painter, x, y, radius, style)

    @staticmethod
    def _draw_note_text(painter, x, y, radius, text1, text2, style):
        """Рисование текста на ноте с учетом стиля"""
        texts = []
        if text1:
            texts.append(text1)
        if text2:
            texts.append(text2)

        if texts:
            text = "\n".join(texts)
            font_size = max(8, radius // 2)
            font = QFont("Arial", font_size, QFont.Bold)
            painter.setFont(font)

            # Выбираем цвет текста в зависимости от стиля
            if style in ['glass', 'ice', 'metal', 'cream', 'honeydew', 'light_cyan',
                         'pale_turquoise', 'light_green', 'bisque', 'wheat']:
                text_color = QColor(0, 0, 0)  # Черный для светлых стилей
            else:
                text_color = QColor(255, 255, 255)  # Белый для темных стилей

            painter.setPen(text_color)

            font_metrics = QFontMetrics(painter.font())
            text_width = font_metrics.width(text.split('\n')[0])
            text_height = font_metrics.height() * len(texts)

            text_x = x - text_width // 2
            text_y = y + text_height // (len(texts) * 2)

            painter.drawText(text_x, text_y, text)

    @staticmethod
    def draw_barre(painter, barre):
        """Рисование баре (закругленный прямоугольник)"""
        x, y, width, height, radius, color = (
            barre['x'], barre['y'], barre['width'],
            barre['height'], barre['radius'], barre['color']
        )

        painter.setBrush(QColor(*color))
        painter.setPen(QColor(0, 0, 0))
        painter.drawRoundedRect(
            x - width // 2,
            y - height // 2,
            width,
            height,
            radius,
            radius
        )