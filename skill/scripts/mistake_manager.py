#!/usr/bin/env python3
"""
Mistake Collection Manager

Provides CRUD operations for a persistent mistake collection stored as JSON.
Supports add, edit, delete, search, filter, and import from CSV/Markdown.

Usage:
    python mistake_manager.py init --output collection.json
    python mistake_manager.py add --collection collection.json --mistake '{"question":"...","subject":"Math"}'
    python mistake_manager.py list --collection collection.json
    python mistake_manager.py search --collection collection.json --query "quadratic"
    python mistake_manager.py filter --collection collection.json --subject Math --error-type ERR_CALC
    python mistake_manager.py edit --collection collection.json --id Q003 --field question --value "..."
    python mistake_manager.py delete --collection collection.json --id Q003
    python mistake_manager.py import --collection collection.json --source mistakes.csv --format csv
    python mistake_manager.py stats --collection collection.json
"""

import json
import sys
import csv
import re
from datetime import datetime
from pathlib import Path


# ── Schema ─────────────────────────────────────────────────────────────────

MISTAKE_SCHEMA = {
    "id": "",
    "question": "",
    "subject": "",
    "stage": "",
    "student_answer": "",
    "correct_answer": "",
    "difficulty": "medium",
    "knowledge_points": [],
    "error_types": [],
    "analysis": "",
    "variants": [],
    "added_date": "",
    "last_reviewed": None,
    "review_count": 0,
    "mastered": False,
    "tags": [],
}

SUBJECTS = ["Math", "Physics", "Chemistry", "Chinese", "English", "Biology", "Geography", "History", "Politics"]
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
ERROR_TYPES = ["ERR_CONCEPT", "ERR_CALC", "ERR_READ", "ERR_METHOD", "ERR_GAP", "ERR_FORMAT", "ERR_PSYCH"]


# ── Collection I/O ─────────────────────────────────────────────────────────


