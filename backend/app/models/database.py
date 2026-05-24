"""
AGSPE Database Models - SQLAlchemy ORM models for PostgreSQL.
"""
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text, Boolean,
    JSON, Enum as SAEnum, Index, create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class NewsArticleDB(Base):
    """News articles with validation metadata."""
    __tablename__ = "news_articles"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    source_tier = Column(Integer, nullable=False)
    url = Column(String, default="")
    published_at = Column(DateTime, default=datetime.utcnow)
    content_snippet = Column(Text, default="")
    validation_score = Column(Float, default=0.0)
    bias_risk_level = Column(String, default="High")
    tag = Column(String, default="Unverified")
    related_companies = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_news_validation", "validation_score"),
        Index("idx_news_source_tier", "source_tier"),
        Index("idx_news_published", "published_at"),
    )


class PredictionDB(Base):
    """Generated predictions with confidence scores."""
    __tablename__ = "predictions"

    id = Column(String, primary_key=True)
    likely_action = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    timeline_start = Column(String, nullable=False)
    timeline_end = Column(String, nullable=False)
    confidence_score = Column(Float, default=0.0)
    supporting_evidence = Column(JSON, default=list)
    risk_factors = Column(JSON, default=list)
    financial_signal = Column(Float, default=0.0)
    political_alignment = Column(Float, default=0.0)
    pattern_match = Column(String, default="")
    data_sources = Column(JSON, default=list)
    validation_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_pred_confidence", "confidence_score"),
        Index("idx_pred_category", "category"),
    )


class FinancialDataDB(Base):
    """Financial data for Adani Group companies."""
    __tablename__ = "financial_data"

    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False, index=True)
    ticker = Column(String, nullable=False)
    market_cap_inr = Column(Float, default=0.0)
    market_cap_usd = Column(Float, default=0.0)
    debt_to_equity = Column(Float, default=0.0)
    stock_price = Column(Float, default=0.0)
    stock_price_usd = Column(Float, default=0.0)
    volume = Column(Integer, default=0)
    sector = Column(String, default="")
    change_percent = Column(Float, default=0.0)
    pe_ratio = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_fin_sector", "sector"),
        Index("idx_fin_market_cap", "market_cap_inr"),
    )


class LobbyingRecordDB(Base):
    """Lobbying and political influence records."""
    __tablename__ = "lobbying_records"

    id = Column(String, primary_key=True)
    entity = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    amount_inr = Column(Float, default=0.0)
    amount_usd = Column(Float, default=0.0)
    quarter = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    law_firm = Column(String, default="")
    disclosure_type = Column(String, nullable=False)
    source_url = Column(String, default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_lobby_country", "country"),
        Index("idx_lobby_year", "year"),
    )


class AcquisitionRecordDB(Base):
    """Acquisition history and asset tracking."""
    __tablename__ = "acquisition_records"

    id = Column(String, primary_key=True)
    company_acquired = Column(String, nullable=False, index=True)
    acquirer = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    valuation_inr = Column(Float, default=0.0)
    valuation_usd = Column(Float, default=0.0)
    status = Column(String, default="Active")
    sector = Column(String, default="")
    source_url = Column(String, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_acq_sector", "sector"),
        Index("idx_acq_year", "year"),
    )


class ValidationAuditDB(Base):
    """Audit trail for all validation decisions."""
    __tablename__ = "validation_audit"

    id = Column(String, primary_key=True)
    action = Column(String, nullable=False, index=True)
    details = Column(JSON, default=dict)
    user_id = Column(String, default="system")
    session_id = Column(String, default="default")
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audit_action", "action"),
        Index("idx_audit_timestamp", "timestamp"),
    )


def init_db(database_url: str = "sqlite:///agspe.db"):
    """Initialize the database and create tables."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session."""
    Session = sessionmaker(bind=engine)
    return Session()
