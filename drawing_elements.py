from PyQt5.QtGui import QPainter, QFont, QPen, QBrush, QColor, QLinearGradient, QRadialGradient
from PyQt5.QtCore import Qt


class DrawingElements:

    @staticmethod
    def get_color_from_data(color_data):
        """Получение QColor из данных цвета"""
        if isinstance(color_data, list) and len(color_data) >= 3:
            return QColor(color_data[0], color_data[1], color_data[2])
        return QColor(0, 0, 0)

    @staticmethod
    def get_brush_from_style(style_name, x=0, y=0, radius=0, width=0, height=0):
        """Получение кисти на основе стиля с поддержкой градиентов"""
        if style_name == "wood":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(210, 180, 140))
            gradient.setColorAt(0.5, QColor(160, 120, 80))
            gradient.setColorAt(1, QColor(210, 180, 140))
            return QBrush(gradient)
        elif style_name == "metal":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(200, 200, 200))
            gradient.setColorAt(0.5, QColor(100, 100, 100))
            gradient.setColorAt(1, QColor(200, 200, 200))
            return QBrush(gradient)
        elif style_name == "rubber":
            gradient = QRadialGradient(x + width / 2, y + height / 2, max(width, height))
            gradient.setColorAt(0, QColor(80, 80, 80))
            gradient.setColorAt(1, QColor(40, 40, 40))
            return QBrush(gradient)
        elif style_name == "gradient":
            gradient = QLinearGradient(x, y, x + width, y + height)
            gradient.setColorAt(0, QColor(189, 183, 107))
            lighter = QColor(189, 183, 107).lighter(150)
            gradient.setColorAt(1, QColor(lighter.red(), lighter.green(), lighter.blue()))
            return QBrush(gradient)
        elif style_name == "striped":
            return QBrush(QColor(189, 183, 107))

        # Стили для нот (50+ вариантов)
        elif style_name == "default":
            return QBrush(QColor(255, 0, 0))
        elif style_name == "blue_gradient":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(100, 150, 255))
            gradient.setColorAt(1, QColor(50, 100, 200))
            return QBrush(gradient)
        elif style_name == "red_3d":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 150, 150))
            gradient.setColorAt(0.7, QColor(220, 50, 50))
            gradient.setColorAt(1, QColor(180, 0, 0))
            return QBrush(gradient)
        elif style_name == "green_3d":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 180))
            gradient.setColorAt(0.7, QColor(80, 200, 80))
            gradient.setColorAt(1, QColor(40, 160, 40))
            return QBrush(gradient)
        elif style_name == "purple_3d":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(230, 200, 255))
            gradient.setColorAt(0.7, QColor(180, 100, 230))
            gradient.setColorAt(1, QColor(140, 60, 200))
            return QBrush(gradient)
        elif style_name == "gold_3d":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(255, 230, 100))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(230, 170, 30))
            return QBrush(gradient)
        elif style_name == "glass":
            return QBrush(QColor(255, 255, 255, 180))
        elif style_name == "fire":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 255, 150))
            gradient.setColorAt(0.5, QColor(255, 200, 50))
            gradient.setColorAt(1, QColor(255, 100, 0))
            return QBrush(gradient)
        elif style_name == "ice":
            gradient = QLinearGradient(x - radius, y - radius, x + radius, y + radius)
            gradient.setColorAt(0, QColor(200, 230, 255))
            gradient.setColorAt(0.5, QColor(150, 200, 255))
            gradient.setColorAt(1, QColor(100, 170, 255))
            return QBrush(gradient)
        elif style_name == "soft_pink":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(255, 200, 220))
            gradient.setColorAt(0.7, QColor(255, 150, 180))
            gradient.setColorAt(1, QColor(230, 100, 150))
            return QBrush(gradient)
        elif style_name == "mint_green":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(180, 255, 180))
            gradient.setColorAt(0.7, QColor(120, 230, 120))
            gradient.setColorAt(1, QColor(80, 200, 80))
            return QBrush(gradient)
        elif style_name == "lavender":
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(220, 200, 255))
            gradient.setColorAt(0.7, QColor(180, 160, 240))
            gradient.setColorAt(1, QColor(140, 120, 220))
            return QBrush(gradient)
        # Добавьте остальные 40+ стилей по аналогии...

        return QBrush(QColor(255, 0, 0))  # Красный по умолчанию

    @staticmethod
    def draw_fret(painter, fret_data):
        """Рисование лада с улучшенными стилями"""
        x = fret_data.get('x', 0)
        y = fret_data.get('y', 0)
        size = fret_data.get('size', 60)
        symbol = fret_data.get('symbol', 'I')
        color = DrawingElements.get_color_from_data(fret_data.get('color'))
        style = fret_data.get('style', 'default')

        # Применяем стили текста
        if style == 'gradient_text':
            gradient = QLinearGradient(x - size, y - size, x + size, y + size)
            gradient.setColorAt(0, QColor(255, 100, 100))
            gradient.setColorAt(0.5, color)
            gradient.setColorAt(1, QColor(100, 100, 255))
            painter.setPen(QPen(gradient, 2))
        elif style == 'shadow':
            shadow_color = QColor(0, 0, 0, 100)
            painter.setPen(QPen(shadow_color, 3))
        elif style == 'gold_embossed':
            gradient = QLinearGradient(x - size, y - size, x + size, y + size)
            gradient.setColorAt(0, QColor(255, 215, 0))
            gradient.setColorAt(0.5, QColor(218, 165, 32))
            gradient.setColorAt(1, QColor(184, 134, 11))
            painter.setPen(QPen(gradient, 3))
        else:
            painter.setPen(QPen(color, 2))

        font = QFont(fret_data.get('font_family', 'Times New Roman'))
        font.setPointSize(size)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(x, y, symbol)

    @staticmethod
    def draw_note(painter, note_data):
        """Рисование ноты/пальца со всеми стилями"""
        x = note_data.get('x', 0)
        y = note_data.get('y', 0)
        radius = note_data.get('radius', 52)
        style = note_data.get('style', 'red_3d')
        text_color = DrawingElements.get_color_from_data(note_data.get('text_color', [255, 255, 255]))

        # Определяем отображаемый текст
        display_text = note_data.get('display_text', 'finger')
        if display_text == 'note_name':
            symbol = note_data.get('note_name', '')
        elif display_text == 'symbol':
            symbol = note_data.get('symbol', '')
        else:  # finger
            symbol = note_data.get('finger', '1')

        # Устанавливаем кисть на основе стиля
        brush = DrawingElements.get_brush_from_style(style, x, y, radius)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(brush)

        # Рисуем круг
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Рисуем текст внутри круга
        if symbol:
            painter.setPen(QPen(text_color))
            font = QFont()
            font.setPointSize(max(10, radius // 2))
            font.setBold(True)
            painter.setFont(font)

            # Центрируем текст
            text_rect = painter.fontMetrics().boundingRect(symbol)
            text_x = x - text_rect.width() // 2
            text_y = y + text_rect.height() // 4

            painter.drawText(text_x, text_y, symbol)

        # Применяем декорации
        decoration = note_data.get('decoration', 'none')
        if decoration == 'double_border':
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius + 2, y - radius + 2, (radius - 2) * 2, (radius - 2) * 2)
        elif decoration == 'glow':
            painter.setPen(QPen(QColor(255, 255, 255, 100), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(x - radius - 2, y - radius - 2, (radius + 2) * 2, (radius + 2) * 2)

    @staticmethod
    def draw_barre(painter, barre_data):
        """Рисование баре с правильными стилями и размерами"""
        x = barre_data.get('x', 0)
        y = barre_data.get('y', 0)
        width = barre_data.get('width', 100)
        height = barre_data.get('height', 20)  # Исправляем высоту - должна быть небольшой
        radius = barre_data.get('radius', 10)
        style = barre_data.get('style', 'wood')
        decoration = barre_data.get('decoration', 'none')

        # Получаем кисть с учетом координат для градиентов
        brush = DrawingElements.get_brush_from_style(style, x, y, 0, width, height)

        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(brush)

        # Рисуем закругленный прямоугольник для баре
        if radius > 0:
            painter.drawRoundedRect(x, y, width, height, radius, radius)
        else:
            painter.drawRect(x, y, width, height)

        # Применяем декорации
        if decoration == 'shadow':
            painter.setPen(QPen(QColor(0, 0, 0, 80), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(x + 2, y + 2, width, height, radius, radius)
        elif decoration == 'glow':
            painter.setPen(QPen(QColor(255, 255, 255, 60), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(x - 1, y - 1, width + 2, height + 2, radius, radius)
        elif decoration == 'stripes' and style == 'striped':
            stripe_color = QColor(189, 183, 107).darker(120)
            painter.setPen(QPen(stripe_color, 1))
            stripe_spacing = height // 4
            for i in range(1, 4):
                stripe_y = y + i * stripe_spacing
                painter.drawLine(x + 2, stripe_y, x + width - 2, stripe_y)