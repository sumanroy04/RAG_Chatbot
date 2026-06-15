from backend.chatbot.processor import is_crisis, remove_emojis
from backend.chatbot.rag_engine import get_mood_acknowledgement, get_retrieval_k

def test_is_crisis():
    # Test keywords triggering crisis warning
    assert is_crisis("I want to end my life") is True
    assert is_crisis("I've been cutting myself") is True
    assert is_crisis("I want to kill myself") is True
    assert is_crisis("I am fine today") is False

def test_remove_emojis():
    # Test text sanitizer
    assert remove_emojis("Hello! 😊") == "Hello! "
    assert remove_emojis("Feeling stressed 😰 and tired 😴") == "Feeling stressed  and tired "
    assert remove_emojis("Just normal text") == "Just normal text"

def test_get_mood_acknowledgement():
    # Test mood acknowledgements
    assert "light and encouraging" in get_mood_acknowledgement("Happy")
    assert "soft and manageable" in get_mood_acknowledgement("Sad")
    assert "grounding and practical" in get_mood_acknowledgement("Stressed")
    assert "Choose a mood" in get_mood_acknowledgement(None)

def test_get_retrieval_k():
    # Test topic retrieval depths
    assert get_retrieval_k("Anxiety") == 5
    assert get_retrieval_k("Sleep Issues") == 4
    assert get_retrieval_k("General Topic") == 3
    assert get_retrieval_k(None) == 3

def test_crisis_database_logging():
    from backend.api.models.crisis import CrisisLog
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.extensions import Base

    # Setup temporary test database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    # Log a mock crisis event
    log = CrisisLog(
        user_id=101,
        message="I want to end my life",
        matched_keywords="end my life"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Retrieve and check fields
    retrieved = db.query(CrisisLog).first()
    assert retrieved is not None
    assert retrieved.user_id == 101
    assert retrieved.message == "I want to end my life"
    assert retrieved.matched_keywords == "end my life"
    
    db.close()
