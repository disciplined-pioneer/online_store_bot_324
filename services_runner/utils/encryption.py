import uuid
import base64
from pathlib import Path
from cryptography.fernet import Fernet


class Encryption:
    
    def __init__(self, key_path: Path):
        """
        Инициализация класса шифрования.
        Если ключа нет — он будет сгенерирован.
        :param key_path: Путь к файлу ключа (например: Path('key.pem')).
        """
        self.key_path = key_path

        # Генерация ключа, если он отсутствует
        if not self.key_path.exists():
            self._generate_and_save_key()

        self.key = self.key_path.read_bytes()
        self.cipher = Fernet(self.key)

    def _generate_and_save_key(self):
        """
        Генерация и сохранение нового ключа.
        """
        key = Fernet.generate_key()
        self.key_path.parent.mkdir(parents=True, exist_ok=True)  # Создать папку, если её нет
        with open(self.key_path, 'wb') as f:
            f.write(key)

    def encrypt(self, data: str) -> bytes:
        """
        Зашифровать строку.
        :param data: строка для шифрования.
        :return: зашифрованные данные (байты).
        """
        return self.cipher.encrypt(data.encode())

    def decrypt(self, token: bytes) -> str:
        """
        Расшифровать строку.
        :param token: зашифрованные байты.
        :return: исходная строка.
        """
        return self.cipher.decrypt(token).decode()


def generate_uuid() -> str:
    """
    Генерация короткого UUID (22 символа).
    :return: base64 UUID строка.
    """
    return (
        base64
        .urlsafe_b64encode(uuid.uuid4().bytes)
        .rstrip(b'=')
        .decode('ascii')
    )
