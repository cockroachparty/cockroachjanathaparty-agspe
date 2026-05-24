"""
AGSPE API Routes - All API endpoint definitions for the dashboard.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime

from ..api.schemas import (
    HealthResponse, ValidationResult, ValidationRequest,
    DashboardSummary, PoliticalRiskIndicator, PoliticalRiskLevel,
    BiasRiskLevel, NewsTag, AcquisitionStatus,
)
from ..models.validation import ValidationEngine
from ..models.predictor import PredictionEngine
from ..models.bias_detector import BiasDetector
from ..utils.audit_logger import audit_logger
from ..data.seed_data import (
    get_seed_news_articles, get_seed_predictions, get_seed_financial_data,
    get_seed_lobbying_records, get_seed_acquisitions, get_seed_political_risk,
)

router = APIRouter()

# ── Initialize engines ──
validation_engine = ValidationEngine()
prediction_engine = PredictionEngine()
bias_detector = BiasDetector()


# ── Health Check ──

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """API health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )


# ── Dashboard Summary ──

@router.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get comprehensive dashboard summary data."""
    predictions = get_seed_predictions()
    news = get_seed_news_articles()
    financials = get_seed_financial_data()
    acquisitions = get_seed_acquisitions()
    lobbying = get_seed_lobbying_records()
    political_risk = get_seed_political_risk()

    total_market_cap_inr = sum(f.get("market_cap_inr", 0) for f in financials)
    total_market_cap_usd = sum(f.get("market_cap_usd", 0) for f in financials)
    total_lobbying_usd = sum(l.get("amount_usd", 0) for l in lobbying)
    active_acquisitions = len([a for a in acquisitions if a.get("status") == "Active"])
    high_conf = len([p for p in predictions if p.get("confidence_score", 0) >= 70])
    avg_confidence = sum(p.get("confidence_score", 0) for p in predictions) / max(len(predictions), 1)

    return {
        "total_predictions": len(predictions),
        "high_confidence_predictions": high_conf,
        "average_confidence": round(avg_confidence, 1),
        "political_risk": political_risk,
        "top_predictions": predictions[:5],
        "recent_validated_news": [n for n in news if n.get("validation_score", 0) >= 0.8][:5],
        "market_cap_total_inr": total_market_cap_inr,
        "market_cap_total_usd": total_market_cap_usd,
        "active_acquisitions": active_acquisitions,
        "total_lobbying_spend_usd": total_lobbying_usd,
        "last_data_update": datetime.utcnow().isoformat(),
    }


# ── Predictions ──

@router.get("/api/predictions")
async def get_predictions(
    category: Optional[str] = None,
    min_confidence: float = Query(default=0.0, ge=0.0, le=100.0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List predictions with optional filters."""
    predictions = get_seed_predictions()

    if category:
        predictions = [p for p in predictions if p.get("category", "").lower() == category.lower()]
    if min_confidence > 0:
        predictions = [p for p in predictions if p.get("confidence_score", 0) >= min_confidence]

    total = len(predictions)
    items = predictions[offset:offset + limit]

    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/api/predictions/{prediction_id}")
async def get_prediction(prediction_id: str):
    """Get a single prediction by ID."""
    predictions = get_seed_predictions()
    for pred in predictions:
        if pred["id"] == prediction_id:
            return pred
    raise HTTPException(status_code=404, detail="Prediction not found")


# ── Financials ──

