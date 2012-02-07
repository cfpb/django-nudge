

class BaseNudgeException(Exception):
    "This is the base Nudge Exception, and you probably shouldn't use it"
    pass
    
class BatchValidationError(BaseNudgeException):
    "This batch contains an error"
    
    def __init__(self,batch):
        self.batch=batch
        self.msg="Hi"