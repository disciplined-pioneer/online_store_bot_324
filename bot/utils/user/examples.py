import os
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from aiogram.types import Message, FSInputFile
from aiogram import Bot

# Путь к кэшу
MEDIA_CACHE_PATH = "bot/data/user/media_store.json"

CATEGORIES = {
    "viewing:pictures": "paintings_metal",
    "viewing:engraving": "custom_engraving"
}

# Расширения
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ANIMATION_EXTENSIONS = {"gif"}
VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}

# Кэш медиа
def load_media_cache() -> dict:
    if os.path.exists(MEDIA_CACHE_PATH):
        with open(MEDIA_CACHE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_media_cache(cache: dict):
    with open(MEDIA_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

media_cache = load_media_cache()

class MediaWrapper:

    """
    Объект-обёртка над медиафайлом (фото или видео),
    содержащий file_id или путь к локальному файлу.
    """

    def __init__(self, kind: str, file_id: Optional[str] = None, path: Optional[str] = None):
        self.kind = kind  # 'photo', 'animation', 'video'
        self.file_id = file_id
        self.path = path

    async def send(self, msg: Message, reply_markup=None, caption: Optional[str] = None) -> Message:
        bot: Bot = msg.bot

        if self.file_id:
            try:
                if self.kind == "photo":
                    return await msg.answer_photo(self.file_id, caption=caption, reply_markup=reply_markup)
                elif self.kind == "animation":
                    return await msg.answer_animation(self.file_id, caption=caption, reply_markup=reply_markup)
                elif self.kind == "video":
                    return await msg.answer_video(self.file_id, caption=caption, reply_markup=reply_markup)
            except Exception as e:
                logging.warning(f"[ERROR] Failed to send by file_id: {self.file_id} — {e}")
                self.file_id = None  # сбрасываем и пробуем загрузку с path


        if self.path:
            input_file = FSInputFile(self.path)

            if self.kind == "photo":
                sent = await msg.answer_photo(input_file, caption=caption, reply_markup=reply_markup)
                file_id = sent.photo[-1].file_id
            elif self.kind == "animation":
                sent = await msg.answer_animation(input_file, caption=caption, reply_markup=reply_markup)
                file_id = sent.animation.file_id
            elif self.kind == "video":
                sent = await msg.answer_video(input_file, caption=caption, reply_markup=reply_markup)
                file_id = sent.video.file_id
            else:
                raise ValueError("Unsupported media type")

            folder = Path(self.path).parent.name
            filename = Path(self.path).stem

            media_cache.setdefault(folder, {})[filename] = {
                "file_id": file_id,
                "kind": self.kind  # ✅ сохраняем тип
            }
            save_media_cache(media_cache)

            return sent

        raise ValueError("No file_id or path provided")


def get_media_by_index(folder: str, index: int) -> Tuple[Optional[MediaWrapper], int]:
    key = str(index)
    cached = media_cache.get(folder, {}).get(key)

    folder_path = os.path.join("bot", "data", "user", folder)
    path = None
    kind = "video"  # fallback
    count = 0

    if os.path.exists(folder_path):
        valid_files = [
            f for f in os.listdir(folder_path)
            if Path(f).suffix[1:].lower() in (IMAGE_EXTENSIONS | ANIMATION_EXTENSIONS | VIDEO_EXTENSIONS)
            and Path(f).stem.isdigit()
        ]
        count = len(valid_files)

        for file in valid_files:
            if int(Path(file).stem) == index:
                path = os.path.join(folder_path, file)
                ext = Path(file).suffix[1:].lower()
                if ext in IMAGE_EXTENSIONS:
                    kind = "photo"
                elif ext in ANIMATION_EXTENSIONS:
                    kind = "animation"
                elif ext in VIDEO_EXTENSIONS:
                    kind = "video"
                break

    # Если есть кэш — используем его
    if cached and cached.get("file_id"):
        kind = cached.get("kind", kind)
        return MediaWrapper(kind=kind, file_id=cached["file_id"], path=path), count

    if path:
        return MediaWrapper(kind=kind, path=path), count

    return None, count
