import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app  # Your FastAPI app
from src.workflow_management.models import Workflow  # Your SQLAlchemy Workflow model
from src.database import async_session_maker,get_db  # Your test db session maker

@pytest.fixture
async def test_db_session():
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.mark.asyncio
async def test_get_workflows_empty(client: AsyncClient, test_db_session: AsyncSession):
    # Override dependency to use test session
    app.dependency_overrides[get_db] = lambda: test_db_session

    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == []  # Assuming DB is empty

    # Clear overrides
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_workflows_with_data(client: AsyncClient, test_db_session: AsyncSession):
    # Override dependency
    app.dependency_overrides[get_db] = lambda: test_db_session

    # Add dummy data
    workflow1 = Workflow(name="Test Workflow 1")
    workflow2 = Workflow(name="Test Workflow 2")
    test_db_session.add_all([workflow1, workflow2])
    await test_db_session.commit()

    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(w["name"] == "Test Workflow 1" for w in data)
    assert any(w["name"] == "Test Workflow 2" for w in data)

    # Clear overrides
    app.dependency_overrides.clear()
