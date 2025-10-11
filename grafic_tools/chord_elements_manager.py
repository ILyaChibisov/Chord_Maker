import copy


class ChordElementsManager:
    """Класс для управления элементами аккордов"""

    def __init__(self):
        self.elements = {
            'frets': [],
            'notes': [],
            'open_notes': [],
            'barres': [],
            'crop_rect': None
        }

    def prepare_elements_for_saving(self, display_type):
        """Подготавливает элементы для сохранения в зависимости от типа отображения"""
        elements_copy = copy.deepcopy(self.elements)

        if display_type == "Расположение нот":
            # Для нот: показываем названия нот
            for note in elements_copy['notes']:
                note['display_text'] = 'note_name'
            for open_note in elements_copy['open_notes']:
                open_note['display_text'] = 'note_name'
        else:
            # Для пальцев: показываем пальцы и символы
            for note in elements_copy['notes']:
                note['display_text'] = 'finger'
            for open_note in elements_copy['open_notes']:
                open_note['display_text'] = 'symbol'

        return elements_copy

    def update_elements_display(self, display_type):
        """Обновляет отображение элементов в реальном времени"""
        if display_type == "Расположение нот":
            for note in self.elements['notes']:
                note['display_text'] = 'note_name'
            for open_note in self.elements['open_notes']:
                open_note['display_text'] = 'note_name'
        else:
            for note in self.elements['notes']:
                note['display_text'] = 'finger'
            for open_note in self.elements['open_notes']:
                open_note['display_text'] = 'symbol'