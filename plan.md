# LiftLink — Project Status & Pending Work

> Generated: 2026-05-28

---

## 1. Project Overview

**LiftLink** is an AI-powered hyper-local campus ride-pooling platform for Parul University (`@paruluniversity.ac.in` only).

| Layer | Stack |
|-------|-------|
| Frontend | React 19 + Vite 8 + Tailwind 3 + Leaflet + Firebase SDK (PWA) |
| Backend | FastAPI + Motor (async MongoDB) + Firebase Admin + Scikit-Learn + RapidFuzz |
| Database | MongoDB Atlas (M0) with `2dsphere` indexes |
| Auth | Firebase Google Sign-In, domain-enforced |

---

## 2. What Is Done (Working)

### Backend (all 18 tests passing)
- [x] Firebase token verification + `@paruluniversity.ac.in` domain enforcement
- [x] User sync/profile CRUD (`POST /auth/sync`, `GET /auth/me`, `GET/POST/PATCH /users/*`)
- [x] Ride offers CRUD (create, list mine, get, update, cancel) with GeoJSON LineString
- [x] Ride requests lifecycle (create, list mine, driver inbox, get detail)
- [x] Request actions with atomic seat updates (accept, reject, cancel, complete)
- [x] Geospatial route matching — 500m point-to-LineString distance with local tangent-plane projection
- [x] Fuzzy POI search using RapidFuzz (score >= 70 threshold)
- [x] K-Means hotspot clustering (`POST /hotspots/refresh`, `GET /hotspots/trending`)
- [x] Fuel-split cost calculator (haversine distance * configurable rate)
- [x] Booking state machine with race-condition-safe seat decrement
- [x] Global exception handlers (structured error responses)
- [x] Seed scripts (init_indexes, seed_pois, seed_offers, seed_requests_for_hotspots)
- [x] Unit tests: auth (4), cost_calc (3), fuzzy_search (2), geo_match (7), hotspot_cluster (2)

### Frontend (lint passes clean)
- [x] Auth flow (Google sign-in popup, domain check, token refresh interceptor, sign-out)
- [x] Pages: Login, Dashboard, OfferRide, FindRide, MyOffers, Profile, DriverInbox, OfferInbox, RequestStatus
- [x] Map view with Leaflet (marker pick for start/end, pickup/dropoff, route overlays)
- [x] Fuzzy location search input hitting backend `/locations/search`
- [x] Ride match cards with fuel-split badge and payment disclaimer
- [x] Active trip widget on dashboard (polls rider requests + driver inbox)
- [x] Trending pickup zones widget (hits `/hotspots/trending`)
- [x] PWA configured via `vite-plugin-pwa` (auto-update, workbox caching)
- [x] 3D UI foundation: Button3D, Panel3D, MapContainer3D, ThreeDProvider with WebGL detection
- [x] React Router with protected routes and app layout

---

## 3. Pending — High Priority (Must Complete for S6)

### 3.1 PWA & Build Verification
- [ ] Verify `npm run build` produces a working production bundle
- [ ] Confirm `vite-plugin-pwa` generates a valid `manifest.webmanifest` at build time
- [ ] Add proper PWA icons (currently only `favicon.svg` — needs `192x192` and `512x512` PNG for install prompts)
- [ ] Test PWA installability on mobile device (iOS Safari + Android Chrome)
- [ ] Verify service worker caches static assets and API calls correctly

### 3.2 Security Checklist (PRD Section 7.3)
- [x] **Rate limiting** — Add rate limiting to `/locations/search` and `/offers/match` (use `slowapi` or similar)
- [x] **XSS sanitization** — Sanitize user-generated `notes` fields in ride offers (use `bleach` or equivalent)
- [x] **Input validation** — Ensure all GeoJSON coordinates are validated against campus bounding box on backend
- [x] **CORS audit** — Verify CORS origins are not overly permissive in production

### 3.3 Dashboard Navigation Fix
- [x] Replace `window.location.href` with React Router `useNavigate()` in `DashboardPage.tsx` (lines 20-21, 32-33) — full page reloads break SPA behavior

### 3.4 OfferInboxPage Completeness
- [x] Verify `OfferInboxPage.tsx` renders all requests for a specific offer with accept/reject actions for the driver

### 3.5 Missing Backend Endpoint
- [x] Add `GET /offers` — list all open offers with filters (status, time range) for general browsing/discovery

### 3.6 Deployment
- [x] Create `Dockerfile` for backend (FastAPI + Uvicorn)
- [x] Create deployment config for frontend (Vercel/Netlify/static hosting)
- [x] Set up production environment variables (MongoDB Atlas, Firebase, CORS_ORIGINS)
- [ ] Add MongoDB Atlas production IP allowlist (remove `0.0.0.0/0`)
- [ ] Document production deployment steps

---

## 4. Pending — Medium Priority (Should Complete for S6)

