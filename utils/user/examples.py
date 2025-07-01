import os
import json
from pathlib import Path
from typing import Optional, Tuple

from aiogram import Bot
from aiogram.types import FSInputFile, Message

MEDIA_CACHE_PATH = "data/media_store.json"

CATEGORIES = {
    "viewing:pictures": "paintings_metal",
    "viewing:engraving": "custom_engraving"
}

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
VIDEO_EXTENSIONS = {"mp4", "mov"}


# Загрузка кэша file_id из файла
def load_media_cache() -> dict:
    if os.path.exists(MEDIA_CACHE_PATH):
        with open(MEDIA_CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


# Сохранение кэша file_id в файл
def save_media_cache(cache: dict):
    with open(MEDIA_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


# Глобальный кэш медиа
media_cache = load_media_cache()


class MediaWrapper:
    """
    Объект-обёртка над медиафайлом (фото или видео),
    содержащий file_id или путь к локальному файлу.
    """

    def __init__(self, kind: str, file_id: Optional[str] = None, path: Optional[str] = None):
        self.kind = kind  # 'photo' или 'video'
        self.file_id = file_id
        self.path = path

    async def send(self, msg: Message, reply_markup=None) -> Message:
        """
        Отправка медиа. Если есть file_id — используем его.
        Если нет — загружаем файл с диска, отправляем и кэшируем file_id.
        """
        bot: Bot = msg.bot

        # Отправка по file_id
        if self.file_id:
            if self.kind == "photo":
                return await msg.answer_photo(self.file_id, reply_markup=reply_markup)
            elif self.kind == "video":
                return await msg.answer_video(self.file_id, reply_markup=reply_markup)

        # Отправка с диска и кэширование
        if self.path:
            input_file = FSInputFile(self.path)
            sent: Message

            if self.kind == "photo":
                sent = await msg.answer_photo(input_file, reply_markup=reply_markup)
                file_id = sent.photo[-1].file_id
            elif self.kind == "video":
                sent = await msg.answer_video(input_file, reply_markup=reply_markup)
                file_id = sent.video.file_id
            else:
                raise ValueError("Unsupported media type")

            # Кэширование file_id
            folder = Path(self.path).parent.name
            filename = Path(self.path).stem
            media_cache.setdefault(folder, {})[filename] = {"file_id": file_id}
            save_media_cache(media_cache)

            return sent

        raise ValueError("No file_id or path provided")


def get_media_by_index(folder: str, index: int) -> Tuple[Optional[MediaWrapper], int]:
    """
    Получает объект MediaWrapper по номеру (1, 2, 3...) и общее количество файлов.
    Работает только с медиафайлами, имя которых является числом.
    """

    folder_path = os.path.join("data", folder)
    if not os.path.exists(folder_path):
        return None, 0

    # Собираем только те файлы, у которых числовое имя
    media_files = []
    for file in os.listdir(folder_path):
        stem = Path(file).stem
        try:
            int(stem)
            media_files.append(file)
        except ValueError:
            continue  # Пропускаем нечисловые (например, .gitkeep)

    # Сортировка по номеру
    media_files.sort(key=lambda x: int(Path(x).stem))
    total = len(media_files)

    if index < 1 or index > total:
        return None, total

    filename = media_files[index - 1]
    ext = filename.split(".")[-1].lower()
    path = os.path.join(folder_path, filename)
    key = Path(filename).stem  # без расширения

    # Проверяем, есть ли уже сохранённый file_id
    cached = media_cache.get(folder, {}).get(key)

    if ext in IMAGE_EXTENSIONS:
        kind = "photo"
    elif ext in VIDEO_EXTENSIONS:
        kind = "video"
    else:
        return None, total  # Неподдерживаемый формат

    if cached:
        return MediaWrapper(kind=kind, file_id=cached["file_id"]), total
    else:
        return MediaWrapper(kind=kind, path=path), total
