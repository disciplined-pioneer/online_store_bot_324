from enum import Enum

class BillStatus(Enum):
    SUCCESS = "success"      # Платёж прошёл успешно
    PENDING = "pending"      # Платёж ожидает подтверждения
    FAIL = "fail"            # Платёж отменён или отклонён
    UNKNOWN = "unknown"      # Неизвестный статус (например, новый тип)
