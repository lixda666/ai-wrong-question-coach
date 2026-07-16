#!/usr/bin/env python3
"""
Progress Tracker

Computes learning progress metrics from a mistake collection over time.
Generates trend data suitable for visualization (line charts, before/after comparisons).

Usage:
    python progress_tracker.py trend --collection collection.json --days 30
    python progress_tracker.py compare --collection collection.json --baseline 2026-07-01 --current 2026-08-01
    python progress_tracker.py summary --collection collection.json --period weekly
    python progress_tracker.py forecast --collection collection.json --target-date 2026-12-01
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path


# ── Helpers ────────────────────────────────────────────────────────────────


def load_collection(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(date_str: str) -> datetime:
    """Flexible date parser supporting ISO and simple formats."""
    formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:19], fmt)
        except ValueError:
            continue
    return datetime.now()


# ── Trend Analysis ─────────────────────────────────────────────────────────


def compute_daily_activity(mistakes: list[dict], days: int = 30) -> dict:
    """Compute daily activity: mistakes added, reviews done per day."""
    now = datetime.now()
    start_date = now - timedelta(days=days)

    daily = defaultdict(lambda: {"added": 0, "reviewed": 0, "mastered": 0})
    for m in mistakes:
        added_date = m.get("added_date", "")
        if added_date:
            ad = parse_date(added_date)
            if ad >= start_date:
                day_key = ad.strftime("%Y-%m-%d")
                daily[day_key]["added"] += 1

        # Count mastered items
        if m.get("mastered"):
            # Use added_date as proxy for when it was resolved
            if added_date:
                ad = parse_date(added_date)
                if ad >= start_date:
                    daily[ad.strftime("%Y-%m-%d")]["mastered"] += 1

    # Fill in missing days
    result = []
    for i in range(days + 1):
        day = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        result.append({
            "date": day,
            "added": daily.get(day, {}).get("added", 0),
            "reviewed": daily.get(day, {}).get("reviewed", 0),
            "mastered": daily.get(day, {}).get("mastered", 0),
        })

    return {"daily_activity": result, "period_days": days}


def compute_error_trends(mistakes: list[dict], days: int = 30) -> dict:
    """Analyze how error types change over time."""
    now = datetime.now()
    start_date = now - timedelta(days=days)
    mid_date = now - timedelta(days=days // 2)

    first_half = []
    second_half = []

    for m in mistakes:
        added_date = m.get("added_date", "")
        if not added_date:
            continue
        ad = parse_date(added_date)
        if ad < start_date:
            continue
        if ad < mid_date:
            first_half.append(m)
        else:
            second_half.append(m)

    def count_errors(items):
        counts = defaultdict(int)
        for m in items:
            for et in m.get("error_types", []):
                counts[et] += 1
        return dict(counts)

    first_counts = count_errors(first_half)
    second_counts = count_errors(second_half)

    # Compute changes
    all_types = set(list(first_counts.keys()) + list(second_counts.keys()))
    trends = {}
    for et in all_types:
        f = first_counts.get(et, 0)
        s = second_counts.get(et, 0)
        if f > 0:
            change_pct = round((s - f) / f * 100, 1)
        else:
            change_pct = 100 if s > 0 else 0
        trends[et] = {
            "first_half": f,
            "second_half": s,
            "change_pct": change_pct,
            "direction": "improving" if change_pct < -10 else "worsening" if change_pct > 10 else "stable",
        }

    return {"error_trends": trends, "period_days": days}


def compute_subject_balance(mistakes: list[dict]) -> dict:
    """Analyze subject distribution and coverage."""
    subjects = defaultdict(lambda: {"total": 0, "mastered": 0, "knowledge_points": set()})
    for m in mistakes:
        subj = m.get("subject", "Unknown")
        subjects[subj]["total"] += 1
        if m.get("mastered"):
            subjects[subj]["mastered"] += 1
        for kp in m.get("knowledge_points", []):
            subjects[subj]["knowledge_points"].add(kp)

    result = {}
    for subj, data in sorted(subjects.items()):
        result[subj] = {
            "total": data["total"],
            "mastered": data["mastered"],
            "mastery_rate": round(data["mastered"] / data["total"] * 100, 1) if data["total"] else 0,
            "unique_kps": len(data["knowledge_points"]),
            "coverage": len(data["knowledge_points"]),
        }

    return {"subject_balance": result}


# ── Period Comparison ──────────────────────────────────────────────────────


def compare_periods(mistakes: list[dict], baseline_str: str, current_str: str) -> dict:
    """Compare mistake patterns between two time periods."""
    baseline_end = parse_date(baseline_str)
    current_end = parse_date(current_str)

    baseline_items = [m for m in mistakes if parse_date(m.get("added_date", "")) <= baseline_end]
    current_items = [m for m in mistakes if parse_date(m.get("added_date", "")) <= current_end]
    new_items = [m for m in current_items if m not in baseline_items]

    def summary(items):
        kps = defaultdict(int)
        errors = defaultdict(int)
        for m in items:
            for kp in m.get("knowledge_points", []):
                kps[kp] += 1
            for et in m.get("error_types", []):
                errors[et] += 1
        return {
            "total": len(items),
            "mastered": sum(1 for m in items if m.get("mastered")),
            "top_kps": dict(sorted(kps.items(), key=lambda x: -x[1])[:5]),
            "top_errors": dict(sorted(errors.items(), key=lambda x: -x[1])),
            "avg_difficulty": sum({"easy": 1, "medium": 2, "hard": 3}.get(m.get("difficulty", "medium"), 2) for m in items) / max(len(items), 1),
        }

    baseline_summary = summary(baseline_items)
    current_summary = summary(current_items)
    new_summary = summary(new_items)

    # Trend: are mistakes decreasing?
    if len(baseline_items) > 0:
        mastery_rate_then = baseline_summary["mastered"] / baseline_summary["total"]
        mastery_rate_now = current_summary["mastered"] / max(current_summary["total"], 1)
        mastery_change = round((mastery_rate_now - mastery_rate_then) * 100, 1)
    else:
        mastery_change = 0

    return {
        "baseline_period": baseline_str,
        "current_period": current_str,
        "baseline": baseline_summary,
        "current": current_summary,
        "new_items": new_summary,
        "mastery_rate_change_pct": mastery_change,
        "total_growth": current_summary["total"] - baseline_summary["total"],
    }


# ── Weekly/Monthly Summary ─────────────────────────────────────────────────


def generate_periodic_summary(mistakes: list[dict], period: str = "weekly") -> dict:
    """Generate a weekly or monthly summary of activity."""
    if not mistakes:
        return {"summary": "No mistakes found"}

    # Group by period
    periods = defaultdict(list)
    for m in mistakes:
        added_date = m.get("added_date", "")
        if not added_date:
            continue
        ad = parse_date(added_date)
        if period == "weekly":
            # ISO week: Year-WW
            week_key = ad.strftime("%Y-W%W")
            periods[week_key].append(m)
        elif period == "monthly":
            month_key = ad.strftime("%Y-%m")
            periods[month_key].append(m)
        else:
            day_key = ad.strftime("%Y-%m-%d")
            periods[day_key].append(m)

    summary_periods = {}
    for period_key, items in sorted(periods.items()):
        kps = defaultdict(int)
        errors = defaultdict(int)
        for m in items:
            for kp in m.get("knowledge_points", []):
                kps[kp] += 1
            for et in m.get("error_types", []):
                errors[et] += 1

        summary_periods[period_key] = {
            "total": len(items),
            "mastered": sum(1 for m in items if m.get("mastered")),
            "new_added": len([m for m in items if m.get("added_date", "")]),
            "top_kp_weakness": max(kps, key=kps.get) if kps else "none",
            "primary_error_type": max(errors, key=errors.get) if errors else "none",
        }

    return {"period_type": period, "periods": summary_periods}


# ── Forecast ───────────────────────────────────────────────────────────────


def forecast_mastery(mistakes: list[dict], target_date_str: str) -> dict:
    """Forecast when remaining items will be mastered based on current pace."""
    target_date = parse_date(target_date_str)
    now = datetime.now()

    total = len(mistakes)
    mastered = sum(1 for m in mistakes if m.get("mastered"))
    remaining = total - mastered

    if total == 0:
        return {"message": "No mistakes in collection"}

    # Calculate mastery rate per day
    earliest = None
    for m in mistakes:
        if m.get("added_date"):
            ad = parse_date(m["added_date"])
            if earliest is None or ad < earliest:
                earliest = ad

    if earliest is None:
        return {"message": "No dates available for forecasting"}

    days_active = max((now - earliest).days, 1)
    mastery_rate_per_day = mastered / days_active if days_active > 0 else 0

    if mastery_rate_per_day <= 0:
        days_to_complete = remaining * 30  # conservative estimate: one mastered per month
    else:
        days_to_complete = remaining / mastery_rate_per_day

    completion_date = (now + timedelta(days=days_to_complete)).strftime("%Y-%m-%d")

    # Days between now and target
    days_until_target = max((target_date - now).days, 1)
    projected_mastered_by_target = min(mastered + mastery_rate_per_day * days_until_target, total)
    projected_rate_by_target = round(projected_mastered_by_target / total * 100, 1)

    return {
        "current_total": total,
        "current_mastered": mastered,
        "current_mastery_rate": f"{round(mastered / total * 100, 1)}%" if total else "0%",
        "remaining": remaining,
        "mastery_rate_per_day": round(mastery_rate_per_day, 3),
        "estimated_completion_date": completion_date,
        "target_date": target_date_str,
        "days_until_target": days_until_target,
        "projected_mastery_by_target": round(projected_mastered_by_target),
        "projected_mastery_rate_by_target": f"{projected_rate_by_target}%",
        "on_track": projected_mastered_by_target >= total,
    }


# ── CLI ────────────────────────────────────────────────────────────────────


def print_usage():
    print("Progress Tracker")
    print()
    print("Commands:")
    print("  trend    --collection FILE [--days N]     Daily activity trend")
    print("  compare  --collection FILE --baseline DATE --current DATE")
    print("  summary  --collection FILE --period weekly|monthly")
    print("  forecast --collection FILE --target-date DATE")


def get_arg(args: list[str], key: str) -> str | None:
    for i, a in enumerate(args):
        if a == key and i + 1 < len(args):
            return args[i + 1]
    return None


def main():
    args = sys.argv[1:]
    if not args:
        print_usage()
        sys.exit(0)

    command = args[0]

    if command == "trend":
        coll_path = get_arg(args, "--collection")
        days = int(get_arg(args, "--days") or "30")
        if not coll_path:
            print("Error: --collection is required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        trends = {}
        trends.update(compute_daily_activity(collection["mistakes"], days))
        trends.update(compute_error_trends(collection["mistakes"], days))
        print(json.dumps(trends, ensure_ascii=False, indent=2))

    elif command == "compare":
        coll_path = get_arg(args, "--collection")
        baseline = get_arg(args, "--baseline")
        current = get_arg(args, "--current")
        if not all([coll_path, baseline, current]):
            print("Error: --collection, --baseline, --current are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        result = compare_periods(collection["mistakes"], baseline, current)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "summary":
        coll_path = get_arg(args, "--collection")
        period = get_arg(args, "--period") or "weekly"
        if not coll_path:
            print("Error: --collection is required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        result = generate_periodic_summary(collection["mistakes"], period)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "forecast":
        coll_path = get_arg(args, "--collection")
        target = get_arg(args, "--target-date")
        if not all([coll_path, target]):
            print("Error: --collection and --target-date are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        result = forecast_mastery(collection["mistakes"], target)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command in ("help", "--help", "-h"):
        print_usage()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
