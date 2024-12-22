from src.exceptions.base import CloudSellAPIException


class PlanInsertFailed(CloudSellAPIException):
    ...

class FailedToCreatePlan(CloudSellAPIException):
    ...

class PricingPlanNotFound(CloudSellAPIException):
    ...