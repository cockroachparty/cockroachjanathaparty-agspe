# AGSPE Data Dictionary
**Repository:** https://github.com/cockroachparty/cockroachjanathaparty-agspe

## Overview
This document describes all data entities, their fields, and relationships
within the Adani Group Strategic Prediction Engine.

---

## Entity: NewsArticle

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique article identifier |
| title | String | Article headline |
| source | String | Publication source name |
| source_tier | Integer | Trust tier (1=High, 2=Medium, 3=Low) |
| url | String | Original article URL |
| published_at | DateTime | Publication timestamp |
| content_snippet | String | First 300 characters of content |
| validation_score | Float | Validation score (0.0-1.0) |
| bias_risk_level | String | Bias risk (Low/Medium/High) |
| tag | String | Verification tag (Verified/Unverified/Requires Verification/Pro-Group) |
| related_companies | Array[String] | Related Adani Group companies |
| keywords | Array[String] | Extracted keywords |

---

## Entity: Prediction

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique prediction identifier |
| likely_action | String | Predicted business move |
| category | String | Category (Infrastructure/Green Energy/M&A/Defense/Digital) |
| timeline_start | String | Predicted start quarter (e.g., "Q3 2026") |
| timeline_end | String | Predicted end quarter (e.g., "Q1 2027") |
| confidence_score | Float | Confidence percentage (0-100) |
| supporting_evidence | Array[String] | List of evidence supporting prediction |
| risk_factors | Array[String] | List of identified risk factors |
| financial_signal | Float | Financial indicators signal (0.0-1.0) |
| political_alignment | Float | Political alignment score (0.0-1.0) |
| pattern_match | String | Matched acquisition/policy pattern |
| data_sources | Array[String] | Sources used for prediction |
| validation_score | Float | Overall data validation score (0.0-1.0) |

---

## Entity: FinancialData

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique record identifier |
| company_name | String | Full company name |
| ticker | String | Stock exchange ticker symbol |
| market_cap_inr | Float | Market capitalization in INR (Crore) |
| market_cap_usd | Float | Market capitalization in USD (Million) |
| debt_to_equity | Float | Debt-to-equity ratio |
| stock_price | Float | Current stock price in INR |
| stock_price_usd | Float | Stock price in USD |
| volume | Integer | Trading volume |
| sector | String | Business sector |
| change_percent | Float | Price change percentage |
| pe_ratio | Float | Price-to-earnings ratio |

---

## Entity: LobbyingRecord

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique record identifier |
| entity | String | Lobbying entity name |
| country | String | Country of lobbying activity |
| amount_inr | Float | Amount in INR |
| amount_usd | Float | Amount in USD |
| quarter | String | Fiscal quarter (Q1-Q4) |
| year | Integer | Fiscal year |
| law_firm | String | Engaged law firm name |
| disclosure_type | String | Type of disclosure (Lobbying/Electoral Bond/Consultancy) |
| source_url | String | Source document URL |
| description | String | Activity description |

---

## Entity: AcquisitionRecord

| Field | Type | Description |
|-------|------|-------------|
| id | String | Unique record identifier |
| company_acquired | String | Name of acquired company/asset |
| acquirer | String | Acquiring Adani Group entity |
| year | Integer | Year of acquisition |
| valuation_inr | Float | Deal valuation in INR (Crore) |
| valuation_usd | Float | Deal valuation in USD (Million) |
| status | String | Status (Active/Integrated/Demerged/Pending Litigation) |
| sector | String | Business sector |
| source_url | String | Source document URL |
| notes | String | Additional notes |

---

## Entity: ValidationResult

| Field | Type | Description |
|-------|------|-------------|
| validation_score | Float | Overall validation score (0.0-1.0) |
| bias_risk_level | String | Bias risk level (Low/Medium/High) |
| flags | Array[String] | List of validation flags |
| cross_verification_status | String | Cross-verification result description |
| tier_1_corroboration | Boolean | Whether Tier 1 source confirmed the claim |
| contradiction_detected | Boolean | Whether Tier 1 sources contradict |

---

## Source Trust Tiers

### Tier 1 (Weight: 0.9) - International / Highly Credible
- Reuters, AP News, BBC, Al Jazeera, OCCRP, Bloomberg, Financial Times

### Tier 2 (Weight: 0.7) - Independent Indian Media
- The Hindu, Scroll.in, The Wire, Business Standard

### Tier 3 (Weight: 0.3) - Requires Verification
- NDTV, Times Now, Republic TV, Zee News, Adani Group PR

---

## Validation Rules

| Rule | Condition | Effect |
|------|-----------|--------|
| Cross-Verification | Tier 3 claim without Tier 1 source within 24h | Score capped at 0.3, flag raised |
| Contradiction Detection | Tier 1 sources conflict | Manual review required, confidence paused |
| Pro-Group Cap | Only pro-group sources present | Score capped at 0.2 |
| Single Source Penalty | Only one source | Score reduced by 20% |
| High Risk | Score < 0.4 | bias_risk_level = "High" |
