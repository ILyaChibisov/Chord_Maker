from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QComboBox, QVBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt


class ControlsManager:
    """Класс для управления элементами управления интерфейса"""

    def __init__(self, parent):
        self.parent = parent
        self.control_widgets = {}

    def setup_controls_container(self, main_layout):
        """Настраивает контейнер для элементов управления"""
        self.controls_container = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_container)
        main_layout.addWidget(self.controls_container)

    def hide_all_controls(self):
        """Скрывает все элементы управления"""
        for widget in self.control_widgets.values():
            if hasattr(widget, 'hide'):
                widget.hide()

    def show_controls(self, control_type):
        """Показывает элементы управления определенного типа"""
        self.hide_all_controls()
        if control_type in self.control_widgets:
            self.control_widgets[control_type].show()

    def register_control_widget(self, name, widget):
        """Регистрирует виджет управления"""
        self.control_widgets[name] = widget
        self.controls_layout.addWidget(widget)
        widget.hide()