import sys
import os
import json
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
import tempfile
import subprocess
import warnings

# Добавляем путь к grafic_tools
sys.path.append(os.path.join(os.path.dirname(__file__), 'grafic_tools'))

# Импорты из нашего пакета
from grafic_tools.professional_drawing import ProfessionalDrawingTab

from scipy import signal

from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QWidget, QPushButton, \
    QFileDialog, QMenu, QMessageBox, QDialog, QLabel, QLineEdit ,QListWidget,QListWidgetItem, QHBoxLayout, QTabWidget,
                             QTextEdit,QFrame, QComboBox,  QAction, QInputDialog,QToolBar,QWidgetAction,QShortcut,QGridLayout,
                             QProgressBar, QSpinBox, QCheckBox,QDoubleSpinBox)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush,QPixmap, QPainter, QPen, QFontMetrics, QFont, QKeySequence

# Пути к FFmpeg
FFMPEG_PATH = r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\ProgramData\chocolatey\bin\ffprobe.exe"

# Подавляем warnings от pydub
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")

# Настраиваем pydub для использования правильного пути
os.environ['PATH'] = r"C:\ProgramData\chocolatey\bin" + os.pathsep + os.environ['PATH']

# Явно устанавливаем пути для pydub
import pydub
pydub.AudioSegment.converter = FFMPEG_PATH
pydub.AudioSegment.ffprobe = FFPROBE_PATH

# Переопределяем функцию which для pydub
import pydub.utils
original_which = pydub.utils.which

def custom_which(program):
    if program == "ffmpeg":
        return FFMPEG_PATH
    elif program == "ffprobe":
        return FFPROBE_PATH
    elif program == "avconv":
        return None
    else:
        return original_which(program)

pydub.utils.which = custom_which

# Создаем папку templates2 если её нет
TEMPLATES2_DIR = "templates2"
if not os.path.exists(TEMPLATES2_DIR):
    os.makedirs(TEMPLATES2_DIR)
    print(f"Создана папка {TEMPLATES2_DIR}")

