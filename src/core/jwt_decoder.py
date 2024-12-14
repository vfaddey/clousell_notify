from src.core.config import settings
from jose import jwt, JWTError

from src.core.exceptions import InvalidToken


class JWTDecoder:

    @staticmethod
    def decode(token: str, algorithm: str = settings.JWT_ALGORITHM, key: str = settings.JWT_PUBLIC_KEY) -> dict:
        try:
            payload = jwt.decode(token, key, algorithms=[algorithm])
            return payload
        except JWTError as e:
            raise InvalidToken('Token is invalid or expired')