from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics
from PyQt5.QtCore import Qt


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
        """Рисование ноты (круг с текстом)"""
        x, y, radius, color = note['x'], note['y'], note['radius'], note['color']
        finger, note_name = note['finger'], note['note_name']

        # Рисуем круг
        painter.setBrush(QColor(*color))
        painter.setPen(QColor(0, 0, 0))
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Подготавливаем текст
        texts = []
        if finger:
            texts.append(finger)
        if note_name:
            texts.append(note_name)

        if texts:
            text = "\n".join(texts)
            font_size = max(8, radius // 2)  # Минимальный размер шрифта
            font = QFont("Arial", font_size, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))  # Белый цвет текста

            font_metrics = QFontMetrics(painter.font())
            text_width = font_metrics.width(text.split('\n')[0])  # Ширина самой длинной строки
            text_height = font_metrics.height() * len(texts)

            text_x = x - text_width // 2
            text_y = y + text_height // (len(texts) * 2)

            painter.drawText(text_x, text_y, text)

    @staticmethod
    def draw_open_note(painter, open_note):
        """Рисование открытой ноты"""
        x, y, radius, color = open_note['x'], open_note['y'], open_note['radius'], open_note['color']
        symbol, note_name = open_note['symbol'], open_note['note_name']

        # Рисуем круг
        painter.setBrush(QColor(*color))
        painter.setPen(QColor(0, 0, 0))
        painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        # Подготавливаем текст
        texts = []
        if symbol:
            texts.append(symbol)
        if note_name:
            texts.append(note_name)

        if texts:
            text = "\n".join(texts)
            font_size = max(8, radius // 2)
            font = QFont("Arial", font_size, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))

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