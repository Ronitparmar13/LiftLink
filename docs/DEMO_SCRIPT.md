# LiftLink — Two-Browser Demo Script (Phase 5)

Use two browsers (or one normal + one incognito) with different `@paruluniversity.ac.in` Google accounts.

## Setup

1. Backend: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
2. Frontend: `cd frontend && npm run dev`
3. MongoDB + Firebase configured in `.env` files
4. Optional: `python scripts/seed_offers.py` after driver signs in once

---

## Browser A — Driver

1. Open http://localhost:5173 → Sign in (driver account)
2. **Offer a Ride** → set start/end on map (Main Gate → Alkapuri corridor)
3. Set departure time **2+ hours ahead**, seats = **1**
4. Publish → **My Offers** → confirm `open`

## Browser B — Rider

1. Sign in (different Parul account)
2. **Find a Ride** → set pickup/dropoff **on the driver's corridor**
3. Search → see match card with fuel-split formula
4. **Request Ride** → lands on status page (`pending`)

## Browser A — Accept

1. Dashboard shows pending request count → **Review requests**
2. **Accept** the rider's request
3. Offer becomes `full` if seats were 1

## Browser B — Confirmed

1. Status page auto-refreshes → **Confirmed**
2. See driver name + phone (if profile filled)
3. Payment disclaimer shown (cash/UPI off-app)

## Both — Complete

1. Either party taps **Mark ride complete**
2. Status → `completed`

---

## Negative tests

| Test | Expected |
|------|----------|
| Rider requests same offer twice | 409 conflict |
| Second accept when seats = 0 | 409 no seats |
| Off-route pickup in Find Ride | 0 matches |