@router.get("/api/financials")
async def get_financials(
    sector: Optional[str] = None,
    sort_by: str = Query(default="market_cap_inr", enum=["market_cap_inr", "debt_to_equity", "change_percent", "pe_ratio"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"]),
):
    """Get financial data for group companies."""
    financials = get_seed_financial_data()

    if sector:
        financials = [f for f in financials if f.get("sector", "").lower() == sector.lower()]

    reverse = sort_order == "desc"
    financials.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

    return {"items": financials, "total": len(financials)}


# ── Lobbying ──

@router.get("/api/lobbying")
async def get_lobbying(
    country: Optional[str] = None,
    year: Optional[int] = None,
    disclosure_type: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Get lobbying and political influence records."""
    records = get_seed_lobbying_records()

    if country:
        records = [r for r in records if r.get("country", "").lower() == country.lower()]
    if year:
        records = [r for r in records if r.get("year") == year]
    if disclosure_type:
        records = [r for r in records if disclosure_type.lower() in r.get("disclosure_type", "").lower()]

    total = len(records)
    items = records[offset:offset + limit]

    return {"items": items, "total": total, "limit": limit, "offset": offset}


# ── News / Intelligence Feed ──

@router.get("/api/news")
async def get_news(
    min_validation_score: float = Query(default=0.0, ge=0.0, le=1.0),
    source_tier: Optional[int] = Query(default=None, ge=1, le=3),
    tag: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Get validated news feed with filters."""
    articles = get_seed_news_articles()

    # Apply filters
    articles = [a for a in articles if a.get("validation_score", 0) >= min_validation_score]

    if source_tier:
        articles = [a for a in articles if a.get("source_tier") == source_tier]
    if tag:
        articles = [a for a in articles if a.get("tag", "").lower() == tag.lower()]
    if search:
        search_lower = search.lower()
        articles = [
            a for a in articles
            if search_lower in a.get("title", "").lower()
            or search_lower in a.get("content_snippet", "").lower()
        ]

    total = len(articles)
    items = articles[offset:offset + limit]

    return {"items": items, "total": total, "limit": limit, "offset": offset}


# ── Acquisitions ──

@router.get("/api/acquisitions")
async def get_acquisitions(
    sector: Optional[str] = None,
    status: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Get acquisition history and asset data."""
    records = get_seed_acquisitions()

    if sector:
        records = [r for r in records if r.get("sector", "").lower() == sector.lower()]
    if status:
        records = [r for r in records if r.get("status", "").lower() == status.lower()]
    if year:
        records = [r for r in records if r.get("year") == year]
    if search:
        search_lower = search.lower()
        records = [
            r for r in records
            if search_lower in r.get("company_acquired", "").lower()
            or search_lower in r.get("notes", "").lower()
        ]

    total = len(records)
    items = records[offset:offset + limit]

    return {"items": items, "total": total, "limit": limit, "offset": offset}


# ── Political Risk Indicator ──

@router.get("/api/risk-indicator")
async def get_risk_indicator():
    """Get current political risk indicator."""
    return get_seed_political_risk()


# ── Validation Endpoint ──

@router.post("/api/validate", response_model=ValidationResult)
async def validate_claim(request: ValidationRequest):
    """
    Validate a claim against multiple sources using the
    Multi-Source Verification Algorithm.
    """
    result = validation_engine.validate_claim(
        claim=request.claim,
        sources=request.sources,
    )

    # Log the validation decision
    audit_logger.log_validation(
        claim=request.claim,
        sources=request.sources,
        result=result,
    )

    return ValidationResult(
        validation_score=result["validation_score"],
        bias_risk_level=BiasRiskLevel(result["bias_risk_level"]),
        flags=result["flags"],
        cross_verification_status=result["cross_verification_status"],
        tier_1_corroboration=result["tier_1_corroboration"],
        contradiction_detected=result["contradiction_detected"],
    )


# ── Source Information ──

@router.get("/api/sources")
async def get_sources():
    """Get all registered sources with tier information."""
    return ValidationEngine.get_all_sources()


# ── Audit Trail ──

@router.get("/api/audit")
async def get_audit_trail(
    action: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Get audit trail entries."""
    entries = audit_logger.get_entries(action=action, limit=limit, offset=offset)
    summary = audit_logger.get_summary()
    return {"entries": entries, "summary": summary}


# ── Bias Detection Report ──

@router.get("/api/bias-report")
async def get_bias_report():
    """Get source reliability and bias detection report."""
    return bias_detector.get_source_reliability_report()