def load_collection(path: str) -> dict:
    """Load mistake collection from JSON file, create if not exists."""
    p = Path(path)
    if not p.exists():
        return {"version": 1, "created_at": datetime.now().isoformat(), "mistakes": [], "id_counter": 0}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_collection(collection: dict, path: str):
    """Save mistake collection to JSON file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)


def generate_id(collection: dict) -> str:
    """Generate next sequential ID: Q001, Q002, etc."""
    counter = collection.get("id_counter", 0) + 1
    collection["id_counter"] = counter
    return f"Q{counter:03d}"


# ── CRUD Operations ────────────────────────────────────────────────────────


def add_mistake(collection: dict, data: dict) -> dict:
    """Add a single mistake to the collection."""
    mistake = dict(MISTAKE_SCHEMA)  # copy schema defaults
    mistake.update({k: v for k, v in data.items() if k in MISTAKE_SCHEMA})
    mistake["id"] = generate_id(collection)
    mistake["added_date"] = mistake.get("added_date") or datetime.now().strftime("%Y-%m-%d")
    if isinstance(mistake["knowledge_points"], str):
        mistake["knowledge_points"] = [kp.strip() for kp in mistake["knowledge_points"].split(",") if kp.strip()]
    if isinstance(mistake["error_types"], str):
        mistake["error_types"] = [et.strip() for et in mistake["error_types"].split(",") if et.strip()]
    if isinstance(mistake["tags"], str):
        mistake["tags"] = [t.strip() for t in mistake["tags"].split(",") if t.strip()]
    collection["mistakes"].append(mistake)
    return mistake


def edit_mistake(collection: dict, mistake_id: str, field: str, value: any) -> dict | None:
    """Edit a field of a specific mistake. Returns the updated mistake or None if not found."""
    for m in collection["mistakes"]:
        if m["id"] == mistake_id:
            # Handle list-type fields
            if field in ("knowledge_points", "error_types", "tags", "variants"):
                if isinstance(value, str):
                    value = [v.strip() for v in value.split(",") if v.strip()]
            # Handle boolean
            if field == "mastered":
                value = value in (True, "true", "True", "1", 1)
            # Handle int
            if field in ("review_count",):
                value = int(value)
            m[field] = value
            return m
    return None


def delete_mistake(collection: dict, mistake_id: str) -> bool:
    """Delete a mistake by ID. Returns True if deleted, False if not found."""
    before = len(collection["mistakes"])
    collection["mistakes"] = [m for m in collection["mistakes"] if m["id"] != mistake_id]
    return len(collection["mistakes"]) < before


def list_mistakes(collection: dict, limit: int = 50, offset: int = 0) -> list[dict]:
    """List mistakes with pagination."""
    return collection["mistakes"][offset : offset + limit]


def search_mistakes(collection: dict, query: str) -> list[dict]:
    """Full-text search across question, analysis, and knowledge points."""
    q = query.lower()
    results = []
    for m in collection["mistakes"]:
        text = m.get("question", "") + " " + m.get("analysis", "") + " " + " ".join(m.get("knowledge_points", []))
        if q in text.lower():
            results.append(m)
    return results


def filter_mistakes(
    collection: dict,
    subject: str = None,
    error_type: str = None,
    difficulty: str = None,
    mastered: bool = None,
    stage: str = None,
    tags: str = None,
) -> list[dict]:
    """Filter mistakes by criteria."""
    results = collection["mistakes"]
    if subject:
        results = [m for m in results if m.get("subject", "").lower() == subject.lower()]
    if error_type:
        results = [m for m in results if error_type in m.get("error_types", [])]
    if difficulty:
        results = [m for m in results if m.get("difficulty") == difficulty]
    if mastered is not None:
        results = [m for m in results if m.get("mastered") == mastered]
    if stage:
        results = [m for m in results if m.get("stage") == stage]
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        results = [m for m in results if any(t in m.get("tags", []) for t in tag_list)]
    return results


# ── Import ─────────────────────────────────────────────────────────────────


def import_csv(collection: dict, source_path: str) -> int:
    """Import mistakes from CSV file. Columns should match MISTAKE_SCHEMA keys."""
    count = 0
    with open(source_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = {k: v for k, v in row.items() if v and k in MISTAKE_SCHEMA}
            if data.get("question"):
                add_mistake(collection, data)
                count += 1
    return count


def import_json(collection: dict, source_path: str) -> int:
    """Import mistakes from JSON file."""
    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    count = 0
    items = data if isinstance(data, list) else data.get("mistakes", [])
    for item in items:
        add_mistake(collection, item)
        count += 1
    return count


def import_markdown(collection: dict, source_path: str) -> int:
    """Import mistakes from a Markdown file. Each question starts with ## Q or ### Q."""
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by question headers
    question_blocks = re.split(r"\n(?=## Q|\n### Q)", content)
    count = 0

    for block in question_blocks:
        block = block.strip()
        if not block:
            continue

        data = {"question": "", "subject": "", "knowledge_points": [], "error_types": []}

        # Extract question text (first significant paragraph after header)
        lines = block.split("\n")
        header = lines[0].lstrip("# ").strip()

        # Try to extract subject from header or content
        for subject in SUBJECTS:
            if subject.lower() in block.lower():
                data["subject"] = subject
                break

        # Extract question text
        question_lines = []
        in_question = False
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.startswith("**Answer") or stripped.startswith("**分析") or stripped.startswith("**Analysis"):
                break
            if stripped.startswith("**Question") or stripped.startswith("**题目"):
                in_question = True
                q_text = stripped.split(":", 1)[-1].split("：", 1)[-1].strip()
                if q_text:
                    question_lines.append(q_text)
                continue
            if in_question and stripped:
                question_lines.append(stripped)
        data["question"] = " ".join(question_lines) or header

        if not data["question"]:
            continue

        # Extract knowledge points
        kp_match = re.search(r"(?:知识点|Knowledge\s*Point)[：:]\s*(.+)", block, re.IGNORECASE)
        if kp_match:
            data["knowledge_points"] = [kp.strip() for kp in re.split(r"[,，;；]", kp_match.group(1)) if kp.strip()]

        # Extract error types
        et_match = re.search(r"(?:错误类型|Error\s*Type)[：:]\s*(.+)", block, re.IGNORECASE)
        if et_match:
            data["error_types"] = [et.strip() for et in re.split(r"[,，;；]", et_match.group(1)) if et.strip()]

        # Extract analysis
        analysis_match = re.search(r"(?:分析|Analysis)[：:]\s*(.+)", block, re.IGNORECASE)
        if analysis_match:
            data["analysis"] = analysis_match.group(1).strip()

        add_mistake(collection, data)
        count += 1

    return count


