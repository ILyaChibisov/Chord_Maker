import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QFileDialog, QMessageBox, QInputDialog,
    QAction, QToolBar, QMenu, QCheckBox, QDialog, QFormLayout, QSpinBox,
    QTextEdit
)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

# Импорты из наших модулей
from .templates_manager import TemplatesManager
from .drawing_elements import DrawingElements
from .chord_save_dialog import ChordSaveDialog
from .chord_elements_manager import ChordElementsManager
from .controls_manager import ControlsManager
from .image_manager import ImageManager


class ProfessionalDrawingTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Профессиональное рисование аккордов")
        self.setGeometry(100, 100, 1000, 700)

        # Инициализация менеджеров
        default_config_path = os.path.join("templates2", "template.json")
        self.templates_manager = TemplatesManager(default_config_path)
        self.elements_manager = ChordElementsManager()
        self.image_manager = ImageManager(self)
        self.controls_manager = ControlsManager(self)

        self.show_crop_rect = True

        self.initUI()
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
        load_image_action.triggered.connect(self.image_manager.load_image)
        file_menu.addAction(load_image_action)

        save_image_action = QAction('Сохранить изображение', self)
        save_image_action.triggered.connect(self.save_image)
        file_menu.addAction(save_image_action)

        save_cropped_action = QAction('Сохранить обрезанное изображение', self)
        save_cropped_action.triggered.connect(self.save_cropped_image)
        file_menu.addAction(save_cropped_action)

        # Меню Аккорды
        chords_menu = menubar.addMenu('Аккорды')

        save_chord_action = QAction('Сохранить аккорд', self)
        save_chord_action.triggered.connect(self.save_chord_config)
        chords_menu.addAction(save_chord_action)

        load_chord_action = QAction('Загрузить аккорд', self)
        load_chord_action.triggered.connect(self.load_chord_config)
        chords_menu.addAction(load_chord_action)

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

        crop_action = QAction("Рамка обрезки", self)
        crop_action.triggered.connect(self.show_crop_controls)
        elements_menu.addAction(crop_action)

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

        self.save_chord_btn = QPushButton("Сохранить аккорд")
        self.save_chord_btn.clicked.connect(self.save_chord_config)
        self.toolbar.addWidget(self.save_chord_btn)

        self.load_chord_btn = QPushButton("Загрузить аккорд")
        self.load_chord_btn.clicked.connect(self.load_chord_config)
        self.toolbar.addWidget(self.load_chord_btn)

        self.toolbar.addSeparator()

        self.show_crop_checkbox = QCheckBox("Показать рамку обрезки")
        self.show_crop_checkbox.setChecked(True)
        self.show_crop_checkbox.stateChanged.connect(self.toggle_crop_rect)
        self.toolbar.addWidget(self.show_crop_checkbox)

        self.save_cropped_btn = QPushButton("Сохранить обрезанное")
        self.save_cropped_btn.clicked.connect(self.save_cropped_image)
        self.toolbar.addWidget(self.save_cropped_btn)

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
        self.setup_crop_controls()

    def setup_frets_controls(self):
        """Элементы управления для ладов"""
        self.frets_widget = QWidget()
        self.frets_layout = QHBoxLayout(self.frets_widget)

        # Поля ввода
        self.fret_x_input = QLineEdit()
        self.fret_x_input.setPlaceholderText("X координата")
        self.fret_y_input = QLineEdit()
        self.fret_y_input.setPlaceholderText("Y координата")
        self.fret_size_input = QLineEdit()
        self.fret_size_input.setPlaceholderText("Размер шрифта")
        self.fret_size_input.setText("20")

        # Выбор символа
        self.fret_symbol_combo = QComboBox()
        self.fret_symbol_combo.addItems(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'])

        # Выбор шрифта
        self.fret_font_combo = QComboBox()
        self.fret_font_combo.addItems([
            'Arial', 'Times New Roman', 'Courier New', 'Verdana',
            'Georgia', 'Palatino', 'Garamond', 'Trebuchet MS',
            'Comic Sans MS', 'Impact', 'Lucida Sans'
        ])
        self.fret_font_combo.setCurrentText('Arial')

        # Выбор стиля текста
        self.fret_style_combo = QComboBox()
        self.fret_style_combo.addItems([
            'default', 'gradient_text', 'shadow', 'glow', 'outline',
            'metallic', 'gold_embossed', 'silver_embossed', 'neon', 'stamped'
        ])
        self.fret_style_combo.setCurrentText('default')

        # Выбор цвета
        self.fret_color_combo = QComboBox()
        self.fret_color_combo.addItems([
            'Черный', 'Белый', 'Красный', 'Синий', 'Зеленый', 'Золотой',
            'Серебряный', 'Бронзовый', 'Пурпурный', 'Бирюзовый', 'Оранжевый'
        ])
        self.fret_color_combo.setCurrentText('Черный')

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
            self.fret_symbol_combo, self.fret_font_combo, self.fret_style_combo,
            self.fret_color_combo, self.add_fret_button, self.remove_fret_button,
            self.save_fret_template_button, self.fret_template_combo
        ]

        for widget in widgets:
            self.frets_layout.addWidget(widget)

        self.main_layout.addWidget(self.frets_widget)

    def setup_barre_controls(self):
        """Элементы управления для баре"""
        self.barre_widget = QWidget()
        self.barre_layout = QHBoxLayout(self.barre_widget)

        # Поля ввода
        self.barre_x_input = QLineEdit()
        self.barre_x_input.setPlaceholderText("X координата")
        self.barre_y_input = QLineEdit()
        self.barre_y_input.setPlaceholderText("Y координата")
        self.barre_width_input = QLineEdit()
        self.barre_width_input.setPlaceholderText("Ширина")
        self.barre_width_input.setText("100")
        self.barre_height_input = QLineEdit()
        self.barre_height_input.setPlaceholderText("Высота")
        self.barre_height_input.setText("20")
        self.barre_radius_input = QLineEdit()
        self.barre_radius_input.setPlaceholderText("Закругление")
        self.barre_radius_input.setText("10")

        # Выбор стиля баре
        self.barre_style_combo = QComboBox()
        self.barre_style_combo.addItems(['default', 'wood', 'metal', 'rubber', 'gradient', 'striped'])
        self.barre_style_combo.setCurrentText('default')

        # Выбор цвета
        self.barre_color_combo = QComboBox()
        self.barre_color_combo.addItems(['Золотистый', 'Коричневый', 'Серый', 'Черный', 'Красный', 'Синий'])
        self.barre_color_combo.setCurrentText('Золотистый')

        # Выбор оформления
        self.barre_decoration_combo = QComboBox()
        self.barre_decoration_combo.addItems(['none', 'shadow', 'glow', 'double_border', 'stripes'])
        self.barre_decoration_combo.setCurrentText('none')

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
            self.barre_height_input, self.barre_radius_input, self.barre_style_combo,
            self.barre_color_combo, self.barre_decoration_combo, self.add_barre_button,
            self.remove_barre_button, self.save_barre_template_button, self.barre_template_combo
        ]

        for widget in widgets:
            self.barre_layout.addWidget(widget)

        self.main_layout.addWidget(self.barre_widget)

    def setup_notes_controls(self):
        """Элементы управления для нот"""
        self.notes_widget = QWidget()
        self.notes_layout = QHBoxLayout(self.notes_widget)

        # Поля ввода
        self.note_x_input = QLineEdit()
        self.note_x_input.setPlaceholderText("X координата")
        self.note_y_input = QLineEdit()
        self.note_y_input.setPlaceholderText("Y координата")
        self.note_radius_input = QLineEdit()
        self.note_radius_input.setPlaceholderText("Радиус")
        self.note_radius_input.setText("15")

        # Выбор стиля (50+ вариантов)
        self.note_style_combo = QComboBox()
        note_styles = [
            'default', 'blue_gradient', 'red_3d', 'green_3d', 'purple_3d', 'gold_3d',
            'glass', 'metal', 'fire', 'ice', 'soft_pink', 'mint_green', 'lavender',
            'peach', 'sky_blue', 'lemon_yellow', 'coral', 'aqua_marine', 'rose_quartz',
            'seafoam', 'buttercup', 'lilac', 'honey', 'turquoise', 'apricot', 'periwinkle',
            'sage', 'melon', 'powder_blue', 'pistachio', 'blush', 'mauve', 'cream', 'teal',
            'salmon', 'orchid', 'mint_blue', 'pear', 'rose_gold', 'lavender_gray', 'honeydew',
            'peach_puff', 'azure', 'pale_green', 'light_coral', 'thistle', 'wheat', 'light_cyan',
            'pale_turquoise', 'light_pink', 'light_salmon', 'light_skyblue', 'light_green', 'plum', 'bisque'
        ]
        self.note_style_combo.addItems(note_styles)
        self.note_style_combo.setCurrentText('red_3d')

        # Выбор оформления
        self.note_decoration_combo = QComboBox()
        self.note_decoration_combo.addItems(['none', 'double_border', 'glow', 'shadow', 'sparkle', 'dotted_border'])
        self.note_decoration_combo.setCurrentText('none')

        # Выбор цвета текста
        self.note_text_color_combo = QComboBox()
        self.note_text_color_combo.addItems(['Белый', 'Черный', 'Красный', 'Синий', 'Зеленый', 'Желтый', 'Золотой'])
        self.note_text_color_combo.setCurrentText('Белый')

        # Выбор стиля шрифта
        self.note_font_style_combo = QComboBox()
        self.note_font_style_combo.addItems(['normal', 'bold', 'light', 'italic', 'bold_italic'])
        self.note_font_style_combo.setCurrentText('bold')

        # Выбор отображаемого текста
        self.note_display_text_combo = QComboBox()
        self.note_display_text_combo.addItems(['Палец', 'Нота'])
        self.note_display_text_combo.setCurrentText('Палец')

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
            self.note_style_combo, self.note_decoration_combo, self.note_text_color_combo,
            self.note_font_style_combo, self.note_display_text_combo, self.note_finger_combo,
            self.note_name_combo, self.add_note_button, self.remove_note_button,
            self.save_note_template_button, self.note_template_combo
        ]

        for widget in widgets:
            self.notes_layout.addWidget(widget)

        self.main_layout.addWidget(self.notes_widget)

    def setup_open_notes_controls(self):
        """Элементы управления для открытых нот"""
        self.open_notes_widget = QWidget()
        self.open_notes_layout = QHBoxLayout(self.open_notes_widget)

        # Поля ввода
        self.open_note_x_input = QLineEdit()
        self.open_note_x_input.setPlaceholderText("X координата")
        self.open_note_y_input = QLineEdit()
        self.open_note_y_input.setPlaceholderText("Y координата")
        self.open_note_radius_input = QLineEdit()
        self.open_note_radius_input.setPlaceholderText("Радиус")
        self.open_note_radius_input.setText("15")

        # Выбор стиля (50+ вариантов)
        self.open_note_style_combo = QComboBox()
        note_styles = [
            'default', 'blue_gradient', 'red_3d', 'green_3d', 'purple_3d', 'gold_3d',
            'glass', 'metal', 'fire', 'ice', 'soft_pink', 'mint_green', 'lavender',
            'peach', 'sky_blue', 'lemon_yellow', 'coral', 'aqua_marine', 'rose_quartz',
            'seafoam', 'buttercup', 'lilac', 'honey', 'turquoise', 'apricot', 'periwinkle',
            'sage', 'melon', 'powder_blue', 'pistachio', 'blush', 'mauve', 'cream', 'teal',
            'salmon', 'orchid', 'mint_blue', 'pear', 'rose_gold', 'lavender_gray', 'honeydew',
            'peach_puff', 'azure', 'pale_green', 'light_coral', 'thistle', 'wheat', 'light_cyan',
            'pale_turquoise', 'light_pink', 'light_salmon', 'light_skyblue', 'light_green', 'plum', 'bisque'
        ]
        self.open_note_style_combo.addItems(note_styles)
        self.open_note_style_combo.setCurrentText('blue_gradient')

        # Выбор оформления
        self.open_note_decoration_combo = QComboBox()
        self.open_note_decoration_combo.addItems(
            ['none', 'double_border', 'glow', 'shadow', 'sparkle', 'dotted_border'])
        self.open_note_decoration_combo.setCurrentText('none')

        # Выбор цвета текста
        self.open_note_text_color_combo = QComboBox()
        self.open_note_text_color_combo.addItems(
            ['Белый', 'Черный', 'Красный', 'Синий', 'Зеленый', 'Желтый', 'Золотой'])
        self.open_note_text_color_combo.setCurrentText('Белый')

        # Выбор стиля шрифта
        self.open_note_font_style_combo = QComboBox()
        self.open_note_font_style_combo.addItems(['normal', 'bold', 'light', 'italic', 'bold_italic'])
        self.open_note_font_style_combo.setCurrentText('bold')

        # Выбор отображаемого текста
        self.open_note_display_text_combo = QComboBox()
        self.open_note_display_text_combo.addItems(['Символ', 'Нота'])
        self.open_note_display_text_combo.setCurrentText('Символ')

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
            self.open_note_style_combo, self.open_note_decoration_combo, self.open_note_text_color_combo,
            self.open_note_font_style_combo, self.open_note_display_text_combo, self.open_note_symbol_combo,
            self.open_note_name_combo, self.add_open_note_button, self.remove_open_note_button,
            self.save_open_note_template_button, self.open_note_template_combo
        ]

        for widget in widgets:
            self.open_notes_layout.addWidget(widget)

        self.main_layout.addWidget(self.open_notes_widget)

    def setup_crop_controls(self):
        """Элементы управления для рамки обрезки"""
        self.crop_widget = QWidget()
        self.crop_layout = QHBoxLayout(self.crop_widget)

        # Поля ввода для рамки
        self.crop_x_input = QLineEdit()
        self.crop_x_input.setPlaceholderText("X координата")
        self.crop_x_input.setText("50")
        self.crop_y_input = QLineEdit()
        self.crop_y_input.setPlaceholderText("Y координата")
        self.crop_y_input.setText("50")
        self.crop_width_input = QLineEdit()
        self.crop_width_input.setPlaceholderText("Ширина")
        self.crop_width_input.setText("400")
        self.crop_height_input = QLineEdit()
        self.crop_height_input.setPlaceholderText("Высота")
        self.crop_height_input.setText("300")

        # Выбор стиля рамки
        self.crop_style_combo = QComboBox()
        self.crop_style_combo.addItems(['dashed', 'dotted', 'solid'])
        self.crop_style_combo.setCurrentText('dashed')

        # Выбор цвета рамки
        self.crop_color_combo = QComboBox()
        self.crop_color_combo.addItems(['Красный', 'Синий', 'Зеленый', 'Черный', 'Белый', 'Желтый', 'Пурпурный'])
        self.crop_color_combo.setCurrentText('Красный')

        # Кнопки
        self.set_crop_button = QPushButton("Установить рамку")
        self.set_crop_button.clicked.connect(self.set_crop_rect)

        self.clear_crop_button = QPushButton("Очистить рамку")
        self.clear_crop_button.clicked.connect(self.clear_crop_rect)

        self.save_crop_template_button = QPushButton("Сохранить шаблон")
        self.save_crop_template_button.clicked.connect(self.save_crop_template)

        # Комбобокс шаблонов
        self.crop_template_combo = QComboBox()
        self.crop_template_combo.setPlaceholderText("Шаблоны рамки")
        self.crop_template_combo.currentIndexChanged.connect(self.load_crop_template)

        # Добавляем все в layout
        widgets = [
            self.crop_x_input, self.crop_y_input, self.crop_width_input,
            self.crop_height_input, self.crop_style_combo, self.crop_color_combo,
            self.set_crop_button, self.clear_crop_button, self.save_crop_template_button,
            self.crop_template_combo
        ]

        for widget in widgets:
            self.crop_layout.addWidget(widget)

        self.main_layout.addWidget(self.crop_widget)

    # Методы управления видимостью элементов управления
    def hide_all_controls(self):
        """Скрыть все элементы управления"""
        self.frets_widget.hide()
        self.notes_widget.hide()
        self.open_notes_widget.hide()
        self.barre_widget.hide()
        self.crop_widget.hide()

    def show_frets_controls(self):
        self.hide_all_controls()
        self.frets_widget.show()

    def show_notes_controls(self):
        self.hide_all_controls()
        self.notes_widget.show()

    def show_open_notes_controls(self):
        self.hide_all_controls()
        self.open_notes_widget.show()

    def show_barre_controls(self):
        self.hide_all_controls()
        self.barre_widget.show()

    def show_crop_controls(self):
        self.hide_all_controls()
        self.crop_widget.show()

    def toggle_crop_rect(self, state):
        """Переключение видимости рамки обрезки"""
        self.show_crop_rect = (state == Qt.Checked)
        self.repaint()

    # Методы работы с аккордами
    def save_chord_config(self):
        """Сохранение конфигурации аккорда"""
        if not self.image_manager.image:
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения аккорда")
            return

        dialog = ChordSaveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            chord_data = dialog.get_chord_data()
            file_suffix = dialog.get_file_suffix()

            if not chord_data['name']:
                QMessageBox.warning(self, "Ошибка", "Введите имя аккорда")
                return

            # Подготавливаем элементы для сохранения
            elements_to_save = self.elements_manager.prepare_elements_for_saving(chord_data['display_type'])

            # Создаем структуру папок
            chord_name = chord_data['name']
            variant = chord_data['variant']

            chord_dir = os.path.join("templates2", "аккорды", chord_name, f"вариант_{variant}")
            os.makedirs(chord_dir, exist_ok=True)

            # Сохраняем конфигурацию
            config_data = {
                'chord_name': chord_name,
                'variant': variant,
                'display_type': chord_data['display_type'],
                'description': chord_data['description'],
                'elements': elements_to_save
            }

            file_name = f"{chord_name}_вариант_{variant}_{file_suffix}.json"
            file_path = os.path.join(chord_dir, file_name)

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)

                QMessageBox.information(self, "Успех", f"Аккорд сохранен в:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить аккорд: {str(e)}")

    def load_chord_config(self):
        """Загрузка конфигурации аккорда"""
        chords_dir = os.path.join("templates2", "аккорды")
        if not os.path.exists(chords_dir):
            QMessageBox.information(self, "Информация", "Папка с аккордами не найдена")
            return

        # Получаем список всех JSON файлов в структуре аккордов
        chord_files = []
        for root, dirs, files in os.walk(chords_dir):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    # Получаем информацию об аккорде из пути
                    relative_path = os.path.relpath(full_path, chords_dir)
                    chord_files.append((full_path, relative_path))

        if not chord_files:
            QMessageBox.information(self, "Информация", "Не найдено сохраненных аккордов")
            return

        # Диалог выбора аккорда
        chord_paths = [path for path, rel in chord_files]
        chord_names = [rel for path, rel in chord_files]

        chord_name, ok = QInputDialog.getItem(
            self,
            "Загрузить аккорд",
            "Выберите аккорд:",
            chord_names,
            0,
            False
        )

        if ok and chord_name:
            # Находим полный путь к выбранному файлу
            selected_index = chord_names.index(chord_name)
            selected_path = chord_paths[selected_index]

            try:
                with open(selected_path, 'r', encoding='utf-8') as f:
                    chord_config = json.load(f)

                # Загружаем информацию об аккорде
                chord_info = chord_config
                QMessageBox.information(self, "Информация об аккорде",
                                        f"Аккорд: {chord_info.get('chord_name', 'Неизвестно')}\n"
                                        f"Вариант: {chord_info.get('variant', 'Неизвестно')}\n"
                                        f"Тип: {chord_info.get('display_type', 'Неизвестно')}\n"
                                        f"Описание: {chord_info.get('description', 'Нет описания')}")

                # Загружаем элементы отрисовки
                self.elements_manager.elements = chord_config.get('elements', {
                    'frets': [], 'notes': [], 'open_notes': [], 'barres': [], 'crop_rect': None
                })

                # Обновляем поля ввода для рамки если есть
                if self.elements_manager.elements['crop_rect']:
                    crop = self.elements_manager.elements['crop_rect']
                    self.crop_x_input.setText(str(crop.get('x', 50)))
                    self.crop_y_input.setText(str(crop.get('y', 50)))
                    self.crop_width_input.setText(str(crop.get('width', 400)))
                    self.crop_height_input.setText(str(crop.get('height', 300)))

                self.repaint()
                QMessageBox.information(self, "Успех", "Конфигурация аккорда загружена")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить аккорд: {str(e)}")

    # Методы работы с изображениями
    def save_image(self):
        """Сохранение изображения с нарисованными элементами"""
        self.image_manager.save_image(self.elements_manager.elements, self.draw_all_elements)

    def save_cropped_image(self):
        """Сохранение обрезанного изображения"""
        if not self.image_manager.image:
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения")
            return

        if not self.elements_manager.elements['crop_rect']:
            QMessageBox.warning(self, "Ошибка", "Не установлена рамка обрезки")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить обрезанное изображение",
            "chord_diagram_cropped.png",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_name:
            # Создаем копию изображения
            result_image = QPixmap(self.image_manager.image)
            painter = QPainter(result_image)

            # Рисуем все элементы
            self.draw_all_elements(painter)
            painter.end()

            # Обрезаем изображение
            crop = self.elements_manager.elements['crop_rect']

            # Проверяем, что область обрезки находится в пределах изображения
            img_width = result_image.width()
            img_height = result_image.height()

            # Корректируем координаты если нужно
            x = max(0, min(crop['x'], img_width - 1))
            y = max(0, min(crop['y'], img_height - 1))
            width = max(1, min(crop['width'], img_width - x))
            height = max(1, min(crop['height'], img_height - y))

            cropped_image = result_image.copy(x, y, width, height)

            # Сохраняем
            if cropped_image.save(file_name):
                QMessageBox.information(self, "Успех", f"Обрезанное изображение сохранено: {file_name}")
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
            font_family = self.fret_font_combo.currentText()
            style = self.fret_style_combo.currentText()

            # Преобразуем название цвета в RGB
            color_name = self.fret_color_combo.currentText()
            color_map = {
                'Черный': (0, 0, 0),
                'Белый': (255, 255, 255),
                'Красный': (255, 0, 0),
                'Синий': (0, 0, 255),
                'Зеленый': (0, 128, 0),
                'Золотой': (255, 215, 0),
                'Серебряный': (192, 192, 192),
                'Бронзовый': (205, 127, 50),
                'Пурпурный': (128, 0, 128),
                'Бирюзовый': (64, 224, 208),
                'Оранжевый': (255, 165, 0)
            }
            color = color_map.get(color_name, (0, 0, 0))

            self.elements_manager.elements['frets'].append({
                'x': x, 'y': y, 'size': size, 'symbol': symbol,
                'font_family': font_family, 'style': style, 'color': color
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
            style = self.barre_style_combo.currentText()
            decoration = self.barre_decoration_combo.currentText()

            # Цвет баре
            color_name = self.barre_color_combo.currentText()
            color_map = {
                'Золотистый': (189, 183, 107),
                'Коричневый': (139, 69, 19),
                'Серый': (128, 128, 128),
                'Черный': (0, 0, 0),
                'Красный': (255, 0, 0),
                'Синий': (0, 0, 255)
            }
            color = color_map.get(color_name, (189, 183, 107))

            self.elements_manager.elements['barres'].append({
                'x': x, 'y': y, 'width': width, 'height': height,
                'radius': radius, 'style': style, 'decoration': decoration, 'color': color
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
            style = self.note_style_combo.currentText()
            decoration = self.note_decoration_combo.currentText()

            # Цвет текста
            color_name = self.note_text_color_combo.currentText()
            color_map = {
                'Белый': (255, 255, 255),
                'Черный': (0, 0, 0),
                'Красный': (255, 0, 0),
                'Синий': (0, 0, 255),
                'Зеленый': (0, 128, 0),
                'Желтый': (255, 255, 0),
                'Золотой': (255, 215, 0)
            }
            text_color = color_map.get(color_name, (255, 255, 255))

            font_style = self.note_font_style_combo.currentText()
            display_text = 'finger' if self.note_display_text_combo.currentText() == 'Палец' else 'note_name'
            finger = self.note_finger_combo.currentText()
            note_name = self.note_name_combo.currentText()

            self.elements_manager.elements['notes'].append({
                'x': x, 'y': y, 'radius': radius, 'style': style, 'decoration': decoration,
                'text_color': text_color, 'font_style': font_style, 'display_text': display_text,
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
            style = self.open_note_style_combo.currentText()
            decoration = self.open_note_decoration_combo.currentText()

            # Цвет текста
            color_name = self.open_note_text_color_combo.currentText()
            color_map = {
                'Белый': (255, 255, 255),
                'Черный': (0, 0, 0),
                'Красный': (255, 0, 0),
                'Синий': (0, 0, 255),
                'Зеленый': (0, 128, 0),
                'Желтый': (255, 255, 0),
                'Золотой': (255, 215, 0)
            }
            text_color = color_map.get(color_name, (255, 255, 255))

            font_style = self.open_note_font_style_combo.currentText()
            display_text = 'symbol' if self.open_note_display_text_combo.currentText() == 'Символ' else 'note_name'
            symbol = self.open_note_symbol_combo.currentText()
            note_name = self.open_note_name_combo.currentText()

            self.elements_manager.elements['open_notes'].append({
                'x': x, 'y': y, 'radius': radius, 'style': style, 'decoration': decoration,
                'text_color': text_color, 'font_style': font_style, 'display_text': display_text,
                'symbol': symbol, 'note_name': note_name
            })
            self.repaint()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", "Проверьте правильность введенных данных")

    def set_crop_rect(self):
        """Установка рамки обрезки"""
        try:
            x = int(self.crop_x_input.text())
            y = int(self.crop_y_input.text())
            width = int(self.crop_width_input.text())
            height = int(self.crop_height_input.text())
            style = self.crop_style_combo.currentText()

            # Цвет рамки
            color_name = self.crop_color_combo.currentText()
            color_map = {
                'Красный': (255, 0, 0),
                'Синий': (0, 0, 255),
                'Зеленый': (0, 128, 0),
                'Черный': (0, 0, 0),
                'Белый': (255, 255, 255),
                'Желтый': (255, 255, 0),
                'Пурпурный': (128, 0, 128)
            }
            color = color_map.get(color_name, (255, 0, 0))

            self.elements_manager.elements['crop_rect'] = {
                'x': x, 'y': y, 'width': width, 'height': height,
                'style': style, 'color': color
            }
            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", "Проверьте правильность введенных данных")

    def clear_crop_rect(self):
        """Очистка рамки обрезки"""
        self.elements_manager.elements['crop_rect'] = None
        self.repaint()

    # Методы удаления элементов
    def remove_fret(self):
        if self.elements_manager.elements['frets']:
            self.elements_manager.elements['frets'].pop()
            self.repaint()

    def remove_note(self):
        if self.elements_manager.elements['notes']:
            self.elements_manager.elements['notes'].pop()
            self.repaint()

    def remove_open_note(self):
        if self.elements_manager.elements['open_notes']:
            self.elements_manager.elements['open_notes'].pop()
            self.repaint()

    def remove_barre(self):
        if self.elements_manager.elements['barres']:
            self.elements_manager.elements['barres'].pop()
            self.repaint()

    def clear_all_elements(self):
        """Очистка всех элементов"""
        for key in self.elements_manager.elements:
            if key == 'crop_rect':
                self.elements_manager.elements[key] = None
            else:
                self.elements_manager.elements[key] = []
        self.repaint()

    # Методы работы с шаблонами
    def save_fret_template(self):
        """Сохранение шаблона лада"""
        color_name = self.fret_color_combo.currentText()
        color_map = {
            'Черный': (0, 0, 0),
            'Белый': (255, 255, 255),
            'Красный': (255, 0, 0),
            'Синий': (0, 0, 255),
            'Зеленый': (0, 128, 0),
            'Золотой': (255, 215, 0),
            'Серебряный': (192, 192, 192),
            'Бронзовый': (205, 127, 50),
            'Пурпурный': (128, 0, 128),
            'Бирюзовый': (64, 224, 208),
            'Оранжевый': (255, 165, 0)
        }
        color = color_map.get(color_name, (0, 0, 0))

        self._save_template('frets', self.fret_template_combo, {
            'x': int(self.fret_x_input.text()),
            'y': int(self.fret_y_input.text()),
            'size': int(self.fret_size_input.text()),
            'symbol': self.fret_symbol_combo.currentText(),
            'font_family': self.fret_font_combo.currentText(),
            'style': self.fret_style_combo.currentText(),
            'color': color
        })

    def save_note_template(self):
        """Сохранение шаблона ноты"""
        color_name = self.note_text_color_combo.currentText()
        color_map = {
            'Белый': (255, 255, 255),
            'Черный': (0, 0, 0),
            'Красный': (255, 0, 0),
            'Синий': (0, 0, 255),
            'Зеленый': (0, 128, 0),
            'Желтый': (255, 255, 0),
            'Золотой': (255, 215, 0)
        }
        text_color = color_map.get(color_name, (255, 255, 255))

        self._save_template('notes', self.note_template_combo, {
            'x': int(self.note_x_input.text()),
            'y': int(self.note_y_input.text()),
            'radius': int(self.note_radius_input.text()),
            'style': self.note_style_combo.currentText(),
            'decoration': self.note_decoration_combo.currentText(),
            'text_color': text_color,
            'font_style': self.note_font_style_combo.currentText(),
            'display_text': 'finger' if self.note_display_text_combo.currentText() == 'Палец' else 'note_name',
            'finger': self.note_finger_combo.currentText(),
            'note_name': self.note_name_combo.currentText()
        })

    def save_open_note_template(self):
        """Сохранение шаблона открытой ноты"""
        color_name = self.open_note_text_color_combo.currentText()
        color_map = {
            'Белый': (255, 255, 255),
            'Черный': (0, 0, 0),
            'Красный': (255, 0, 0),
            'Синий': (0, 0, 255),
            'Зеленый': (0, 128, 0),
            'Желтый': (255, 255, 0),
            'Золотой': (255, 215, 0)
        }
        text_color = color_map.get(color_name, (255, 255, 255))

        self._save_template('open_notes', self.open_note_template_combo, {
            'x': int(self.open_note_x_input.text()),
            'y': int(self.open_note_y_input.text()),
            'radius': int(self.open_note_radius_input.text()),
            'style': self.open_note_style_combo.currentText(),
            'decoration': self.open_note_decoration_combo.currentText(),
            'text_color': text_color,
            'font_style': self.open_note_font_style_combo.currentText(),
            'display_text': 'symbol' if self.open_note_display_text_combo.currentText() == 'Символ' else 'note_name',
            'symbol': self.open_note_symbol_combo.currentText(),
            'note_name': self.open_note_name_combo.currentText()
        })

    def save_barre_template(self):
        """Сохранение шаблона баре"""
        color_name = self.barre_color_combo.currentText()
        color_map = {
            'Золотистый': (189, 183, 107),
            'Коричневый': (139, 69, 19),
            'Серый': (128, 128, 128),
            'Черный': (0, 0, 0),
            'Красный': (255, 0, 0),
            'Синий': (0, 0, 255)
        }
        color = color_map.get(color_name, (189, 183, 107))

        self._save_template('barres', self.barre_template_combo, {
            'x': int(self.barre_x_input.text()),
            'y': int(self.barre_y_input.text()),
            'width': int(self.barre_width_input.text()),
            'height': int(self.barre_height_input.text()),
            'radius': int(self.barre_radius_input.text()),
            'style': self.barre_style_combo.currentText(),
            'decoration': self.barre_decoration_combo.currentText(),
            'color': color
        })

    def save_crop_template(self):
        """Сохранение шаблона рамки обрезки"""
        if not self.elements_manager.elements['crop_rect']:
            QMessageBox.warning(self, "Ошибка", "Нет рамки для сохранения в шаблон")
            return

        try:
            template_name, ok = QInputDialog.getText(
                self,
                "Сохранить шаблон рамки",
                "Введите название шаблона:"
            )

            if ok and template_name:
                crop_data = self.elements_manager.elements['crop_rect'].copy()
                if self.templates_manager.add_template('crop_rects', template_name, crop_data):
                    self.templates_manager.save_templates()
                    self.crop_template_combo.addItem(template_name)
                    QMessageBox.information(self, "Успех", f"Шаблон рамки '{template_name}' сохранен")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить шаблон")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

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
                    self.templates_manager.save_templates()
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
            'fret_symbol_combo': 'symbol',
            'fret_font_combo': 'font_family',
            'fret_style_combo': 'style',
            'fret_color_combo': lambda x: self._get_color_name(x)
        })

    def load_note_template(self):
        """Загрузка шаблона ноты"""
        self._load_template('notes', self.note_template_combo, {
            'note_x_input': 'x',
            'note_y_input': 'y',
            'note_radius_input': 'radius',
        }, additional_setters={
            'note_style_combo': 'style',
            'note_decoration_combo': 'decoration',
            'note_text_color_combo': lambda x: self._get_text_color_name(x),
            'note_font_style_combo': 'font_style',
            'note_display_text_combo': lambda x: 'Палец' if x == 'finger' else 'Нота',
            'note_finger_combo': 'finger',
            'note_name_combo': 'note_name'
        })

    def load_open_note_template(self):
        """Загрузка шаблона открытой ноты"""
        self._load_template('open_notes', self.open_note_template_combo, {
            'open_note_x_input': 'x',
            'open_note_y_input': 'y',
            'open_note_radius_input': 'radius',
        }, additional_setters={
            'open_note_style_combo': 'style',
            'open_note_decoration_combo': 'decoration',
            'open_note_text_color_combo': lambda x: self._get_text_color_name(x),
            'open_note_font_style_combo': 'font_style',
            'open_note_display_text_combo': lambda x: 'Символ' if x == 'symbol' else 'Нота',
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
        }, additional_setters={
            'barre_style_combo': 'style',
            'barre_decoration_combo': 'decoration',
            'barre_color_combo': lambda x: self._get_barre_color_name(x)
        })

    def load_crop_template(self):
        """Загрузка шаблона рамки обрезки"""
        template_name = self.crop_template_combo.currentText()
        template = self.templates_manager.get_template('crop_rects', template_name)

        if template:
            self.crop_x_input.setText(str(template['x']))
            self.crop_y_input.setText(str(template['y']))
            self.crop_width_input.setText(str(template['width']))
            self.crop_height_input.setText(str(template['height']))
            self.crop_style_combo.setCurrentText(template.get('style', 'dashed'))

            # Устанавливаем цвет
            color = template.get('color', (255, 0, 0))
            color_map = {
                (255, 0, 0): 'Красный',
                (0, 0, 255): 'Синий',
                (0, 128, 0): 'Зеленый',
                (0, 0, 0): 'Черный',
                (255, 255, 255): 'Белый',
                (255, 255, 0): 'Желтый',
                (128, 0, 128): 'Пурпурный'
            }
            color_name = color_map.get(tuple(color), 'Красный')
            self.crop_color_combo.setCurrentText(color_name)

    def _get_color_name(self, color_tuple):
        """Преобразует RGB кортеж в название цвета"""
        color_map = {
            (0, 0, 0): 'Черный',
            (255, 255, 255): 'Белый',
            (255, 0, 0): 'Красный',
            (0, 0, 255): 'Синий',
            (0, 128, 0): 'Зеленый',
            (255, 215, 0): 'Золотой',
            (192, 192, 192): 'Серебряный',
            (205, 127, 50): 'Бронзовый',
            (128, 0, 128): 'Пурпурный',
            (64, 224, 208): 'Бирюзовый',
            (255, 165, 0): 'Оранжевый'
        }
        return color_map.get(tuple(color_tuple), 'Черный')

    def _get_text_color_name(self, color_tuple):
        """Преобразует RGB кортеж в название цвета текста"""
        color_map = {
            (255, 255, 255): 'Белый',
            (0, 0, 0): 'Черный',
            (255, 0, 0): 'Красный',
            (0, 0, 255): 'Синий',
            (0, 128, 0): 'Зеленый',
            (255, 255, 0): 'Желтый',
            (255, 215, 0): 'Золотой'
        }
        return color_map.get(tuple(color_tuple), 'Белый')

    def _get_barre_color_name(self, color_tuple):
        """Преобразует RGB кортеж в название цвета баре"""
        color_map = {
            (189, 183, 107): 'Золотистый',
            (139, 69, 19): 'Коричневый',
            (128, 128, 128): 'Серый',
            (0, 0, 0): 'Черный',
            (255, 0, 0): 'Красный',
            (0, 0, 255): 'Синий'
        }
        return color_map.get(tuple(color_tuple), 'Золотистый')

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
                        if callable(template_key):
                            field.setCurrentText(template_key(template[template_key]))
                        else:
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
            'barres': self.barre_template_combo,
            'crop_rects': self.crop_template_combo
        }

        for template_type, combo in combo_mapping.items():
            combo.clear()
            combo.addItem("")  # Пустой элемент
            for template_name in templates[template_type].keys():
                combo.addItem(template_name)

    # Методы рисования
    def paintEvent(self, event):
        """Обработчик события перерисовки"""
        if self.image_manager.image and not self.image_manager.image.isNull():
            # Создаем временное изображение для рисования
            temp_pixmap = QPixmap(self.image_manager.image)
            painter = QPainter(temp_pixmap)

            # Рисуем все элементы
            self.draw_all_elements(painter)

            # Рисуем рамку обрезки если включена
            if self.show_crop_rect and self.elements_manager.elements['crop_rect']:
                DrawingElements.draw_crop_rect(painter, self.elements_manager.elements['crop_rect'])

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
        for barre in self.elements_manager.elements['barres']:
            DrawingElements.draw_barre(painter, barre)

        for fret in self.elements_manager.elements['frets']:
            DrawingElements.draw_fret(painter, fret)

        for note in self.elements_manager.elements['notes']:
            DrawingElements.draw_note(painter, note)

        for open_note in self.elements_manager.elements['open_notes']:
            DrawingElements.draw_open_note(painter, open_note)

    def repaint(self):
        """Перерисовка изображения"""
        self.update()