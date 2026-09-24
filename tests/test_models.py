from memora.memory.models import Memory
from datetime import datetime

def test_model():
    model = Memory(
    id=1,
    content="postgresql is the database",
    created_at=datetime.now(),
    status="active"
)
    assert model.id==1
    assert model.content=="postgresql is the database"
    assert model.status=="active"
    assert isinstance(model.created_at, datetime)