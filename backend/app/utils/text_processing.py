"""
AGSPE Text Processing Utilities
NLP utilities for claim matching, keyword extraction, and text similarity.
"""
import re
import math
from typing import List, Dict, Tuple
from collections import Counter


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using simple TF-based approach."""
    # Common stop words to filter
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "this", "that",
        "these", "those", "i", "you", "he", "she", "it", "we", "they",
        "me", "him", "her", "us", "them", "my", "your", "his", "its",
        "our", "their", "not", "no", "nor", "so", "if", "then", "than",
        "too", "very", "just", "about", "above", "after", "again", "all",
        "also", "am", "any", "because", "before", "between", "both",
        "each", "few", "more", "most", "other", "out", "over", "own",
        "same", "some", "such", "up", "what", "when", "where", "which",
        "while", "who", "whom", "why", "how", "said", "says", "new",
    }

    # Tokenize and clean
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    words = [w for w in words if w not in stop_words]

    # Count frequencies
    word_counts = Counter(words)

    # Return top keywords
    keywords = [word for word, count in word_counts.most_common(max_keywords)]
    return keywords


def compute_text_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using TF vectors.
    Returns a value between 0.0 and 1.0.
    """
    # Tokenize
    words1 = re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower())
    words2 = re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower())

    if not words1 or not words2:
        return 0.0

    # Build term frequency vectors
    all_words = set(words1 + words2)
    tf1 = Counter(words1)
    tf2 = Counter(words2)

    # Compute cosine similarity
    dot_product = sum(tf1[word] * tf2[word] for word in all_words)
    magnitude1 = math.sqrt(sum(tf1[word] ** 2 for word in all_words))
    magnitude2 = math.sqrt(sum(tf2[word] ** 2 for word in all_words))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def detect_pro_group_language(text: str) -> Dict:
    """
    Detect pro-group or promotional language patterns in text.
    Returns a dict with detection results and confidence.
    """
    pro_group_phrases = [
        "world-class", "game-changer", "revolutionary", "unprecedented",
        "transforming india", "nation-building", "visionary leadership",
        "milestone achievement", "historic", "trailblazing", "pioneering",
        "commitment to excellence", "driving growth", "empowering millions",
        "benchmark", "setting new standards", "towering achievement",
    ]

    negative_phrases = [
        "controversial", "alleged", "under investigation", "scrutiny",
        "irregularities", "conflict of interest", "overvalued", "debt-laden",
        "governance concerns", "regulatory action", "penalty", "fine",
    ]

    text_lower = text.lower()

    pro_count = sum(1 for phrase in pro_group_phrases if phrase in text_lower)
    neg_count = sum(1 for phrase in negative_phrases if phrase in text_lower)

    total_checks = len(pro_group_phrases) + len(negative_phrases)
    pro_ratio = pro_count / max(len(pro_group_phrases), 1)
    neg_ratio = neg_count / max(len(negative_phrases), 1)

    bias_score = pro_ratio - neg_ratio  # Positive = pro-group bias

    return {
        "pro_group_indicators": pro_count,
        "negative_indicators": neg_count,
        "bias_score": round(bias_score, 3),
        "is_likely_promotional": pro_count >= 3 and neg_count == 0,
        "detected_pro_phrases": [p for p in pro_group_phrases if p in text_lower],
        "detected_neg_phrases": [p for p in negative_phrases if p in text_lower],
    }


def normalize_company_name(name: str) -> str:
    """Normalize a company name for matching purposes."""
    # Remove common suffixes
    suffixes = ["Ltd", "Limited", "Pvt", "Private", "Inc", "Corp", "Corporation", "& Co", "LLC"]
    normalized = name.strip()
    for suffix in suffixes:
        normalized = re.sub(rf'\b{suffix}\.?\b', '', normalized, flags=re.IGNORECASE)
    return normalized.strip()


def extract_entities(text: str) -> List[str]:
    """Extract potential entity/company names from text using simple pattern matching."""
    # Look for capitalized multi-word phrases that might be company names
    pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
    matches = re.findall(pattern, text)

    # Filter out common non-entity phrases
    non_entities = {
        "The Hindu", "New Delhi", "Mumbai Maharashtra", "New York",
        "United States", "Prime Minister", "Finance Minister",
    }

    return [m for m in matches if m not in non_entities]
