

class BaseNudgeException(Exception):
    "This is the base Nudge Exception, and you probably shouldn't use it"
    pass
    
class BatchValidationError(BaseNudgeException):
    "This batch contains an error"
    
    def __init__(self,batch):
        self.batch=batch
        self.msg="Batch Validation Failed"
        
class BatchPushFailure(BaseNudgeException):
    "Pushing this batch failed"
    
    def __init__(self, http_status=500):
        self.http_status=http_status