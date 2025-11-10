# FastAPI Python API

Project-specific guidance for FastAPI applications.

---

## 🔍 Detection

Auto-detected when `requirements.txt` or `pyproject.toml` contains `fastapi`.

---

## 🛠️ Commands

```bash
# Development
uvicorn app.main:app --reload

# Testing
pytest
pytest --cov=app tests/

# Linting
flake8 app/
pylint app/
black app/  # Format
mypy app/   # Type checking
```

---

## 📁 Common Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── users.py
│   │   │   └── auth.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   └── core/
│       ├── config.py
│       └── security.py
├── tests/
│   ├── __init__.py
│   ├── test_users.py
│   └── conftest.py
├── requirements.txt
└── .env
```

---

## ⚙️ FastAPI Patterns

### Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import users, auth

app = FastAPI(title="My API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Routes

```python
# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.user import User, UserCreate
from app.services import user_service
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    """Get all users"""
    return await user_service.get_all_users()

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """Create new user"""
    return await user_service.create_user(user)
```

### Schemas (Pydantic)

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool = True

    class Config:
        from_attributes = True  # Formerly orm_mode
```

### Database Models (SQLAlchemy)

```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
```

### Dependency Injection

```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user(user_id)
    if user is None:
        raise credentials_exception
    return user
```

---

## 🧪 Testing

```python
# tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users_requires_auth():
    response = client.get("/api/users/")
    assert response.status_code == 401

def test_create_user():
    response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
```

---

## 🔧 Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

```bash
# .env
DATABASE_URL=postgresql://localhost/myapp
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ✅ Quality Gates

- [ ] `pytest` passes
- [ ] `pytest --cov` ≥ 70%
- [ ] `flake8` passes
- [ ] `mypy` passes
- [ ] `black --check` passes
- [ ] All endpoints have proper validation
- [ ] Authentication implemented
- [ ] Error handling in place

---

## 🚀 Deployment

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Run:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📚 Auto-Generated Docs

FastAPI automatically generates documentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**Reference:** https://fastapi.tiangolo.com/
