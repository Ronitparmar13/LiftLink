# LiftLink — Product Requirements Document (PRD)

| Field | Value |
|-------|-------|
| **Product Name** | LiftLink |
| **Version** | 1.0.0 (Semester 6 — Academic Minor Project) |
| **Document Status** | Approved for Development |
| **Last Updated** | 2026-05-21 |
| **Primary Audience** | Developers, AI coding assistants, academic evaluators |
| **Platform** | Responsive Web Application (PWA), mobile-first |
| **Institution Scope** | Parul University students and staff only |

---

## Table of Contents

1. [Introduction & Objectives](#1-introduction--objectives)
2. [Tech Stack Definition](#2-tech-stack-definition)
3. [Database Architecture](#3-database-architecture)
4. [API Endpoints List](#4-api-endpoints-list)
5. [User Flows](#5-user-flows)
6. [Future Scope (Semester 7)](#6-future-scope-semester-7)
7. [Appendices](#7-appendices)

---

## 1. Introduction & Objectives

### 1.1 Product Vision

**LiftLink** is an AI-powered, hyper-local campus ride-pooling system designed exclusively for the Parul University community. It connects drivers (students/staff offering spare seats in their vehicles or two-wheelers) with riders traveling along similar routes, using geospatial matching instead of traditional origin–destination-only ride-hailing logic.

The system reduces commute costs through transparent **fuel-split pricing**, improves campus mobility during peak hours, and surfaces **intelligent pickup hotspots** derived from historical demand patterns.

### 1.2 Problem Statement

| Pain Point | Current Behavior | LiftLink Solution |
|------------|------------------|-------------------|
| High solo commute cost | Students pay full cab/Rapido fare | Fuel-split model (~₹3–₹4/km, ~50% of commercial rates) |
| Informal ride coordination | WhatsApp groups, ad-hoc timing | Structured offer/request flow with acceptance |
| Route mismatch | "Going to Vadodara" vs. "Need lift near gate" | LineString route matching within 500 m of rider pickup/drop |
| Location ambiguity | Colloquial names ("Uni Gate", "Hostel 3") | NLP fuzzy search maps slang to canonical coordinates |
| Unknown demand clusters | No visibility into busy pickup areas | K-Means clustering → "Trending Pickup Zones" on dashboard |

### 1.3 Target Users

| Persona | Description | Primary Actions |
|---------|-------------|-----------------|
| **Rider** | Student/staff needing a lift along a driver's route | Search locations, find matching offers, request ride, pay off-app |
| **Driver** | Student/staff with vehicle offering shared ride | Publish route (start → end), accept/reject requests, complete ride |
| **System Admin** (optional S6) | Internal moderation | View flagged users, disable abusive accounts |

**Hard constraint:** Only users with verified `@paruluniversity.ac.in` Google accounts may access the platform.

### 1.4 Semester 6 Objectives (In Scope)

| ID | Objective | Success Metric |
|----|-----------|----------------|
| O1 | Verified campus-only ecosystem | 100% sign-ins use `@paruluniversity.ac.in`; rejected otherwise |
| O2 | Geospatial route matching | Rider sees relevant drivers when route passes within **500 m** of pickup and drop |
| O3 | NLP location resolution | Fuzzy queries resolve to canonical POIs with acceptable match score |
| O4 | Intelligent hotspots | Dashboard shows ≥3 trending zones when sufficient historical data exists |
| O5 | Fuel-split transparency | Estimated cost shown before request; formula documented |
| O6 | Complete booking loop | Request → Driver Accept → Ride status `confirmed` → `completed` |

### 1.5 Explicit Non-Goals (Semester 6)

- Real-time GPS tracking of driver/rider during ride
- In-app payment gateway (Razorpay, Stripe, etc.)
- Multi-university tenancy
- Native iOS/Android apps (PWA only)
- Automated driver matching / auto-accept
- Chat or voice calling between users
- Rating/review system (deferred)
- Admin analytics dashboard (minimal logging only)

### 1.6 Assumptions & Constraints

- Campus geography is bounded; all coordinates fall within a defined bounding box around Parul University, Vadodara.
- Drivers manually confirm acceptance; no SLA guarantees.
- Payments occur **off-app** (cash or UPI) after ride completion or by mutual agreement.
- Internet connectivity is assumed; offline mode is out of scope.
- OpenStreetMap + Leaflet provide map tiles and geocoding assistance; no paid map API keys.
- MongoDB Atlas free tier is sufficient for academic demo volume.

---

## 2. Tech Stack Definition

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client (PWA)                                 │
│  React 18 + Vite + Tailwind CSS + Leaflet.js + Firebase SDK   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS (REST + JWT)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  API Layer (FastAPI)                             │
│  Auth middleware │ Geospatial services │ ML services │ CRUD     │
└────────────┬───────────────────────┬──────────────────────────┘
             │                       │
             ▼                       ▼
┌────────────────────┐    ┌─────────────────────────────────────┐
│  MongoDB Atlas     │    │  External / Embedded Services        │
│  GeoJSON indexes   │    │  Firebase Auth (Google, domain lock) │
│  2dsphere          │    │  Scikit-Learn (K-Means batch job)    │
└────────────────────┘    │  TheFuzz (location string matching)  │
                          │  OpenStreetMap Nominatim (optional)  │
                          └─────────────────────────────────────┘
```

### 2.2 Frontend

| Layer | Technology | Version (recommended) | Purpose |
|-------|------------|----------------------|---------|
| Framework | React.js | 18.x | Component-based UI |
| Build | Vite | 5.x | Fast dev server, PWA plugin |
| Styling | Tailwind CSS | 3.x | Mobile-first responsive design |
| Maps | Leaflet.js | 1.9.x | Interactive map, markers, polylines |
| Tiles | OpenStreetMap | — | Free map tiles, no API key |
| Auth | Firebase Auth SDK | 10.x | Google Sign-In, ID token |
| HTTP | Axios or fetch | — | REST calls with `Authorization: Bearer` |
| PWA | vite-plugin-pwa | — | Installable web app, service worker |
| State | React Context / Zustand | — | Auth session, active ride state |

**Frontend directory convention (recommended):**

```
frontend/
├── public/
├── src/
│   ├── components/     # Map, RideCard, HotspotBadge, etc.
│   ├── pages/          # Dashboard, OfferRide, FindRide, Profile
│   ├── hooks/          # useAuth, useGeolocation
│   ├── services/       # api.ts, firebase.ts
│   ├── utils/          # distance formatters, cost calculator
│   └── App.tsx
├── tailwind.config.js
└── vite.config.ts
```

### 2.3 Backend

| Layer | Technology | Version (recommended) | Purpose |
|-------|------------|----------------------|---------|
| Framework | FastAPI | 0.110+ | Async REST API, OpenAPI docs |
| Server | Uvicorn | — | ASGI server |
| ODM / Driver | Motor (async) or PyMongo | — | MongoDB access |
| Validation | Pydantic v2 | — | Request/response schemas |
| Auth verification | `firebase-admin` | — | Verify ID tokens server-side |
| Geospatial | MongoDB aggregation | — | `$near`, `$geoIntersects` |
| ML — Clustering | Scikit-Learn | 1.4+ | K-Means on pickup coordinates |
| NLP — Fuzzy match | TheFuzz (`fuzzywuzzy` / `rapidfuzz`) | — | Colloquial → canonical POI |
| CORS | `fastapi.middleware.cors` | — | Allow frontend origin |

**Backend directory convention (recommended):**

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies/   # get_current_user, db session
│   ├── routers/        # users, offers, requests, locations, hotspots
│   ├── services/       # geo_match, fuzzy_search, cost_calc, kmeans
│   ├── models/         # Pydantic schemas
│   └── ml/             # hotspot_cluster.py
├── requirements.txt
└── .env
```

### 2.4 Database

| Component | Choice | Notes |
|-----------|--------|-------|
| Database | MongoDB Atlas | M0 free tier acceptable |
| Geo index | `2dsphere` on all GeoJSON fields | Required for `$near`, `$geoIntersects` |
| Connection | `mongodb+srv://` with IP whitelist | Store URI in environment variables |

### 2.5 Authentication Flow

1. User clicks **Sign in with Google** on PWA.
2. Firebase Auth enforces Google provider; **client-side** checks email ends with `@paruluniversity.ac.in`.
3. On success, client obtains Firebase **ID Token** (`getIdToken()`).
4. Every API request sends: `Authorization: Bearer <firebase_id_token>`.
5. FastAPI middleware calls Firebase Admin `verify_id_token()`; extracts `uid`, `email`, `name`, `picture`.
6. Backend upserts `User` document on first login; rejects non-university domain with `403`.

**Firebase Console configuration:**

- Enable Google Sign-In provider.
- Authorized domain: production + `localhost` for dev.
- Optional: Firebase App Check for abuse reduction (S7).

### 2.6 Environment Variables

| Variable | Location | Description |
|----------|----------|-------------|
| `VITE_FIREBASE_*` | Frontend | Firebase web config |
| `VITE_API_BASE_URL` | Frontend | FastAPI base URL |
| `MONGODB_URI` | Backend | Atlas connection string |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Backend | Admin SDK credentials path or JSON |
| `ALLOWED_EMAIL_DOMAIN` | Backend | `paruluniversity.ac.in` |
| `GEO_MATCH_RADIUS_METERS` | Backend | Default `500` |
| `FUEL_SPLIT_RATE_PER_KM` | Backend | Default `3.5` (INR) |
| `CORS_ORIGINS` | Backend | Frontend URL(s) |

### 2.7 PWA Requirements

- `manifest.json`: name, icons, `theme_color`, `display: standalone`
- Service worker: cache static assets; API calls network-first
- Viewport meta: mobile-first breakpoints (`sm`, `md`, `lg` in Tailwind)
- Touch targets ≥ 44×44 px for primary actions

---

## 3. Database Architecture

### 3.1 Collections Overview

| Collection | Purpose | Key Indexes |
|------------|---------|-------------|
| `users` | Profile linked to Firebase UID | `firebaseUid` (unique), `email` (unique) |
| `ride_offers` | Driver-published routes | `route` (2dsphere), `driverId`, `status`, `departureTime` |
| `ride_requests` | Rider booking attempts | `pickup`/`dropoff` (2dsphere), `riderId`, `offerId`, `status` |
| `campus_pois` | Canonical locations for fuzzy search | `name`, `aliases`, `location` (2dsphere) |
| `hotspot_snapshots` | Cached K-Means output | `generatedAt` (TTL optional) |

### 3.2 GeoJSON Standards

All geographic data **MUST** follow [RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946):

- Coordinates order: `[longitude, latitude]` (not lat/lng).
- Point: `{ "type": "Point", "coordinates": [lng, lat] }`
- LineString: `{ "type": "LineString", "coordinates": [[lng, lat], ...] }`

**Campus bounding box (reference for validation):**

```json
{
  "minLng": 73.18,
  "minLat": 22.28,
  "maxLng": 73.25,
  "maxLat": 22.35
}
```

Adjust after ground-truthing with actual campus coordinates.

### 3.3 Collection: `users`

#### 3.3.1 Mongoose Schema (Reference)

```javascript
const UserSchema = new mongoose.Schema({
  firebaseUid: { type: String, required: true, unique: true, index: true },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: /@paruluniversity\.ac\.in$/
  },
  displayName: { type: String, required: true, trim: true },
  photoUrl: { type: String, default: null },
  phone: { type: String, default: null }, // optional, user-provided
  role: {
    type: String,
    enum: ['rider', 'driver', 'both'],
    default: 'both'
  },
  vehicle: {
    type: { type: String, enum: ['two_wheeler', 'car', 'other'], default: null },
    description: { type: String, default: null } // e.g. "White Activa"
  },
  stats: {
    ridesAsDriver: { type: Number, default: 0 },
    ridesAsRider: { type: Number, default: 0 }
  },
  isActive: { type: Boolean, default: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
}, { collection: 'users' });
```

#### 3.3.2 MongoDB JSON Document Example

```json
{
  "_id": { "$oid": "665a1b2c3d4e5f6789012345" },
  "firebaseUid": "abc123firebaseUid",
  "email": "student.name@paruluniversity.ac.in",
  "displayName": "Rahul Sharma",
  "photoUrl": "https://lh3.googleusercontent.com/...",
  "phone": "+919876543210",
  "role": "both",
  "vehicle": {
    "type": "two_wheeler",
    "description": "Black Activa 5G"
  },
  "stats": {
    "ridesAsDriver": 12,
    "ridesAsRider": 8
  },
  "isActive": true,
  "createdAt": { "$date": "2026-01-15T08:00:00.000Z" },
  "updatedAt": { "$date": "2026-05-20T10:30:00.000Z" }
}
```

### 3.4 Collection: `ride_offers`

Driver publishes a route from **start** to **end** as a `LineString`. Optional waypoints may be included in the coordinate array for curved paths.

#### 3.4.1 Mongoose Schema (Reference)

```javascript
const RideOfferSchema = new mongoose.Schema({
  driverId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  route: {
    type: {
      type: String,
      enum: ['LineString'],
      required: true
    },
    coordinates: {
      type: [[Number]], // [[lng, lat], [lng, lat], ...]
      required: true,
      validate: {
        validator: (v) => Array.isArray(v) && v.length >= 2,
        message: 'Route must have at least 2 coordinates'
      }
    }
  },
  startLabel: { type: String, required: true },  // Human-readable
  endLabel: { type: String, required: true },
  startPoint: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], required: true } // [lng, lat]
  },
  endPoint: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], required: true }
  },
  departureTime: { type: Date, required: true, index: true },
  availableSeats: { type: Number, required: true, min: 1, max: 6, default: 1 },
  status: {
    type: String,
    enum: ['open', 'full', 'in_progress', 'completed', 'cancelled'],
    default: 'open',
    index: true
  },
  estimatedDistanceKm: { type: Number, required: true },
  fuelSplitRatePerKm: { type: Number, default: 3.5 },
  estimatedFuelSplitTotal: { type: Number, required: true },
  notes: { type: String, maxlength: 200, default: '' },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
}, { collection: 'ride_offers' });

RideOfferSchema.index({ route: '2dsphere' });
RideOfferSchema.index({ startPoint: '2dsphere' });
RideOfferSchema.index({ endPoint: '2dsphere' });
RideOfferSchema.index({ status: 1, departureTime: 1 });
```

#### 3.4.2 MongoDB JSON Document Example

```json
{
  "_id": { "$oid": "665a1b2c3d4e5f6789012346" },
  "driverId": { "$oid": "665a1b2c3d4e5f6789012345" },
  "route": {
    "type": "LineString",
    "coordinates": [
      [73.2105, 22.3120],
      [73.2120, 22.3145],
      [73.2150, 22.3180],
      [73.2200, 22.3250]
    ]
  },
  "startLabel": "Parul University Main Entrance",
  "endLabel": "Alkapuri, Vadodara",
  "startPoint": {
    "type": "Point",
    "coordinates": [73.2105, 22.3120]
  },
  "endPoint": {
    "type": "Point",
    "coordinates": [73.2200, 22.3250]
  },
  "departureTime": { "$date": "2026-05-22T07:30:00.000Z" },
  "availableSeats": 2,
  "status": "open",
  "estimatedDistanceKm": 8.4,
  "fuelSplitRatePerKm": 3.5,
  "estimatedFuelSplitTotal": 29.4,
  "notes": "Leaving sharp 7:30 AM",
  "createdAt": { "$date": "2026-05-21T18:00:00.000Z" },
  "updatedAt": { "$date": "2026-05-21T18:00:00.000Z" }
}
```

### 3.5 Collection: `ride_requests`

Rider specifies **pickup** and **dropoff** as `Point` geometries. Matching logic finds `ride_offers` whose `route` LineString passes within 500 m of both points.

#### 3.5.1 Mongoose Schema (Reference)

```javascript
const RideRequestSchema = new mongoose.Schema({
  riderId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  offerId: { type: mongoose.Schema.Types.ObjectId, ref: 'RideOffer', required: true, index: true },
  pickup: {
    type: { type: String, enum: ['Point'], required: true },
    coordinates: { type: [Number], required: true }
  },
  dropoff: {
    type: { type: String, enum: ['Point'], required: true },
    coordinates: { type: [Number], required: true }
  },
  pickupLabel: { type: String, required: true },
  dropoffLabel: { type: String, required: true },
  riderDistanceKm: { type: Number, required: true },
  estimatedFuelSplitCost: { type: Number, required: true },
  status: {
    type: String,
    enum: ['pending', 'accepted', 'rejected', 'cancelled', 'completed'],
    default: 'pending',
    index: true
  },
  driverResponseAt: { type: Date, default: null },
  paymentMethodNote: {
    type: String,
    enum: ['cash', 'upi', 'unspecified'],
    default: 'unspecified'
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
}, { collection: 'ride_requests' });

RideRequestSchema.index({ pickup: '2dsphere' });
RideRequestSchema.index({ dropoff: '2dsphere' });
RideRequestSchema.index({ riderId: 1, status: 1 });
RideRequestSchema.index({ offerId: 1, status: 1 });
```

#### 3.5.2 MongoDB JSON Document Example

```json
{
  "_id": { "$oid": "665a1b2c3d4e5f6789012347" },
  "riderId": { "$oid": "665a1b2c3d4e5f6789012348" },
  "offerId": { "$oid": "665a1b2c3d4e5f6789012346" },
  "pickup": {
    "type": "Point",
    "coordinates": [73.2110, 22.3130]
  },
  "dropoff": {
    "type": "Point",
    "coordinates": [73.2180, 22.3220]
  },
  "pickupLabel": "Uni Gate",
  "dropoffLabel": "Sayajigunj Circle",
  "riderDistanceKm": 6.2,
  "estimatedFuelSplitCost": 21.7,
  "status": "pending",
  "driverResponseAt": null,
  "paymentMethodNote": "unspecified",
  "createdAt": { "$date": "2026-05-21T19:15:00.000Z" },
  "updatedAt": { "$date": "2026-05-21T19:15:00.000Z" }
}
```

### 3.6 Collection: `campus_pois` (Fuzzy Search Reference)

```javascript
const CampusPoiSchema = new mongoose.Schema({
  name: { type: String, required: true, index: true },
  aliases: [{ type: String }], // ["Uni Gate", "Main Gate", "PU Entrance"]
  location: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], required: true }
  },
  category: {
    type: String,
    enum: ['gate', 'hostel', 'academic', 'landmark', 'bus_stop', 'other'],
    default: 'landmark'
  },
  isActive: { type: Boolean, default: true }
}, { collection: 'campus_pois' });

CampusPoiSchema.index({ location: '2dsphere' });
```

### 3.7 Geospatial Matching Logic

#### 3.7.1 Match Radius

`GEO_MATCH_RADIUS_METERS = 500`

#### 3.7.2 Rider → Driver Discovery Query

For a rider with `pickup` and `dropoff` Points, find open offers where:

1. `route` is within 500 m of `pickup` (using `$geoIntersects` with a buffer polygon **or** `$near` on route with max distance — implementation may use `$geoIntersects` on a `LineString` buffered to polygon server-side).
2. Same for `dropoff`.
3. `status === 'open'`
4. `departureTime` within user-selected time window (e.g. ±60 minutes)
5. `availableSeats > 0`

**Recommended aggregation pattern (conceptual):**

```javascript
// Step 1: Build 500m buffer circles around pickup/dropoff (GeoJSON Polygon)
// Step 2: Match offers where route intersects both buffers

db.ride_offers.find({
  status: "open",
  departureTime: { $gte: ISODate("..."), $lte: ISODate("...") },
  availableSeats: { $gt: 0 },
  route: {
    $geoIntersects: {
      $geometry: { type: "Polygon", coordinates: [/* pickup buffer */] }
    }
  }
  // AND repeat geoIntersects for dropoff buffer
})
```

**Alternative (simpler S6 approach):**

- Use `$near` on `startPoint` / `endPoint` as coarse filter.
- Post-filter in Python: compute minimum distance from rider points to LineString using Shapely / `geopy`, threshold 500 m.

Document the chosen approach in `backend/app/services/geo_match.py`.

#### 3.7.3 Distance & Cost Calculation

```
riderDistanceKm = haversine_distance(pickup, dropoff)  // or routed distance if OSRM added later
estimatedFuelSplitCost = round(riderDistanceKm * fuelSplitRatePerKm, 2)
fuelSplitRatePerKm = 3.5  // configurable; range ₹3–₹4 per km
```

Driver offer total uses full route length:

```
estimatedFuelSplitTotal = round(estimatedDistanceKm * fuelSplitRatePerKm, 2)
```

### 3.8 Hotspot Clustering Data Model

**Input:** Last N days of `ride_requests.pickup` coordinates (status ∈ `accepted`, `completed`).

**Process:** K-Means with `k = min(5, floor(n_samples / 10))` (minimum 3 clusters if data allows).

**Output collection `hotspot_snapshots`:**

```json
{
  "_id": { "$oid": "..." },
  "generatedAt": { "$date": "2026-05-21T06:00:00.000Z" },
  "clusters": [
    {
      "clusterId": 0,
      "centroid": { "type": "Point", "coordinates": [73.2115, 22.3135] },
      "label": "Near Main Gate",
      "requestCount": 47,
      "radiusMeters": 320
    }
  ],
  "sampleSize": 156,
  "algorithm": "kmeans",
  "k": 4
}
```

**Cron / manual trigger:** `POST /api/v1/hotspots/refresh` (admin or scheduled daily).

---

## 4. API Endpoints List

**Base URL:** `/api/v1`  
**Auth:** All endpoints except health check require `Authorization: Bearer <Firebase ID Token>`  
**Content-Type:** `application/json`  
**Error format:**

```json
{
  "detail": "Human-readable message",
  "code": "ERROR_CODE",
  "status": 400
}
```

### 4.1 Health & Auth

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Service health check | No |
| `POST` | `/auth/sync` | Upsert user from Firebase token claims | Yes |
| `GET` | `/auth/me` | Get current user profile | Yes |

#### `POST /auth/sync`

Creates or updates user after login.

**Response 200:**

```json
{
  "id": "665a1b2c3d4e5f6789012345",
  "email": "student@paruluniversity.ac.in",
  "displayName": "Rahul Sharma",
  "role": "both"
}
```

### 4.2 Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me` | Alias for profile (or merge with `/auth/me`) |
| `PATCH` | `/users/me` | Update phone, vehicle, role |
| `GET` | `/users/{user_id}` | Public profile (name, photo, vehicle type only) |

**`PATCH /users/me` body:**

```json
{
  "phone": "+919876543210",
  "role": "driver",
  "vehicle": { "type": "car", "description": "Swift Dzire" }
}
```

### 4.3 Campus Locations (Fuzzy Search)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/locations/search?q={query}&limit=10` | Fuzzy match against POI names/aliases |
| `GET` | `/locations/pois` | List all active POIs (map picker) |
| `POST` | `/locations/pois` | Admin seed POI (dev only) |

#### `GET /locations/search`

**Query params:** `q` (required), `limit` (default 10)

**Logic:**

1. Load active `campus_pois`.
2. Run `thefuzz.process.extract` against `name` + `aliases`.
3. Return matches with `score >= 70` (tunable).

**Response 200:**

```json
{
  "results": [
    {
      "poiId": "...",
      "name": "Parul University Main Entrance",
      "matchedAlias": "Uni Gate",
      "score": 92,
      "location": { "type": "Point", "coordinates": [73.2105, 22.3120] },
      "category": "gate"
    }
  ]
}
```

### 4.4 Ride Offers (Driver)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/offers` | Create new ride offer |
| `GET` | `/offers` | List offers (filters: status, driverId, time range) |
| `GET` | `/offers/{offer_id}` | Get offer details |
| `PATCH` | `/offers/{offer_id}` | Update offer (only if `open`) |
| `DELETE` | `/offers/{offer_id}` | Cancel offer |
| `GET` | `/offers/mine` | Current user's offers as driver |
| `POST` | `/offers/match` | **Rider** — find matching offers for pickup/dropoff |

#### `POST /offers`

**Request body:**

```json
{
  "startPoint": { "type": "Point", "coordinates": [73.2105, 22.3120] },
  "endPoint": { "type": "Point", "coordinates": [73.2200, 22.3250] },
  "route": {
    "type": "LineString",
    "coordinates": [
      [73.2105, 22.3120],
      [73.2150, 22.3180],
      [73.2200, 22.3250]
    ]
  },
  "startLabel": "Parul University Main Entrance",
  "endLabel": "Alkapuri",
  "departureTime": "2026-05-22T07:30:00Z",
  "availableSeats": 2,
  "notes": "Sharp 7:30 AM"
}
```

**Response 201:** Full `RideOffer` object with computed `estimatedDistanceKm`, `estimatedFuelSplitTotal`.

#### `POST /offers/match`

**Request body:**

```json
{
  "pickup": { "type": "Point", "coordinates": [73.2110, 22.3130] },
  "dropoff": { "type": "Point", "coordinates": [73.2180, 22.3220] },
  "pickupLabel": "Uni Gate",
  "dropoffLabel": "Sayajigunj",
  "departureAfter": "2026-05-22T06:00:00Z",
  "departureBefore": "2026-05-22T10:00:00Z"
}
```

**Response 200:**

```json
{
  "matches": [
    {
      "offer": { /* RideOffer summary */ },
      "driver": { "displayName": "...", "photoUrl": "...", "vehicle": {} },
      "riderDistanceKm": 6.2,
      "estimatedFuelSplitCost": 21.7,
      "matchScore": 0.95
    }
  ],
  "matchRadiusMeters": 500
}
```

### 4.5 Ride Requests (Rider + Driver Actions)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/requests` | Rider creates request on an offer |
| `GET` | `/requests/{request_id}` | Get request details |
| `GET` | `/requests/mine` | Rider's own requests |
| `GET` | `/offers/{offer_id}/requests` | Driver views pending requests for their offer |
| `PATCH` | `/requests/{request_id}/accept` | Driver accepts |
| `PATCH` | `/requests/{request_id}/reject` | Driver rejects |
| `PATCH` | `/requests/{request_id}/cancel` | Rider cancels (if `pending`) |
| `PATCH` | `/requests/{request_id}/complete` | Either party marks completed |

#### `POST /requests`

**Request body:**

```json
{
  "offerId": "665a1b2c3d4e5f6789012346",
  "pickup": { "type": "Point", "coordinates": [73.2110, 22.3130] },
  "dropoff": { "type": "Point", "coordinates": [73.2180, 22.3220] },
  "pickupLabel": "Uni Gate",
  "dropoffLabel": "Sayajigunj"
}
```

**Response 201:** `RideRequest` with `status: "pending"`.

#### `PATCH /requests/{request_id}/accept`

- Validates caller is offer's driver.
- Sets request `status` → `accepted`.
- Decrements `availableSeats` on offer; if 0, offer `status` → `full`.
- Sets `driverResponseAt`.

### 4.6 Hotspots (ML)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/hotspots/trending` | Latest hotspot snapshot for dashboard |
| `POST` | `/hotspots/refresh` | Re-run K-Means (admin/cron) |

**`GET /hotspots/trending` response:**

```json
{
  "generatedAt": "2026-05-21T06:00:00Z",
  "zones": [
    {
      "label": "Trending: Main Gate",
      "centroid": [73.2115, 22.3135],
      "requestCount": 47
    }
  ]
}
```

### 4.7 HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Missing/invalid token |
| 403 | Non-university email or forbidden action |
| 404 | Resource not found |
| 409 | Duplicate request / offer full |
| 422 | Pydantic validation failure |
| 500 | Server error |

### 4.8 OpenAPI

FastAPI auto-generates docs at `/docs` (Swagger) and `/redoc`. Disable or protect in production.

---

## 5. User Flows

### 5.1 Authentication Flow (All Users)

```
1. User opens PWA URL
2. Landing page → "Sign in with Google"
3. Firebase Google OAuth popup
4. IF email NOT ending @paruluniversity.ac.in → show error, sign out
5. ELSE → obtain ID token → POST /auth/sync
6. Redirect to Dashboard (role-aware: Driver / Rider tabs)
```

### 5.2 Driver Flow — Publish Ride Offer

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | Driver | Tap **Offer a Ride** | Open offer form |
| 2 | Driver | Search start location (fuzzy) | `GET /locations/search` → select POI |
| 3 | Driver | Search end location | Same |
| 4 | Driver | Tap map to adjust pins OR accept suggested route | Leaflet draws polyline |
| 5 | Driver | Set departure time, seats, notes | Client validation |
| 6 | Driver | Submit | `POST /offers` → offer `status: open` |
| 7 | Driver | View **My Offers** | `GET /offers/mine` |
| 8 | Driver | Wait for requests | Poll or refresh `GET /offers/{id}/requests` |

### 5.3 Driver Flow — Accept / Reject Request

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | Driver | Notification UI: new pending request | Show rider pickup/drop, cost |
| 2 | Driver | Tap **Accept** | `PATCH /requests/{id}/accept` |
| 3 | System | — | Request → `accepted`; seats -= 1 |
| 4 | Driver | View rider contact (phone if shared) | Display from `users` |
| 5 | Driver | After ride, tap **Complete** | `PATCH /requests/{id}/complete`; stats++ |
| Alt 2b | Driver | Tap **Reject** | `PATCH /requests/{id}/reject` |

### 5.4 Rider Flow — Find & Book Ride

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | Rider | Tap **Find a Ride** | Open search form |
| 2 | Rider | Enter pickup ("Uni Gate") | Fuzzy search → canonical Point |
| 3 | Rider | Enter dropoff | Same |
| 4 | Rider | Set time window (optional) | Default: next 4 hours |
| 5 | Rider | Tap **Search** | `POST /offers/match` |
| 6 | Rider | Browse match cards | Show driver name, route labels, cost, departure |
| 7 | Rider | Tap **Request Ride** on one card | `POST /requests` → `pending` |
| 8 | Rider | Wait on status screen | Poll `GET /requests/{id}` |
| 9a | Rider | Driver accepts | UI → "Confirmed"; show driver details |
| 9b | Rider | Driver rejects | UI → "Try another ride" |
| 10 | Rider | Pay driver off-app (cash/UPI) | No API; optional note in UI |
| 11 | Rider | Mark ride complete | `PATCH /requests/{id}/complete` |

### 5.5 Dashboard Flow (Common)

```
┌──────────────────────────────────────┐
│  LiftLink Dashboard                   │
├──────────────────────────────────────┤
│  [Trending Pickup Zones]  ← GET /hotspots/trending
│   • Main Gate (47 requests)           │
│   • Hostel Block B (31)                 │
├──────────────────────────────────────┤
│  Quick Actions:                       │
│   [Find a Ride]  [Offer a Ride]        │
├──────────────────────────────────────┤
│  Active Trip / Request Status         │
│   (pending | accepted | completed)    │
└──────────────────────────────────────┘
```

### 5.6 State Machines

#### Ride Offer Status

```
open → full (seats exhausted)
open → in_progress (first accept — optional S6)
open → cancelled (driver cancels)
in_progress → completed
```

#### Ride Request Status

```
pending → accepted | rejected | cancelled (rider)
accepted → completed | cancelled (edge: no-show policy manual)
```

### 5.7 Edge Cases & Business Rules

| Scenario | Rule |
|----------|------|
| Rider requests same offer twice | `409` if existing `pending` or `accepted` |
| Offer departure in past | Reject on create/match |
| Driver accepts when seats = 0 | `409 Conflict` |
| Pickup/drop not within 500 m of route | Excluded from match results |
| Insufficient hotspot data | Return empty zones with message |
| Fuzzy score < 70 | Return empty with "Did you mean?" suggestions |

---

## 6. Future Scope (Semester 7)

### 6.1 Real-Time GPS Tracking

| Feature | Description |
|---------|-------------|
| Live driver location | WebSocket or Firebase Realtime Database stream of `driverLocation` Point |
| Rider map view | Animated marker along route; ETA recalculation |
| Geofence alerts | Notify rider when driver within 200 m of pickup |
| Safety | Share trip link with trusted contact |
| Tech additions | `socket.io` / FastAPI WebSockets, background geolocation API (PWA permissions) |

**Schema extension (preview):**

```json
{
  "liveTracking": {
    "enabled": true,
    "lastKnownLocation": { "type": "Point", "coordinates": [73.21, 22.31] },
    "updatedAt": "2026-09-01T08:05:00Z"
  }
}
```

### 6.2 In-App Payment Gateway

| Feature | Description |
|---------|-------------|
| Gateway | Razorpay or PhonePe SDK (UPI-first) |
| Escrow model | Hold fuel-split amount until ride `completed` |
| Wallet | Optional campus credits for frequent users |
| Receipts | Email + in-app PDF invoice |
| Compliance | PCI-DSS via gateway; no raw card storage |

**New collections:** `payments`, `transactions` with statuses `initiated`, `captured`, `refunded`.

### 6.3 Additional S7 Enhancements (Backlog)

- Push notifications (FCM) for request/accept events
- Driver/rider rating and trust score
- Route optimization via OSRM
- Multi-stop carpooling
- Female-only ride preference filter
- University admin dashboard with ride analytics
- SOS / emergency contact integration
- Hindi/Gujarati i18n

---

## 7. Appendices

### 7.1 Glossary

| Term | Definition |
|------|------------|
| **Fuel Split** | Shared fuel cost model charged per km at ~50% of commercial ride-hail |
| **POI** | Point of Interest — canonical campus location |
| **LineString** | GeoJSON type representing driver's path |
| **2dsphere** | MongoDB geospatial index type for spherical geometry |
| **PWA** | Progressive Web App — installable web application |

### 7.2 Sample Campus POI Seed Data

| Canonical Name | Aliases | Approx Coordinates [lng, lat] |
|----------------|---------|-------------------------------|
| Parul University Main Entrance | Uni Gate, Main Gate, PU Gate | [73.2105, 22.3120] |
| PIET Hostel Block | Hostel PIET, PIET BH | [73.2120, 22.3140] |
| Vadodara Bus Station | CBS, Bus Stand | [73.1950, 22.3070] |

*Replace with surveyed GPS coordinates before deployment.*

### 7.3 Security Checklist

- [ ] Verify Firebase tokens on every mutating endpoint
- [ ] Enforce `@paruluniversity.ac.in` on backend (not client-only)
- [ ] Rate-limit `/locations/search` and `/offers/match`
- [ ] Sanitize user-generated `notes` fields (XSS prevention)
- [ ] Use HTTPS everywhere; secure MongoDB Atlas IP allowlist
- [ ] Never commit `.env` or Firebase service account to Git

### 7.4 Testing Requirements (Academic)

| Area | Minimum Tests |
|------|---------------|
| Geo matching | Unit tests: point-to-LineString distance < 500 m |
| Fuzzy search | Unit tests: "Uni Gate" → Main Entrance score ≥ 70 |
| Auth | Integration: reject non-university token |
| Booking | E2E: create offer → request → accept → complete |
| Hotspots | Unit: K-Means returns k clusters for sample data |

### 7.5 Milestone Timeline (Suggested)

| Week | Deliverable |
|------|-------------|
| 1–2 | Firebase auth + User CRUD + PWA shell |
| 3–4 | POI seed + fuzzy search + map UI |
| 5–6 | Ride offers + geospatial matching |
| 7–8 | Requests + accept flow + cost calculator |
| 9 | K-Means hotspots + dashboard |
| 10 | Testing, documentation, demo video |

### 7.6 AI Assistant Implementation Notes

When implementing from this PRD:

1. **Always** store coordinates as `[longitude, latitude]`.
2. Create `2dsphere` indexes before running geo queries.
3. Implement `geo_match.py` with unit-tested distance logic; document deviation from pure Mongo `$geoIntersects` if using Shapely post-filter.
4. Keep Firebase domain validation on **both** client and server.
5. Use Pydantic models mirroring the JSON schemas in Section 3.
6. Frontend map: draw `LineString` for offers; `Point` markers for pickup/drop.
7. Do not implement Semester 7 features unless explicitly requested.

---

**Document Owner:** LiftLink Project Team — Parul University  
**Approval:** Ready for Semester 6 implementation
