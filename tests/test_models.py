from memora.memory.models import Memory
from datetime import datetime


def test_model():
    model = Memory(
        id=1,
        content="postgresql is the database",
        created_at=datetime.now(),
        status="active",
        importance=0.9,
        confidence=0.95
    )

    assert model.id == 1
    assert model.content == "postgresql is the database"
    assert model.status == "active"
    assert isinstance(model.created_at, datetime)
    assert model.importance == 0.9
    assert model.confidence == 0.95