# ── Statistics ─────────────────────────────────────────────────────────────


def compute_statistics(collection: dict) -> dict:
    """Compute summary statistics for the collection."""
    mistakes = collection["mistakes"]
    if not mistakes:
        return {"total": 0, "message": "No mistakes in collection"}

    subjects = {}
    error_types = {}
    difficulties = {}
    knowledge_points = {}
    mastered_count = 0
    unanalyzed = 0

    for m in mistakes:
        subj = m.get("subject", "Unknown")
        subjects[subj] = subjects.get(subj, 0) + 1

        diff = m.get("difficulty", "medium")
        difficulties[diff] = difficulties.get(diff, 0) + 1

        for et in m.get("error_types", []):
            error_types[et] = error_types.get(et, 0) + 1

        for kp in m.get("knowledge_points", []):
            knowledge_points[kp] = knowledge_points.get(kp, 0) + 1

        if m.get("mastered"):
            mastered_count += 1
        if not m.get("analysis"):
            unanalyzed += 1

    # Sort knowledge points by count descending
    top_kp = sorted(knowledge_points.items(), key=lambda x: -x[1])[:10]

    return {
        "total": len(mistakes),
        "mastered": mastered_count,
        "mastery_rate": f"{round(mastered_count / len(mistakes) * 100, 1)}%" if mistakes else "0%",
        "unanalyzed": unanalyzed,
        "by_subject": dict(sorted(subjects.items(), key=lambda x: -x[1])),
        "by_difficulty": difficulties,
        "by_error_type": dict(sorted(error_types.items(), key=lambda x: -x[1])),
        "top_weak_kps": dict(top_kp),
        "avg_review_count": round(sum(m.get("review_count", 0) for m in mistakes) / len(mistakes), 1),
        "oldest": min((m.get("added_date", "") for m in mistakes if m.get("added_date")), default=""),
        "newest": max((m.get("added_date", "") for m in mistakes if m.get("added_date")), default=""),
    }


# ── CLI ────────────────────────────────────────────────────────────────────


def print_usage():
    print("Mistake Collection Manager")
    print()
    print("Commands:")
    print("  init   --output FILE                    Create a new collection")
    print("  add    --collection FILE --mistake JSON Add a mistake")
    print("  list   --collection FILE [--limit N]    List mistakes")
    print("  search --collection FILE --query TEXT   Search mistakes")
    print("  filter --collection FILE [--subject S] [--error-type E] [--difficulty D] [--stage S]")
    print("  edit   --collection FILE --id ID --field F --value V")
    print("  delete --collection FILE --id ID")
    print("  import --collection FILE --source FILE --format csv|json|md")
    print("  stats  --collection FILE")
    print()
    print("JSON mistake format:")
    print(json.dumps(MISTAKE_SCHEMA, ensure_ascii=False, indent=2))


