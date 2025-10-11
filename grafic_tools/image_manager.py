import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt


class ImageManager:
    """Класс для управления изображениями"""

    def __init__(self, parent):
        self.parent = parent
        self.image = None
        self.current_image_path = None

    def load_image(self):
        """Загрузка изображения"""
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Открыть изображение грифа",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.display_image(file_name)

    def display_image(self, file_path):
        """Отображение изображения"""
        self.current_image_path = file_path
        self.image = QPixmap(file_path)

        if not self.image.isNull():
            # Масштабируем изображение под размер label
            scaled_pixmap = self.image.scaled(
                self.parent.image_label.width(),
                self.parent.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.parent.image_label.setPixmap(scaled_pixmap)
        else:
            QMessageBox.warning(self.parent, "Ошибка", "Не удалось загрузить изображение")

    def save_image(self, elements, draw_function):
        """Сохранение изображения с нарисованными элементами"""
        if not self.image:
            QMessageBox.warning(self.parent, "Ошибка", "Нет изображения для сохранения")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Сохранить изображение",
            "chord_diagram.png",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_name:
            # Создаем копию изображения для рисования
            result_image = QPixmap(self.image)
            painter = QPainter(result_image)

            # Рисуем все элементы
            draw_function(painter)

            painter.end()

            # Сохраняем изображение
            result_image.save(file_name)
            QMessageBox.information(self.parent, "Успех", f"Изображение сохранено: {file_name}")