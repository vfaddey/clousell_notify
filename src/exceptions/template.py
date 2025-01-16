from src.exceptions.base import CloudsellNotifyException


class TemplateInsertFailed(CloudsellNotifyException):
    ...

class NoSuchTemplate(CloudsellNotifyException):
    ...
