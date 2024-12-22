from src.exceptions.base import CloudSellAPIException


class UserNotFound(CloudSellAPIException):
    ...


class AuthorizationFailed(CloudSellAPIException):
    ...
