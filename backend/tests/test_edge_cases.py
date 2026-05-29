"""Edge case tests — booking state machine guards."""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.services.booking import accept_request, cancel_request, complete_request, reject_request


def _fake_db(offers=None, requests=None, users=None):
    class _Col:
        def __init__(self, docs):
            self._docs = list(docs)

        async def find_one(self, q):
            for d in self._docs:
                if all(d.get(k) == v for k, v in q.items()):
                    return d
            return None

        async def update_one(self, q, update):
            for d in self._docs:
                if all(d.get(k) == v for k, v in q.items()):
                    if "$set" in update:
                        d.update(update["$set"])
                    if "$inc" in update:
                        for k, v in update["$inc"].items():
                            d[k] = d.get(k, 0) + v
                    break

        async def find_one_and_update(self, q, update, return_document=True):
            for d in self._docs:
                if all(d.get(k) == v for k, v in q.items()):
                    if "$set" in update:
                        d.update(update["$set"])
                    if "$inc" in update:
                        for k, v in update["$inc"].items():
                            d[k] = d.get(k, 0) + v
                    return d
            return None

    db = MagicMock()
    db.ride_offers = _Col(offers or [])
    db.ride_requests = _Col(requests or [])
    db.users = _Col(users or [])
    return db


def _offer(driver_id, seats=3, status="open"):
    return {
        "_id": ObjectId(),
        "driverId": driver_id,
        "status": status,
        "availableSeats": seats,
        "departureTime": datetime.now(timezone.utc) + timedelta(hours=2),
        "updatedAt": datetime.now(timezone.utc),
    }


def _request(rider_id, offer_id, status="pending"):
    return {
        "_id": ObjectId(),
        "offerId": offer_id,
        "riderId": rider_id,
        "status": status,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }


@pytest.mark.asyncio
async def test_accept_non_pending_request_returns_409():
    driver = ObjectId()
    rider = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"], status="accepted")
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await accept_request(db, req["_id"], driver)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_accept_by_non_driver_returns_403():
    driver = ObjectId()
    other = ObjectId()
    rider = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"])
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await accept_request(db, req["_id"], other)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_self_request_rejected():
    """Driver cannot request their own offer (enforced at request creation)."""
    driver = ObjectId()
    offer = _offer(driver)
    req = _request(driver, offer["_id"])
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await accept_request(db, req["_id"], driver)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_accept_full_offer_returns_409():
    driver = ObjectId()
    rider = ObjectId()
    offer = _offer(driver, seats=0, status="full")
    req = _request(rider, offer["_id"])
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await accept_request(db, req["_id"], driver)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_cancel_non_pending_request_returns_409():
    rider = ObjectId()
    driver = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"], status="accepted")
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await cancel_request(db, req["_id"], rider)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_cancel_by_non_rider_returns_403():
    rider = ObjectId()
    other = ObjectId()
    driver = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"])
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await cancel_request(db, req["_id"], other)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_complete_non_accepted_request_returns_409():
    rider = ObjectId()
    driver = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"], status="pending")
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await complete_request(db, req["_id"], driver)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_complete_by_unauthorized_user_returns_403():
    rider = ObjectId()
    driver = ObjectId()
    other = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"], status="accepted")
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await complete_request(db, req["_id"], other)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_reject_non_pending_request_returns_409():
    driver = ObjectId()
    rider = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"], status="accepted")
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await reject_request(db, req["_id"], driver)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_reject_by_non_driver_returns_403():
    driver = ObjectId()
    other = ObjectId()
    rider = ObjectId()
    offer = _offer(driver)
    req = _request(rider, offer["_id"])
    db = _fake_db([offer], [req])

    with pytest.raises(HTTPException) as exc:
        await reject_request(db, req["_id"], other)
    assert exc.value.status_code == 403
