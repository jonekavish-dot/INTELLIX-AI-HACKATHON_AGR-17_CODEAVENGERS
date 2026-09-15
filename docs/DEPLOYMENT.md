# AgriDiff AI — Cloud Deployment Guide: Render & Vercel

**Project:** AgriDiff AI — Agricultural Document Comparison & Change Intelligence  
**Team:** CODEAVENGERS | BIT-AI-001 | AGR-17  
**Version:** 1.1.0  
**Last Updated:** September 2026

This guide provides step-by-step instructions to deploy the complete AgriDiff AI production stack:
- **Backend API:** Hosted on **Render** (FastAPI Python ASGI Web Service)
- **Frontend SPA:** Hosted on **Vercel** (High-performance Vite React Single Page Application)

---

## 1. Architecture & Deployment Topology

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│         VERCEL FRONTEND         │           │         RENDER BACKEND          │
│   (Vite + React 18 + Tailwind)  │           │       (FastAPI + Uvicorn)       │
│                                 │           │                                 │
│  https://agridiff.vercel.app    │  ──API──> │  https://agridiff.onrender.com  │
│                                 │  Requests │                                 │
│  • Single Page App (SPA)        │  (Axios)  │  • Multi-page PDF Extractor     │
│  • Mobile & Desktop Responsive  │           │  • Semantic Chunk Aligner       │
│  • Interactive Evidence Modal   │           │  • Structured Land Deed Parser  │
│  • Configured via VITE_API_URL  │           │  • Gemini LLM & Rule Fallback   │
└─────────────────────────────────┘           └─────────────────────────────────┘
```

---

## 2. Deploying the Backend on Render

Render provides free and affordable Python web service hosting with automatic HTTPS, continuous deployment from GitHub, and health checks.

### Step 2.1: Create a Render Web Service
1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub account and select the **AgriDiff AI** repository.

### Step 2.2: Configure Web Service Settings
Fill in the deployment parameters:

| Configuration Field | Value | Notes |
| :--- | :--- | :--- |
| **Name** | `agridiff-backend` | Choose your preferred service name |
| **Region** | *Choose closest region* | e.g. Frankfurt, Oregon, Singapore |
| **Branch** | `main` | Production branch |
| **Root Directory** | *(Leave blank)* | Uses root of repo |
| **Runtime** | `Python 3` | Native Python runtime |
| **Build Command** | `pip install -r backend/requirements.txt` | Installs pinned backend packages |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` | Starts production ASGI server |
| **Instance Type** | `Free` or `Starter` | Free tier provides 512 MB RAM |

### Step 2.3: Set Environment Variables
In the **Environment Variables** section on Render, add:

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `AIzaSy...your_actual_key` | Google Gemini API key (optional; system falls back gracefully if absent) |
| `LLM_MODEL` | `gemini-1.5-flash` | Gemini model name |
| `PYTHON_VERSION` | `3.11.9` | Recommended stable Python version on Render |
| `LLM_TIMEOUT_SECONDS`| `30` | Timeout threshold for API calls |

### Step 2.4: Set Health Check Path
- Scroll down to **Advanced** settings.
- Set **Health Check Path** to: `/api/health`
- Render will ping this endpoint to verify that the service is healthy before routing traffic.

### Step 2.5: Deploy
- Click **Create Web Service**.
- Render will pull the repository, run `pip install -r backend/requirements.txt`, and launch Uvicorn.
- Once deployed, copy your public Render URL:
  `https://agridiff-backend.onrender.com` (Save this for frontend setup).

---

## 3. Deploying the Frontend on Vercel

Vercel provides edge CDN hosting, instantaneous global distribution, and automated builds for React Vite applications.

### Step 3.1: Import Project into Vercel
1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Select and import the **AgriDiff AI** repository from GitHub.

### Step 3.2: Configure Build & Directory Settings
> [!IMPORTANT]
> The React Vite application resides in the `frontend/` subdirectory. You **must** set the Root Directory to `frontend`.

