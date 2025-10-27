from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QLabel, QScrollArea, QGridLayout,
                             QGroupBox, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
import os
import pandas as pd

from chord_config_manager import ChordConfigManager


class ChordConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ChordConfigManager()
        self.current_display_type = "fingers"  # fingers или notes
        self.current_group = None
        self.current_chords = []
        self.current_chord = None
        self.original_pixmap = None  # Сохраняем оригинальное изображение

        self.initUI()
        self.load_configuration()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Верхняя панель с настройками - ВСЕ В ОДНУ СТРОКУ
        top_layout = QHBoxLayout()

        # Комбобокс выбора типа отображения
        self.display_type_combo = QComboBox()
        self.display_type_combo.addItems(["Пальцы", "Ноты"])
        self.display_type_combo.currentTextChanged.connect(self.on_display_type_changed)
        top_layout.addWidget(QLabel("Тип:"))
        top_layout.addWidget(self.display_type_combo)

        # Комбобокс выбора группы аккордов
        self.group_combo = QComboBox()
        self.group_combo.currentTextChanged.connect(self.on_group_changed)
        top_layout.addWidget(QLabel("Группа:"))
        top_layout.addWidget(self.group_combo)

        # Область для кнопок аккордов - ТОЖЕ В ЭТУ ЖЕ СТРОКУ
        top_layout.addWidget(QLabel("Аккорды:"))

        # Scroll area для кнопок аккордов
        self.chords_scroll = QScrollArea()
        self.chords_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chords_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chords_scroll.setFixedHeight(45)  # Минимальная высота
        self.chords_widget = QWidget()
        self.chords_layout = QHBoxLayout(self.chords_widget)  # Горизонтальный layout
        self.chords_layout.setContentsMargins(5, 5, 5, 5)
        self.chords_layout.setSpacing(3)  # Минимальный отступ между кнопками
        self.chords_scroll.setWidget(self.chords_widget)
        self.chords_scroll.setWidgetResizable(True)

        top_layout.addWidget(self.chords_scroll, 1)  # Растягиваем на оставшееся место
        top_layout.setSpacing(5)

        layout.addLayout(top_layout)

        # Область для изображения с прокруткой
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Выравнивание по верхнему левому углу
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_label.setText("Загрузка...")
        self.image_scroll.setWidget(self.image_label)
        layout.addWidget(self.image_scroll, 1)  # Растягиваем область с изображением

    def load_configuration(self):
        """Загрузка конфигурации"""
        if self.config_manager.load_config_data():
            # Загружаем оригинальное изображение
            if os.path.exists(self.config_manager.image_path):
                self.original_pixmap = QPixmap(self.config_manager.image_path)
                if not self.original_pixmap.isNull():
                    # Показываем оригинальное изображение при запуске
                    self.display_original_image()
                else:
                    self.image_label.setText("Ошибка загрузки изображения")
            else:
                self.image_label.setText(f"Изображение не найдено: {self.config_manager.image_path}")

            # Заполняем комбобокс групп
            groups = self.config_manager.get_chord_groups()
            self.group_combo.clear()
            self.group_combo.addItems(groups)

            if groups:
                self.current_group = groups[0]
                self.load_chord_buttons()
            else:
                self.image_label.setText("Группы аккордов не найдены")
        else:
            self.image_label.setText("Ошибка загрузки конфигурации. Проверьте файлы в папке templates2")

    def display_original_image(self):
        """Отображение оригинального изображения при запуске БЕЗ масштабирования"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # Устанавливаем изображение в оригинальном размере
            self.image_label.setPixmap(self.original_pixmap)
            self.image_label.resize(self.original_pixmap.size())
            print(f"📏 Оригинальное изображение: {self.original_pixmap.width()}x{self.original_pixmap.height()}")

    def load_chord_buttons(self):
        """Загрузка кнопок аккордов для текущей группы"""
        # Очищаем layout
        for i in reversed(range(self.chords_layout.count())):
            widget = self.chords_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Получаем аккорды для текущей группы
        self.current_chords = self.config_manager.get_chords_by_group(self.current_group)

        if not self.current_chords:
            label = QLabel("Аккорды не найдены")
            self.chords_layout.addWidget(label)
            return

        # Создаем кнопки - все в одну строку
        for chord_info in self.current_chords:
            btn = QPushButton(chord_info['name'])
            btn.setFixedSize(50, 30)  # Фиксированный маленький размер
            btn.setStyleSheet("font-size: 10px;")  # Маленький шрифт
            btn.clicked.connect(lambda checked, c=chord_info: self.on_chord_clicked(c))
            self.chords_layout.addWidget(btn)

    def on_display_type_changed(self, display_type):
        """Обработчик изменения типа отображения"""
        self.current_display_type = "fingers" if display_type == "Пальцы" else "notes"
        if self.current_chord:
            self.display_chord(self.current_chord)

    def on_group_changed(self, group):
        """Обработчик изменения группы аккордов"""
        self.current_group = group
        self.load_chord_buttons()

        # АВТОМАТИЧЕСКИ ЗАГРУЖАЕМ ПЕРВЫЙ АККОРД НОВОЙ ГРУППЫ
        if self.current_chords:
            self.current_chord = self.current_chords[0]
            self.display_chord(self.current_chord)
        else:
            self.current_chord = None
            if self.original_pixmap:
                self.display_original_image()
            else:
                self.image_label.setText("Аккорды не найдены")

    def on_chord_clicked(self, chord_info):
        """Обработчик клика по кнопке аккорда"""
        self.current_chord = chord_info
        self.display_chord(chord_info)

    def display_chord(self, chord_info):
        """Отображение выбранного аккорда на изображении размером с область обрезки"""
        try:
            if not self.original_pixmap or self.original_pixmap.isNull():
                self.image_label.setText("Ошибка: изображение не загружено")
                return

            # Получаем область обрезки из RAM для этого конкретного аккорда
            ram_key = chord_info['data'].get('RAM')
            crop_rect = self.config_manager.get_ram_crop_area(ram_key)

            # Получаем элементы для отображения
            elements = self.config_manager.get_chord_elements(
                chord_info['data'],
                self.current_display_type
            )

            print(f"🎯 Отображение аккорда: {chord_info['name']}")
            print(f"📊 Найдено элементов: {len(elements)}")
            print(f"🔧 RAM ключ: {ram_key}")
            print(f"📐 Область обрезки: {crop_rect}")

            # ВСЕГДА используем обрезку по RAM, если она определена
            if crop_rect:
                crop_x, crop_y, crop_width, crop_height = crop_rect

                # Проверяем границы и корректируем при необходимости
                crop_x = max(0, min(crop_x, self.original_pixmap.width() - 1))
                crop_y = max(0, min(crop_y, self.original_pixmap.height() - 1))
                crop_width = max(1, min(crop_width, self.original_pixmap.width() - crop_x))
                crop_height = max(1, min(crop_height, self.original_pixmap.height() - crop_y))

                # СОЗДАЕМ НОВОЕ ИЗОБРАЖЕНИЕ РАЗМЕРОМ С ОБЛАСТЬ ОБРЕЗКИ
                result_pixmap = QPixmap(crop_width, crop_height)
                result_pixmap.fill(Qt.white)  # Заполняем белым фоном

                # Копируем область из оригинального изображения
                painter = QPainter(result_pixmap)
                source_rect = (crop_x, crop_y, crop_width, crop_height)
                painter.drawPixmap(0, 0, self.original_pixmap,
                                   crop_x, crop_y, crop_width, crop_height)

                # Рисуем элементы на НОВОМ изображении с правильными координатами
                self.config_manager.draw_elements_on_canvas(
                    painter, elements, (crop_x, crop_y, crop_width, crop_height)
                )
                painter.end()

                # Устанавливаем изображение в ОРИГИНАЛЬНОМ РАЗМЕРЕ ОБЛАСТИ ОБРЕЗКИ
                if not result_pixmap.isNull():
                    self.image_label.setPixmap(result_pixmap)
                    self.image_label.resize(result_pixmap.size())
                    print(f"📏 Создано изображение размером: {crop_width}x{crop_height}")
                else:
                    self.image_label.setText("Ошибка создания изображения")

            else:
                # Если нет обрезки, рисуем на полном изображении
                result_pixmap = self.config_manager.draw_elements_on_image(
                    self.original_pixmap, elements, None
                )
                self.image_label.setPixmap(result_pixmap)
                self.image_label.resize(result_pixmap.size())

        except Exception as e:
            self.image_label.setText(f"Ошибка отображения: {str(e)}")
            print(f"Ошибка при отображении аккорда: {e}")
            import traceback
            traceback.print_exc()