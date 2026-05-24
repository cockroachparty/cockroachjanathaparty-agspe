# AGSPE - Adani Group Strategic Prediction Engine
**Repository:** https://github.com/cockroachparty/cockroachjanathaparty-agspe

## Overview
The AGSPE Prediction Model is a hybrid logic engine that combines statistical
trend analysis with heuristic rules to generate probabilistic predictions
about the Adani Group's future business moves.

---

## Model Architecture

### Three-Signal System

The model generates predictions based on three weighted signals:

1. **Financial Indicators** (Weight: 35%)
2. **Political Alignment** (Weight: 35%)
3. **Pattern Recognition** (Weight: 30%)

### Signal 1: Financial Indicators

Four sub-signals are calculated:

| Sub-Signal | Weight | Calculation |
|------------|--------|-------------|
| Debt Signal | 25% | `1 - (weighted_dte / 5.0)`, clamped to [0,1] |
| Capex Signal | 30% | `min(1.0, total_capex / 200000)` |
| Volatility Signal | 20% | `1 - (avg_volatility / 60.0)`, clamped to [0,1] |
| Growth Signal | 25% | `min(1.0, avg_growth / 0.3)`, clamped to [0,1] |

- **Debt Signal**: Lower debt-to-equity = stronger signal (inverse)
- **Capex Signal**: Higher capex commitment = expansion intent
- **Volatility Signal**: Lower volatility = more stable = higher confidence
- **Growth Signal**: Higher revenue growth = stronger momentum

### Signal 2: Political Alignment

Score based on proximity to government policy announcements:

```
alignment = Σ(relevance × tier_weight × impact) / Σ(relevance × tier_weight)
```

Where:
- `relevance`: How relevant the event is to Adani Group (0-1)
- `tier_weight`: Source credibility weight (1.0/0.7/0.3)
- `impact`: Event's positive/negative impact on group (0-1)

### Signal 3: Pattern Recognition

Known acquisition and policy correlation patterns:

#### Standard Acquisition Cycle
Fragmented Sector → Large Acquisition → Consolidation → Listing/Demerger
- Typical Duration: 18 months
- Base Confidence: 70%

#### Green Energy Expansion
Gov Target → Policy Incentives → Capacity Announcement → JV Formation → Commissioning
- Typical Duration: 24 months
- Base Confidence: 75%

#### Port & Infrastructure Play
Gov Infrastructure Push → Bid Preparation → Concession Win → Expansion
- Typical Duration: 12 months
- Base Confidence: 80%

#### Distressed Asset Acquisition
NCLT Proceedings → Valuation → Bid → Creditor Approval → Takeover
- Typical Duration: 15 months
- Base Confidence: 65%

---

## Policy Correlations

| Trigger | Predicted Action | Base Probability |
|---------|-----------------|------------------|
| BJP infrastructure push | Adani port/airport bid win | 82% |
| Renewable target raised | Adani Green expansion/JV | 78% |
| Defense procurement policy | Adani Defense contract | 65% |
| Housing/infra policy boost | Cement capacity expansion | 72% |

---

## Confidence Score Calculation

```
confidence = (
    financial_signal × 0.35 +
    political_alignment × 0.35 +
    pattern_confidence × 0.30
) ± random_variation(±5%)
```

The small random variation simulates market uncertainty and prevents
over-fitting to exact values.

---

## Timeline Generation

Timeline confidence intervals are based on signal strength:

- **Strong signals** (combined > 0.7): Shorter timeline (3-6 months)
- **Moderate signals** (0.4-0.7): Medium timeline (6-12 months)
- **Weak signals** (< 0.4): Longer timeline (9-18 months)

Output format: Quarter notation (e.g., "Q3 2026 - Q1 2027")

---

## Validation Integration

Predictions are filtered through the Validation Engine:

1. Only data with `validation_score >= 0.4` enters the model
2. Tier 3-only claims are excluded from prediction input
3. Contradicted claims trigger confidence reduction
4. The prediction's `validation_score` reflects the average data quality

---

## Risk Factor Identification

Risk factors are generated based on financial and political signals:

| Condition | Risk Factor |
|-----------|-------------|
| debt_signal < 0.4 | "High debt-to-equity ratio across group companies" |
| volatility_signal < 0.4 | "Elevated stock price volatility" |
| political_alignment < 0.4 | "Weakening political alignment score" |
| political_alignment > 0.8 | "Over-reliance on political connections - regulatory risk" |
| Always | "Regulatory scrutiny risk (SEBI/Hindenburg aftermath)" |
| Always | "Global commodity price fluctuation risk" |
| Always | "Currency risk (INR depreciation impact on USD debt)" |

---

## Model Limitations

1. **Historical Bias**: Patterns are based on historical behavior which may not repeat
2. **Data Availability**: Only publicly available data is used
3. **Black Swan Events**: Cannot predict unforeseen regulatory or market shocks
4. **Political Volatility**: Rapid political changes may invalidate alignment scores
5. **Confirmation Bias Risk**: Pattern matching may over-fit to known Adani strategies

---

## Backtesting Framework

Weekly validation workflow:
1. Run predictions for current week
2. Compare against actual outcomes after 3 months
3. Calculate accuracy: predictions_within_confidence_interval / total_predictions
4. Adjust base probabilities if accuracy drops below 60%
5. Generate report in `/docs/reports/`

---

## Disclaimer

This model is for informational and research purposes only.
It does not constitute financial advice, investment recommendations,
or insider information. All data is derived from publicly available sources.
