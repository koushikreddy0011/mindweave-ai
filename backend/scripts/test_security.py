"""Security module validation script testing Argon2 hashing and JWT handling."""

import sys
import uuid
from datetime import timedelta
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def run_security_tests() -> int:
    """Run comprehensive tests against password hashing and JWT issuance."""
    print("=" * 60)
    print("MindWeave AI — Security Module Verification")
    print("=" * 60)

    # Test 1: Password hashing produces a non-plaintext hash
    raw_password = "SuperSecretPassword123!"
    hashed = hash_password(raw_password)
    assert hashed != raw_password, "Hashed password must not equal plain password"
    assert "$argon2id$" in hashed, "Hash should be in Argon2id format"
    print("  [✓] Test 1: Password hashing produces valid Argon2id hash.")

    # Test 2: Valid password verification succeeds
    assert verify_password(raw_password, hashed) is True, "Valid password must verify True"
    print("  [✓] Test 2: Valid password verification matches hash.")

    # Test 3: Invalid password verification fails
    assert verify_password("WrongPassword123!", hashed) is False, "Invalid password must verify False"
    print("  [✓] Test 3: Invalid password verification returns False.")

    # Test 4: JWT access token creation and decoding
    test_user_id = uuid.uuid4()
    token = create_access_token(subject=test_user_id)
    payload = decode_access_token(token)
    assert payload is not None, "Valid token must decode successfully"
    assert payload["sub"] == str(test_user_id), "Token subject must match user UUID"
    assert payload["type"] == "access", "Token type must be 'access'"
    print(f"  [✓] Test 4: JWT creation & decoding matches subject ({test_user_id}).")

    # Test 5: Tampered token verification fails
    tampered_token = token[:-5] + "XXXXX"
    tampered_payload = decode_access_token(tampered_token)
    assert tampered_payload is None, "Tampered token must return None"
    print("  [✓] Test 5: Tampered token correctly rejected (returns None).")

    # Test 6: Expired token verification fails
    expired_token = create_access_token(
        subject=test_user_id,
        expires_delta=timedelta(seconds=-10),
    )
    expired_payload = decode_access_token(expired_token)
    assert expired_payload is None, "Expired token must return None"
    print("  [✓] Test 6: Expired token correctly rejected (returns None).")

    print("\n" + "=" * 60)
    print("[SUCCESS] All 6 cryptographic and JWT security tests passed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(run_security_tests())
