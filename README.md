# AGSPE — Adani Group Strategic Prediction Engine

> An open-source automated intelligence platform developed under the broader research and transparency ethos associated with the Cockroach Janta Party movement — focused on ingesting public data about the Adani Group ecosystem, validating information through a multi-tier cross-source protocol, and generating probabilistic predictions on future business moves with confidence scores and timelines.

Inspired by the satirical anti-corruption and transparency-oriented political culture associated with the Cockroach Janta Party, AGSPE emphasizes open data analysis, source transparency, public accountability, and verifiable intelligence workflows built entirely on publicly available information.

> Yeh Website pakka chalta hai 😅😝

**Live website:** [https://cockroachjanathaparty-agspe.vercel.app/](https://cockroachjanathaparty-agspe.vercel.app/) 

---

## Vision

AGSPE is designed as a public-interest analytical platform that combines:

Open-source intelligence (OSINT)
Cross-source validation
Bias-aware scoring systems
Public financial analysis
Transparent probabilistic forecasting

The project reflects the broader Cockroach Janta Party philosophy of:

decentralized public scrutiny,
anti-corruption transparency,
open civic technology,
and accessible investigative tooling.

AGSPE does not claim insider access, privileged information, or political affiliation with any corporate or governmental entity. All analysis is derived from publicly accessible datasets, regulatory filings, news archives, and algorithmic inference models.

## Features

- **Predictive Analytics Dashboard** — Hybrid prediction engine combining financial indicators (35%), political alignment scoring (35%), and pattern recognition (30%) to forecast probable business moves with confidence intervals
- **Multi-Source Validation Engine** — Three-tier source trust weighting (Tier 1 = 0.9, Tier 2 = 0.7, Tier 3 = 0.3) with cross-verification rules, contradiction detection, and pro-group source capping
- **Financial Intelligence** — Dual-currency (INR/USD) display of 10 listed Adani Group companies with market cap, debt-to-equity heatmap, P/E ratios, and sortable tables
- **Lobbying & Political Tracker** — Global lobbying spend across 5 countries, electoral bond donation tracker, law firm engagement mapping
- **Intelligence Feed** — Filterable news feed with source tier badges, validation score bars, bias detection warnings, and keyword search
- **Acquisition History** — 20 major acquisitions catalogued with valuations, status tracking, sector filtering, and year-range filtering
- **Bias Detection** — Automatic flagging of pro-group sources, Tier 3 claims without Tier 1 corroboration, and contradiction alerts between Tier 1 sources
- **Daily Data Pipeline** — Vercel Cron Jobs fetch fresh data from public sources (Reuters RSS, BBC RSS, SEC EDGAR) every day at 6 AM UTC, run validation and prediction pipelines, and update the dashboard
- **Zero-Config Deployment** — Deploy to Vercel in one click; works immediately with built-in mock data as fallback — no API keys required

---

## Core Principles
| Principle         | Description                                                                             |
| ----------------- | --------------------------------------------------------------------------------------- |
| Transparency      | Every prediction includes validation metadata, source weighting, and confidence scoring |
| Public Data Only  | No private databases, leaks, or unauthorized access                                     |
| Open Verification | Claims are cross-checked across independent media and regulatory filings                |
| Bias Awareness    | Source weighting and contradiction detection are visible to users                       |
| Civic Technology  | Built as a public-interest research platform using open-source infrastructure           |
| Explainability    | Prediction logic and scoring models are documented and auditable                        |



## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, Tailwind CSS 4, Shadcn/UI, Recharts |
| API / Backend | Next.js API Routes (TypeScript), Vercel Serverless Functions |
| Validation Engine | TypeScript port of Python multi-tier verification algorithm |
| Prediction Engine | TypeScript hybrid model (Financial + Political + Pattern) |
| Data Fetching | `fetch()`-based RSS/API crawlers (serverless-compatible) |
| Cron Jobs | Vercel Cron (daily at 6 AM UTC) |
| Full-Stack (Optional) | Python 3.11 + FastAPI + Celery + PostgreSQL + Redis |
| CI/CD | GitHub Actions (3 workflows) |

---

## Why This Exists

AGSPE emerged from the idea that:

- large corporate ecosystems increasingly influence public infrastructure, energy, logistics, finance, and policy,
- public understanding of these systems often depends on fragmented reporting,
- and open-source analytical tooling can help researchers, journalists, students, and citizens better understand systemic corporate behavior patterns.

The platform therefore attempts to:

- aggregate dispersed public information,
- validate claims through weighted-source verification,
- identify recurring strategic patterns,
- and present findings in an auditable and transparent manner.

## Research Orientation

The project draws inspiration from:

- OSINT methodologies,
- investigative journalism workflows,
- financial risk analysis systems,
- civic-tech transparency initiatives,
- and decentralized open research communities.

AGSPE is intentionally structured so that:

- all scoring logic is inspectable,
- all datasets can be audited,
- all source weighting rules are visible,
- and all predictions remain probabilistic rather than deterministic.

## Quick Start

### Option 1: Deploy to Vercel (Recommended — One Click)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/cockroachparty/cockroachjanathaparty-agspe)

1. Click the button above or import the repo on [vercel.com/new](https://vercel.com/new)
2. Vercel auto-detects Next.js — just click **Deploy**
3. Your dashboard is live at `https://your-project.vercel.app`
4. Cron jobs are automatically configured via `vercel.json`

**No environment variables required.** The app works immediately with built-in mock data. The cron job will attempt to fetch live data from public RSS feeds and APIs; if those are unavailable, it gracefully falls back to the mock dataset.

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/cockroachparty/cockroachjanathaparty-agspe.git
cd cockroachjanathaparty-agspe

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — the dashboard works immediately. All API routes (`/api/predictions`, `/api/financials`, etc.) return mock data by default.

To test the cron refresh pipeline locally:

```bash
curl http://localhost:3000/api/cron/refresh
```

### Option 3: Full Stack with Docker Compose (Advanced)

For the full Python backend with PostgreSQL and Redis:

```bash
cp .env.example .env
# Edit .env with your API keys (optional)
docker-compose up --build
```

This starts:
- **Next.js Frontend** on `http://localhost:3000`
- **FastAPI Backend** on `http://localhost:8000` (Swagger docs at `/docs`)
- **PostgreSQL** on `localhost:5432`
- **Redis** on `localhost:6379`
- **Celery Worker** for async data ingestion tasks

---

## Vercel Deployment Details

### How It Works

AGSPE runs entirely on Vercel as a single Next.js application:

1. **Frontend** — React components rendered by Next.js, fetching data from API routes
2. **API Routes** — Serverless functions at `/api/*` that serve data from an in-memory cache
3. **Data Pipeline** — Vercel Cron triggers `/api/cron/refresh` daily, which:
   - Fetches latest news from Reuters RSS, BBC RSS, The Hindu RSS
   - Fetches regulatory filings from SEC EDGAR public API
   - Runs all articles through the Multi-Source Validation Engine
   - Generates new predictions using the Hybrid Prediction Engine
   - Updates the in-memory cache with validated, scored data
4. **Graceful Fallback** — If external sources are unavailable, all data falls back to a comprehensive mock dataset

### Cron Schedule

| Schedule | Endpoint | Description |
|----------|----------|-------------|
| Daily at 6 AM UTC | `/api/cron/refresh` | Fetches fresh data, runs validation & prediction pipelines |

The cron is configured in `vercel.json` and activates automatically on deployment.

### Optional Environment Variables

| Variable | Purpose |
|----------|---------|
| `CRON_SECRET` | If set, the `/api/cron/refresh` endpoint verifies the `Authorization: Bearer <CRON_SECRET>` header |
| `NEWS_API_KEYS` | Comma-separated News API keys for enhanced news fetching |

These are **entirely optional** — the app works without them.

### Vercel Configuration

The `vercel.json` file configures:

```json
{
  "crons": [{
    "path": "/api/cron/refresh",
    "schedule": "0 6 * * *"
  }],
  "functions": {
    "src/app/api/cron/refresh/route.ts": {
      "maxDuration": 60
    }
  },
  "headers": [{
    "source": "/api/(.*)",
    "headers": [
      { "key": "Cache-Control", "value": "s-maxage=3600, stale-while-revalidate=86400" }
    ]
  }]
}
```

- Cron runs daily at 6 AM UTC
- The refresh function has a 60-second timeout (max for Vercel Hobby plan)
- API responses are cached for 1 hour with 24-hour stale-while-revalidate

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api` | GET | System info (name, version, status, last refresh) |
| `/api/predictions` | GET | Strategic predictions with confidence scores |
| `/api/financials` | GET | Financial data for 10 Adani Group companies |
| `/api/news` | GET | Validated news articles with bias scores |
| `/api/lobbying` | GET | Lobbying records and electoral bond data |
| `/api/acquisitions` | GET | Acquisition history with valuations |
| `/api/health` | GET | System health status and data freshness |
| `/api/cron/refresh` | GET | Cron-triggered data refresh pipeline |

All endpoints return JSON with the structure: `{ "data": [...], "source": "live" | "mock", "lastRefresh": "ISO timestamp" }`

---

## Project Structure

```
├── .github/workflows/
│   ├── data-ingestion-cron.yaml      # Scheduled data pipeline (every 4hrs)
│   ├── model-validation.yaml         # Weekly model backtesting
│   └── security-scan.yaml            # Security audits on push
├── backend/                           # Python FastAPI (optional full-stack)
│   ├── app/
│   │   ├── api/routes.py             # FastAPI endpoints
│   │   ├── crawlers/                 # Python web crawlers
│   │   ├── models/                   # Python engine code
│   │   ├── data/                     # Seed data & source tiers
│   │   ├── utils/                    # Currency, text, audit
│   │   └── config.py                 # Backend config
│   ├── tests/                        # Python test suite
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── data_dictionary.md            # Data entity documentation
│   └── model_logic.md                # Prediction model documentation
├── src/
│   ├── app/
│   │   ├── api/                      # Next.js API Routes (Vercel backend)
│   │   │   ├── route.ts              # Root API endpoint
│   │   │   ├── predictions/route.ts  # Predictions API
│   │   │   ├── financials/route.ts   # Financials API
│   │   │   ├── news/route.ts         # News API
│   │   │   ├── lobbying/route.ts     # Lobbying API
│   │   │   ├── acquisitions/route.ts # Acquisitions API
│   │   │   ├── health/route.ts       # Health check
│   │   │   └── cron/refresh/route.ts # Cron refresh pipeline
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Main dashboard page
│   │   └── globals.css               # Global styles
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── PredictionDashboard.tsx
│   │   │   ├── FinancialsTab.tsx
│   │   │   ├── LobbyingTab.tsx
│   │   │   ├── IntelligenceFeed.tsx
│   │   │   └── AcquisitionsTab.tsx
│   │   └── ui/                       # Shadcn/UI components
│   ├── lib/
│   │   ├── engine/                   # TypeScript engine code
│   │   │   ├── types.ts              # Shared types & config
│   │   │   ├── validation.ts         # Multi-Source Verification Engine
│   │   │   ├── predictor.ts          # Hybrid Prediction Engine
│   │   │   ├── bias-detector.ts      # Bias detection
│   │   │   └── data-fetcher.ts       # Serverless data fetcher
│   │   ├── data/
│   │   │   └── store.ts              # In-memory data cache
│   │   ├── mock-data.ts             # Mock dataset (fallback)
│   │   ├── utils.ts                  # Utility functions
│   │   └── db.ts                     # Database client
│   └── hooks/                        # Custom React hooks
├── public/
│   └── logo.svg                      # AGSPE logo
├── docker-compose.yml                # Full-stack Docker config
├── Dockerfile.frontend               # Frontend Docker
├── vercel.json                       # Vercel cron & config
├── .env.example                      # Environment variables
├── next.config.ts                    # Next.js configuration
├── package.json
├── LICENSE                           # MIT License
└── README.md
```

---

## Validation Engine

The Multi-Source Verification Algorithm is the core of AGSPE's reliability:

### Source Trust Tiers

| Tier | Weight | Examples | Behavior |
|------|--------|----------|----------|
| Tier 1 | 0.9 | Reuters, AP, BBC, Bloomberg, Financial Times, OCCRP | Highest trust; can corroborate Tier 3 claims |
| Tier 2 | 0.7 | The Hindu, Scroll.in, Business Standard | Independent Indian media; moderate trust |
| Tier 3 | 0.3 | NDTV, Times Now, Republic TV, Adani Group PR | Requires Tier 1 confirmation within 24hrs |

### Cross-Verification Rules

1. **Tier 3 claims** without Tier 1 corroboration within 24 hours get their validation score capped at 0.3 and are flagged "Requires Verification"
2. **Contradicting Tier 1 sources** trigger a manual review flag and pause confidence scoring
3. **Pro-group-only sources** (all sources are pro-Adani) get scores capped at 0.2
4. **Single source penalty** — any claim backed by only one source suffers a 20% score reduction

### Output

| Field | Type | Description |
|-------|------|-------------|
| `validation_score` | Float (0.0–1.0) | Weighted confidence based on source tiers |
| `bias_risk_level` | String | "Low" / "Medium" / "High" |
| `flags` | Array | Specific validation flags raised |

---

## Prediction Model

The Hybrid Prediction Engine generates forecasts using a three-signal system:

### Signal Weights

| Signal | Weight | Description |
|--------|--------|-------------|
| Financial Indicators | 35% | Debt-to-equity, capex, volatility, revenue growth |
| Political Alignment | 35% | Proximity to government policy, relevance scoring |
| Pattern Recognition | 30% | Known acquisition cycles, policy correlations |

### Known Patterns

| Pattern | Typical Duration | Base Confidence |
|---------|-----------------|----------------|
| Standard Acquisition Cycle | 18 months | 70% |
| Green Energy Expansion | 24 months | 75% |
| Port & Infrastructure Play | 12 months | 80% |
| Distressed Asset Acquisition | 15 months | 65% |

### Policy Correlations

| Trigger | Predicted Action | Base Probability |
|---------|-----------------|------------------|
| BJP infrastructure push | Adani port/airport bid win | 82% |
| Renewable target raised | Adani Green expansion/JV | 78% |
| Defense procurement policy | Adani Defense contract | 65% |
| Housing/infra policy boost | Cement capacity expansion | 72% |

---

## Data Pipeline

### Daily Refresh Flow

```
Vercel Cron (6 AM UTC)
    │
    ▼
/api/cron/refresh
    │
    ├── Fetch Reuters RSS → Parse articles
    ├── Fetch BBC RSS → Parse articles
    ├── Fetch The Hindu RSS → Parse articles
    ├── Fetch SEC EDGAR API → Parse filings
    │
    ▼
Validation Engine
    │
    ├── Apply tier weights (0.9 / 0.7 / 0.3)
    ├── Cross-verification checks
    ├── Contradiction detection
    ├── Pro-group bias capping
    └── Generate validation_score + bias_risk_level
    │
    ▼
Prediction Engine
    │
    ├── Calculate financial signals
    ├── Score political alignment
    ├── Match acquisition/policy patterns
    └── Generate predictions with confidence + timeline
    │
    ▼
Update Cache
    │
    ├── Store validated articles
    ├── Store fresh predictions
    ├── Store financial data
    └── Update lastRefresh timestamp
    │
    ▼
Dashboard Updated
```

### Graceful Degradation

If external data sources are unreachable:
1. The data fetcher logs the error and continues
2. The store retains the previous cache (or mock data on first run)
3. Predictions are generated from available data
4. The dashboard always displays data — never shows a blank state
5. The `/api/health` endpoint reports the data source as `"mock"` when using fallback data

---

## GitHub Actions Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `data-ingestion-cron.yaml` | Every 4 hours / manual | Runs Python crawlers + validation (full-stack mode) |
| `model-validation.yaml` | Weekly Monday / manual | Runs test suite + backtests predictions |
| `security-scan.yaml` | Push to `main`/`develop` | Dependency audits, credential scanning, GDPR check |

---

## Environment Variables

See `.env.example` for the full list. **None are required** for Vercel deployment.

| Variable | Required | Description |
|----------|----------|-------------|
| `CRON_SECRET` | No | Optional bearer token to secure the cron endpoint |
| `NEWS_API_KEYS` | No | Comma-separated News API keys for enhanced fetching |
| `DATABASE_URL` | Full stack only | PostgreSQL connection string |
| `REDIS_URL` | Full stack only | Redis connection for caching |
| `SECRET_KEY` | Full stack only | Application secret key |
| `PROXY_ROTATOR_URL` | Full stack only | Proxy service for web scraping |

---

## Security & Ethics

- **No PII collection** — The system does not collect or store any personal information
- **Public data only** — All data sources are publicly available records, filings, and news
- **GDPR/DPDP India compliant** — Automated compliance checks in CI/CD pipeline
- **Rate limiting** — All crawlers respect rate limits (2-second delay, max 30 requests/minute)
- **Bias transparency** — Every data point displays its validation score, source tier, and bias risk level
- **Not financial advice** — This tool is for informational and research purposes only

---

## Disclaimer

This project is for informational, educational, and research purposes only.

AGSPE does not provide:

- investment advice,
- legal advice,
- insider information,
- political endorsements,
- or financial recommendations.

All predictions are probabilistic estimates derived from publicly available information and historical pattern analysis. Users should independently verify all findings before making business, legal, political, or financial decisions.

The project reflects open-source civic-tech and transparency ideals associated with the Cockroach Janta Party ecosystem, but operates as an independent research and software initiative.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
