import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QComboBox, QFrame, QFileDialog,
    QMessageBox, QInputDialog, QAction, QToolBar, QMenu
)
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt

# Импорты из нашего пакета
from .templates_manager import TemplatesManager
from .drawing_elements import DrawingElements


class ProfessionalDrawingTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Профессиональное рисование аккордов")
        self.setGeometry(100, 100, 1000, 700)

        # Инициализация менеджера шаблонов с путем к templates2
        default_config_path = os.path.join("templates2", "template.json")
        self.templates_manager = TemplatesManager(default_config_path)

        # Хранилище элементов
        self.elements = {
            'frets': [],
            'notes': [],
            'open_notes': [],
            'barres': []
        }

        self.image = None
        self.current_image_path = None

        self.initUI()
        # Автоматически загружаем шаблоны при старте
        self.update_template_comboboxes()

    def initUI(self):
        """Инициализация пользовательского интерфейса"""
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_main_layout()
        self.setup_controls()
        self.hide_all_controls()

    def setup_menubar(self):
        """Настройка меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu('Файл')

        load_image_action = QAction('Загрузить изображение', self)
        load_image_action.triggered.connect(self.load_image)
        file_menu.addAction(load_image_action)

        save_image_action = QAction('Сохранить изображение', self)
        save_image_action.triggered.connect(self.save_image)
        file_menu.addAction(save_image_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Шаблоны
        templates_menu = menubar.addMenu('Шаблоны')

        load_template_action = QAction('Загрузить шаблон', self)
        load_template_action.triggered.connect(self.load_config_file)
        templates_menu.addAction(load_template_action)

        save_template_action = QAction('Сохранить шаблон', self)
        save_template_action.triggered.connect(self.save_config_file)
        templates_menu.addAction(save_template_action)

        reload_template_action = QAction('Обновить шаблоны', self)
        reload_template_action.triggered.connect(self.update_template_comboboxes)
        templates_menu.addAction(reload_template_action)

        # Меню Элементы
        elements_menu = menubar.addMenu('Элементы')

        frets_action = QAction("Лады", self)
        frets_action.triggered.connect(self.show_frets_controls)
        elements_menu.addAction(frets_action)

        notes_action = QAction("Ноты", self)
        notes_action.triggered.connect(self.show_notes_controls)
        elements_menu.addAction(notes_action)

        open_notes_action = QAction("Открытые ноты", self)
        open_notes_action.triggered.connect(self.show_open_notes_controls)
        elements_menu.addAction(open_notes_action)

        barre_action = QAction("Баре", self)
        barre_action.triggered.connect(self.show_barre_controls)
        elements_menu.addAction(barre_action)

        elements_menu.addSeparator()

        clear_action = QAction("Очистить все", self)
        clear_action.triggered.connect(self.clear_all_elements)
        elements_menu.addAction(clear_action)

    def setup_toolbar(self):
        """Настройка панели инструментов"""
        self.toolbar = QToolBar("Основные инструменты")
        self.addToolBar(self.toolbar)

        # Кнопки быстрого доступа
        self.clear_btn = QPushButton("Очистить все")
        self.clear_btn.clicked.connect(self.clear_all_elements)
        self.toolbar.addWidget(self.clear_btn)

        self.toolbar.addSeparator()

        self.load_template_btn = QPushButton("Загрузить шаблон")
        self.load_template_btn.clicked.connect(self.load_config_file)
        self.toolbar.addWidget(self.load_template_btn)

        self.save_template_btn = QPushButton("Сохранить шаблон")
        self.save_template_btn.clicked.connect(self.save_config_file)
        self.toolbar.addWidget(self.save_template_btn)

        self.reload_template_btn = QPushButton("Обновить")
        self.reload_template_btn.clicked.connect(self.update_template_comboboxes)
        self.toolbar.addWidget(self.reload_template_btn)

    # ... остальные методы setup_main_layout, setup_controls и т.д. остаются без изменений ...
    # (используйте код из предыдущего ответа для этих методов)

    def setup_main_layout(self):
        """Настройка основного layout"""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Область для изображения
        self.image_label = QLabel(self)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setFrameStyle(QFrame.Sunken | QFrame.Raised)
        self.image_label.setLineWidth(2)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Загрузите изображение грифа гитары")
        self.main_layout.addWidget(self.image_label)

    def setup_controls(self):
        """Настройка элементов управления для разных типов элементов"""
        self.setup_frets_controls()
        self.setup_notes_controls()
        self.setup_open_notes_controls()
        self.setup_barre_controls()

    def setup_frets_controls(self):
        """Элементы управления для ладов"""
        self.frets_widget = QWidget()
        self.frets_layout = QHBoxLayout(self.frets_widget)

        # Поля ввода
        self.fret_x_input = QLineEdit();
        self.fret_x_input.setPlaceholderText("X координата")
        self.fret_y_input = QLineEdit();
        self.fret_y_input.setPlaceholderText("Y координата")
        self.fret_size_input = QLineEdit();
        self.fret_size_input.setPlaceholderText("Размер шрифта");
        self.fret_size_input.setText("20")

        # Выбор символа
        self.fret_symbol_combo = QComboBox()
        self.fret_symbol_combo.addItems(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'])

        # Кнопки
        self.add_fret_button = QPushButton("Добавить лад")
        self.add_fret_button.clicked.connect(self.add_fret)

        self.remove_fret_button = QPushButton("Удалить лад")
        self.remove_fret_button.clicked.connect(self.remove_fret)

        self.save_fret_template_button = QPushButton("Сохранить шаблон")
        self.save_fret_template_button.clicked.connect(self.save_fret_template)

        # Комбобокс шаблонов
        self.fret_template_combo = QComboBox()
        self.fret_template_combo.setPlaceholderText("Шаблоны ладов")
        self.fret_template_combo.currentIndexChanged.connect(self.load_fret_template)

        # Добавляем все в layout
        widgets = [
            self.fret_x_input, self.fret_y_input, self.fret_size_input,
            self.fret_symbol_combo, self.add_fret_button, self.remove_fret_button,
            self.save_fret_template_button, self.fret_template_combo
        ]

        for widget in widgets:
            self.frets_layout.addWidget(widget)

        self.main_layout.addWidget(self.frets_widget)

    def setup_notes_controls(self):
        """Элементы управления для нот"""
        self.notes_widget = QWidget()
        self.notes_layout = QHBoxLayout(self.notes_widget)

        # Поля ввода
        self.note_x_input = QLineEdit();
        self.note_x_input.setPlaceholderText("X координата")
        self.note_y_input = QLineEdit();
        self.note_y_input.setPlaceholderText("Y координата")
        self.note_radius_input = QLineEdit();
        self.note_radius_input.setPlaceholderText("Радиус");
        self.note_radius_input.setText("15")
        self.note_color_input = QLineEdit();
        self.note_color_input.setPlaceholderText("Цвет R,G,B");
        self.note_color_input.setText("255,0,0")

        # Выбор пальца и ноты
        self.note_finger_combo = QComboBox()
        self.note_finger_combo.addItems(['', '1', '2', '3', '4', 'T'])

        self.note_name_combo = QComboBox()
        self.note_name_combo.addItems(['', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'])

        # Кнопки
        self.add_note_button = QPushButton("Добавить ноту")
        self.add_note_button.clicked.connect(self.add_note)

        self.remove_note_button = QPushButton("Удалить ноту")
        self.remove_note_button.clicked.connect(self.remove_note)

        self.save_note_template_button = QPushButton("Сохранить шаблон")
        self.save_note_template_button.clicked.connect(self.save_note_template)

        # Комбобокс шаблонов
        self.note_template_combo = QComboBox()
        self.note_template_combo.setPlaceholderText("Шаблоны нот")
        self.note_template_combo.currentIndexChanged.connect(self.load_note_template)

        # Добавляем все в layout
        widgets = [
            self.note_x_input, self.note_y_input, self.note_radius_input,
            self.note_color_input, self.note_finger_combo, self.note_name_combo,
            self.add_note_button, self.remove_note_button, self.save_note_template_button,
            self.note_template_combo
        ]

        for widget in widgets:
            self.notes_layout.addWidget(widget)

        self.main_layout.addWidget(self.notes_widget)

    def setup_open_notes_controls(self):
        """Элементы управления для открытых нот"""
        self.open_notes_widget = QWidget()
        self.open_notes_layout = QHBoxLayout(self.open_notes_widget)

        # Поля ввода
        self.open_note_x_input = QLineEdit();
        self.open_note_x_input.setPlaceholderText("X координата")
        self.open_note_y_input = QLineEdit();
        self.open_note_y_input.setPlaceholderText("Y координата")
        self.open_note_radius_input = QLineEdit();
        self.open_note_radius_input.setPlaceholderText("Радиус");
        self.open_note_radius_input.setText("15")
        self.open_note_color_input = QLineEdit();
        self.open_note_color_input.setPlaceholderText("Цвет R,G,B");
        self.open_note_color_input.setText("0,0,255")

        # Выбор символа и ноты
        self.open_note_symbol_combo = QComboBox()
        self.open_note_symbol_combo.addItems(['', 'X', 'O'])

        self.open_note_name_combo = QComboBox()
        self.open_note_name_combo.addItems(['', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'])

        # Кнопки
        self.add_open_note_button = QPushButton("Добавить открытую ноту")
        self.add_open_note_button.clicked.connect(self.add_open_note)

        self.remove_open_note_button = QPushButton("Удалить открытую ноту")
        self.remove_open_note_button.clicked.connect(self.remove_open_note)

        self.save_open_note_template_button = QPushButton("Сохранить шаблон")
        self.save_open_note_template_button.clicked.connect(self.save_open_note_template)

        # Комбобокс шаблонов
        self.open_note_template_combo = QComboBox()
        self.open_note_template_combo.setPlaceholderText("Шаблоны открытых нот")
        self.open_note_template_combo.currentIndexChanged.connect(self.load_open_note_template)

        # Добавляем все в layout
        widgets = [
            self.open_note_x_input, self.open_note_y_input, self.open_note_radius_input,
            self.open_note_color_input, self.open_note_symbol_combo, self.open_note_name_combo,
            self.add_open_note_button, self.remove_open_note_button,
            self.save_open_note_template_button, self.open_note_template_combo
        ]

        for widget in widgets:
            self.open_notes_layout.addWidget(widget)

        self.main_layout.addWidget(self.open_notes_widget)

    def setup_barre_controls(self):
        """Элементы управления для баре"""
        self.barre_widget = QWidget()
        self.barre_layout = QHBoxLayout(self.barre_widget)

        # Поля ввода
        self.barre_x_input = QLineEdit();
        self.barre_x_input.setPlaceholderText("X координата")
        self.barre_y_input = QLineEdit();
        self.barre_y_input.setPlaceholderText("Y координата")
        self.barre_width_input = QLineEdit();
        self.barre_width_input.setPlaceholderText("Ширина");
        self.barre_width_input.setText("100")
        self.barre_height_input = QLineEdit();
        self.barre_height_input.setPlaceholderText("Высота");
        self.barre_height_input.setText("20")
        self.barre_radius_input = QLineEdit();
        self.barre_radius_input.setPlaceholderText("Закругление");
        self.barre_radius_input.setText("10")
        self.barre_color_input = QLineEdit();
        self.barre_color_input.setPlaceholderText("Цвет R,G,B");
        self.barre_color_input.setText("189,183,107")

        # Кнопки
        self.add_barre_button = QPushButton("Добавить баре")
        self.add_barre_button.clicked.connect(self.add_barre)

        self.remove_barre_button = QPushButton("Удалить баре")
        self.remove_barre_button.clicked.connect(self.remove_barre)

        self.save_barre_template_button = QPushButton("Сохранить шаблон")
        self.save_barre_template_button.clicked.connect(self.save_barre_template)

        # Комбобокс шаблонов
        self.barre_template_combo = QComboBox()
        self.barre_template_combo.setPlaceholderText("Шаблоны баре")
        self.barre_template_combo.currentIndexChanged.connect(self.load_barre_template)

        # Добавляем все в layout
        widgets = [
            self.barre_x_input, self.barre_y_input, self.barre_width_input,
            self.barre_height_input, self.barre_radius_input, self.barre_color_input,
            self.add_barre_button, self.remove_barre_button, self.save_barre_template_button,
            self.barre_template_combo
        ]

        for widget in widgets:
            self.barre_layout.addWidget(widget)

        self.main_layout.addWidget(self.barre_widget)

    # Методы управления видимостью элементов управления
    def hide_all_controls(self):
        """Скрыть все элементы управления"""
        self.frets_widget.hide()
        self.notes_widget.hide()
        self.open_notes_widget.hide()
        self.barre_widget.hide()

    def show_frets_controls(self):
        """Показать элементы управления для ладов"""
        self.hide_all_controls()
        self.frets_widget.show()

    def show_notes_controls(self):
        """Показать элементы управления для нот"""
        self.hide_all_controls()
        self.notes_widget.show()

    def show_open_notes_controls(self):
        """Показать элементы управления для открытых нот"""
        self.hide_all_controls()
        self.open_notes_widget.show()

    def show_barre_controls(self):
        """Показать элементы управления для баре"""
        self.hide_all_controls()
        self.barre_widget.show()

    # Методы работы с изображениями
    def load_image(self):
        """Загрузка изображения"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
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
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")

    def save_image(self):
        """Сохранение изображения с нарисованными элементами"""
        if not self.image:
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить изображение",
            "chord_diagram.png",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_name:
            # Создаем копию изображения для рисования
            result_image = QPixmap(self.image)
            painter = QPainter(result_image)

            # Рисуем все элементы
            self.draw_all_elements(painter)
            painter.end()

            # Сохраняем
            if result_image.save(file_name):
                QMessageBox.information(self, "Успех", f"Изображение сохранено: {file_name}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изображение")

    # Методы добавления элементов
    def add_fret(self):
        """Добавление лада"""
        try:
            x = int(self.fret_x_input.text())
            y = int(self.fret_y_input.text())
            size = int(self.fret_size_input.text())
            symbol = self.fret_symbol_combo.currentText()

            self.elements['frets'].append({
                'x': x, 'y': y, 'size': size, 'symbol': symbol
            })
            self.repaint()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", "Проверьте правильность введенных данных")

    def add_note(self):
        """Добавление ноты"""
        try:
            x = int(self.note_x_input.text())
            y = int(self.note_y_input.text())
            radius = int(self.note_radius_input.text())
            color = tuple(map(int, self.note_color_input.text().split(',')))
            finger = self.note_finger_combo.currentText()
            note_name = self.note_name_combo.currentText()

            self.elements['notes'].append({
                'x': x, 'y': y, 'radius': radius, 'color': color,
                'finger': finger, 'note_name': note_name
            })
            self.repaint()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", "Проверьте правильность введенных данных")

    def add_open_note(self):
        """Добавление открытой ноты"""
        try:
            x = int(self.open_note_x_input.text())
            y = int(self.open_note_y_input.text())
            radius = int(self.open_note_radius_input.text())
            color = tuple(map(int, self.open_note_color_input.text().split(',')))
            symbol = self.open_note_symbol_combo.currentText()
            note_name = self.open_note_name_combo.currentText()

            self.elements['open_notes'].append({
                'x': x, 'y': y, 'radius': radius, 'color': color,
                'symbol': symbol, 'note_name': note_name
            })
            self.repaint()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", "Проверьте правильность введенных данных")

    def add_barre(self):
        """Добавление баре"""
        try:
            x = int(self.barre_x_input.text())
            y = int(self.barre_y_input.text())
            width = int(self.barre_width_input.text())
            height = int(self.barre_height_input.text())
            radius = int(self.barre_radius_input.text())
            color = tuple(map(int, self.barre_color_input.text().split(',')))

            self.elements['barres'].append({
                'x': x, 'y': y, 'width': width, 'height': height,
                'radius': radius, 'color': color
            })
            self.repaint()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", "Проверьте правильность введенных данных")

    # Методы удаления элементов
    def remove_fret(self):
        if self.elements['frets']:
            self.elements['frets'].pop()
            self.repaint()

    def remove_note(self):
        if self.elements['notes']:
            self.elements['notes'].pop()
            self.repaint()

    def remove_open_note(self):
        if self.elements['open_notes']:
            self.elements['open_notes'].pop()
            self.repaint()

    def remove_barre(self):
        if self.elements['barres']:
            self.elements['barres'].pop()
            self.repaint()

    def clear_all_elements(self):
        """Очистка всех элементов"""
        for key in self.elements:
            self.elements[key] = []
        self.repaint()

    # Методы работы с шаблонами
    def save_fret_template(self):
        """Сохранение шаблона лада"""
        self._save_template('frets', self.fret_template_combo, {
            'x': int(self.fret_x_input.text()),
            'y': int(self.fret_y_input.text()),
            'size': int(self.fret_size_input.text()),
            'symbol': self.fret_symbol_combo.currentText()
        })

    def save_note_template(self):
        """Сохранение шаблона ноты"""
        self._save_template('notes', self.note_template_combo, {
            'x': int(self.note_x_input.text()),
            'y': int(self.note_y_input.text()),
            'radius': int(self.note_radius_input.text()),
            'color': tuple(map(int, self.note_color_input.text().split(','))),
            'finger': self.note_finger_combo.currentText(),
            'note_name': self.note_name_combo.currentText()
        })

    def save_open_note_template(self):
        """Сохранение шаблона открытой ноты"""
        self._save_template('open_notes', self.open_note_template_combo, {
            'x': int(self.open_note_x_input.text()),
            'y': int(self.open_note_y_input.text()),
            'radius': int(self.open_note_radius_input.text()),
            'color': tuple(map(int, self.open_note_color_input.text().split(','))),
            'symbol': self.open_note_symbol_combo.currentText(),
            'note_name': self.open_note_name_combo.currentText()
        })

    def save_barre_template(self):
        """Сохранение шаблона баре"""
        self._save_template('barres', self.barre_template_combo, {
            'x': int(self.barre_x_input.text()),
            'y': int(self.barre_y_input.text()),
            'width': int(self.barre_width_input.text()),
            'height': int(self.barre_height_input.text()),
            'radius': int(self.barre_radius_input.text()),
            'color': tuple(map(int, self.barre_color_input.text().split(',')))
        })

    def _save_template(self, template_type, combo_box, template_data):
        """Общий метод сохранения шаблона"""
        try:
            template_name, ok = QInputDialog.getText(
                self,
                "Сохранить шаблон",
                "Введите название шаблона:"
            )

            if ok and template_name:
                if self.templates_manager.add_template(template_type, template_name, template_data):
                    self.templates_manager.save_templates()  # Сохраняем в файл
                    combo_box.addItem(template_name)
                    QMessageBox.information(self, "Успех", f"Шаблон '{template_name}' сохранен")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить шаблон")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def load_fret_template(self):
        """Загрузка шаблона лада"""
        self._load_template('frets', self.fret_template_combo, {
            'fret_x_input': 'x',
            'fret_y_input': 'y',
            'fret_size_input': 'size'
        }, additional_setters={
            'fret_symbol_combo': 'symbol'
        })

    def load_note_template(self):
        """Загрузка шаблона ноты"""
        self._load_template('notes', self.note_template_combo, {
            'note_x_input': 'x',
            'note_y_input': 'y',
            'note_radius_input': 'radius',
            'note_color_input': lambda x: ','.join(map(str, x))
        }, additional_setters={
            'note_finger_combo': 'finger',
            'note_name_combo': 'note_name'
        })

    def load_open_note_template(self):
        """Загрузка шаблона открытой ноты"""
        self._load_template('open_notes', self.open_note_template_combo, {
            'open_note_x_input': 'x',
            'open_note_y_input': 'y',
            'open_note_radius_input': 'radius',
            'open_note_color_input': lambda x: ','.join(map(str, x))
        }, additional_setters={
            'open_note_symbol_combo': 'symbol',
            'open_note_name_combo': 'note_name'
        })

    def load_barre_template(self):
        """Загрузка шаблона баре"""
        self._load_template('barres', self.barre_template_combo, {
            'barre_x_input': 'x',
            'barre_y_input': 'y',
            'barre_width_input': 'width',
            'barre_height_input': 'height',
            'barre_radius_input': 'radius',
            'barre_color_input': lambda x: ','.join(map(str, x))
        })

    def _load_template(self, template_type, combo_box, field_mapping, additional_setters=None):
        """Общий метод загрузки шаблона"""
        template_name = combo_box.currentText()
        template = self.templates_manager.get_template(template_type, template_name)

        if template:
            # Устанавливаем значения в поля ввода
            for field_name, template_key in field_mapping.items():
                field = getattr(self, field_name)
                if callable(template_key):
                    field.setText(template_key(template[template_key]))
                else:
                    field.setText(str(template[template_key]))

            # Устанавливаем значения в комбобоксы
            if additional_setters:
                for field_name, template_key in additional_setters.items():
                    field = getattr(self, field_name)
                    if template_key in template:
                        field.setCurrentText(template[template_key])

    def load_config_file(self):
        """Загрузка конфигурации из файла"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл конфигурации",
            "templates2",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_name:
            if self.templates_manager.load_config(file_name):
                self.update_template_comboboxes()
                QMessageBox.information(self, "Успех", "Конфигурация загружена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить конфигурацию")

    def save_config_file(self):
        """Сохранение конфигурации в файл"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить конфигурацию",
            os.path.join("templates2", "chord_templates.json"),
            "JSON Files (*.json);;All Files (*)"
        )

        if file_name:
            if self.templates_manager.save_templates(file_name):
                QMessageBox.information(self, "Успех", f"Конфигурация сохранена: {file_name}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить конфигурацию")

    def update_template_comboboxes(self):
        """Обновление комбобоксов шаблонов"""
        templates = self.templates_manager.templates

        # Обновляем комбобоксы для каждого типа элементов
        combo_mapping = {
            'frets': self.fret_template_combo,
            'notes': self.note_template_combo,
            'open_notes': self.open_note_template_combo,
            'barres': self.barre_template_combo
        }

        for template_type, combo in combo_mapping.items():
            combo.clear()
            combo.addItem("")  # Пустой элемент
            for template_name in templates[template_type].keys():
                combo.addItem(template_name)

    # Методы рисования
    def paintEvent(self, event):
        """Обработчик события перерисовки"""
        if self.image and not self.image.isNull():
            # Создаем временное изображение для рисования
            temp_pixmap = QPixmap(self.image)
            painter = QPainter(temp_pixmap)

            # Рисуем все элементы
            self.draw_all_elements(painter)
            painter.end()

            # Масштабируем для отображения
            scaled_pixmap = temp_pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def draw_all_elements(self, painter):
        """Рисование всех элементов на изображении"""
        # Рисуем элементы в определенном порядке
        for barre in self.elements['barres']:
            DrawingElements.draw_barre(painter, barre)

        for fret in self.elements['frets']:
            DrawingElements.draw_fret(painter, fret)

        for note in self.elements['notes']:
            DrawingElements.draw_note(painter, note)

        for open_note in self.elements['open_notes']:
            DrawingElements.draw_open_note(painter, open_note)