# Создаем базовый конфиг если его нет
DEFAULT_CONFIG_PATH = os.path.join(TEMPLATES2_DIR, "template.json")
if not os.path.exists(DEFAULT_CONFIG_PATH):
    default_config = {
        'frets': {},
        'notes': {},
        'open_notes': {},
        'barres': {}
    }
    with open(DEFAULT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    print(f"Создан базовый конфиг: {DEFAULT_CONFIG_PATH}")

# Варианты для вкладок
class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Контент Менеджер')
        self.setGeometry(100, 100, 1200, 800)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Создаём вкладки
        self.chord_redactor = ImageEditor()  # Закомментировано, если нет этого класса
        self.chord_recorder = ChordRecorderTab()  # Закомментировано, если нет этого класса
        self.pro_drawing = ProfessionalDrawingTab()  # Основная вкладка профессионального рисования

        self.tabs.addTab(self.chord_redactor, "Базовое рисование")
        self.tabs.addTab(self.chord_recorder, "Запись аккордов")
        self.tabs.addTab(self.pro_drawing, "Профессиональное рисование")


# модуль 1 (Рисование аккордов)
class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор аккордов")
        self.setGeometry(100, 100, 700, 600)
        self.initUI()
        self.hide_controls()

    def initUI(self):
        # Создание меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        file_menu2 = menubar.addMenu('Шаблоны')
        figure_menu = menubar.addMenu('Элементы')

        load_image_action = QAction('Загрузить', self)
        load_image_action.triggered.connect(self.load_image)
        file_menu.addAction(load_image_action)

        save_image_action = QAction('Сохранить', self)
        save_image_action.triggered.connect(self.save_image)
        file_menu.addAction(save_image_action)

        load_template_action = QAction('Загрузить', self)
        load_template_action.triggered.connect(self.load_config_file)
        file_menu2.addAction(load_template_action)

        note_action = QAction("Нота", self)
        note_action.triggered.connect(self.show_circle_controls)
        figure_menu.addAction(note_action)

        string_action = QAction("Глухая струна", self)
        string_action.triggered.connect(self.show_cross_controls)
        figure_menu.addAction(string_action)

        barre_action = QAction("Баре", self)
        barre_action.triggered.connect(self.show_ellipse_controls)
        figure_menu.addAction(barre_action)

        symbol_action = QAction("Разметка ладов", self)
        symbol_action.triggered.connect(self.show_symbol_controls)
        figure_menu.addAction(symbol_action)

        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)

        self.toolbar2 = QToolBar("Toolbar2")
        self.addToolBar(self.toolbar2)

        #####################################################################

        # Создаем основной виджет и рамку для изображения
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.image_label = QLabel(self)
        self.image_label.setFrameShape(QFrame.Box)  # Рамка для изображения
        self.image_label.setFrameStyle(QFrame.Sunken | QFrame.Raised)
        self.image_label.setLineWidth(2)
        self.image_label.setFixedSize(1600, 800)  # Устанавливаем фиксированный размер для отображения изображения

        # Упаковка элементов в вертикальный layout
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.image_label)

        # параметры хранящие фигуры
        self.circles = []  # Хранит информацию о кругах
        self.ellipses = []
        self.crosses = []
        self.symbols = []
        self.image = None
        self.templates = {
            'circles': {},
            'crosses': {},
            'ellipses': {},
            'symbols': {}
        }
        self.config_file_path = None  # Путь к открытому файлу конфигурации

        # настройки круга
        ################################################################################################################
        # Поля для ввода координат круга
        self.circle_x_input = QLineEdit(self)
        self.circle_x_input.setPlaceholderText("X")
        self.circle_y_input = QLineEdit(self)
        self.circle_y_input.setPlaceholderText("Y")
        self.circle_radius_input = QLineEdit(self)
        self.circle_radius_input.setPlaceholderText("Радиус")
        self.symbol_input = QLineEdit(self)
        self.symbol_input.setPlaceholderText("Cимвол ")
        self.fill_color_input = QLineEdit(self)
        self.fill_color_input.setPlaceholderText("Цвет")

        # Кнопки для добавления и удаления кругов
        self.add_note_button = QPushButton("Добавить ноту", self)
        self.add_note_button.clicked.connect(self.add_circle)

        self.remove_note_button = QPushButton("Убрать ноту", self)
        self.remove_note_button.clicked.connect(self.remove_circle)

        self.save_template_button = QPushButton("Сохранить", self)
        self.save_template_button.clicked.connect(self.save_circle_template)

        # Комбобокс для выбора шаблонов
        self.template_combo = QComboBox(self)
        self.template_combo.setPlaceholderText("Выберите шаблон")
        self.template_combo.currentIndexChanged.connect(self.load_circle_template)

        # Горизонтальный layout для всех элементов
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.circle_x_input)
        input_layout.addWidget(self.circle_y_input)
        input_layout.addWidget(self.circle_radius_input)
        input_layout.addWidget(self.symbol_input)
        input_layout.addWidget(self.fill_color_input)
        input_layout.addWidget(self.add_note_button)
        input_layout.addWidget(self.remove_note_button)
        input_layout.addWidget(self.save_template_button)
        input_layout.addWidget(self.template_combo)

        layout.addLayout(input_layout)  # Добавляем горизонтальный layout с элементами
        ################################################################################################################

        # элементы для крестиков
        # Поля для ввода координат крестика
        self.cross_x_input = QLineEdit(self)
        self.cross_x_input.setPlaceholderText("X")
        self.cross_y_input = QLineEdit(self)
        self.cross_y_input.setPlaceholderText("Y")
        self.cross_size_input = QLineEdit(self)
        self.cross_size_input.setPlaceholderText("Размер")

        self.save_cross_template_button = QPushButton("Сохранить", self)
        self.save_cross_template_button.clicked.connect(self.save_cross_template)

        # Кнопки для добавления и удаления крестиков
        self.add_cross_button = QPushButton("Добавить крестик", self)
        self.add_cross_button.clicked.connect(self.add_cross)

        self.remove_cross_button = QPushButton("Убрать крестик", self)
        self.remove_cross_button.clicked.connect(self.remove_cross)

        # Горизонтальный layout для всех элементов крестиков
        cross_input_layout = QHBoxLayout()
        cross_input_layout.addWidget(self.cross_x_input)
        cross_input_layout.addWidget(self.cross_y_input)
        cross_input_layout.addWidget(self.cross_size_input)
        cross_input_layout.addWidget(self.add_cross_button)
        cross_input_layout.addWidget(self.remove_cross_button)

        # Добавляем кнопку в горизонтальный layout для крестиков
        cross_input_layout.addWidget(self.save_cross_template_button)
        # Добавляем горизонтальный layout с элементами крестиков в основной layout
        layout.addLayout(cross_input_layout)

        # Комбобокс для выбора шаблонов крестиков
        self.cross_template_combo = QComboBox(self)
        self.cross_template_combo.setPlaceholderText("Выберите шаблон крестика")
        self.cross_template_combo.currentIndexChanged.connect(self.load_cross_template)

        # Добавляем комбобокс в горизонтальный layout для крестиков
        cross_input_layout.addWidget(self.cross_template_combo)

        ############################################################
        # меню эллипса

        # Добавьте эти элементы в ваш основной layout
        self.ellipse_x_input = QLineEdit(self)
        self.ellipse_x_input.setPlaceholderText("X")
        self.ellipse_y_input = QLineEdit(self)
        self.ellipse_y_input.setPlaceholderText("Y")
        self.ellipse_width_input = QLineEdit(self)
        self.ellipse_width_input.setPlaceholderText("Ширина")
        self.ellipse_height_input = QLineEdit(self)
        self.ellipse_height_input.setPlaceholderText("Высота")

        self.ellipse_radius_input = QLineEdit(self)
        self.ellipse_radius_input.setPlaceholderText("Закругление")

        self.add_ellipse_button = QPushButton("Добавить баре", self)
        self.add_ellipse_button.clicked.connect(self.add_ellipse)

        self.remove_ellipse_button = QPushButton("Удалить баре", self)
        self.remove_ellipse_button.clicked.connect(self.remove_ellipse)

        self.save_ellipse_template_button = QPushButton("Сохранить", self)
        self.save_ellipse_template_button.clicked.connect(self.save_ellipse_template)

        self.ellipse_template_combo = QComboBox(self)
        self.ellipse_template_combo.setPlaceholderText("баре")
        self.ellipse_template_combo.currentIndexChanged.connect(self.load_ellipse_template)

        # Добавьте элементы в layout
        ellipse_input_layout = QHBoxLayout()
        ellipse_input_layout.addWidget(self.ellipse_x_input)
        ellipse_input_layout.addWidget(self.ellipse_y_input)
        ellipse_input_layout.addWidget(self.ellipse_width_input)
        ellipse_input_layout.addWidget(self.ellipse_height_input)
        ellipse_input_layout.addWidget(self.ellipse_radius_input)
        ellipse_input_layout.addWidget(self.add_ellipse_button)
        ellipse_input_layout.addWidget(self.remove_ellipse_button)
        ellipse_input_layout.addWidget(self.save_ellipse_template_button)
        ellipse_input_layout.addWidget(self.ellipse_template_combo)
        layout.addLayout(ellipse_input_layout)
        ##################################################################################
        # создание символа меню

        self.roman_numeral_combo = QComboBox(self)
        self.roman_numeral_combo.addItems(
            ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', '1'])

        # Новые элементы для стилизации символов
        self.symbol_color_combo = QComboBox(self)
        self.symbol_color_combo.addItems(['Белый', 'Черный', 'Красный', 'Золотой'])
        self.symbol_color_combo.setCurrentText('Белый')

        self.symbol_bg_combo = QComboBox(self)
        self.symbol_bg_combo.addItems(['Без фона', 'Темный', 'Светлый', 'Полупрозрачный'])
        self.symbol_bg_combo.setCurrentText('Темный')

        self.symbol_style_combo = QComboBox(self)
        self.symbol_style_combo.addItems(['Обычный', 'С обводкой', 'Жирный'])
        self.symbol_style_combo.setCurrentText('С обводкой')

        self.symbol_x_input = QLineEdit(self)
        self.symbol_x_input.setPlaceholderText("X")
        self.symbol_y_input = QLineEdit(self)
        self.symbol_y_input.setPlaceholderText("Y")
        self.symbol_size_input = QLineEdit(self)
        self.symbol_size_input.setPlaceholderText("Размер")

        self.add_symbol_button = QPushButton("Добавить символ", self)
        self.add_symbol_button.clicked.connect(self.add_symbol)

        self.remove_symbol_button = QPushButton("Удалить символ", self)
        self.remove_symbol_button.clicked.connect(self.remove_symbol)

        self.save_symbol_template_button = QPushButton("Сохранить", self)
        self.save_symbol_template_button.clicked.connect(self.save_symbol_template)

        self.symbol_template_combo = QComboBox(self)
        self.symbol_template_combo.setPlaceholderText("символы")
        self.symbol_template_combo.setEditable(True)
        line_edit = self.symbol_template_combo.lineEdit()
        line_edit.setText("")
        self.symbol_template_combo.currentIndexChanged.connect(self.load_symbol_template)

        symbol_input_layout = QHBoxLayout(self)
        symbol_input_layout.addWidget(self.symbol_x_input)
        symbol_input_layout.addWidget(self.symbol_y_input)
        symbol_input_layout.addWidget(self.symbol_size_input)
        symbol_input_layout.addWidget(self.roman_numeral_combo)
        symbol_input_layout.addWidget(QLabel("Цвет:"))
        symbol_input_layout.addWidget(self.symbol_color_combo)
        symbol_input_layout.addWidget(QLabel("Фон:"))
        symbol_input_layout.addWidget(self.symbol_bg_combo)
        symbol_input_layout.addWidget(QLabel("Стиль:"))
        symbol_input_layout.addWidget(self.symbol_style_combo)
        symbol_input_layout.addWidget(self.add_symbol_button)
        symbol_input_layout.addWidget(self.remove_symbol_button)
        symbol_input_layout.addWidget(self.save_symbol_template_button)
        symbol_input_layout.addWidget(self.symbol_template_combo)

        layout.addLayout(symbol_input_layout)  # добавляем вывод для элементов символов в строку

        # self.template_bt = QPushButton("Нота  ")
        # self.template_bt.clicked.connect(self.add_circle)

        self.template_bt_del = QPushButton("DEL")
        self.template_bt_del.setFixedSize(40, 30)
        self.template_bt_del.clicked.connect(self.remove_circle)

        # self.cross_bt = QPushButton(" Глушение  ")
        # self.cross_bt.clicked.connect(self.add_cross)
        self.cross_bt_del = QPushButton("DEL")
        self.cross_bt_del.setFixedSize(40, 30)
        self.cross_bt_del.clicked.connect(self.remove_note)

        self.ellipse_bt = QPushButton(" Баре  ")
        self.ellipse_bt.clicked.connect(self.add_ellipse)

        # кнопки баре
        self.bar1 = QPushButton("B1")
        self.bar1.setFixedSize(30, 30)
        self.bar1.clicked.connect(lambda: self.bar_put('b'))
        self.bar2 = QPushButton("B2")
        self.bar2.setFixedSize(30, 30)
        self.bar2.clicked.connect(lambda: self.bar_put('b4'))
        self.bar3 = QPushButton("B3")
        self.bar3.setFixedSize(30, 30)
        self.bar3.clicked.connect(lambda: self.bar_put('b5'))

        ####
        self.bar4 = QPushButton("B13")
        self.bar4.setFixedSize(30, 30)
        self.bar4.clicked.connect(lambda: self.bar_put('13b'))
        self.bar5 = QPushButton("B13")
        self.bar5.setFixedSize(30, 30)
        self.bar5.clicked.connect(lambda: self.bar_put('13b4'))
        self.bar6 = QPushButton("B13")
        self.bar6.setFixedSize(30, 30)
        self.bar6.clicked.connect(lambda: self.bar_put('13b5'))

        ###
        self.bar7 = QPushButton("B14")
        self.bar7.setFixedSize(30, 30)
        self.bar7.clicked.connect(lambda: self.bar_put('14b'))
        self.bar8 = QPushButton("B14")
        self.bar8.setFixedSize(30, 30)
        self.bar8.clicked.connect(lambda: self.bar_put('14b4'))
        self.bar9 = QPushButton("B14")
        self.bar9.setFixedSize(30, 30)
        self.bar9.clicked.connect(lambda: self.bar_put('14b5'))

        self.ellipse_bt_del = QPushButton("DEL")
        self.ellipse_bt_del.setFixedSize(40, 30)
        self.ellipse_bt_del.clicked.connect(self.remove_bar)

        self.symbol_bt = QPushButton(" Разметка  ")
        self.symbol_bt.clicked.connect(self.add_symbol)
        self.symbol_bt_del = QPushButton("DEL")
        self.symbol_bt_del.setFixedSize(40, 30)
        self.symbol_bt_del.clicked.connect(self.remove_symbol)

        self.items_dict = {}  # ключ - число, значение - dict с путями к файлам
        images_dir = 'templates'
        json_dir = 'templates'

        # Собираем картинки
        images_files = {}
        for filename in os.listdir(images_dir):
            if filename.lower().endswith('.png'):
                # Предположим, что имя файла содержит число
                # Например: template_1.png
                num_part = filename.split('_')[1].split('.')[0]  # извлечь число после 'template_'
                images_files[num_part] = os.path.join(images_dir, filename)
        print(images_files)
        # Собираем json
        json_files = {}
        for filename in os.listdir(json_dir):
            if filename.lower().endswith('.json'):
                num_part = filename.split('_')[1].split('.')[0]
                json_files[num_part] = os.path.join(json_dir, filename)

        # Объединяем в один словарь
        all_items = set(images_files.keys()) & set(json_files.keys())  # только совпадающие по числу
        self.items_dict = {}
        for num in all_items:
            self.items_dict[num] = {
                'image': images_files[num],
                'json': json_files[num]
            }
        self.combo_box_json_img = QComboBox()
        for num in sorted(self.items_dict.keys(), key=int):
            self.combo_box_json_img.addItem(f"{num}")

        self.combo_box_json_img.currentIndexChanged.connect(self.template_change)
        ###

        self.clear_bt = QPushButton("DEL")
        self.clear_bt.setFixedSize(40, 30)
        self.clear_bt.clicked.connect(self.clear_all)

        # номера пальцев
        self.finger_bt1 = QPushButton("1")
        self.finger_bt1.setFixedSize(20, 30)
        self.finger_bt1.clicked.connect(lambda: self.finger('1'))

        self.finger_bt2 = QPushButton("2")
        self.finger_bt2.setFixedSize(20, 30)
        self.finger_bt2.clicked.connect(lambda: self.finger('2'))

        self.finger_bt3 = QPushButton("3")
        self.finger_bt3.setFixedSize(20, 30)
        self.finger_bt3.clicked.connect(lambda: self.finger('3'))

        self.finger_bt4 = QPushButton("4")
        self.finger_bt4.setFixedSize(20, 30)
        self.finger_bt4.clicked.connect(lambda: self.finger('4'))

        self.toolbar.addWidget(self.combo_box_json_img)
        self.toolbar.addWidget(self.clear_bt)

        self.add_spacer()

        self.toolbar.addWidget(self.finger_bt1)
        self.toolbar.addWidget(self.finger_bt2)
        self.toolbar.addWidget(self.finger_bt3)
        self.toolbar.addWidget(self.finger_bt4)

        self.symbol_input.setFixedSize(20, 30)
        self.toolbar.addWidget(self.symbol_input)
        # self.toolbar.addWidget(self.template_bt)

        button_labels = [str(elem) for elem in list(range(11, 17)) + list(range(21, 27)) + list(range(31, 37)) + list(
            range(41, 47))]  # Можно добавить сколько угодно

        # Создаем список для хранения кнопок, если нужно
        self.buttons = []

        for label in button_labels:
            btn = QPushButton(label)
            btn.setFixedSize(30, 30)
            btn.clicked.connect(self.test)  # подключение к одному слоту
            self.toolbar.addWidget(btn)
            self.buttons.append(btn)

        self.toolbar.addWidget(self.template_bt_del)

        self.add_spacer()

        self.put_bt1 = QPushButton("1Х")
        self.put_bt1.setFixedSize(30, 30)
        self.put_bt1.clicked.connect(lambda: self.put(1))
        self.put_bt2 = QPushButton("2Х")
        self.put_bt2.setFixedSize(30, 30)
        self.put_bt2.clicked.connect(lambda: self.put(2))
        self.put_bt3 = QPushButton("3Х")
        self.put_bt3.setFixedSize(30, 30)
        self.put_bt3.clicked.connect(lambda: self.put(3))
        self.put_bt4 = QPushButton("4Х")
        self.put_bt4.setFixedSize(30, 30)
        self.put_bt4.clicked.connect(lambda: self.put(4))
        self.put_bt5 = QPushButton("5Х")
        self.put_bt5.setFixedSize(30, 30)
        self.put_bt5.clicked.connect(lambda: self.put(5))
        self.put_bt6 = QPushButton("6Х")
        self.put_bt6.setFixedSize(30, 30)
        self.put_bt6.clicked.connect(lambda: self.put(6))

        for elem in [self.put_bt1, self.put_bt2, self.put_bt3, self.put_bt4, self.put_bt5, self.put_bt6]:
            self.toolbar.addWidget(elem)
        self.toolbar.addWidget(self.cross_bt_del)

        self.add_spacer()

        # self.ellipse_template_combo.setFixedSize(60, 24)
        # self.toolbar.addWidget(self.ellipse_template_combo)
        self.toolbar.addWidget(self.bar1)
        self.toolbar.addWidget(self.bar2)
        self.toolbar.addWidget(self.bar3)
        self.toolbar.addWidget(self.bar4)
        self.toolbar.addWidget(self.bar5)
        self.toolbar.addWidget(self.bar6)
        self.toolbar.addWidget(self.bar7)
        self.toolbar.addWidget(self.bar8)
        self.toolbar.addWidget(self.bar9)
        # self.toolbar.addWidget(self.ellipse_bt)
        self.toolbar.addWidget(self.ellipse_bt_del)

    ########################################################################################################################

    def add_spacer(self):
        spacer_widget = QWidget()
        # Устанавливаем фиксированную ширину для пространства (например, 20 пикселей)
        spacer_widget.setFixedWidth(10)
        # Добавляем виджет-пробел в панель инструментов
        self.toolbar.addWidget(spacer_widget)

    def finger(self, finger):
        self.symbol_input.setText(finger)

    def load_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp)",
                                                   options=options)
        if file_name:
            self.display_image(file_name)

    def change_image(self, index):
        if 0 <= index < len(self.images_files):
            file_path = self.images_files[index]
            self.display_image(file_path)

    def change_json(self, index):
        try:
            if 0 <= index < len(self.json_files):
                file_path = self.json_files[index]
                self.load_config(file_path)
                ln = int(self.json_combo_box.currentText().split('_')[0])

                ln1, ln2, ln3, ln4 = ln * 10, (ln + 1) * 10, (ln + 2) * 10, (ln + 3) * 10
                new_button_labels = [elem for elem in
                                     list(range(ln1 + 1, ln1 + 7)) + list(range(ln2 + 1, ln2 + 7)) + list(
                                         range(ln3 + 1, ln3 + 7)) + list(range(ln4 + 1, ln4 + 7))]
                for btn, label in zip(self.buttons, new_button_labels):
                    btn.setText(str(label))
        except Exception as e:
            print(e)

    def template_change(self, index):
        try:
            if index < 0:
                return
            num_str = self.combo_box_json_img.currentText()
            if num_str in self.items_dict:
                paths = self.items_dict[num_str]
                # Загружаем изображение
                self.display_image(paths['image'])
                # Загружаем шаблон (вызываете вашу функцию)
                self.load_config(paths['json'])
                ln = int(self.combo_box_json_img.currentText().split('_')[0])

                ln1, ln2, ln3, ln4 = ln * 10, (ln + 1) * 10, (ln + 2) * 10, (ln + 3) * 10
                new_button_labels = [elem for elem in
                                     list(range(ln1 + 1, ln1 + 7)) + list(range(ln2 + 1, ln2 + 7)) + list(
                                         range(ln3 + 1, ln3 + 7)) + list(range(ln4 + 1, ln4 + 7))]
                for btn, label in zip(self.buttons, new_button_labels):
                    btn.setText(str(label))
        except Exception as e:
            print(e)

    def display_image(self, file_path):
        self.image = QPixmap(file_path)
        self.image_label.setPixmap(self.image)
        self.image_label.repaint()

    def paintEvent(self, event):
        if self.image:
            painter = QPainter(self.image_label.pixmap())
            painter.drawPixmap(0, 0, self.image)
            # Рисуем круги на новом изображении
            for circle in self.circles:
                # Внешний круг
                painter.setBrush(QColor(*circle['color_outer']))
                painter.drawEllipse(circle['x'] - circle['radius_outer'], circle['y'] - circle['radius_outer'],
                                    circle['radius_outer'] * 2, circle['radius_outer'] * 2)

                # Рисуем символ, если он есть
                if circle['symbol']:
                    # Устанавливаем размер шрифта в зависимости от радиуса
                    font_size = circle['radius_outer'] // 1  # Например, размер шрифта равен половине радиуса
                    font = QFont("Arial", font_size, QFont.Bold)  # Устанавливаем шрифт, размер и стиль (жирный)
                    painter.setFont(font)

                    # Получаем размеры текста
                    font_metrics = QFontMetrics(painter.font())
                    text_width = font_metrics.width(circle['symbol'])
                    text_height = font_metrics.height()

                    # Вычисляем координаты для центрирования текста
                    text_x = circle['x'] - text_width // 2
                    text_y = circle['y'] + text_height // 3  # Смещение по Y для центрирования

                    painter.drawText(text_x, text_y, circle['symbol'])  # Рисуем символ в центре круга

            for cross in self.crosses:
                painter.setPen(QPen(QColor(*cross['color']), 3))  # Здесь 3 - это ширина линии
                size = cross['size']
                x = cross['x']
                y = cross['y']
                painter.drawLine(x - size, y - size, x + size, y + size)  # Первая диагональ
                painter.drawLine(x + size, y - size, x - size, y + size)  # Вторая диагональ

            for ellipse in self.ellipses:
                painter.setBrush(QColor(*ellipse['color']))
                # Рисуем прямоугольник с закругленными углами вместо эллипса
                painter.drawRoundedRect(
                    ellipse['x'] - ellipse['width'] // 2,
                    ellipse['y'] - ellipse['height'] // 2,
                    ellipse['width'],
                    ellipse['height'],
                    ellipse['radius'],  # Радиус закругления углов
                    ellipse['radius']  # Радиус закругления углов
                )

            # Улучшенная отрисовка символов с обводкой и фоном
            for symbol in self.symbols:
                x = symbol['x']
                y = symbol['y']
                size = symbol['size']
                text = symbol['symbol']

                # Получаем дополнительные параметры (с значениями по умолчанию)
                color = symbol.get('color', (255, 255, 255))
                outline_color = symbol.get('outline_color', (0, 0, 0))
                outline_width = symbol.get('outline_width', 1)
                font_family = symbol.get('font_family', 'Arial')
                bold = symbol.get('bold', True)
                has_background = symbol.get('has_background', False)
                background_color = symbol.get('background_color', (50, 50, 50, 180))
                corner_radius = symbol.get('corner_radius', 5)

                # Настраиваем шрифт
                font = QFont(font_family, size, QFont.Bold if bold else QFont.Normal)
                painter.setFont(font)

                # Получаем размеры текста
                font_metrics = QFontMetrics(painter.font())
                text_width = font_metrics.width(text)
                text_height = font_metrics.height()

                # Отступы вокруг текста
                padding = size // 3
                rect_width = text_width + padding * 2
                rect_height = text_height + padding * 2

                # Координаты для фона
                bg_x = x - rect_width // 2
                bg_y = y - rect_height // 2

                # Рисуем фон если нужно
                if has_background:
                    painter.setBrush(QColor(*background_color))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(bg_x, bg_y, rect_width, rect_height, corner_radius, corner_radius)

                # Координаты для текста (центрирование)
                text_x = x - text_width // 2
                text_y = y + text_height // 3

                # Рисуем обводку текста
                if outline_width > 0:
                    painter.setPen(QPen(QColor(*outline_color), outline_width))
                    # Рисуем текст со смещениями для обводки
                    for dx in [-outline_width, 0, outline_width]:
                        for dy in [-outline_width, 0, outline_width]:
                            if dx != 0 or dy != 0:
                                painter.drawText(text_x + dx, text_y + dy, text)

                # Рисуем основной текст
                painter.setPen(QColor(*color))
                painter.drawText(text_x, text_y, text)

            self.image_label.update()

    ####################################################################################################################
    # добавление элементов

    # добавление круга с буквой (нота и обозначение)
    def add_circle(self):
        try:
            x = int(self.circle_x_input.text())
            y = int(self.circle_y_input.text())
            radius = int(self.circle_radius_input.text())

            if not (x and y and radius):
                raise ValueError("Все поля должны быть заполнены.")

            if x - radius < 0 or x + radius > self.image.width() or y - radius < 0 or y + radius > self.image.height():
                raise ValueError("Круг выходит за границы изображения.")

            # Получаем символ из текстового поля
            symbol = self.symbol_input.text()

            # Получаем цвет заливки из текстового поля
            fill_color_input = self.fill_color_input.text()
            if fill_color_input:
                try:
                    fill_color = tuple(map(int, fill_color_input.split(',')))
                except ValueError:
                    raise ValueError("Неверный формат цвета. Используйте формат R,G,B.")
            else:
                fill_color = (255, 0, 0)  # Красный цвет по умолчанию

            self.circles.append({
                'x': x,
                'y': y,
                'radius_outer': radius,
                'color_outer': fill_color,  # цвет для внешнего круга
                'color_inner': fill_color,  # цвет для внутреннего круга
                'symbol': symbol
            })

            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    # добавляем крестик (глушение ноты)
    def add_cross(self):
        try:
            x = int(self.cross_x_input.text())
            y = int(self.cross_y_input.text())
            size = int(self.cross_size_input.text())

            # Проверка на положительность размера
            if size <= 0:
                raise ValueError("Размер должен быть положительным числом.")

            # Проверка, чтобы крестик не выходил за границы изображения
            if (x - size < 0 or x + size > self.image.width() or
                    y - size < 0 or y + size > self.image.height()):
                raise ValueError("Крестик выходит за границы изображения.")

            self.crosses.append({
                'x': x,
                'y': y,
                'size': size,
                'color': (0, 0, 0)  # Цвет для крестика 189, 183, 107
            })

            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    # добавляем эллипс (баре)
    def add_ellipse(self):
        try:
            x = int(self.ellipse_x_input.text())
            y = int(self.ellipse_y_input.text())
            width = int(self.ellipse_width_input.text())
            height = int(self.ellipse_height_input.text())
            # radius = int(self.ellipse_radius_input.text())  # Добавьте ввод радиуса
            # if radius == '':
            #     radius = 10

            # Проверка на положительность ширины и высоты
            if width <= 0 or height <= 0:
                raise ValueError(
                    "Ширина и высота должны быть положительными числами, а радиус не может быть отрицательным.")

            # Проверка, чтобы прямоугольник не выходил за границы изображения
            if (x - width // 2 < 0 or x + width // 2 > self.image.width() or
                    y - height // 2 < 0 or y + height // 2 > self.image.height()):
                raise ValueError("Эллипс выходит за границы изображения.")

            self.ellipses.append({
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'radius': 10,  # Радиус закругления углов
                'color': (189, 183, 107)  # Цвет эллипса
            })

            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))
            print(e)

    # улучшенное добавление символа (номер лада римская цифра)
    def add_symbol(self):
        try:
            x = int(self.symbol_x_input.text())
            y = int(self.symbol_y_input.text())
            size = int(self.symbol_size_input.text())
            symbol = self.roman_numeral_combo.currentText()

            if not (x and y and size and symbol):
                raise ValueError("Все поля должны быть заполнены.")

            # Определяем цвет текста
            color_map = {
                'Белый': (255, 255, 255),
                'Черный': (0, 0, 0),
                'Красный': (255, 0, 0),
                'Золотой': (255, 215, 0)
            }

            # Определяем настройки фона
            bg_map = {
                'Без фона': {'has_background': False},
                'Темный': {'has_background': True, 'background_color': (50, 50, 50, 220)},
                'Светлый': {'has_background': True, 'background_color': (240, 240, 240, 220)},
                'Полупрозрачный': {'has_background': True, 'background_color': (0, 0, 0, 128)}
            }

            # Определяем стиль
            style_map = {
                'Обычный': {'outline_width': 0, 'bold': False},
                'С обводкой': {'outline_width': 2, 'bold': True},
                'Жирный': {'outline_width': 0, 'bold': True}
            }

            # Базовые настройки
            symbol_config = {
                'x': x,
                'y': y,
                'size': size,
                'symbol': symbol,
                'color': color_map[self.symbol_color_combo.currentText()],
                'outline_color': (0, 0, 0),
                'font_family': 'Arial',
                'corner_radius': 5
            }

            # Добавляем настройки фона и стиля
            symbol_config.update(bg_map[self.symbol_bg_combo.currentText()])
            symbol_config.update(style_map[self.symbol_style_combo.currentText()])

            # Добавляем символ в список символов
            self.symbols.append(symbol_config)

            # Обновляем изображение
            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    # глушение струн
    def put(self, number):
        try:
            # из шаблона
            name_srt = ['01E', '02B', '03G', '04D', '05A', '06E']
            choice_str = name_srt[number - 1]
            data = self.templates['circles']
            circle_put = data[choice_str]
            data2 = self.templates['crosses']
            cross_put = data2[str(number)]

            # рисуем круг
            self.circles.append({
                'x': circle_put['x'],
                'y': circle_put['y'],
                'radius_outer': circle_put['radius'],
                'color_outer': circle_put['fill_color'],
                'color_inner': circle_put['fill_color'],
                'symbol': ''
            })

            # глушим
            self.crosses.append({
                'x': cross_put['x'],
                'y': cross_put['y'],
                'size': cross_put['size'],
                'color': (0, 0, 0)  # Цвет для крестика 189, 183, 107
            })

            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    def test(self):
        sender = self.sender()
        print(f"Нажата кнопка с меткой: {sender.text()}")
        data = self.templates['circles']
        circle_put = data[sender.text()]

        self.circles.append({
            'x': circle_put['x'],
            'y': circle_put['y'],
            'radius_outer': circle_put['radius'],
            'color_outer': circle_put['fill_color'],
            'color_inner': circle_put['fill_color'],
            'symbol': self.symbol_input.text()
        })

        self.repaint()

    def bar_put(self, bar_type):
        try:
            data = self.templates['ellipses']
            data2 = self.templates['symbols']
            bar_put = data[bar_type]
            label_bar_put = data2[bar_type]

            self.ellipses.append({
                'x': bar_put['x'],
                'y': bar_put['y'],
                'width': bar_put['width'],
                'height': bar_put['height'],
                'radius': 10,  # Радиус закругления углов
                'color': (189, 183, 107)  # Цвет эллипса
            })

            self.symbols.append({
                'x': label_bar_put['x'],
                'y': label_bar_put['y'],
                'size': label_bar_put['size'],
                'symbol': label_bar_put['symbol']
            })

            self.repaint()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    ####################################################################################################################
    # удаление элементов
    # удаляем круг(ноту)
    def remove_circle(self):
        if self.circles:
            self.circles.pop()  # Удаляем последний круг
            self.repaint()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет кругов для удаления.")

    def remove_cross(self):
        if self.crosses:
            self.crosses.pop()
            self.repaint()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет крестиков для удаления.")

    def remove_note(self):
        if self.crosses:
            self.crosses.pop()
            self.circles.pop()
            # Удаляем последний крестик
            self.repaint()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет глухих нот для удаления.")

    def remove_ellipse(self):
        if self.ellipses:
            self.ellipses.pop()  # Удаляем последний эллипс
            self.repaint()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет эллипсов для удаления.")

    def remove_bar(self):
        if self.ellipses:
            self.ellipses.pop()
            self.symbols.pop()
            self.repaint()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет баре для удаления.")

    # удаляем символ (номер лада)
    def remove_symbol(self):
        if self.symbols:
            self.symbols.pop()  # Удаляем последний эллипс
            self.repaint()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет эллипсов для удаления.")

    def clear_all(self):
        self.circles, self.crosses, self.ellipses, self.symbols = [], [], [], []
        self.repaint()

    ####################################################################################################################
    # сохранение шаблонов
    # сохраняем круг(ноту)
    def save_circle_template(self):
        try:
            x = int(self.circle_x_input.text())
            y = int(self.circle_y_input.text())
            radius = int(self.circle_radius_input.text())
            symbol = self.symbol_input.text()  # Получаем символ из текстового поля

            if not (x and y and radius):
                raise ValueError("Все поля должны быть заполнены.")

            # Получаем цвет заливки из текстового поля
            fill_color_input = self.fill_color_input.text()
            if fill_color_input:
                try:
                    fill_color = tuple(map(int, fill_color_input.split(',')))
                except ValueError:
                    raise ValueError("Неверный формат цвета. Используйте формат R,G,B.")
            else:
                fill_color = (255, 0, 0)  # Красный цвет по умолчанию

            template_name, ok = QInputDialog.getText(self, "Сохранить шаблон", "Введите название шаблона:")
            if ok and template_name:
                template = {
                    'x': x,
                    'y': y,
                    'radius': radius,
                    'fill_color': fill_color,  # Сохраняем цвет заливки
                    'symbol': symbol  # Сохраняем символ
                }
                self.templates['circles'][template_name] = template
                if self.config_file_path:
                    self.save_templates_to_file(self.config_file_path)
                self.template_combo.addItem(template_name)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    # сохраняем крестик(нота глушится)
    def save_cross_template(self):
        try:
            x = int(self.cross_x_input.text())
            y = int(self.cross_y_input.text())
            size = int(self.cross_size_input.text())

            if not (x and y and size):
                raise ValueError("Все поля должны быть заполнены.")

            template_name, ok = QInputDialog.getText(self, "Сохранить шаблон крестика", "Введите название шаблона:")
            if ok and template_name:
                template = {
                    'x': x,
                    'y': y,
                    'size': size
                }
                self.templates['crosses'][template_name] = template
                if self.config_file_path:
                    self.save_templates_to_file(self.config_file_path)
                self.cross_template_combo.addItem(template_name)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    # сохраняем эллипс
    def save_ellipse_template(self):
        try:
            x = int(self.ellipse_x_input.text())
            y = int(self.ellipse_y_input.text())
            width = int(self.ellipse_width_input.text())
            height = int(self.ellipse_height_input.text())

            if not (x and y and width and height):
                raise ValueError("Все поля должны быть заполнены.")

            template_name, ok = QInputDialog.getText(self, "Сохранить шаблон эллипса", "Введите название шаблона:")
            if ok and template_name:
                template = {
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height
                }
                self.templates['ellipses'][template_name] = template
                if self.config_file_path:
                    self.save_templates_to_file(self.config_file_path)
                self.ellipse_template_combo.addItem(template_name)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    # улучшенное сохранение символа
    def save_symbol_template(self):
        try:
            x = int(self.symbol_x_input.text())
            y = int(self.symbol_y_input.text())
            size = int(self.symbol_size_input.text())
            symbol = self.roman_numeral_combo.currentText()

            if not (x and y and size and symbol):
                raise ValueError("Все поля должны быть заполнены.")

            # Сохраняем все параметры стиля
            template_name, ok = QInputDialog.getText(self, "Сохранить шаблон символа", "Введите название шаблона:")
            if ok and template_name:
                template = {
                    'x': x,
                    'y': y,
                    'size': size,
                    'symbol': symbol,
                    'color': (255, 255, 255),  # или из комбобоксов
                    'outline_width': 2,
                    'has_background': True,
                    'background_color': (50, 50, 50, 180),
                    'bold': True,
                    'font_family': 'Arial',
                    'corner_radius': 5
                }
                self.templates['symbols'][template_name] = template
                if self.config_file_path:
                    self.save_templates_to_file(self.config_file_path)
                self.symbol_template_combo.addItem(template_name)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    ########################################################################################################################
    # работа с файлом конфигурации
    # сохранение в JSON файл конфигурации
    def save_templates_to_file(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.templates, f)

    # загрузка файла конфигурации
    def load_config_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл конфигурации", "",
                                                   "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            self.load_config(file_name)

    ########################################################################################################################
    # загрузка конфигурации и обновление комбобоксов
    def load_config(self, file_name):
        try:
            self.config_file_path = file_name
            with open(file_name, "r") as f:
                self.templates = json.load(f)

            # Проверка структуры шаблонов
            if 'circles' not in self.templates or 'crosses' not in self.templates or 'ellipses' not in self.templates or 'symbols' not in self.templates:
                raise ValueError("Неверная структура файла конфигурации.")

            self.update_template_comboboxes()

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл не найден.")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Ошибка",
                                 "Ошибка чтения файла конфигурации. Убедитесь, что файл имеет правильный формат JSON.")
        except ValueError as ve:
            QMessageBox.critical(self, "Ошибка", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    def update_template_comboboxes(self):
        self.template_combo.clear()
        self.cross_template_combo.clear()
        self.ellipse_template_combo.clear()
        self.symbol_template_combo.clear()

        for template_name in self.templates['circles'].keys():
            self.template_combo.addItem(template_name)

        for template_name in self.templates['crosses'].keys():
            self.cross_template_combo.addItem(template_name)

        for template_name in self.templates['ellipses'].keys():
            self.ellipse_template_combo.addItem(template_name)

        for template_name in self.templates['symbols'].keys():
            self.symbol_template_combo.addItem(template_name)

    def save_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_name:
            # Создаем новое изображение для рисования
            image_to_save = QPixmap(self.image.size())
            image_to_save.fill(Qt.white)  # Заполняем белым фоном

            painter = QPainter(image_to_save)
            painter.drawPixmap(0, 0, self.image)  # Рисуем оригинальное изображение

            # Рисуем круги на новом изображении
            for circle in self.circles:
                # Внешний круг
                painter.setBrush(QColor(*circle['color_outer']))
                painter.drawEllipse(circle['x'] - circle['radius_outer'], circle['y'] - circle['radius_outer'],
                                    circle['radius_outer'] * 2, circle['radius_outer'] * 2)

                # Рисуем символ, если он есть
                if circle['symbol']:
                    # Устанавливаем размер шрифта в зависимости от радиуса
                    font_size = circle['radius_outer'] // 1  # Например, размер шрифта равен половине радиуса
                    font = QFont("Arial", font_size, QFont.Bold)  # Устанавливаем шрифт, размер и стиль (жирный)
                    painter.setFont(font)

                    # Получаем размеры текста
                    font_metrics = QFontMetrics(painter.font())
                    text_width = font_metrics.width(circle['symbol'])
                    text_height = font_metrics.height()

                    # Вычисляем координаты для центрирования текста
                    text_x = circle['x'] - text_width // 2
                    text_y = circle['y'] + text_height // 3  # Смещение по Y для центрирования

                    painter.drawText(text_x, text_y, circle['symbol'])  # Рисуем символ в центре круга

            # Рисуем эллипсы на новом изображении
            for ellipse in self.ellipses:
                painter.setBrush(QColor(*ellipse['color']))
                painter.drawRoundedRect(
                    ellipse['x'] - ellipse['width'] // 2,
                    ellipse['y'] - ellipse['height'] // 2,
                    ellipse['width'],
                    ellipse['height'],
                    ellipse['radius'],  # Радиус закругления углов
                    ellipse['radius']  # Радиус закругления углов
                )

            # Рисуем крестики на новом изображении
            for cross in self.crosses:
                painter.setPen(QPen(QColor(*cross['color']), 3))  # Здесь 3 - это ширина линии
                size = cross['size']
                x = cross['x']
                y = cross['y']
                painter.drawLine(x - size, y - size, x + size, y + size)  # Первая диагональ
                painter.drawLine(x + size, y - size, x - size, y + size)  # Вторая диагональ

            # Улучшенная отрисовка символов при сохранении
            for symbol in self.symbols:
                x = symbol['x']
                y = symbol['y']
                size = symbol['size']
                text = symbol['symbol']

                color = symbol.get('color', (255, 255, 255))
                outline_color = symbol.get('outline_color', (0, 0, 0))
                outline_width = symbol.get('outline_width', 1)
                font_family = symbol.get('font_family', 'Arial')
                bold = symbol.get('bold', True)
                has_background = symbol.get('has_background', False)
                background_color = symbol.get('background_color', (50, 50, 50, 180))
                corner_radius = symbol.get('corner_radius', 5)

                font = QFont(font_family, size, QFont.Bold if bold else QFont.Normal)
                painter.setFont(font)

                font_metrics = QFontMetrics(painter.font())
                text_width = font_metrics.width(text)
                text_height = font_metrics.height()

                padding = size // 3
                rect_width = text_width + padding * 2
                rect_height = text_height + padding * 2

                bg_x = x - rect_width // 2
                bg_y = y - rect_height // 2

                if has_background:
                    painter.setBrush(QColor(*background_color))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(bg_x, bg_y, rect_width, rect_height, corner_radius, corner_radius)

                text_x = x - text_width // 2
                text_y = y + text_height // 3

                if outline_width > 0:
                    painter.setPen(QPen(QColor(*outline_color), outline_width))
                    for dx in [-outline_width, 0, outline_width]:
                        for dy in [-outline_width, 0, outline_width]:
                            if dx != 0 or dy != 0:
                                painter.drawText(text_x + dx, text_y + dy, text)

                painter.setPen(QColor(*color))
                painter.drawText(text_x, text_y, text)

            painter.end()  # Завершаем рисование

            # Сохраняем изображение
            if not image_to_save.save(file_name):
                QMessageBox.warning(self, "Ошибка сохранения", "Не удалось сохранить изображение.")

    ######################################################################################################################
    # загрузка шаблонов
    # загрузка круга (ноты)
    def load_circle_template(self):
        template_name = self.template_combo.currentText()
        if template_name in self.templates['circles']:
            template = self.templates['circles'][template_name]
            self.circle_x_input.setText(str(template['x']))
            self.circle_y_input.setText(str(template['y']))
            self.circle_radius_input.setText(str(template['radius']))

            # Устанавливаем цвет заливки
            fill_color = template.get('fill_color', (255, 0, 0))  # Если цвет не найден, используем красный
            self.fill_color_input.setText(','.join(map(str, fill_color)))  # Преобразуем к строке

            # Устанавливаем символ
            self.symbol_input.setText(template.get('symbol', ''))  # Если символ не найден, оставляем пустым

    # загрузка крестика (глушение)
    def load_cross_template(self):
        template_name = self.cross_template_combo.currentText()
        if template_name in self.templates['crosses']:
            template = self.templates['crosses'][template_name]
            self.cross_x_input.setText(str(template['x']))
            self.cross_y_input.setText(str(template['y']))
            self.cross_size_input.setText(str(template['size']))

    # загрузка эллипса (баре)
    def load_ellipse_template(self):
        template_name = self.ellipse_template_combo.currentText()
        if template_name in self.templates['ellipses']:
            template = self.templates['ellipses'][template_name]
            self.ellipse_x_input.setText(str(template['x']))
            self.ellipse_y_input.setText(str(template['y']))
            self.ellipse_width_input.setText(str(template['width']))
            self.ellipse_height_input.setText(str(template['height']))

    # загрузка символов (разметка ладов)
    def load_symbol_template(self):
        template_name = self.symbol_template_combo.currentText()
        if template_name in self.templates['symbols']:
            template = self.templates['symbols'][template_name]
            self.symbol_x_input.setText(str(template['x']))
            self.symbol_y_input.setText(str(template['y']))
            self.symbol_size_input.setText(str(template['size']))
            self.roman_numeral_combo.setCurrentText(template['symbol'])

    ####################################################################################################################
    # видимость элементов управления
    def hide_controls(self):
        self.clear_controls()  # Скрываем все элементы управления

    def show_circle_controls(self):
        self.clear_controls()  # Скрываем все элементы управления
        # Здесь добавьте элементы управления для кругов
        self.circle_x_input.show()
        self.circle_y_input.show()
        self.circle_radius_input.show()
        self.add_note_button.show()  # Кнопка для добавления круга
        self.remove_note_button.show()
        self.save_template_button.show()
        self.template_combo.show()
        self.symbol_input.show()
        self.fill_color_input.show()

    def show_cross_controls(self):
        self.clear_controls()  # Скрываем все элементы управления
        self.cross_x_input.show()
        self.cross_y_input.show()
        self.cross_size_input.show()
        self.add_cross_button.show()  # Кнопка для добавления крестика
        self.save_cross_template_button.show()
        self.remove_cross_button.show()
        self.cross_template_combo.show()

    def show_ellipse_controls(self):
        self.clear_controls()
        self.ellipse_x_input.show()
        self.ellipse_y_input.show()
        self.ellipse_width_input.show()
        self.ellipse_height_input.show()
        self.add_ellipse_button.show()  # Кнопка для добавления эллипса
        self.remove_ellipse_button.show()
        self.save_ellipse_template_button.show()
        self.ellipse_template_combo.show()
        self.ellipse_radius_input.show()

    def show_symbol_controls(self):
        self.clear_controls()
        self.symbol_x_input.show()
        self.symbol_y_input.show()
        self.symbol_size_input.show()
        self.roman_numeral_combo.show()
        self.symbol_color_combo.show()
        self.symbol_bg_combo.show()
        self.symbol_style_combo.show()
        self.add_symbol_button.show()
        self.remove_symbol_button.show()
        self.save_symbol_template_button.show()
        self.symbol_template_combo.show()

    def clear_controls(self):
        self.circle_x_input.hide()
        self.circle_y_input.hide()
        self.circle_radius_input.hide()
        self.add_note_button.hide()
        self.remove_note_button.hide()
        self.save_template_button.hide()
        self.template_combo.hide()
        self.symbol_input.hide()
        self.fill_color_input.hide()

        self.cross_x_input.hide()
        self.cross_y_input.hide()
        self.cross_size_input.hide()
        self.add_cross_button.hide()
        self.save_cross_template_button.hide()
        self.remove_cross_button.hide()
        self.cross_template_combo.hide()

        self.ellipse_x_input.hide()
        self.ellipse_y_input.hide()
        self.ellipse_width_input.hide()
        self.ellipse_height_input.hide()
        self.add_ellipse_button.hide()
        self.remove_ellipse_button.hide()
        self.save_ellipse_template_button.hide()
        self.ellipse_template_combo.hide()
        self.ellipse_radius_input.hide()

        self.symbol_x_input.hide()
        self.symbol_y_input.hide()
        self.symbol_size_input.hide()
        self.roman_numeral_combo.hide()
        self.symbol_color_combo.hide()
        self.symbol_bg_combo.hide()
        self.symbol_style_combo.hide()
        self.add_symbol_button.hide()
        self.remove_symbol_button.hide()
        self.save_symbol_template_button.hide()
        self.symbol_template_combo.hide()

class ChordRecorderTab(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.chords = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Заголовок
        title = QLabel('Запись аккордов')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 18px; font-weight: bold; margin: 10px;')
        layout.addWidget(title)

        # Загрузка файла
        file_layout = QVBoxLayout()
        self.file_label = QLabel('Файл не выбран')
        self.load_btn = QPushButton('Загрузить MP3 файл')
        self.load_btn.clicked.connect(self.load_audio_file)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.load_btn)
        layout.addLayout(file_layout)

        # Настройки детектирования
        settings_layout = QGridLayout()

        # Порог тишины
        settings_layout.addWidget(QLabel('Порог тишины:'), 0, 0)
        self.silence_thresh = QSpinBox()
        self.silence_thresh.setRange(-60, -20)
        self.silence_thresh.setValue(-45)
        self.silence_thresh.setSuffix(" dB")
        settings_layout.addWidget(self.silence_thresh, 0, 1)

        # Минимальная длительность аккорда
        settings_layout.addWidget(QLabel('Мин. длительность:'), 0, 2)
        self.min_chord_duration = QSpinBox()
        self.min_chord_duration.setRange(300, 3000)
        self.min_chord_duration.setValue(800)
        self.min_chord_duration.setSuffix(" мс")
        settings_layout.addWidget(self.min_chord_duration, 0, 3)

        # Длительность тишины перед аккордом
        settings_layout.addWidget(QLabel('Тишина перед:'), 1, 0)
        self.leading_silence = QSpinBox()
        self.leading_silence.setRange(100, 1000)
        self.leading_silence.setValue(300)
        self.leading_silence.setSuffix(" мс")
        settings_layout.addWidget(self.leading_silence, 1, 1)

        # Минимальная амплитуда аккорда
        settings_layout.addWidget(QLabel('Мин. амплитуда:'), 1, 2)
        self.min_amplitude = QDoubleSpinBox()
        self.min_amplitude.setRange(1, 50)
        self.min_amplitude.setValue(4.0)
        self.min_amplitude.setSuffix(" %")
        settings_layout.addWidget(self.min_amplitude, 1, 3)

        # Порог затухания
        settings_layout.addWidget(QLabel('Порог затухания:'), 2, 0)
        self.fade_threshold = QDoubleSpinBox()
        self.fade_threshold.setRange(0.5, 5.0)
        self.fade_threshold.setValue(0.5)
        self.fade_threshold.setSingleStep(0.1)
        self.fade_threshold.setSuffix(" %")
        settings_layout.addWidget(self.fade_threshold, 2, 1)

        # Фильтр низких частот (для устранения шума)
        settings_layout.addWidget(QLabel('Фильтр ВЧ шума:'), 2, 2)
        self.lowpass_filter = QSpinBox()
        self.lowpass_filter.setRange(0, 10000)
        self.lowpass_filter.setValue(8000)
        self.lowpass_filter.setSuffix(" Hz")
        settings_layout.addWidget(self.lowpass_filter, 2, 3)

        layout.addLayout(settings_layout)

        # Кнопка разбивки
        self.split_btn = QPushButton('Найти и извлечь аккорды')
        self.split_btn.clicked.connect(self.split_chords)
        self.split_btn.setEnabled(False)
        layout.addWidget(self.split_btn)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Информация о разбивке
        self.info_label = QLabel('')
        self.info_label.setStyleSheet('font-weight: bold; color: green;')
        layout.addWidget(self.info_label)

        # Сохранение аккордов
        save_layout = QVBoxLayout()
        save_layout.addWidget(QLabel('Название аккорда:'))
        self.chord_name_edit = QLineEdit()
        self.chord_name_edit.setPlaceholderText('Введите название (например: A)')
        save_layout.addWidget(self.chord_name_edit)

        self.save_btn = QPushButton('Сохранить аккорды MP3 320k')
        self.save_btn.clicked.connect(self.save_chords)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)

        layout.addLayout(save_layout)

        # Лог сообщений
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

        self.log_message("Готов к работе. Загрузите MP3 файл.")
        self.log_message("Алгоритм: находим аккорды по амплитуде и длительности → фильтруем шумы")

    def log_message(self, message):
        """Добавляет сообщение в лог"""
        self.log_text.append(f"{message}")

    def load_audio_file(self):
        """Загрузка аудио файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите MP3 файл", "", "MP3 Files (*.mp3)")

        if file_path:
            self.audio_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.split_btn.setEnabled(True)
            self.log_message(f"✅ Загружен файл: {os.path.basename(file_path)}")

    def apply_lowpass_filter(self, audio_segment, cutoff_freq):
        """Применяет низкочастотный фильтр для устранения ВЧ шума"""
        if cutoff_freq <= 0:
            return audio_segment

        try:
            # Конвертируем в numpy array
            samples = np.array(audio_segment.get_array_of_samples())
            sample_rate = audio_segment.frame_rate

            # Создаем lowpass filter
            nyquist = sample_rate / 2
            normal_cutoff = cutoff_freq / nyquist
            b, a = signal.butter(4, normal_cutoff, btype='low', analog=False)

            # Применяем фильтр
            filtered_samples = signal.filtfilt(b, a, samples)

            # Конвертируем обратно в AudioSegment
            if audio_segment.channels == 2:
                filtered_samples = filtered_samples.astype(np.int16)
                filtered_bytes = filtered_samples.tobytes()
            else:
                filtered_samples = filtered_samples.astype(np.int16)
                filtered_bytes = filtered_samples.tobytes()

            return AudioSegment(
                filtered_bytes,
                frame_rate=sample_rate,
                sample_width=audio_segment.sample_width,
                channels=audio_segment.channels
            )
        except Exception as e:
            self.log_message(f"⚠️ Ошибка фильтрации: {e}")
            return audio_segment

    def find_chords_robust(self, audio_segment, silence_thresh=-35, min_chord_duration=800,
                           min_amplitude=10, fade_threshold=1.0, lowpass_cutoff=8000):
        """Находит аккорды, игнорируя шумы и шипение"""

        # Применяем фильтр для устранения ВЧ шума
        if lowpass_cutoff > 0:
            audio_segment = self.apply_lowpass_filter(audio_segment, lowpass_cutoff)

        # Получаем семплы
        samples = np.array(audio_segment.get_array_of_samples())
        sample_rate = audio_segment.frame_rate

        # Конвертируем в моно для анализа
        if audio_segment.channels == 2:
            samples = samples.reshape(-1, 2)
            samples = np.mean(samples, axis=1)

        # Нормализуем амплитуду
        max_amplitude = np.max(np.abs(samples))
        if max_amplitude == 0:
            return []

        normalized = np.abs(samples) / max_amplitude * 100  # в процентах

        # Сглаживаем огибающую
        window_size = int(0.02 * sample_rate)  # 20ms window
        if window_size < 1:
            window_size = 1
        envelope = np.convolve(normalized, np.ones(window_size) / window_size, mode='same')

        # Пороги в линейной шкале
        silence_thresh_linear = 10 ** (silence_thresh / 20) * 100  # в процентах
        min_amp_linear = min_amplitude  # уже в процентах
        fade_thresh_linear = fade_threshold  # уже в процентах

        # Находим сегменты выше порога тишины
        is_sound = envelope > silence_thresh_linear

        # Находим изменения состояния
        changes = np.diff(is_sound.astype(int))
        sound_starts = np.where(changes == 1)[0]  # тишина -> звук
        sound_ends = np.where(changes == -1)[0]  # звук -> тишина

        # Корректируем границы
        if len(sound_starts) == 0 or len(sound_ends) == 0:
            return []

        if sound_starts[0] > sound_ends[0]:
            sound_ends = sound_ends[1:]
        if len(sound_starts) > len(sound_ends):
            sound_ends = np.append(sound_ends, len(envelope))

        chord_segments = []

        for start_idx, end_idx in zip(sound_starts, sound_ends):
            segment_length_ms = (end_idx - start_idx) * 1000 / sample_rate

            # Пропускаем слишком короткие сегменты
            if segment_length_ms < min_chord_duration:
                continue

            # Проверяем максимальную амплитуду в сегменте
            segment_envelope = envelope[start_idx:end_idx]
            max_segment_amp = np.max(segment_envelope)

            # Пропускаем сегменты со слишком низкой амплитудой (шумы)
            if max_segment_amp < min_amp_linear:
                continue

            # Находим точку затухания (где амплитуда падает ниже порога)
            fade_point = end_idx
            for i in range(len(segment_envelope) - 1, max(0, len(segment_envelope) - int(3 * sample_rate)), -1):
                if segment_envelope[i] > fade_thresh_linear:
                    fade_point = start_idx + i
                    break

            # Добавляем небольшую плавность в конце
            fade_point = min(fade_point + int(0.1 * sample_rate), len(samples))

            # Извлекаем сегмент
            chord_samples = samples[start_idx:fade_point]

            # Проверяем, что это не шум (анализ спектра)
            if len(chord_samples) > 1024:
                fft = np.abs(np.fft.rfft(chord_samples[:4096]))
                freqs = np.fft.rfftfreq(4096, 1 / sample_rate)

                # Ищем низкочастотные компоненты (аккорды имеют низкие частоты)
                low_freq_energy = np.sum(fft[freqs < 1000])
                total_energy = np.sum(fft)

                if total_energy > 0 and low_freq_energy / total_energy < 0.3:
                    # Слишком много высоких частот - вероятно шум
                    continue

            # Создаем аудиосегмент
            if audio_segment.channels == 2:
                chord_array = np.column_stack([chord_samples, chord_samples]).flatten().astype(np.int16)
            else:
                chord_array = chord_samples.astype(np.int16)

            chord_segment = AudioSegment(
                chord_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=audio_segment.sample_width,
                channels=audio_segment.channels
            )

            chord_segments.append(chord_segment)

        return chord_segments

    def split_chords(self):
        """Разбивка аудио на аккорды с фильтрацией шумов"""
        if not self.audio_file:
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            self.log_message("🎵 Начинаю поиск аккордов с фильтрацией шумов...")
            self.log_message(f"Мин. амплитуда: {self.min_amplitude.value()}%")
            self.log_message(f"Мин. длительность: {self.min_chord_duration.value()}мс")

            # Загружаем аудио файл
            audio = AudioSegment.from_file(self.audio_file, format="mp3")
            self.progress_bar.setValue(20)

            # Нормализуем аудио
            audio = audio.normalize()
            self.progress_bar.setValue(40)

            # Находим аккорды с фильтрацией
            chord_segments = self.find_chords_robust(
                audio,
                silence_thresh=self.silence_thresh.value(),
                min_chord_duration=self.min_chord_duration.value(),
                min_amplitude=self.min_amplitude.value(),
                fade_threshold=self.fade_threshold.value(),
                lowpass_cutoff=self.lowpass_filter.value()
            )
            self.progress_bar.setValue(80)

            # Обрабатываем каждый аккорд
            self.chords = []
            leading_silence_duration = self.leading_silence.value()

            for i, segment in enumerate(chord_segments):
                # Добавляем тишину перед аккордом
                silence = AudioSegment.silent(duration=leading_silence_duration)
                final_chord = silence + segment

                self.chords.append(final_chord)

                total_duration = len(final_chord) / 1000.0
                sound_duration = len(segment) / 1000.0
                self.log_message(f"🎵 Аккорд {i + 1}: {total_duration:.2f} сек (звук: {sound_duration:.2f}сек)")

            self.progress_bar.setValue(100)

            # Выводим информацию
            total_chords = len(self.chords)
            self.info_label.setText(f"🎉 Найдено аккордов: {total_chords}")

            if total_chords > 0:
                durations = [len(chord) / 1000.0 for chord in self.chords]
                self.log_message(f"✅ Найдено {total_chords} качественных аккордов")
                self.log_message(f"📊 Длительность: от {min(durations):.2f} до {max(durations):.2f} сек")
            else:
                self.log_message("⚠️ Аккорды не найдены. Попробуйте:")
                self.log_message("   - Уменьшить 'Мин. амплитуду'")
                self.log_message("   - Уменьшить 'Мин. длительность'")
                self.log_message("   - Увеличить 'Фильтр ВЧ шума'")

            # Активируем кнопку сохранения
            self.save_btn.setEnabled(total_chords > 0)

            self.progress_bar.setVisible(False)

        except Exception as e:
            self.log_message(f"❌ Ошибка при поиске аккордов: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
            self.progress_bar.setVisible(False)

    def save_chords(self):
        """Сохранение аккордов в MP3 320kbps"""
        if not self.chords or not self.chord_name_edit.text():
            QMessageBox.warning(self, "Ошибка", "Нет аккордов для сохранения или не указано название")
            return

        try:
            save_dir = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
            if not save_dir:
                return

            base_name = self.chord_name_edit.text().strip()
            saved_count = 0

            for i, chord in enumerate(self.chords):
                if i == 0:
                    filename = f"{base_name}.mp3"
                else:
                    filename = f"{base_name}(вариант{i + 1}).mp3"

                file_path = os.path.join(save_dir, filename)
                chord.export(file_path, format="mp3", bitrate="320k")
                saved_count += 1

                duration = len(chord) / 1000.0
                self.log_message(f"💾 Сохранен: {filename} ({duration:.2f} сек)")

            self.log_message(f"✅ Успешно сохранено {saved_count} аккордов")
            QMessageBox.information(self, "Успех", f"Сохранено {saved_count} аккордов в папку: {save_dir}")

        except Exception as e:
            self.log_message(f"❌ Ошибка при сохранении: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить аккорды: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())