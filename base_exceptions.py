class BaseAppException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UserAlreadyExistsException(BaseAppException):
    def __init__(self, name: str):
        super().__init__(f"Пользователь с именем '{name}' уже существует.")


class UserNotFoundException(BaseAppException):
    def __init__(self, user_id: int):
        super().__init__(f"Пользователь с ID '{user_id}' не найден.")


class InvalidDataException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(f"Ошибка данных: {message}")


class EncryptionException(BaseAppException):

    def __init__(self, message: str):
        super().__init__(f"Ошибка шифрования: {message}")
