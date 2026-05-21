# LiftLink Viva Talking Points

## One-Minute Summary

LiftLink is a campus-only ride-pooling PWA for Parul University. It lets verified `@paruluniversity.ac.in` users publish routes, find route-compatible rides, request seats, and coordinate payment off-app. The “AI taste” features are fuzzy campus location search and K-Means trending pickup zones.

## Why These Technologies

| Area | Choice | Why it fits |
|------|--------|-------------|
| Frontend | React + Vite + Tailwind | Fast development, typed UI, mobile-first PWA workflow. |
| Maps | Leaflet + OpenStreetMap | Lightweight map picker without paid map APIs. |
| Backend | FastAPI | Async Python API, clear Swagger docs, good Pydantic validation. |
| Database | MongoDB Atlas | Natural fit for GeoJSON documents and 2dsphere indexes. |
| Auth | Firebase Google Sign-In | Reliable Google account flow; backend verifies tokens. |
| Fuzzy Search | RapidFuzz | Fast matching for aliases like `Uni Gate`, `CBS`, and `PIET BH`. |
| Hotspots | Scikit-Learn K-Means | Simple, explainable clustering for pickup demand. |

## Core Security Points

- Client-side Google hosted-domain hints are not trusted by themselves.
- Backend verifies Firebase ID tokens on protected endpoints.
- Backend rejects non-`@paruluniversity.ac.in` emails.
- `.env` files and Firebase service account JSON are gitignored.
- MongoDB credentials live only in `backend/.env`.

## GeoJSON And Matching

- GeoJSON coordinates are always `[longitude, latitude]`, not `[latitude, longitude]`.
- Offers store a driver route as a `LineString`.
- Rider pickup and dropoff are `Point` geometries.
- A match requires both rider points to be within `GEO_MATCH_RADIUS_METERS`, default 500 m, of the route.
- The implementation uses MongoDB coarse filters first, then Python route-distance post-filtering for reliability at semester-project scale.

## Booking State Machine

- Requests start as `pending`.
- Driver can `accept` or `reject`.
- Rider can cancel only while pending.
- Either party can mark an accepted ride complete.
- Accept uses an atomic MongoDB seat decrement to avoid double-booking when one seat remains.

## Fuel Split

- Cost is an estimate: `rider distance km × fuel split rate`.
- The rate is configurable with `FUEL_SPLIT_RATE_PER_KM`.
- LiftLink does not process payments; cash/UPI happens off-app.

## Fuzzy Search Demo

Good demo queries:

- `Uni Gate` → Parul University Main Entrance
- `Main Gate` → Parul University Main Entrance
- `CBS` → Vadodara Bus Station
- `PIET BH` → PIET Hostel Block

## K-Means Hotspot Demo

1. Seed accepted/completed requests with varied pickup locations.
2. Trigger `POST /api/v1/hotspots/refresh` or click dashboard refresh.
3. Dashboard shows clusters labeled by nearest POI with request counts.

## Common Questions

**Why not pure MongoDB geospatial matching?**  
MongoDB is great for GeoJSON storage and indexing, but route-within-distance matching against both pickup and dropoff can get tricky. The project uses MongoDB for coarse filtering and Python for exact, testable route distance logic.

**Why not payment inside the app?**  
For a minor project, payment processing adds compliance, refund, and security complexity. The product keeps transparent estimates and leaves settlement to cash/UPI off-app.

**What is the biggest technical risk?**  
Coordinate order. GeoJSON uses `[lng, lat]`; Leaflet uses `[lat, lng]`. The frontend explicitly converts between the two.
