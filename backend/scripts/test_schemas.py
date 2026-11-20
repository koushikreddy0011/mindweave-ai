"""Validation script for User and Token Pydantic schemas."""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from pydantic import ValidationError
from app.schemas import Token, TokenPayload, UserCreate, UserLogin, UserRead, UserUpdate


class MockUserORM:
    """Mock representing an SQLAlchemy User ORM instance."""

    def __init__(self) -> None:
        self.id = uuid.uuid4()
        self.email = "testuser@example.com"
        self.full_name = "Test User"
        self.hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$mockhashvalue"
        self.is_active = True
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


def run_schema_tests() -> int:
    """Test schema validation contracts and ORM serialization rules."""
    print("=" * 60)
    print("MindWeave AI — Pydantic Schemas Verification")
    print("=" * 60)

    # Test 1: Valid UserCreate succeeds and normalizes email
    user_in = UserCreate(
        email="User.Name@Example.COM",
        password="ValidPassword123!",
        full_name="User Name",
    )
    assert user_in.email == "User.Name@example.com", "Email should be normalized to lowercase domain"
    assert user_in.password == "ValidPassword123!"
    print("  [✓] Test 1: Valid UserCreate succeeds and normalizes email.")

    # Test 2: Invalid email format raises ValidationError
    invalid_email_caught = False
    try:
        UserCreate(email="not-an-email", password="ValidPassword123!")
    except ValidationError:
        invalid_email_caught = True
    assert invalid_email_caught, "Invalid email must raise ValidationError"
    print("  [✓] Test 2: Invalid email format raises ValidationError.")

    # Test 3: Password shorter than 8 chars raises ValidationError
    short_pw_caught = False
    try:
        UserCreate(email="test@example.com", password="short")
    except ValidationError:
        short_pw_caught = True
    assert short_pw_caught, "Password < 8 chars must raise ValidationError"
    print("  [✓] Test 3: Password shorter than 8 chars raises ValidationError.")

    # Test 4: UserRead ORM validation strictly omits hashed_password
    mock_orm = MockUserORM()
    user_read = UserRead.model_validate(mock_orm)
    dumped = user_read.model_dump()
    assert dumped["id"] == mock_orm.id
    assert dumped["email"] == mock_orm.email
    assert "hashed_password" not in dumped, "hashed_password must NEVER be exposed in UserRead"
    print("  [✓] Test 4: UserRead maps ORM model and strictly excludes hashed_password.")

    # Test 5: Token model serializes with default token_type 'bearer'
    token = Token(access_token="sample-jwt-access-token-string")
    assert token.token_type == "bearer"
    token_dict = token.model_dump()
    assert token_dict == {
        "access_token": "sample-jwt-access-token-string",
        "token_type": "bearer",
    }
    print("  [✓] Test 5: Token model serializes with default 'bearer' token_type.")

    print("\n" + "=" * 60)
    print("[SUCCESS] All 5 User and Token schema tests passed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_schema_tests())
