# MongoDB Atlas Setup (Phase 1.2)

## Steps

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign in.
2. **Create Deployment** → Shared (M0 FREE) → name cluster `liftlink-dev` → region closest to India.
3. **Database Access** → Add New Database User → username/password → role: `readWriteAnyDatabase` (or scoped to `liftlink`).
4. **Network Access** → Add IP Address → for local dev you may use `0.0.0.0/0` (allow from anywhere). **Tighten before production demo.**
5. **Connect** → Drivers → copy connection string → replace `<password>` and set database name `liftlink`.

## Configure backend

```bash
# backend/.env
MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster.mongodb.net/liftlink?retryWrites=true&w=majority
```

## Verify

```bash
cd backend
source .venv/bin/activate
python scripts/test_mongodb.py
```

Expected output: `MongoDB ping: OK`
