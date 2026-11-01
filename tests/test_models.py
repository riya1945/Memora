
from datetime import datetime, timezone
from uuid import uuid4

from memora.memory.models import Memory


def test_model():
    owner_id = uuid4()

    model = Memory(
        id=uuid4(),
        owner_id=owner_id,
        content="postgresql is the database",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        status="active",
        importance=0.9,
        confidence=0.95,
    )

    assert model.content == "postgresql is the database"
    assert model.owner_id == owner_id
    assert model.status == "active"
    assert model.importance == 0.9
    assert model.confidence == 0.95
