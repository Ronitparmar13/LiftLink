# Firebase Setup (Phase 1.3)

## Steps

1. [Firebase Console](https://console.firebase.google.com/) → **Add project** → e.g. `liftlink-parul`.
2. **Build** → **Authentication** → **Sign-in method** → enable **Google**.
3. **Authentication** → **Settings** → **Authorized domains** → ensure `localhost` is listed.
4. **Project settings** → **Your apps** → **Web** (`</>`) → register app → copy SDK config.

## Frontend (`frontend/.env`)

```env
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

## Backend service account

1. **Project settings** → **Service accounts** → **Generate new private key**.
2. Save as `backend/firebase-service-account.json` (already in `.gitignore`).

```env
# backend/.env
FIREBASE_SERVICE_ACCOUNT_JSON=./firebase-service-account.json
ALLOWED_EMAIL_DOMAIN=paruluniversity.ac.in
```

Only `@paruluniversity.ac.in` emails may use the app (enforced in Phase 2/3 on the server).
