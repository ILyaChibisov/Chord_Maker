import pandas as pd
import os
import json
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt


class ChordConfigManager:
    def __init__(self):
        self.excel_path = os.path.join("templates2", "chord_config.xlsx")
        self.template_path = os.path.join("templates2", "template.json")
        self.image_path = os.path.join("templates2", "img.png")
        self.chord_data = {}
        self.ram_data = {}
        self.templates = {}

    def load_config_data(self):
        """Загрузка всех данных из Excel и JSON"""
        try:
            # Загружаем Excel файл
            if os.path.exists(self.excel_path):
                # Основной лист с аккордами
                df_chords = pd.read_excel(self.excel_path, sheet_name=0)
                print("=" * 80)
                print("КОЛОНКИ В EXCEL:", df_chords.columns.tolist())

                # Конвертируем в словари
                self.chord_data = df_chords.to_dict('records')
                print(f"Загружено {len(self.chord_data)} аккордов")

            else:
                print(f"Excel файл не найден: {self.excel_path}")
                return False

            # Загружаем JSON шаблоны
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
                print("JSON шаблоны загружены")
            else:
                print(f"JSON файл не найден: {self.template_path}")
                return False

            return True

        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_chord_groups(self):
        """Получение списка групп аккордов"""
        groups = set()
        for chord in self.chord_data:
            chord_name = chord.get('CHORD')
            if chord_name:
                chord_name = str(chord_name)
                base_chord = ''.join([c for c in chord_name if c.isalpha()])
                if base_chord:
                    groups.add(base_chord)
        return sorted(list(groups))

    def get_chords_by_group(self, group):
        """Получение аккордов по группе"""
        chords = []
        for chord in self.chord_data:
            chord_name = chord.get('CHORD')
            variant = chord.get('VARIANT')

            if chord_name and variant is not None:
                chord_name = str(chord_name)
                base_chord = ''.join([c for c in chord_name if c.isalpha()])
                if base_chord == group:
                    chords.append({
                        'name': f"{chord_name}{variant}",
                        'chord': chord_name,
                        'variant': variant,
                        'data': chord
                    })
        return sorted(chords, key=lambda x: x['name'])

    def get_ram_crop_area(self, ram_name):
        """Получение области обрезки из RAM в JSON"""
        if not ram_name or self._is_empty_value(ram_name):
            print(f"RAM '{ram_name}' пустой или не найден")
            return None

        ram_name = str(ram_name).strip()
        print(f"🔍 Поиск области обрезки для RAM: '{ram_name}'")

        # Ищем RAM в разделе crop_rects
        if 'crop_rects' in self.templates and ram_name in self.templates['crop_rects']:
            crop_data = self.templates['crop_rects'][ram_name]
            area = (
                crop_data.get('x', 0),
                crop_data.get('y', 0),
                crop_data.get('width', 100),
                crop_data.get('height', 100)
            )
            print(f"✅ Найдена область обрезки '{ram_name}': {area}")
            return area

        print(f"❌ Область обрезки для '{ram_name}' не найдена в JSON")
        return None

    def get_ram_elements(self, ram_name):
        """Получение элементов RAM по имени"""
        elements = []
        if not ram_name or self._is_empty_value(ram_name):
            return elements

        ram_name = str(ram_name).strip()

        # Ищем элементы RAM в frets
        if ram_name in self.templates.get('frets', {}):
            elements.append({
                'type': 'fret',
                'data': self.templates['frets'][ram_name]
            })

        # Ищем элементы с суффиксами (RAM1, RAM2 и т.д.)
        for i in range(1, 5):
            element_key = f"{ram_name}{i}"
            if element_key in self.templates.get('frets', {}):
                elements.append({
                    'type': 'fret',
                    'data': self.templates['frets'][element_key]
                })

        return elements

    def _is_empty_value(self, value):
        """Проверка на пустое значение"""
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == '':
            return True
        return False

    def get_elements_from_column(self, column_value, element_type):
        """Получение элементов из колонки Excel"""
        elements = []

        if self._is_empty_value(column_value):
            return elements

        element_str = str(column_value)
        element_list = element_str.split(',')

        for element_key in element_list:
            element_key = element_key.strip()

            # Ищем элемент в соответствующем разделе templates
            if element_key in self.templates.get(element_type, {}):
                elements.append({
                    'type': element_type[:-1] if element_type.endswith('s') else element_type,
                    'data': self.templates[element_type][element_key]
                })

        return elements

    def get_chord_elements(self, chord_config, display_type):
        """Получение элементов аккорда в зависимости от типа отображения"""
        elements = []

        # Добавляем RAM элементы (всегда)
        ram_key = chord_config.get('RAM')
        if ram_key:
            ram_elements = self.get_ram_elements(ram_key)
            elements.extend(ram_elements)

        if display_type == "notes":
            # Для нот: используем FN
            fn_elements = self.get_elements_from_column(chord_config.get('FN'), 'notes')
            elements.extend(fn_elements)

        else:  # fingers
            # Для пальцев: используем FO и F2
            fo_elements = self.get_elements_from_column(chord_config.get('FO'), 'notes')
            f2_elements = self.get_elements_from_column(chord_config.get('F2'), 'notes')

            elements.extend(fo_elements)
            elements.extend(f2_elements)

        return elements

    def draw_elements_on_image(self, pixmap, elements, crop_rect=None):
        """Рисование элементов на изображении с учетом масштаба"""
        if pixmap.isNull():
            return pixmap

        result_pixmap = QPixmap(pixmap)
        painter = QPainter(result_pixmap)

        try:
            for element in elements:
                if element['type'] == 'fret':
                    self.draw_fret(painter, element['data'], crop_rect)
                elif element['type'] == 'note':
                    self.draw_note(painter, element['data'], crop_rect)

        finally:
            painter.end()

        return result_pixmap

    def draw_fret(self, painter, fret_data, crop_rect=None):
        """Рисование лада с учетом масштаба"""
        try:
            # Адаптируем координаты к масштабу обрезанного изображения
            adapted_data = self._adapt_coordinates(fret_data, crop_rect)
            from drawing_elements import DrawingElements
            DrawingElements.draw_fret(painter, adapted_data)
        except ImportError:
            adapted_data = self._adapt_coordinates(fret_data, crop_rect)
            x = adapted_data.get('x', 0)
            y = adapted_data.get('y', 0)
            size = adapted_data.get('size', 20)
            symbol = adapted_data.get('symbol', 'I')

            painter.setPen(Qt.black)
            font = painter.font()
            font.setPointSize(size)
            painter.setFont(font)
            painter.drawText(x, y, symbol)
        except Exception as e:
            print(f"Ошибка рисования лада: {e}")

    def draw_note(self, painter, note_data, crop_rect=None):
        """Рисование ноты с учетом масштаба"""
        try:
            # Адаптируем координаты к масштабу обрезанного изображения
            adapted_data = self._adapt_coordinates(note_data, crop_rect)
            from drawing_elements import DrawingElements
            DrawingElements.draw_note(painter, adapted_data)
        except ImportError:
            adapted_data = self._adapt_coordinates(note_data, crop_rect)
            x = adapted_data.get('x', 0)
            y = adapted_data.get('y', 0)
            radius = adapted_data.get('radius', 15)
            symbol = adapted_data.get('symbol', '1') or adapted_data.get('finger', '1')

            painter.setPen(Qt.black)
            painter.setBrush(Qt.red)
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(Qt.white)
            painter.drawText(x - 3, y + 3, symbol)
        except Exception as e:
            print(f"Ошибка рисования ноты: {e}")

    def _adapt_coordinates(self, element_data, crop_rect):
        """Адаптация координат элемента к обрезанному изображению"""
        if not crop_rect:
            return element_data.copy()

        # Копируем данные элемента
        adapted_data = element_data.copy()

        # Получаем координаты обрезки
        crop_x, crop_y, crop_width, crop_height = crop_rect

        # Предполагаем, что оригинальные координаты заданы для полного изображения
        # Вычитаем координаты обрезки, чтобы перевести в систему координат обрезанного изображения
        if 'x' in adapted_data:
            adapted_data['x'] = adapted_data['x'] - crop_x

        if 'y' in adapted_data:
            adapted_data['y'] = adapted_data['y'] - crop_y

        return adapted_data