class BaseNudgeException(Exception):
    """Base class for all Nudge exceptions. Should never be raised directly"""
    pass


class CommandException(BaseNudgeException):
    """An exception occurred while trying to perform a remote Nudge command"""

    def __init__(self, msg, orig_exception):
        self.orig_exception = orig_exception
        self.msg = msg


class BatchValidationError(BaseNudgeException):
    "This batch contains an error"
    
    def __init__(self, batch):
        self.batch = batch
        self.msg = "Batch Validation Failed"


class BatchPushFailure(BaseNudgeException):
    "Pushing this batch failed"

    def __init__(self, http_status=500):
        self.http_status=http_status
