from pydantic import BaseModel

class FeedbackBase(BaseModel):
    campaign_id: int
    metric_id: int
    texto_feedback: str
    
class FeedbackCreate(FeedbackBase):
    pass

class FeedbackOut(FeedbackBase):
    id: int

    class Config:
        from_attributes = True