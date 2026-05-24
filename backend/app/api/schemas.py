"""
AGSPE API Schemas - Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date
from enum import Enum


class BiasRiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PoliticalRiskLevel(str, Enum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"


class AcquisitionStatus(str, Enum):
    ACTIVE = "Active"
    INTEGRATED = "Integrated"
    DEMERGED = "Demerged"
    PENDING_LITIGATION = "Pending Litigation"


class NewsTag(str, Enum):
    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"
    PRO_GROUP = "Pro-Group"


# ── News Schemas ──

class NewsArticle(BaseModel):
    id: str
    title: str
    source: str
    source_tier: int = Field(ge=1, le=3)
    url: str = ""
    published_at: datetime
    content_snippet: str
    validation_score: float = Field(ge=0.0, le=1.0)
    bias_risk_level: BiasRiskLevel
    tag: NewsTag = NewsTag.UNVERIFIED
    related_companies: List[str] = []
    keywords: List[str] = []


class NewsFilterParams(BaseModel):
    min_validation_score: float = 0.0
    source_tier: Optional[int] = None
    tag: Optional[NewsTag] = None
    bias_risk_level: Optional[BiasRiskLevel] = None
    search: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# ── Prediction Schemas ──

class Prediction(BaseModel):
    id: str
    likely_action: str
    category: str
    timeline_start: str  # e.g., "Q3 2026"
    timeline_end: str    # e.g., "Q1 2027"
    confidence_score: float = Field(ge=0.0, le=100.0)
    supporting_evidence: List[str] = []
    risk_factors: List[str] = []
    created_at: datetime
    validation_score: float = Field(ge=0.0, le=1.0)


class PredictionDetail(Prediction):
    financial_signals: Dict = {}
    political_alignment: float = 0.0
    pattern_match: str = ""
    data_sources: List[str] = []


# ── Financial Schemas ──

class FinancialData(BaseModel):
    id: str
    company_name: str
    ticker: str
    market_cap_inr: float
    market_cap_usd: float
    debt_to_equity: float
    stock_price: float
    stock_price_usd: float
    volume: int
    sector: str
    change_percent: float = 0.0
    pe_ratio: float = 0.0
    last_updated: datetime


# ── Lobbying Schemas ──

class LobbyingRecord(BaseModel):
    id: str
    entity: str
    country: str
    amount_inr: float = 0.0
    amount_usd: float = 0.0
    quarter: str
    year: int
    law_firm: str = ""
    disclosure_type: str
    source_url: str = ""
    description: str = ""


# ── Acquisition Schemas ──

class AcquisitionRecord(BaseModel):
    id: str
    company_acquired: str
    acquirer: str
    year: int
    valuation_inr: float
    valuation_usd: float
    status: AcquisitionStatus
    sector: str
    source_url: str = ""
    notes: str = ""


# ── Validation Schemas ──

class ValidationRequest(BaseModel):
    claim: str
    sources: List[Dict]  # [{name, tier, weight, agrees: bool}]


class ValidationResult(BaseModel):
    validation_score: float = Field(ge=0.0, le=1.0)
    bias_risk_level: BiasRiskLevel
    flags: List[str] = []
    cross_verification_status: str = ""
    tier_1_corroboration: bool = False
    contradiction_detected: bool = False


# ── Political Risk Schemas ──

class PoliticalRiskIndicator(BaseModel):
    level: PoliticalRiskLevel
    factors: List[str] = []
    last_updated: datetime
    government_alignment_score: float = 0.0
    upcoming_events: List[Dict] = []


# ── Dashboard Summary ──

class DashboardSummary(BaseModel):
    total_predictions: int
    high_confidence_predictions: int
    average_confidence: float
    political_risk: PoliticalRiskIndicator
    top_predictions: List[Prediction]
    recent_validated_news: List[NewsArticle]
    market_cap_total_inr: float
    market_cap_total_usd: float
    active_acquisitions: int
    total_lobbying_spend_usd: float
    last_data_update: datetime


# ── Generic Response ──

class PaginatedResponse(BaseModel):
    items: List = []
    total: int = 0
    limit: int = 20
    offset: int = 0


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime
