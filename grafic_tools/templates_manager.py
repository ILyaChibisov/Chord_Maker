import json
import os


class TemplatesManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join("templates2", "template.json")

        self.config_path = config_path
        self.templates = {
            'frets': {},
            'notes': {},
            'open_notes': {},
            'barres': {},
            'crop_rects': {}
        }

        self._ensure_config_exists()

        if os.path.exists(config_path):
            self.load_config(config_path)

    def _ensure_config_exists(self):
        """Создает папку и конфиг если они не существуют"""
        templates_dir = os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else "templates2"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            print(f"Создана папка: {templates_dir}")

        if not os.path.exists(self.config_path):
            default_config = {
                'frets': {},
                'notes': {},
                'open_notes': {},
                'barres': {},
                'crop_rects': {}
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"Создан базовый конфиг: {self.config_path}")

    def load_config(self, file_path):
        """Загрузка конфигурации из JSON файла"""
        try:
            self.config_path = file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_templates = json.load(f)

                for key in self.templates:
                    if key in loaded_templates:
                        self.templates[key] = loaded_templates[key]

            print(f"Конфигурация загружена из: {file_path}")
            return True
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return False

    def save_templates(self, file_path=None):
        """Сохранение шаблонов в JSON файл"""
        if file_path:
            self.config_path = file_path

        if self.config_path:
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.templates, f, indent=2, ensure_ascii=False)
                print(f"Шаблоны сохранены в: {self.config_path}")
                return True
            except Exception as e:
                print(f"Ошибка сохранения шаблонов: {e}")
                return False
        return False

    def add_template(self, template_type, name, data):
        """Добавление нового шаблона"""
        if template_type in self.templates:
            self.templates[template_type][name] = data
            return True
        return False

    def get_template(self, template_type, name):
        """Получение шаблона по имени"""
        return self.templates.get(template_type, {}).get(name)

    def get_all_templates(self, template_type):
        """Получение всех шаблонов определенного типа"""
        return self.templates.get(template_type, {})