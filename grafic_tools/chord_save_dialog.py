import os
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QTextEdit, QPushButton, QHBoxLayout, QComboBox
)


class ChordSaveDialog(QDialog):
    """Диалог сохранения конфигурации аккорда"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сохранить аккорд")
        self.setGeometry(200, 200, 400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        # Поле для имени аккорда
        self.chord_name_input = QLineEdit()
        self.chord_name_input.setPlaceholderText("Например: A, C, Dm, G7")
        layout.addRow("Имя аккорда:", self.chord_name_input)

        # Спинбокс для варианта аккорда
        self.chord_variant_spin = QSpinBox()
        self.chord_variant_spin.setRange(1, 100)
        self.chord_variant_spin.setValue(1)
        layout.addRow("Вариант аккорда:", self.chord_variant_spin)

        # Выбор типа отображения
        self.display_type_combo = QComboBox()
        self.display_type_combo.addItems(["Расположение нот", "Расположение пальцев"])
        layout.addRow("Тип отображения:", self.display_type_combo)

        # Поле для описания
        self.chord_description_input = QTextEdit()
        self.chord_description_input.setMaximumHeight(80)
        self.chord_description_input.setPlaceholderText("Описание аккорда...")
        layout.addRow("Описание:", self.chord_description_input)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addRow(button_layout)

    def get_chord_data(self):
        """Возвращает данные аккорда"""
        return {
            'name': self.chord_name_input.text().strip(),
            'variant': self.chord_variant_spin.value(),
            'display_type': self.display_type_combo.currentText(),
            'description': self.chord_description_input.toPlainText().strip()
        }

    def get_file_suffix(self):
        """Возвращает суффикс файла в зависимости от типа отображения"""
        if self.display_type_combo.currentText() == "Расположение нот":
            return "N"  # Notes
        else:
            return "F"  # Fingers