def get_arg(args: list[str], key: str) -> str | None:
    """Extract value for --key from args list."""
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

    if command == "init":
        output = get_arg(args, "--output") or "mistake_collection.json"
        collection = load_collection(output)
        save_collection(collection, output)
        print(f"Collection created: {output}")

    elif command == "add":
        coll_path = get_arg(args, "--collection")
        mistake_json = get_arg(args, "--mistake")
        if not coll_path or not mistake_json:
            print("Error: --collection and --mistake are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        mistake_data = json.loads(mistake_json)
        new_mistake = add_mistake(collection, mistake_data)
        save_collection(collection, coll_path)
        print(f"Added: {new_mistake['id']} -- {new_mistake['question'][:50]}...")

    elif command == "list":
        coll_path = get_arg(args, "--collection")
        limit = int(get_arg(args, "--limit") or "50")
        if not coll_path:
            print("Error: --collection is required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        mistakes = list_mistakes(collection, limit=limit)
        if not mistakes:
            print("Collection is empty.")
        else:
            for m in mistakes:
                print(f"  {m['id']} [{m.get('subject', '?')}] {m.get('question', '')[:60]}...")

    elif command == "search":
        coll_path = get_arg(args, "--collection")
        query = get_arg(args, "--query")
        if not coll_path or not query:
            print("Error: --collection and --query are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        results = search_mistakes(collection, query)
        print(f"Found {len(results)} match(es):")
        for m in results:
            print(f"  {m['id']} [{m.get('subject', '?')}] {m.get('question', '')[:60]}...")

    elif command == "filter":
        coll_path = get_arg(args, "--collection")
        if not coll_path:
            print("Error: --collection is required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        results = filter_mistakes(
            collection,
            subject=get_arg(args, "--subject"),
            error_type=get_arg(args, "--error-type"),
            difficulty=get_arg(args, "--difficulty"),
            stage=get_arg(args, "--stage"),
            tags=get_arg(args, "--tags"),
        )
        print(f"Filtered: {len(results)} match(es):")
        for m in results:
            kps = ", ".join(m.get("knowledge_points", [])[:2])
            print(f"  {m['id']} [{m.get('subject', '?')}] {m.get('question', '')[:50]}... | KP: {kps}")

    elif command == "edit":
        coll_path = get_arg(args, "--collection")
        mid = get_arg(args, "--id")
        field = get_arg(args, "--field")
        value = get_arg(args, "--value")
        if not all([coll_path, mid, field, value]):
            print("Error: --collection, --id, --field, --value are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        result = edit_mistake(collection, mid, field, value)
        if result:
            save_collection(collection, coll_path)
            print(f"Updated {mid}: {field} = {value}")
        else:
            print(f"Mistake {mid} not found.", file=sys.stderr)
            sys.exit(1)

    elif command == "delete":
        coll_path = get_arg(args, "--collection")
        mid = get_arg(args, "--id")
        if not all([coll_path, mid]):
            print("Error: --collection and --id are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        if delete_mistake(collection, mid):
            save_collection(collection, coll_path)
            print(f"Deleted: {mid}")
        else:
            print(f"Mistake {mid} not found.", file=sys.stderr)
            sys.exit(1)

    elif command == "import":
        coll_path = get_arg(args, "--collection")
        source = get_arg(args, "--source")
        fmt = get_arg(args, "--format") or "csv"
        if not all([coll_path, source]):
            print("Error: --collection and --source are required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)

        if fmt == "csv":
            count = import_csv(collection, source)
        elif fmt == "json":
            count = import_json(collection, source)
        elif fmt in ("md", "markdown"):
            count = import_markdown(collection, source)
        else:
            print(f"Unknown format: {fmt} (use csv, json, or md)", file=sys.stderr)
            sys.exit(1)

        save_collection(collection, coll_path)
        print(f"Imported {count} mistake(s) from {source}")

    elif command == "stats":
        coll_path = get_arg(args, "--collection")
        if not coll_path:
            print("Error: --collection is required", file=sys.stderr)
            sys.exit(1)
        collection = load_collection(coll_path)
        stats = compute_statistics(collection)
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif command in ("help", "--help", "-h"):
        print_usage()
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
