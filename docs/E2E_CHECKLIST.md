# LiftLink E2E Checklist

Use this after MongoDB Atlas and Firebase are configured.

## Environment

- [ ] `backend/.env` has a real `MONGODB_URI`.
- [ ] `backend/firebase-service-account.json` exists.
- [ ] `frontend/.env` has all `VITE_FIREBASE_*` values.
- [ ] `GET http://localhost:8000/health` shows MongoDB `ok`.
- [ ] `GET http://localhost:8000/health` shows Firebase `configured`.
- [ ] `python scripts/init_indexes.py` completes.
- [ ] `python scripts/seed_pois.py` completes.

## Driver Flow

- [ ] Driver signs in with `@paruluniversity.ac.in`.
- [ ] Driver completes profile with phone and vehicle.
- [ ] Driver creates offer from Main Gate to Alkapuri.
- [ ] Offer appears in My Offers as `open`.
- [ ] Offer document in MongoDB uses GeoJSON `[lng, lat]`.

## Rider Flow

- [ ] Rider signs in with a different Parul account.
- [ ] Fuzzy search resolves `Uni Gate`.
- [ ] Rider searches near the driver route and sees at least one match.
- [ ] Rider searches off-route and sees zero matches.
- [ ] Rider requests a ride.
- [ ] Rider status page shows `pending`.

## Booking Flow

- [ ] Driver dashboard shows pending request count.
- [ ] Driver accepts the request.
- [ ] Rider status auto-refreshes to confirmed.
- [ ] Contact details appear after acceptance.
- [ ] Offer becomes `full` when seats reach zero.
- [ ] Either party marks ride complete.
- [ ] User ride stats increment after completion.

## Hotspots

- [ ] `python scripts/seed_requests_for_hotspots.py` completes.
- [ ] Dashboard refresh generates hotspot zones.
- [ ] At least three trending zones are visible.

## Negative Tests

- [ ] Non-Parul Google account is rejected.
- [ ] Duplicate rider request returns conflict.
- [ ] Driver cannot request their own offer.
- [ ] Past departure offer cannot be requested.