| Setting | Value |
| :--- | :--- |
| **Framework Preset** | `Vite` |
| **Root Directory** | Click **Edit** and choose `frontend` |
| **Build Command** | `npm run build` (default) |
| **Output Directory** | `dist` (default) |
| **Install Command** | `npm install` (default) |

### Step 3.3: Configure Environment Variables
In the **Environment Variables** panel in Vercel, add:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://agridiff-backend.onrender.com` | **Your exact Render backend URL** (Do NOT include a trailing slash) |

### Step 3.4: Client-Side Routing (SPA Rewrites)
The repository already includes [frontend/vercel.json](file:///d:/INTELLIX/repo/frontend/vercel.json):
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
This ensures that refreshing pages on deep routes (`/results`, `/compare`, etc.) correctly resolves to the React client application without 404 errors.

### Step 3.5: Deploy
- Click **Deploy**.
- Vercel will transpile the React bundle in ~20 seconds and assign a production URL:
  `https://agridiff.vercel.app` (or custom domain).

---

## 4. Alternative: Deploying Frontend on Render (Static Site)

If you prefer keeping both frontend and backend on Render:

1. In Render Dashboard, click **New +** -> **Static Site**.
2. Connect your GitHub repository.
3. Configure settings:
   - **Name:** `agridiff-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Publish Directory:** `dist`
4. Under **Redirects/Rewrites**:
   - **Source:** `/*`
   - **Destination:** `/index.html`
   - **Action:** `Rewrite`
5. Under **Environment Variables**:
   - Set `VITE_API_URL` to your Render backend URL.
6. Click **Create Static Site**.

---

## 5. Infrastructure-as-Code: Render Blueprint (`render.yaml`)

For 1-click deployment of the entire backend stack on Render, the repository provides a `render.yaml` configuration in the project root:

```yaml
services:
  - type: web
    name: agridiff-backend
    runtime: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: LLM_MODEL
        value: gemini-1.5-flash
      - key: GEMINI_API_KEY
        sync: false
```

---

## 6. Verifying Production Deployment

Once deployed, run these verification checks:

### 1. Backend Health Check
```bash
curl https://agridiff-backend.onrender.com/api/health
```
**Expected Response:**
```json
{"status":"ok","service":"AgriDiff AI","version":"1.1.0"}
```

### 2. Available Presets Check
```bash
curl https://agridiff-backend.onrender.com/api/presets
```
**Expected Response:**
Lists `preset_policy` (Kharif/Rabi scheme) and `preset_land_record` (Patta land deed).

### 3. Frontend Verification
1. Open your Vercel URL in any desktop or mobile browser.
2. Log in using any demo account:
   - **Farmer:** `farmer` / `farmer123`
   - **Officer:** `officer` / `officer123`
   - **Reviewer:** `reviewer` / `reviewer123`
3. Click **Load Preset: Fertilizer & Irrigation Policy**.
4. Observe the real-time comparison progress bar and redirect to `/results`.
5. Verify:
   - **Tab 1 (Exhaustive Comparison):** All 24 detected changes with dual-format Operational Notes and Action Directives.
   - **Tab 2 (Consequential Impact):** Prioritized high/medium changes.
   - **Tab 3 (Structured Land Records):** Formatted deed attributes.
   - **Evidence Modal:** Click **View Evidence** on any card to confirm side-by-side source passages.

---

## 7. Troubleshooting Cloud Deployments

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| **CORS Error in browser console** | Backend rejecting requests from Vercel origin | AgriDiff AI has `allow_origins=["*"]` configured in `backend/main.py`. Ensure your Render backend service is running and not sleeping. |
| **Free Render Web Service sleeping** | Render Free instances spin down after 15 min of inactivity | The first request after sleep takes 30-50 seconds to spin up. Subsequent requests respond instantly. |
| **Frontend 404 on page reload** | Missing SPA rewrite rules on Vercel | Verify [frontend/vercel.json](file:///d:/INTELLIX/repo/frontend/vercel.json) exists with the rewrite rule to `/index.html`. |
| **API calls failing with 404** | `VITE_API_URL` missing or trailing slash | In Vercel Environment Variables, set `VITE_API_URL` without a trailing slash: `https://agridiff-backend.onrender.com`. |
