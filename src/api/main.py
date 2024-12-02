import os

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from src.common.db import get_db, ensure_db_ready
from src.common.tables import Review as DbReview
from src.common.dto import Review

ensure_db_ready()
app = FastAPI(
    title="Reviews API",
    description="API for managing reviews",
    version="1.0.0",
    contact={"name": "Stefan Kecskes", "email": "mr.kecskes@gmail.com"}
)

@app.get("/", include_in_schema=False)
async def read_root():
    """Redirects to the API documentation"""
    return RedirectResponse(url="/docs")


@app.post("/reviews", tags=["Reviews"])
async def create_review(review: Review, db: Session = Depends(get_db)):
    """Create a new review"""
    review_data = review.model_dump()
    db_review = DbReview(**review_data)
    db.add(db_review)
    db.commit()
    return {"id": db_review.id}

@app.get("/reviews_by/{user_email}", tags=["Reviews"])
async def reviews_by_user(user_email: str, db: Session = Depends(get_db)):
    """Get all reviews by user email"""
    # result = db.execute(text("SELECT * FROM reviews WHERE email_address = :user_email"), {"user_email": user_email}).fetchall()
    result = db.query(DbReview).filter(DbReview.email_address == user_email).all()
    if result:
        return {"reviews_by_user": user_email, "data": result}
    else:
        raise HTTPException(status_code=404, detail="User not reviewed any product yet")

@app.put("/reviews", tags=["Reviews"])
async def update_review(review: Review, db: Session = Depends(get_db)):
    """Update an existing review"""
    review_data = review.model_dump()
    db_review = db.query(DbReview).filter(DbReview.id == review.id).first()
    if db_review:
        for key, value in review_data.items():
            setattr(db_review, key, value)
        db.commit()
        return {"id": db_review.id}
    else:
        raise HTTPException(status_code=404, detail="Review not found")

@app.delete("/reviews", tags=["Reviews"])
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete an existing review by review id"""
    db_review = db.query(DbReview).filter(DbReview.id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
        return {"deleted": True, "id": review_id}
    else:
        raise HTTPException(status_code=404, detail="Review not found")

@app.get("/reviews", tags=["Reviews"])
async def reviews(records: int = Query(10, ge=1, le=25), page: int = Query(1, ge=1), db: Session = Depends(get_db)):
    """Get a paginated list of reviews"""
    limit = records
    offset = (page - 1) * records
    result = db.query(DbReview).limit(limit).offset(offset).all()
    return {"data": result}

if __name__ == "__main__":
    port = int(os.getenv("HTTP_SERVER_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)