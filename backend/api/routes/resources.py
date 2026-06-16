from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from backend.app.extensions import get_db
from backend.api.models.resource import Resource

resources_router = APIRouter()

class ResourceSchema(BaseModel):
    id: int
    title: str
    category: str
    content: str
    tags: Optional[str] = None

    class Config:
        from_attributes = True

DEFAULT_RESOURCES = [
    {
        "title": "Understanding Anxiety and Panic Attacks",
        "category": "Anxiety",
        "content": "Anxiety is a normal human response to stress, but when it becomes persistent and overwhelming, it may indicate an anxiety disorder. Symptoms include rapid heart rate, shallow breathing, sweating, and feelings of dread. To manage intense anxiety, practice the 5-4-3-2-1 grounding technique: name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. Slow, deep belly breathing also helps trigger the body's relaxation response.",
        "tags": "grounding,panic,anxiety,breathing"
    },
    {
        "title": "Sleep Hygiene Guidelines for Restless Nights",
        "category": "Sleep Issues",
        "content": "Good sleep hygiene is essential for mental well-being. To sleep better: 1. Keep a consistent sleep schedule, waking up and going to bed at the same time daily. 2. Avoid electronic screens (phones, laptops) for at least 30-60 minutes before bedtime, as blue light disrupts melatonin production. 3. Keep your bedroom cool, quiet, and dark. 4. Avoid heavy meals, caffeine, and alcohol close to bedtime. If you can't fall asleep after 20 minutes, get out of bed and do a quiet, non-stimulating activity (like reading a physical book) under low light until you feel sleepy.",
        "tags": "sleep,insomnia,fatigue,rest"
    },
    {
        "title": "Building Healthy Relationship Boundaries",
        "category": "Relationships",
        "content": "Healthy boundaries are guidelines, rules, or limits that a person creates to identify safe, permissible, and practical ways for other people to behave around them. Setting boundaries involves: 1. Clearly defining your needs. 2. Communicating them directly and honestly without anger. 3. Listening to the other person's boundaries. 4. Saying 'no' when a request compromises your well-being. Remember, saying no to others is often saying yes to yourself and your own mental peace. It is not selfish to prioritize your health.",
        "tags": "communication,boundaries,conflict,trust"
    },
    {
        "title": "Coping with Academic and Exam Stress",
        "category": "Study Stress",
        "content": "Exam stress and academic burnout are common. To manage study stress: 1. Use the Pomodoro Technique: study for 25 minutes, then take a 5-minute break. This keeps the brain fresh. 2. Break large study topics into smaller, manageable chunks. 3. Plan your study sessions in advance and stick to a realistic schedule. 4. Prioritize sleep, nutrition, and light exercise. No exam or grade is worth compromising your physical or mental health. Reach out to advisors or peers if you feel overwhelmed.",
        "tags": "study,exam,burnout,procrastination"
    }
]

def seed_resources_if_empty(db: Session):
    count = db.query(Resource).count()
    if count == 0:
        for r_data in DEFAULT_RESOURCES:
            resource = Resource(**r_data)
            db.add(resource)
        db.commit()

@resources_router.get("/", response_model=List[ResourceSchema])
def get_resources(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # Ensure default resources are seeded
    seed_resources_if_empty(db)
    
    query = db.query(Resource)
    if category:
        query = query.filter(Resource.category == category)
    if q:
        query = query.filter(
            Resource.title.ilike(f"%{q}%") | Resource.content.ilike(f"%{q}%")
        )
    return query.all()
