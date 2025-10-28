import os
import shutil
import sys
import argparse


def create_sounds_folder():
    """Создает папку sounds по относительному пути если её нет"""
    sounds_path = os.path.join(os.getcwd(), "sounds")
    if not os.path.exists(sounds_path):
        os.makedirs(sounds_path)
        print(f"Создана папка: {sounds_path}")
    else:
        print(f"Папка уже существует: {sounds_path}")
    return sounds_path


def has_mp3_files(folder_path):
    """Проверяет, есть ли в папке MP3 файлы"""
    try:
        for item in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, item)):
                if item.lower().endswith('.mp3'):
                    return True
        return False
    except PermissionError:
        print(f"Нет доступа к папке: {folder_path}")
        return False


def is_terminal_folder(folder_path):
    """Проверяет, является ли папка конечной (не содержит подпапок)"""
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                return False
        return True
    except PermissionError:
        print(f"Нет доступа к папке: {folder_path}")
        return False


def copy_only_mp3_files(source_folder, target_folder):
    """Копирует только MP3 файлы из исходной папки в целевую"""
    copied_files = 0
    try:
        # Создаем целевую папку если её нет
        os.makedirs(target_folder, exist_ok=True)

        # Копируем только MP3 файлы
        for item in os.listdir(source_folder):
            source_path = os.path.join(source_folder, item)
            if os.path.isfile(source_path) and item.lower().endswith('.mp3'):
                target_path = os.path.join(target_folder, item)
                shutil.copy2(source_path, target_path)
                copied_files += 1
                print(f"  Скопирован MP3: {item}")

        return copied_files > 0
    except Exception as e:
        print(f"Ошибка при копировании файлов из {source_folder}: {e}")
        return False


def find_and_copy_mp3_folders(source_directory, target_directory):
    """Находит конечные папки с MP3 файлами и копирует только MP3 в целевую директорию"""
    copied_folders = []

    for root, dirs, files in os.walk(source_directory):
        # Если это конечная папка (без подпапок)
        if is_terminal_folder(root):
            # Проверяем есть ли MP3 файлы
            if has_mp3_files(root):
                folder_name = os.path.basename(root)
                target_path = os.path.join(target_directory, folder_name)

                # Копируем только MP3 файлы
                try:
                    if os.path.exists(target_path):
                        print(f"Папка уже существует в назначении: {folder_name}")
                    else:
                        print(f"Копируем MP3 из: {folder_name}")
                        if copy_only_mp3_files(root, target_path):
                            copied_folders.append(folder_name)
                            print(f"Успешно скопирована папка: {folder_name}")
                        else:
                            # Если не удалось скопировать MP3 файлы, удаляем пустую папку
                            if os.path.exists(target_path):
                                os.rmdir(target_path)
                except Exception as e:
                    print(f"Ошибка при обработке папки {folder_name}: {e}")

    return copied_folders


def main():
    parser = argparse.ArgumentParser(description='Копирование только MP3 файлов из папок')
    parser.add_argument('source_dir', nargs='?', help='Исходная директория для поиска')

    args = parser.parse_args()

    # Создаем папку sounds
    sounds_folder = create_sounds_folder()

    # Получаем исходную директорию
    if args.source_dir:
        source_dir = args.source_dir
    else:
        source_dir = input("Введите путь к исходной директории: ").strip()

    # Проверяем существование исходной директории
    if not os.path.exists(source_dir):
        print("Ошибка: Указанная директория не существует!")
        return

    if not os.path.isdir(source_dir):
        print("Ошибка: Указанный путь не является директорией!")
        return

    print(f"\nПоиск папок с MP3 файлами в: {source_dir}")
    print(f"Копирование ТОЛЬКО MP3 файлов в: {sounds_folder}\n")

    # Находим и копируем папки с MP3
    copied_folders = find_and_copy_mp3_folders(source_dir, sounds_folder)

    # Выводим результат
    print(f"\n{'=' * 50}")
    if copied_folders:
        print(f"Успешно скопировано папок: {len(copied_folders)}")
        print("Скопированные папки (только с MP3 файлами):")
        for folder in copied_folders:
            print(f"  - {folder}")
    else:
        print("Не найдено папок с MP3 файлами для копирования")


if __name__ == "__main__":
    main()