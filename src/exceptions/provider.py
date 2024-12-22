from src.exceptions.base import CloudSellAPIException


class ProviderInsertFailed(CloudSellAPIException):
    ...


class ProviderNotFound(CloudSellAPIException):
    ...


class ProviderAlreadyExists(CloudSellAPIException):
    ...


class ProviderDeleteFailed(CloudSellAPIException):
    ...