import json
import openpyxl
import os


def update_note_styles_no_pandas():
    """
    Версия без использования pandas
    """
    excel_path = os.path.join("templates2", "chord_config.xlsx")
    json_path = os.path.join("templates2", "template.json")

    try:
        print("Чтение Excel файла...")
        workbook = openpyxl.load_workbook(excel_path)
        sheet = workbook['COLOR']

        # Создаем словарь для сопоставления нот и стилей
        note_to_style = {}

        # Находим колонки
        headers = [cell.value for cell in sheet[1]]
        try:
            ton_col = headers.index('ton')
            color_col = headers.index('color')
        except ValueError:
            print("Ошибка: В таблице должны быть колонки 'ton' и 'color'")
            return

        # Читаем данные
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
            if row[ton_col] and row[color_col]:
                note_name = str(row[ton_col]).strip()
                style_name = str(row[color_col]).strip()
                note_to_style[note_name] = style_name
                print(f"Загружено: {note_name} -> {style_name}")

        print(f"Всего загружено {len(note_to_style)} соответствий")

        # Чтение и обновление JSON
        print("Чтение JSON файла...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'notes' not in data:
            print("Ошибка: В JSON нет раздела 'notes'")
            return

        updated_count = 0
        for note_key, note_data in data['notes'].items():
            if 'note_name' in note_data:
                note_name = note_data['note_name']
                if note_name in note_to_style:
                    old_style = note_data.get('style', 'не установлен')
                    note_data['style'] = note_to_style[note_name]
                    updated_count += 1
                    print(f"Обновлено: {note_key} - '{note_name}' - '{old_style}' -> '{note_to_style[note_name]}'")

        # Сохранение
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Готово! Обновлено {updated_count} записей")

    except Exception as e:
        print(f"Ошибка: {e}")


# Запуск
if __name__ == "__main__":
    update_note_styles_no_pandas()