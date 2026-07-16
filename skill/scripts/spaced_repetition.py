#!/usr/bin/env python3
"""
Spaced Repetition Engine - Hybrid Ebbinghaus + SM-2 Algorithm

This module computes optimal review schedules for wrong questions using a
hybrid model that combines Ebbinghaus forgetting curve intervals with SM-2
difficulty adjustment.

Ebbinghaus base intervals: 1, 2, 4, 7, 15, 30, 60, 120 (days)
SM-2: adjusts ease factor based on recall quality (0-5)

Call from command line:
    python spaced_repetition.py --input data.json --output schedule.json
"""

import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────────

# Ebbinghaus base intervals in days
EBBINGHAUS_INTERVALS = [1, 2, 4, 7, 15, 30, 60, 120]

# SM-2 defaults
DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
EASE_BONUS = 0.15
EASE_PENALTY = 0.20

# Target retention rate: when average recall drops below this,
# the question needs re-review
TARGET_RETENTION = 0.85

# ── Core Functions ─────────────────────────────────────────────────────────


def compute_next_interval(
    current_interval_days: int,
    recall_quality: int,
    ease_factor: float,
    review_count: int,
) -> tuple[int, float]:
    """
    Compute the next review interval using hybrid Ebbinghaus + SM-2.

    Args:
        current_interval_days: Days since last review (0 for first review)
        recall_quality: 0-5 rating (0=complete blackout, 5=perfect recall)
        ease_factor: Current SM-2 ease factor
        review_count: Number of times this item has been reviewed

    Returns:
        (next_interval_days, new_ease_factor)
    """
    # Adjust ease factor based on recall quality
    if recall_quality >= 4:
        new_ef = ease_factor + EASE_BONUS
    elif recall_quality >= 2:
        new_ef = ease_factor
    else:
        new_ef = ease_factor - EASE_PENALTY
        # Reset interval on poor recall
        return EBBINGHAUS_INTERVALS[0], max(new_ef, MIN_EASE_FACTOR)

    new_ef = max(new_ef, MIN_EASE_FACTOR)

    # For first review, use Ebbinghaus base
    if review_count == 0:
        return EBBINGHAUS_INTERVALS[0], new_ef

    # For subsequent reviews, scale Ebbinghaus by ease factor
    ebbinghaus_idx = min(review_count, len(EBBINGHAUS_INTERVALS) - 1)
    base_interval = EBBINGHAUS_INTERVALS[ebbinghaus_idx]

    # SM-2 formula: interval * ease_factor
    next_interval = max(1, round(base_interval * new_ef))

    return next_interval, new_ef


def compute_forgetting_retention(days_since_review: int, ease_factor: float) -> float:
    """
    Estimate retention probability using exponential decay with ease factor adjustment.

    R = e^(-t / (S * EF))
    where t = days since review, S = stability constant, EF = ease factor
    """
    STABILITY = 30  # base stability in days - after 30 days, 36.8% retention at EF=1
    adjusted_stability = STABILITY * ease_factor
    retention = math.exp(-days_since_review / adjusted_stability) if adjusted_stability > 0 else 0.0
    return round(retention, 4)


def generate_review_schedule(
    mistakes: list[dict],
    start_date: str,
    total_items: int,
) -> dict:
    """
    Generate a complete review schedule for a set of mistakes.

    Args:
        mistakes: List of mistake dicts with keys:
            - id: unique identifier
            - difficulty: 'easy' | 'medium' | 'hard'
            - added_date: ISO date string
        start_date: ISO date string for schedule start
        total_items: Total items in the full mistake set

    Returns:
        Schedule dict with daily plan, retention curves, and statistics
    """
    difficulty_ef_map = {"easy": 2.8, "medium": 2.5, "hard": 2.2}

    schedule = {
        "generated_at": datetime.now().isoformat(),
        "start_date": start_date,
        "total_items": total_items,
        "daily_plan": {},
        "retention_curve": [],
        "statistics": {},
    }

    start = datetime.fromisoformat(start_date)

    # Generate daily plan for 120 days
    daily_items = {}
    all_retention_points = []

    for item in mistakes:
        ef = difficulty_ef_map.get(item.get("difficulty", "medium"), DEFAULT_EASE_FACTOR)
        review_count = 0
        current_date = start

        while review_count < min(len(EBBINGHAUS_INTERVALS), 5):  # Plan 5 review cycles
            interval, ef = compute_next_interval(
                current_interval_days=EBBINGHAUS_INTERVALS[min(review_count, len(EBBINGHAUS_INTERVALS) - 1)],
                recall_quality=4,  # Assume target quality for planning
                ease_factor=ef,
                review_count=review_count,
            )
            current_date += timedelta(days=interval)
            date_str = current_date.strftime("%Y-%m-%d")

            if date_str not in daily_items:
                daily_items[date_str] = []
            daily_items[date_str].append(item["id"])
            review_count += 1

    # Sort daily plan by date
    schedule["daily_plan"] = dict(sorted(daily_items.items()))

    # Generate retention curve (daily projection for 60 days)
    for day in range(0, 61):
        avg_retention = compute_forgetting_retention(day, DEFAULT_EASE_FACTOR)
        schedule["retention_curve"].append({"day": day, "retention": avg_retention})

    # Statistics
    interval_days = []
    for item in mistakes:
        ef = difficulty_ef_map.get(item.get("difficulty", "medium"), DEFAULT_EASE_FACTOR)
        review_count = 0
        current_date = start
        while review_count < 5:
            interval, ef = compute_next_interval(
                EBBINGHAUS_INTERVALS[min(review_count, len(EBBINGHAUS_INTERVALS) - 1)],
                4, ef, review_count,
            )
            interval_days.append(interval)
            review_count += 1

    if interval_days:
        schedule["statistics"] = {
            "avg_review_interval_days": round(sum(interval_days) / len(interval_days), 1),
            "total_review_sessions": len(schedule["daily_plan"]),
            "coverage_start": start.strftime("%Y-%m-%d"),
            "coverage_end": max(schedule["daily_plan"].keys()) if schedule["daily_plan"] else start.strftime("%Y-%m-%d"),
            "estimated_daily_minutes": round(total_items * 0.5, 1),  # ~30s per review item
        }

    return schedule


# ── CLI Entry Point ────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 3:
        print("Usage: python spaced_repetition.py --input <mistakes.json> --output <schedule.json>")
        print("       python spaced_repetition.py --help")
        print()
        print("Input JSON format:")
        print(json.dumps({
            "mistakes": [
                {"id": "Q001", "difficulty": "medium", "added_date": "2026-07-16"},
            ],
            "start_date": "2026-07-16",
            "total_items": 10,
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    args = sys.argv[1:]
    input_path = None
    output_path = None

    i = 0
    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        else:
            i += 1

    if not input_path or not output_path:
        print("Error: --input and --output are required", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schedule = generate_review_schedule(
        mistakes=data.get("mistakes", []),
        start_date=data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
        total_items=data.get("total_items", len(data.get("mistakes", []))),
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)

    print(f"Schedule generated: {output_path}")
    print(f"  Review sessions: {schedule['statistics'].get('total_review_sessions', 0)}")
    print(f"  Coverage: {schedule['statistics'].get('coverage_start')} -> {schedule['statistics'].get('coverage_end')}")


if __name__ == "__main__":
    main()
