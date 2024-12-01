from typing import Optional
from pydantic import BaseModel


class Review(BaseModel):
    id: Optional[int] = None
    reviewer_name: str
    review_title: str
    review_rating: int
    review_content: str
    email_address: str
    country: str
    review_date: str