### 4.1 Testing Gaps
- [x] **Backend integration tests** — Full API flow tests (create user → create offer → match → request → accept → complete)
- [x] **Backend edge case tests** — Duplicate request 409, self-request rejection, past departure rejection, seat exhaustion race
- [ ] **Frontend tests** — Add Vitest + React Testing Library; write tests for:
  - Auth context (sign-in, domain enforcement, sign-out)
  - Offer creation form validation
  - Find ride search and request flow
  - Cost calculation utility functions
- [ ] **E2E tests** — Playwright or Cypress for the full driver-rider booking flow (see `docs/E2E_CHECKLIST.md`)

### 4.2 Frontend Error Handling
- [ ] Verify `frontend/src/utils/errors.ts` handles all axios error shapes (401, 403, 409, 422, 500)
- [ ] Add toast/snackbar notifications for success/error feedback (instead of inline text only)
- [ ] Add loading skeletons for dashboard and list pages

### 4.3 Profile Page Improvements
- [ ] Add phone number validation (+91 format)
- [ ] Add vehicle description max-length enforcement
- [ ] Show ride stats (ridesAsDriver, ridesAsRider) on profile page

### 4.4 MyOffersPage Improvements
- [ ] Add ability to cancel an open offer from the list
- [ ] Show request count badge on each offer card
- [ ] Show status transitions (open → full → completed)

### 4.5 Backend Observability
- [ ] Add structured logging (JSON logs with request ID, user ID, timestamp)
- [ ] Add health check endpoint to report version number
- [ ] Add request ID middleware for tracing

---

## 5. Pending — Low Priority (Nice to Have for S6)

### 5.1 3D UI Enhancements (PRD_3D_UI.md)
- [ ] Implement `Modal3D` component with 3D fade-in animation
- [ ] Implement `Input3D` with inset shadow focus states
- [ ] Add haptic feedback on button press (for supported mobile devices)
- [ ] Add optional click sound feedback (configurable in settings)
- [ ] Create 2D fallback components (currently falls back via CSS only)
- [ ] Add performance monitoring hook (FPS tracking for 3D canvas)
- [ ] Conduct accessibility audit (keyboard nav, screen reader, `prefers-reduced-motion`)
- [ ] Add Storybook documentation for 3D components

### 5.2 UI Polish
- [ ] Add a proper bottom navigation bar for mobile (Dashboard, Find, Offer, Inbox, Profile)
- [ ] Add pull-to-refresh on list pages (MyOffers, DriverInbox)
- [ ] Add confirmation modals for destructive actions (cancel offer, reject request)
- [ ] Add dark/light theme toggle (currently dark-only)
- [ ] Improve empty states with illustrations
- [ ] Add offline indicator banner when backend is unreachable

### 5.3 Code Quality
- [ ] Create `ProjectBreakdown.md` (referenced in README but missing)
- [ ] Add JSDoc/TSDoc comments to complex frontend functions
- [ ] Add Python type hints audit (ensure all functions have complete annotations)
- [ ] Add pre-commit hooks (black, ruff, eslint)

---

## 6. Semester 7 Scope (Not for S6 — Document Only)

These items are explicitly **out of scope** for the current semester but should be tracked:

- [ ] Real-time GPS tracking (WebSocket/Firebase Realtime DB)
- [ ] In-app payment gateway (Razorpay/PhonePe)
- [ ] Push notifications (FCM) for request/accept events
- [ ] Driver/rider rating and trust score system
- [ ] Route optimization via OSRM
- [ ] Multi-stop carpooling
- [ ] Female-only ride preference filter
- [ ] University admin dashboard with ride analytics
- [ ] SOS / emergency contact integration
- [ ] Hindi/Gujarati i18n
- [ ] Native iOS/Android apps (or improved PWA)
- [ ] Chat or voice calling between users

---

## 7. Files Referenced But Missing

| File | Status |
|------|--------|
| `ProjectBreakdown.md` | Referenced in README but does not exist |
| `frontend/public/manifest.json` | Generated by vite-plugin-pwa at build time — verify |
| `frontend/public/192x192.png` | Missing — needed for PWA install prompt |
| `frontend/public/512x512.png` | Missing — needed for PWA install prompt |

---

## 8. Quick Wins (Can Do Now)

1. **Fix DashboardPage navigation** — Replace `window.location.href` with `useNavigate()` ✅
2. **Add `GET /offers` endpoint** — Simple list with filters ✅
3. **Add rate limiting** — `pip install slowapi`, apply to search/match endpoints ✅
4. **Add PWA icons** — Generate 192x192 and 512x512 PNG from existing `favicon.svg` ✅
5. **Run `npm run build`** — Verify production build works ✅
6. **Create `ProjectBreakdown.md`** — Track milestones as referenced in README ✅

---

## 9. Test Status Summary

| Area | Status | Count |
|------|--------|-------|
| Backend unit tests | All passing | 18/18 |
| Backend integration tests | All passing | 3/3 |
| Backend edge case tests | All passing | 10/10 |
| Frontend unit tests | No framework configured | 0 |
| Frontend E2E tests | Not written | 0 |
| Lint (frontend) | Passing | 0 errors |
| Build (frontend) | Passing | ✓ |
