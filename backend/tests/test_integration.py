"""Integration tests — full API flow simulation with mocked dependencies."""

from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId


def _make_user(uid: str = "uid-1", email: str = "student@paruluniversity.ac.in"):
    return {
        "_id": ObjectId(),
        "firebaseUid": uid,
        "email": email,
        "displayName": "Test Student",
        "photoUrl": None,
        "phone": None,
        "role": "both",
        "vehicle": None,
        "stats": {"ridesAsDriver": 0, "ridesAsRider": 0},
        "isActive": True,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }


def _make_offer(driver_id: ObjectId, **overrides):
    now = datetime.now(timezone.utc)
    doc = {
        "_id": ObjectId(),
        "driverId": driver_id,
        "route": {
            "type": "LineString",
            "coordinates": [
                [73.20, 22.30],
                [73.21, 22.31],
                [73.22, 22.32],
            ],
        },
        "startLabel": "Main Gate",
        "endLabel": "Hostel Block A",
        "startPoint": {"type": "Point", "coordinates": [73.20, 22.30]},
        "endPoint": {"type": "Point", "coordinates": [73.22, 22.32]},
        "departureTime": now + timedelta(hours=2),
        "availableSeats": 3,
        "status": "open",
        "estimatedDistanceKm": 3.5,
        "fuelSplitRatePerKm": 3.5,
        "estimatedFuelSplitTotal": 12.25,
        "notes": "",
        "createdAt": now,
        "updatedAt": now,
    }
    doc.update(overrides)
    return doc


def _make_request(rider_id: ObjectId, offer_id: ObjectId, **overrides):
    now = datetime.now(timezone.utc)
    doc = {
        "_id": ObjectId(),
        "offerId": offer_id,
        "riderId": rider_id,
        "pickup": {"type": "Point", "coordinates": [73.205, 22.305]},
        "dropoff": {"type": "Point", "coordinates": [73.215, 22.315]},
        "pickupLabel": "Near Cafeteria",
        "dropoffLabel": "Library",
        "riderDistanceKm": 1.5,
        "estimatedFuelSplitCost": 5.25,
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
    }
    doc.update(overrides)
    return doc


class FakeCollection:
    def __init__(self, docs: list[dict] | None = None):
        self._docs = list(docs or [])

    def _match(self, doc, query):
        for k, v in query.items():
            if isinstance(v, dict):
                if "$gt" in v and not (doc.get(k, 0) > v["$gt"]):
                    return False
                if "$gte" in v and not (doc.get(k, 0) >= v["$gte"]):
                    return False
                if "$lt" in v and not (doc.get(k, 0) < v["$lt"]):
                    return False
                if "$lte" in v and not (doc.get(k, 0) <= v["$lte"]):
                    return False
                if "$ne" in v and doc.get(k) == v["$ne"]:
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def find_one(self, query):
        for d in self._docs:
            if self._match(d, query):
                return d
        return None

    def find(self, query):
        results = [d for d in self._docs if self._match(d, query)]

        class _Cursor:
            def __init__(self, items):
                self._items = items

            def sort(self, *args):
                return self

            def skip(self, *args):
                return self

            def limit(self, *args):
                return self

            async def to_list(self, length=100):
                return self._items[:length]

            def __aiter__(self):
                async def _gen():
                    for item in self._items:
                        yield item
                return _gen()

        return _Cursor(results)

    async def insert_one(self, doc):
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self._docs.append(doc)
        result = MagicMock()
        result.inserted_id = doc["_id"]
        return result

    async def update_one(self, query, update):
        for d in self._docs:
            if self._match(d, query):
                if "$set" in update:
                    d.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        d[k] = d.get(k, 0) + v
                break
        return MagicMock()

    async def find_one_and_update(self, query, update, return_document=True):
        for d in self._docs:
            if self._match(d, query):
                if "$set" in update:
                    d.update(update["$set"])
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        d[k] = d.get(k, 0) + v
                return d
        return None


class FakeDB:
    def __init__(self):
        self.ride_offers = FakeCollection()
        self.ride_requests = FakeCollection()
        self.users = FakeCollection()
        self.campus_pois = FakeCollection()


@pytest.mark.asyncio
async def test_offer_create_and_list():
    """Create an offer and list it back."""
    from app.routers.offers import create_offer, list_my_offers

    db = FakeDB()
    user = _make_user()
    now = datetime.now(timezone.utc) + timedelta(hours=3)

    from app.models.offer import OfferCreate
    from app.models.geo import GeoPoint, GeoLineString

    body = OfferCreate(
        startPoint=GeoPoint(coordinates=[73.20, 22.30]),
        endPoint=GeoPoint(coordinates=[73.22, 22.32]),
        route=GeoLineString(coordinates=[[73.20, 22.30], [73.22, 22.32]]),
        startLabel="Main Gate",
        endLabel="Hostel A",
        departureTime=now,
        availableSeats=2,
        notes="Test ride",
    )

    with patch("app.routers.offers.get_settings") as mock_settings:
        mock_settings.return_value = SimpleNamespace(fuel_split_rate_per_km=3.5)
        created = await create_offer(body, user, db)

    assert created.driverId == str(user["_id"])
    assert created.status.value == "open"

    my_offers = await list_my_offers(user, db)
    assert len(my_offers) == 1
    assert my_offers[0].id == created.id


@pytest.mark.asyncio
async def test_full_booking_flow():
    """Simulate: create offer -> match request -> accept -> complete."""
    from app.services.booking import accept_request, complete_request

    db = FakeDB()
    driver = _make_user(uid="driver-1", email="driver@paruluniversity.ac.in")
    rider = _make_user(uid="rider-1", email="rider@paruluniversity.ac.in")

    db.users._docs = [driver, rider]

    offer = _make_offer(driver["_id"])
    db.ride_offers._docs = [offer]

    req = _make_request(rider["_id"], offer["_id"], offerId=offer["_id"])
    db.ride_requests._docs = [req]

    updated = await accept_request(db, req["_id"], driver["_id"])
    assert updated["status"] == "accepted"

    offer_after = await db.ride_offers.find_one({"_id": offer["_id"]})
    assert offer_after["availableSeats"] == 2

    completed = await complete_request(db, req["_id"], driver["_id"])
    assert completed["status"] == "completed"


@pytest.mark.asyncio
async def test_reject_request():
    """Reject a request and verify seats unchanged."""
    from app.services.booking import reject_request

    db = FakeDB()
    driver = _make_user(uid="driver-1", email="driver@paruluniversity.ac.in")
    rider = _make_user(uid="rider-1", email="rider@paruluniversity.ac.in")

    db.users._docs = [driver, rider]

    offer = _make_offer(driver["_id"])
    db.ride_offers._docs = [offer]

    req = _make_request(rider["_id"], offer["_id"], offerId=offer["_id"])
    db.ride_requests._docs = [req]

    updated = await reject_request(db, req["_id"], driver["_id"])
    assert updated["status"] == "rejected"

    offer_after = await db.ride_offers.find_one({"_id": offer["_id"]})
    assert offer_after["availableSeats"] == 3
