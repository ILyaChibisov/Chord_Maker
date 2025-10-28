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
        self.current_scale_type = "small1"  # small1, small2, medium1, medium2 или original
        self.current_fret_type = "roman"  # roman или numeric
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

        # Комбобокс выбора масштаба (НОВЫЙ)
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Маленький 1", "Маленький 2", "Средний 1", "Средний 2", "Оригинальный размер"])
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        top_layout.addWidget(QLabel("Масштаб:"))
        top_layout.addWidget(self.scale_combo)

        # Комбобокс выбора типа отображения
        self.display_type_combo = QComboBox()
        self.display_type_combo.addItems(["Пальцы", "Ноты"])
        self.display_type_combo.currentTextChanged.connect(self.on_display_type_changed)
        top_layout.addWidget(QLabel("Тип:"))
        top_layout.addWidget(self.display_type_combo)

        # Комбобокс выбора типа ладов (НОВЫЙ)
        self.fret_type_combo = QComboBox()
        self.fret_type_combo.addItems(["Римские", "Обычные"])
        self.fret_type_combo.currentTextChanged.connect(self.on_fret_type_changed)
        top_layout.addWidget(QLabel("Лад:"))
        top_layout.addWidget(self.fret_type_combo)

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

        # Кнопка обновления конфигурации (НОВАЯ)
        self.refresh_button = QPushButton("Обновить конфигурацию")
        self.refresh_button.setFixedSize(150, 30)
        self.refresh_button.clicked.connect(self.refresh_configuration)
        top_layout.addWidget(self.refresh_button)

        top_layout.setSpacing(5)

        layout.addLayout(top_layout)

        # Область для изображения с прокруткой
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_label.setText("Загрузка...")
        self.image_label.setMinimumSize(400, 300)  # Оригинальный минимальный размер
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

    def refresh_configuration(self):
        """Обновление конфигурации из Excel файла"""
        try:
            print("🔄 Обновление конфигурации...")

            # Сохраняем текущее состояние
            current_group = self.current_group
            current_chord = self.current_chord

            # Перезагружаем данные
            if self.config_manager.load_config_data():
                # Перезагружаем изображение
                if os.path.exists(self.config_manager.image_path):
                    self.original_pixmap = QPixmap(self.config_manager.image_path)

                # Обновляем комбобокс групп
                groups = self.config_manager.get_chord_groups()
                self.group_combo.clear()
                self.group_combo.addItems(groups)

                if groups:
                    # Пытаемся восстановить предыдущее состояние
                    if current_group in groups:
                        self.current_group = current_group
                        self.group_combo.setCurrentText(current_group)
                    else:
                        self.current_group = groups[0]
                        self.group_combo.setCurrentText(groups[0])

                    self.load_chord_buttons()

                    # Пытаемся восстановить предыдущий аккорд
                    if current_chord:
                        chord_names = [chord['name'] for chord in self.current_chords]
                        if current_chord['name'] in chord_names:
                            # Находим и активируем кнопку нужного аккорда
                            index = chord_names.index(current_chord['name'])
                            self.current_chord = self.current_chords[index]
                            self.display_chord(self.current_chord)
                        else:
                            # Показываем первый аккорд группы
                            self.current_chord = self.current_chords[0]
                            self.display_chord(self.current_chord)
                    else:
                        # Показываем первый аккорд группы
                        self.current_chord = self.current_chords[0]
                        self.display_chord(self.current_chord)
                else:
                    self.image_label.setText("Группы аккордов не найдены после обновления")

                QMessageBox.information(self, "Успех", "Конфигурация успешно обновлена из Excel файла!")
                print("✅ Конфигурация обновлена успешно")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить конфигурацию из Excel файла")
                print("❌ Ошибка обновления конфигурации")

        except Exception as e:
            error_msg = f"Ошибка при обновлении конфигурации: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()

    def display_original_image(self):
        """Отображение оригинального изображения при запуске с масштабированием"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            # Масштабируем изображение для отображения (оригинальный размер)
            scaled_pixmap = self.original_pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            print(
                f"📏 Оригинальное изображение: {self.original_pixmap.width()}x{self.original_pixmap.height()} -> {scaled_pixmap.width()}x{scaled_pixmap.height()}")

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

        # АВТОМАТИЧЕСКИ ЗАГРУЖАЕМ ПЕРВЫЙ АККОРД ГРУППЫ
        if self.current_chords:
            self.current_chord = self.current_chords[0]
            self.display_chord(self.current_chord)

    def on_scale_changed(self, scale_type):
        """Обработчик изменения масштаба"""
        if scale_type == "Маленький 1":
            self.current_scale_type = "small1"
        elif scale_type == "Маленький 2":
            self.current_scale_type = "small2"
        elif scale_type == "Средний 1":
            self.current_scale_type = "medium1"
        elif scale_type == "Средний 2":
            self.current_scale_type = "medium2"
        else:
            self.current_scale_type = "original"

        if self.current_chord:
            self.display_chord(self.current_chord)
        elif self.original_pixmap:
            self.display_original_image()

    def on_display_type_changed(self, display_type):
        """Обработчик изменения типа отображения"""
        self.current_display_type = "fingers" if display_type == "Пальцы" else "notes"
        if self.current_chord:
            self.display_chord(self.current_chord)

    def on_fret_type_changed(self, fret_type):
        """Обработчик изменения типа отображения ладов"""
        self.current_fret_type = "roman" if fret_type == "Римские" else "numeric"
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
        """Отображение выбранного аккорда на изображении с выбранным масштабом"""
        try:
            if not self.original_pixmap or self.original_pixmap.isNull():
                self.image_label.setText("Ошибка: изображение не загружено")
                return

            # Получаем область обрезки из RAM для этого конкретного аккорда
            ram_key = chord_info['data'].get('RAM')
            crop_rect = self.config_manager.get_ram_crop_area(ram_key)

            print(f"🎯 Оригинальное изображение: {self.original_pixmap.width()}x{self.original_pixmap.height()}")
            print(f"🎯 Область обрезки для RAM '{ram_key}': {crop_rect}")

            # Получаем элементы для отображения
            elements = self.config_manager.get_chord_elements(
                chord_info['data'],
                self.current_display_type
            )

            print(f"🎯 Отображение аккорда: {chord_info['name']}")
            print(f"📊 Найдено элементов: {len(elements)}")

            # Преобразуем символы ладов в зависимости от выбранного типа
            if self.current_fret_type == "numeric":
                elements = self.convert_frets_to_numeric(elements)

            # ВСЕГДА используем обрезку по RAM, если она определена
            if crop_rect:
                crop_x, crop_y, crop_width, crop_height = crop_rect

                # Проверяем границы и корректируем при необходимости
                crop_x = max(0, min(crop_x, self.original_pixmap.width() - 1))
                crop_y = max(0, min(crop_y, self.original_pixmap.height() - 1))
                crop_width = max(1, min(crop_width, self.original_pixmap.width() - crop_x))
                crop_height = max(1, min(crop_height, self.original_pixmap.height() - crop_y))

                print(f"🎯 Финальная область обрезки: ({crop_x}, {crop_y}, {crop_width}, {crop_height})")

                # СОЗДАЕМ НОВОЕ ИЗОБРАЖЕНИЕ РАЗМЕРОМ С ОБЛАСТЬ ОБРЕЗКИ
                result_pixmap = QPixmap(crop_width, crop_height)
                result_pixmap.fill(Qt.white)  # Белый фон

                # Создаем painter для нового изображения
                painter = QPainter(result_pixmap)

                # Копируем область из оригинального изображения
                painter.drawPixmap(0, 0, self.original_pixmap,
                                   crop_x, crop_y, crop_width, crop_height)

                # Рисуем элементы на НОВОМ изображении с правильными координатами
                self.config_manager.draw_elements_on_canvas(
                    painter, elements, (crop_x, crop_y, crop_width, crop_height)
                )
                painter.end()

                # Применяем выбранный масштаб
                if self.current_scale_type == "small1":
                    # МАЛЕНЬКИЙ 1 - как было раньше (авто масштаб)
                    display_width = min(400, crop_width)
                    scale_factor = display_width / crop_width
                    display_height = int(crop_height * scale_factor)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Маленький 1: {crop_width}x{crop_height} -> {display_width}x{display_height}")

                elif self.current_scale_type == "small2":
                    # МАЛЕНЬКИЙ 2 - 30% от оригинального
                    display_width = int(crop_width * 0.3)
                    display_height = int(crop_height * 0.3)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Маленький 2 (30%): {crop_width}x{crop_height} -> {display_width}x{display_height}")

                elif self.current_scale_type == "medium1":
                    # СРЕДНИЙ 1 - 50% от оригинального
                    display_width = int(crop_width * 0.5)
                    display_height = int(crop_height * 0.5)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Средний 1 (50%): {crop_width}x{crop_height} -> {display_width}x{display_height}")

                elif self.current_scale_type == "medium2":
                    # СРЕДНИЙ 2 - 70% от оригинального
                    display_width = int(crop_width * 0.7)
                    display_height = int(crop_height * 0.7)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Средний 2 (70%): {crop_width}x{crop_height} -> {display_width}x{display_height}")

                else:
                    # ОРИГИНАЛЬНЫЙ РАЗМЕР
                    self.image_label.setPixmap(result_pixmap)
                    print(f"📏 Оригинальный размер: {crop_width}x{crop_height}")

            else:
                # Если нет обрезки, рисуем на полном изображении
                result_pixmap = self.config_manager.draw_elements_on_image(
                    self.original_pixmap, elements, None
                )

                # Применяем выбранный масштаб
                if self.current_scale_type == "small1":
                    # МАЛЕНЬКИЙ 1
                    scaled_pixmap = result_pixmap.scaled(
                        self.image_label.width(),
                        self.image_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Маленький 1 полного изображения")

                elif self.current_scale_type == "small2":
                    # МАЛЕНЬКИЙ 2 - 30% от оригинального
                    display_width = int(result_pixmap.width() * 0.3)
                    display_height = int(result_pixmap.height() * 0.3)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Маленький 2 (30%) полного изображения")

                elif self.current_scale_type == "medium1":
                    # СРЕДНИЙ 1 - 50% от оригинального
                    display_width = int(result_pixmap.width() * 0.5)
                    display_height = int(result_pixmap.height() * 0.5)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Средний 1 (50%) полного изображения")

                elif self.current_scale_type == "medium2":
                    # СРЕДНИЙ 2 - 70% от оригинального
                    display_width = int(result_pixmap.width() * 0.7)
                    display_height = int(result_pixmap.height() * 0.7)

                    scaled_pixmap = result_pixmap.scaled(
                        display_width,
                        display_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"📏 Средний 2 (70%) полного изображения")

                else:
                    # ОРИГИНАЛЬНЫЙ РАЗМЕР
                    self.image_label.setPixmap(result_pixmap)
                    print(f"📏 Оригинальный размер полного изображения")

        except Exception as e:
            self.image_label.setText(f"Ошибка отображения: {str(e)}")
            print(f"Ошибка при отображении аккорда: {e}")
            import traceback
            traceback.print_exc()

    def convert_frets_to_numeric(self, elements):
        """Преобразование римских цифр ладов в обычные цифры"""
        roman_to_numeric = {
            'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
            'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10',
            'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15',
            'XVI': '16'
        }

        converted_elements = []
        for element in elements:
            if element['type'] == 'fret':
                # Создаем копию данных элемента
                converted_element = element.copy()
                fret_data = converted_element['data'].copy()

                # Преобразуем символ лада
                original_symbol = fret_data.get('symbol', 'I')
                if original_symbol in roman_to_numeric:
                    fret_data['symbol'] = roman_to_numeric[original_symbol]
                    print(f"🎯 Преобразован лад: {original_symbol} -> {fret_data['symbol']}")

                converted_element['data'] = fret_data
                converted_elements.append(converted_element)
            else:
                # Для других типов элементов оставляем как есть
                converted_elements.append(element)

        return converted_elements