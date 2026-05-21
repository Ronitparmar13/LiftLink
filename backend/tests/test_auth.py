"""Authentication dependency tests."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies import auth as auth_module


def _credentials(token: str = "token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.mark.asyncio
async def test_missing_authorization_header_returns_401():
    with pytest.raises(HTTPException) as exc:
        await auth_module.verify_firebase_token(None)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_invalid_firebase_token_returns_401(monkeypatch, tmp_path: Path):
    service_account = tmp_path / "firebase.json"
    service_account.write_text("{}")

    monkeypatch.setattr(
        auth_module,
        "get_settings",
        lambda: SimpleNamespace(
            firebase_credentials_path=service_account,
            allowed_email_domain="paruluniversity.ac.in",
        ),
    )

    from firebase_admin import auth as firebase_auth

    def raise_invalid_token(_token: str):
        raise ValueError("bad token")

    monkeypatch.setattr(firebase_auth, "verify_id_token", raise_invalid_token)

    with pytest.raises(HTTPException) as exc:
        await auth_module.verify_firebase_token(_credentials())

    assert exc.value.status_code == 401
    assert "Invalid Firebase token" in exc.value.detail


@pytest.mark.asyncio
async def test_wrong_email_domain_returns_403(monkeypatch, tmp_path: Path):
    service_account = tmp_path / "firebase.json"
    service_account.write_text("{}")

    monkeypatch.setattr(
        auth_module,
        "get_settings",
        lambda: SimpleNamespace(
            firebase_credentials_path=service_account,
            allowed_email_domain="paruluniversity.ac.in",
        ),
    )

    from firebase_admin import auth as firebase_auth

    monkeypatch.setattr(
        firebase_auth,
        "verify_id_token",
        lambda _token: {
            "uid": "uid-1",
            "email": "student@gmail.com",
            "name": "Student",
            "picture": None,
        },
    )

    with pytest.raises(HTTPException) as exc:
        await auth_module.verify_firebase_token(_credentials())

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_valid_parul_token_returns_claims(monkeypatch, tmp_path: Path):
    service_account = tmp_path / "firebase.json"
    service_account.write_text("{}")

    monkeypatch.setattr(
        auth_module,
        "get_settings",
        lambda: SimpleNamespace(
            firebase_credentials_path=service_account,
            allowed_email_domain="paruluniversity.ac.in",
        ),
    )

    from firebase_admin import auth as firebase_auth

    monkeypatch.setattr(
        firebase_auth,
        "verify_id_token",
        lambda _token: {
            "uid": "uid-1",
            "email": "STUDENT@PARULUNIVERSITY.AC.IN",
            "name": "Student",
            "picture": "https://example.com/avatar.png",
        },
    )

    claims = await auth_module.verify_firebase_token(_credentials())

    assert claims.uid == "uid-1"
    assert claims.email == "student@paruluniversity.ac.in"
