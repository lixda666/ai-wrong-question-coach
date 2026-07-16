---
name: ai-wrong-question-coach
description: AI Wrong Question Coach (AI错题教练) is a comprehensive K12 mistake analysis and remediation system. It handles importing wrong questions, AI-powered error root cause analysis with knowledge point mapping, generating similar variant exercises, creating scientifically-scheduled review plans, tracking learning progress, and producing visual analysis reports with charts. Use this skill when the user mentions 错题, 错题本, 错题分析, 复习计划, 变式题, 知识点诊断, 学习报告, or AI错题教练.
agent_created: true
---

# AI Wrong Question Coach (AI错题教练)

## Overview

AI Wrong Question Coach transforms raw mistake data into actionable learning insights.
The core workflow: import mistakes, analyze error causes, map to knowledge points,
generate variant exercises, produce a spaced-repetition review plan, and deliver
interactive visual reports (HTML + Markdown).

This skill integrates four Python scripts with comprehensive reference data to
automate the entire pipeline from data input to report delivery, mistake management,
and progress tracking.

## When to Use This Skill

Use this skill when the user:

- Provides text descriptions or files containing wrong/mistake questions
- Asks for analysis of why mistakes were made ("为什么这道题错了")
- Requests similar practice questions for a weak topic ("生成同类题")
- Wants a scientifically-scheduled review plan ("帮我制定复习计划")
- Needs a visual mistake analysis report with charts ("生成错题分析报告")
- Wants to track progress over time or get a stage summary ("学习进度总结")
- Asks to manage a mistake collection: add, edit, delete, or categorize mistakes

## Core Workflow

### Phase 1: Input & Confirmation

1. **Receive input** -- the user may provide mistakes via:
   - Direct text description in conversation
   - File upload (CSV with columns: question, subject, student_answer, correct_answer)
   - JSON file following the `assets/analysis_template.json` structure
   - Markdown formatted mistake list
   - **Existing persistent collection** -- load `mistake_collection.json` from the
     workspace; all previous mistakes are already stored there

2. **Confirm context** -- before analysis, confirm with the user:
   - **Stage (学段)**: Junior High / Senior High / Primary. Ask explicitly if not provided.
   - **Subject**: Auto-detect from question content. Confirm with user if ambiguous.
   - **Scope**: Is this a one-time import or an ongoing collection? Ask once for new users.
     If the user has a `mistake_collection.json`, default to "ongoing" and reuse it.

3. **Handle collection state.** If a `mistake_collection.json` exists in the
   workspace, load it first. The analysis in Phase 2 should operate on the
   full collection, not just newly added items, unless the user specifically
   requests analysis of a subset. Unanalyzed mistakes (those whose `analysis`
   field is empty) should be prioritized in the analysis pass.

### Phase 2: AI-Powered Analysis

For each mistake, perform deep analysis and produce a structured output:

1. **Error Cause Classification** -- use `references/error_patterns.md` to classify each mistake into one primary error type:
   - ERR_CONCEPT (Concept Confusion)
   - ERR_CALC (Calculation Error)
   - ERR_READ (Misreading Question)
   - ERR_METHOD (Method Error)
   - ERR_GAP (Knowledge Gap)
   - ERR_FORMAT (Non-standard Solution)
   - ERR_PSYCH (Test-taking Factors)

2. **Knowledge Point Mapping** -- use `references/knowledge_points.md` to map each mistake to specific knowledge points by `kp_id`. If a knowledge point is not in the taxonomy, note it for future expansion.

3. **Difficulty Assessment** -- classify each mistake as `easy`, `medium`, or `hard` based on:
   - Error type (gaps and concept confusion tend toward harder)
   - Question complexity
   - Student's demonstrated partial understanding

4. **Root Cause Analysis** -- produce a concise, specific analysis (2-4 sentences) that:
   - Pinpoints the exact step or concept where the error occurred
   - Uses plain, instructional language
   - Avoids vague statements like "needs more practice"

### Phase 3: Generate Variant Exercises

For each mistake, generate 1-2 similar practice questions that:
- Target the same knowledge point at the same difficulty level
- Modify surface features (numbers, names, context) while preserving the core concept
- Are clearly solvable (the skill should know or be able to derive the correct answer)
- Use the same subject conventions and notation

### Phase 4: Build the Analysis Data Structure

Assemble all analysis results into a JSON structure matching the format in `assets/analysis_template.json`. The structure must include:

```json
{
  "title": "...",
  "subject": "...",
  "stage": "...",
  "statistics": { "items": [...] },
  "error_distribution": { "ERR_TYPE": count },
  "kp_error_counts": { "Knowledge Point Name": count },
  "retention_curve": [{ "day": N, "retention": value }],
  "mistakes": [{ "id", "subject", "question", "analysis", "knowledge_points": [...], "error_types": [...], "variants": [...] }],
  "schedule_timeline": [{ "date": "...", "items": "..." }],
  "suggestions": [{ "title", "description", "priority": "high|medium|low" }]
}
```

### Phase 5: Generate Reports

#### A. Review Schedule

Run `scripts/spaced_repetition.py` to compute the review schedule:

```bash
python scripts/spaced_repetition.py --input mistakes_input.json --output schedule.json
```

The input JSON structure:
```json
{
  "mistakes": [
    {"id": "Q001", "difficulty": "medium", "added_date": "2026-07-16"}
  ],
  "start_date": "2026-07-16",
  "total_items": 15
}
```

The script uses a hybrid Ebbinghaus + SM-2 algorithm:
- Base intervals: 1, 2, 4, 7, 15, 30, 60, 120 days
- SM-2 ease factor adjusts intervals based on difficulty
- Target retention: 85%

Merge the schedule output into the analysis JSON:
- Populate `retention_curve` from the schedule's retention projection
- Populate `schedule_statistics` items
- Populate `schedule_timeline` for the first 15 review days

#### B. HTML + Markdown Reports

Run `scripts/report_generator.py` to produce both output formats:

```bash
python scripts/report_generator.py --input analysis.json --output report
```

This produces `report.html` (interactive, with Chart.js visualizations) and `report.md`.
Both reports include:
- Summary statistics panel
- Error type distribution (doughnut + horizontal bar charts in HTML)
- Knowledge point weakness analysis (horizontal bar + radar charts in HTML)
- Retention curve projection (line chart in HTML)
- Detailed mistake breakdowns with analysis and variant exercises
- Interactive review schedule timeline -- click any day to open a modal with that
  day's question details, analysis, knowledge points, and variant exercises
- Prioritized improvement suggestions

#### C. Report Design Principles

The HTML report follows these design rules:
- **No emoji** -- use clean typography and color coding instead
- **Minimalist aesthetic** -- light background, restrained color palette, subtle shadows
- **Data-forward** -- charts and statistics drive the narrative, not decorative elements
- **Actionable** -- each section connects insight to concrete next steps
- **Chinese-first** -- all labels, descriptions, and UI text use Chinese by default
- **Robust chart data** -- every chart must render meaningful data even when optional
  fields are missing. The error-type bar chart reads from `error_distribution` (which
  is always present) rather than `error_by_subject` (which is optional). If a chart
  would otherwise be empty, swap data sources or hide it.
- **Interactive Schedule Timeline** -- each `schedule-day` in the review schedule
  is clickable. Clicking opens a modal that shows the day's question details,
  including question text, error analysis, related knowledge points, and variant
  practice questions. See the **Schedule Modal Spec** section below.

#### Schedule Modal Spec

The Schedule Timeline is the most actionable part of the report. To make it useful
in practice, every `schedule-day` must be clickable, and the click must surface
the full review content for that day.

**Data injection.** The generator embeds two payloads into the HTML page as a
single global object:

```js
window.__REVIEW_DATA__ = {
  schedule: [
    { "date": "2026-07-16", "day": 0, "items": "Q1-Q10（初次分析）" },
    { "date": "2026-07-17", "day": 1, "items": "Q5, Q9（易错题，先复习）" },
    ...
  ],
  mistakes: [ /* full mistake objects with id, question, analysis, knowledge_points, variants, error_types */ ],
  totalMistakes: 10,
};
```

**Question ID parsing.** The `items` field is a free-text Chinese string. The
client must extract question IDs from it. The parser must handle three forms:

1. **Range** -- `"Q1-Q10（初次分析）"` → `[Q1, Q2, ..., Q10]`. Accept hyphens,
   en-dashes, and em-dashes (`-`, `–`, `—`).
2. **List** -- `"Q5, Q9（易错题，先复习）"` → `[Q5, Q9]`. Also accepts
   `Q4, Q8, Q10（中值定理/交换次序/微分方程）`.
3. **All-N shorthand** -- `"全部10题（第一轮全面复习 + 变式题练习）"`
   → expand to `Q1, Q2, ..., QN` where N is the parsed number (fall back to
   `totalMistakes` if no number is present).

**Modal content layout.** For the parsed question IDs, the modal must show:

- Header: the date and a subtitle like `第 1 天 · 涉及 2 道题`
- Aggregated knowledge-point chips at the top (`涉及知识点：...`)
- For each question: a card with
  - Question ID badge (`#Q5`)
  - Error-type tags
  - Question text
  - Error analysis block
  - Knowledge-point chips (per question)
  - Variant practice questions with their answers

**Fallback.** If `lookupMistakes` returns zero results for a given day (data
missing), show a small "该日无详细题目数据" message with the raw `items` string
so the user can still see what was scheduled.

**Interaction rules.** Modal closes on: clicking the close button, clicking the
backdrop overlay, or pressing `Esc`. Body scroll is locked while the modal is
open.

### Phase 6: Deliver & Iterate

1. Present both the HTML report (open in browser preview) and the Markdown file to the user
2. Highlight the top 3 actionable findings
3. If the user has follow-up requests:
   - **Add more mistakes** via text or file → go to Ongoing Features B/C, then re-run Phase 2–6
   - **Delete mistakes** → go to Ongoing Features D, then re-run Phase 2–6
   - **More variants, adjust schedule** → iterate from the appropriate phase
4. If this is a continuing collection, update the running JSON file and regenerate reports

## Ongoing Features

## Ongoing Features

### Mistake Collection Management

The core persistent data unit is a JSON collection file (suggest
`mistake_collection.json` in the workspace). Every mistake added, deleted, or
imported is stored here. This file also feeds analysis, progress tracking, and
report generation.

Use `scripts/mistake_manager.py` for all CRUD operations. The script handles
the JSON file I/O; your job is to orchestrate the conversational flow.

#### A. Initializing a Collection

When starting fresh with a user, create the collection:

```bash
python scripts/mistake_manager.py init --output mistake_collection.json
```

If a collection already exists in the workspace, reuse it. Always use an
absolute path when calling the script so the collection is discoverable.

#### B. Adding Mistakes via Text Description

This is the most common flow. The user describes a mistake in natural language
and you must transform it into a valid mistake JSON, confirm with the user, then
persist it.

**Step 1 — Parse the description.** Extract these fields from whatever the user
provides:

| Field | Required | Notes |
|---|---|---|
| `question` | Yes | The actual question text or problem statement |
| `subject` | Ask if ambiguous | Map to a value in `SUBJECTS`: Math, Physics, Chemistry, Chinese, English, Biology, Geography, History, Politics |
| `stage` | Ask if ambiguous | Junior High, Senior High, Primary, University |
| `student_answer` | No | What the user wrote |
| `correct_answer` | No | The correct solution |
| `difficulty` | No (default: medium) | easy / medium / hard |
| `error_types` | No | Auto-suggest based on patterns (e.g. "算错了" → ERR_CALC, "公式记混了" → ERR_CONCEPT, "看不懂题" → ERR_READ) |
| `knowledge_points` | No | Can be filled later during analysis |
| `analysis` | No | Can be filled later during analysis |

If the user says "我昨晚做错了一道数列极限，用洛必达法则对离散变量直接求导了",
you would produce:

```json
{
  "question": "用洛必达法则求数列极限 lim_{n→∞} n·(a^(1/n)-1)",
  "subject": "Math",
  "stage": "University",
  "student_answer": "对 n 直接求导",
  "difficulty": "medium",
  "error_types": ["ERR_METHOD"]
}
```

**Step 2 — Confirm.** Print a human-readable summary of what you parsed and ask
the user to confirm before saving. Example:

```
解析结果：
  题目：用洛必达法则求数列极限 lim_{n→∞} n·(a^(1/n)-1)
  科目：Math（高等数学）
  学段：大学
  难度：medium
  错误类型：方法错误 (ERR_METHOD)

确认加入错题集？(回复「确认」或修改)
```

**Step 3 — Save.** Once confirmed, call the CLI:

```bash
python scripts/mistake_manager.py add --collection COLLECTION_PATH \
  --mistake '{"question":"...","subject":"Math","stage":"University",...}'
```

Use single-quotes around the JSON and double-quotes inside, or escape accordingly
for the shell.

**Step 4 — Offer follow-up.** After saving, ask:

```
已加入错题集（ID: Q011）。要现在做 AI 分析并更新报告吗？
或者待积累更多错题后批量分析？
```

If the user says "分析", proceed to Phase 2–6 using the updated collection.

If the user adds multiple mistakes in a row, batch them into a single final
confirmation ("共 3 道题，全部加入？") rather than confirming one by one.

#### C. Adding Mistakes via File Import

When the user provides a file (dragged, pasted path, or attached):

1. **Detect the format** from the extension:
   - `.csv` → `--format csv`
   - `.json` → `--format json`
   - `.md` / `.markdown` → `--format md`

2. **Run the import**:

```bash
python scripts/mistake_manager.py import --collection COLLECTION_PATH \
  --source /path/to/file --format csv
```

3. **Report results.** Print the import count and a short summary:

```
已导入 5 道错题，合计错题集共 15 道。
要立即对这些新错题做 AI 分析并生成报告吗？
```

If the import fails (format error, empty file, no `question` column), report the
error with actionable advice ("CSV 文件需要包含 `question` 列").

For CSV format expectations, see `references/config_examples.md`.

#### D. Deleting Mistakes

When the user asks to delete a mistake, the critical rule is **confirm before
deleting**.

**Step 1 — Find the ID.** If the user says "删除那道极限的题" but doesn't give
an ID, search first:

```bash
python scripts/mistake_manager.py search --collection COLLECTION_PATH \
  --query "极限"
```

Then present the matches and ask which one.

**Step 2 — Confirm.** Show the full question text and ask:

```
确认删除 Q002：「用洛必达法则求数列极限...」？
此操作不可撤销。回复「确认删除」以继续。
```

**Step 3 — Delete and report.** Run the CLI and report:

```bash
python scripts/mistake_manager.py delete --collection COLLECTION_PATH --id Q002
```

Response: `已删除 Q002。错题集剩余 9 道题。`

After deletion, offer to regenerate the analysis report so charts and
schedule stay accurate.

#### E. Collection Lifecycle

- The collection JSON is the single source of truth. Never maintain duplicate
  data in the conversation.
- After any add/delete/import operation, the collection stats change. The user
  may want an updated report — offer it.
- If a collection grows beyond 50 mistakes, suggest splitting by subject or
  creating a stage-specific collection.

#### F. Web UI Management (Alternative)

For a visual, interactive management experience, start the Web UI:

```bash
python scripts/mistake_webui.py --collection COLLECTION.json --port 5000
```

This launches a browser-based management console where the user can add, delete,
import, and regenerate reports with clicks instead of text commands. The Web UI
is a Flask server — it must be started before the user opens the page.

When the user asks for "管理错题" or "打开管理界面" or "可视化操作", prefer
starting the Web UI over CLI-only operations. After the user closes the Web UI
and indicates they are done, proceed to regenerate the analysis report from the
updated collection.

### Progress Tracking

When the user requests a progress summary ("学习进度", "阶段性总结"):

1. Load the full mistake collection
2. Run `scripts/progress_tracker.py` for quantitative analysis:
   - **Trend**: `python scripts/progress_tracker.py trend --collection FILE --days 30`
   - **Compare**: `python scripts/progress_tracker.py compare --collection FILE --baseline DATE --current DATE`
   - **Summary**: `python scripts/progress_tracker.py summary --collection FILE --period weekly`
   - **Forecast**: `python scripts/progress_tracker.py forecast --collection FILE --target-date DATE`
3. Calculate metrics:
   - Error type trends (is ERR_CALC decreasing?)
   - Knowledge point coverage (are new weak points emerging?)
   - Subject balance
   - Average difficulty trend
   - Mastery rate and estimated completion date
4. Generate a progress report with before/after comparisons
5. Produce both HTML (with trend charts) and Markdown

### Stage Summary

When the user asks for a stage summary:
- Aggregate all mistakes within the requested period
- Identify the top 3 knowledge points requiring attention
- Recommend pace adjustments based on volume and difficulty trends
- Generate a focused summary report

## Reference Files

### references/knowledge_points.md
Complete K12 knowledge point taxonomy covering:
- Mathematics (Junior + Senior High) -- 36 categories
- Physics (Junior + Senior High) -- 30 categories
- Chemistry (Junior + Senior High) -- 20 categories
- Chinese Language -- 11 categories
- English -- 12 categories

Each knowledge point has a unique `kp_id`, `name`, `subject`, and `stage` indicator.
Load this file when mapping mistakes to knowledge points. If a mistake does not fit
any existing category, use the closest parent and note the gap.

### references/error_patterns.md
Error type classification system with 7 primary categories, each with:
- Detailed description and examples
- Remediation strategy
- Mutual exclusion rules (e.g., Concept Confusion vs Knowledge Gap)
- Confidence scoring guidelines (>=0.8 high, 0.5-0.8 medium, <0.5 low)

Load this file during the analysis phase. Every mistake must receive at least one
error type classification.

### references/usage_guide.md
End-to-end usage scenarios covering:
- Scenario 1: First-time setup and mistake collection creation
- Scenario 2: Batch import from CSV
- Scenario 3: Import from Markdown
- Scenario 4: Progress tracking workflows
- Scenario 5: Filtering and searching
- Scenario 6: Monthly stage summary generation
- Scenario 7: Editing and managing mistakes
- Complete script reference table

Load this file when the user is new to the system or needs guidance on a specific workflow.

### references/config_examples.md
Detailed input format examples and configuration reference:
- CSV import format (minimal and full)
- JSON import format (single and batch)
- Markdown import format (simple and detailed)
- Analysis JSON structure for report generation
- Schedule input format for spaced_repetition.py
- Error type codes reference table
- Knowledge point ID naming convention

Load this file when the user provides input files or asks about supported formats.

## Script Reference

### scripts/mistake_manager.py
CRUD operations and batch import for the mistake collection.

**Commands**: init, add, list, search, filter, edit, delete, import, stats
**Import formats**: CSV, JSON, Markdown
**Usage examples**:
```bash
python scripts/mistake_manager.py init --output collection.json
python scripts/mistake_manager.py import --collection collection.json --source mistakes.csv --format csv
python scripts/mistake_manager.py filter --collection collection.json --subject Math --difficulty hard
python scripts/mistake_manager.py stats --collection collection.json
```

### scripts/mistake_webui.py

Interactive web-based management console for the mistake collection. Provides a
browser UI (served by Flask) with:

- **Add mistakes** via a text form (question + subject + stage + difficulty +
  error types + knowledge points + analysis)
- **Delete mistakes** with a confirmation modal
- **Batch import** via drag-and-drop file upload (CSV / JSON / Markdown)
- **One-click report regeneration** — after adding/deleting, a button
  regenerates `report.html` and `report.md` from the updated collection
- **Live stats** — total, mastery rate, unanalyzed count, average review count

Start with:
```bash
python scripts/mistake_webui.py --collection COLLECTION.json --port 5000 --output DIR
```

Then open `http://localhost:5000` in a browser.

When using this skill and the user already has a `mistake_collection.json`,
offer to start the web UI so the user can manage mistakes visually. After the
user finishes managing, re-run the analysis pipeline to reflect changes in
the report.

### scripts/spaced_repetition.py
Standalone Python script for computing review schedules.

**Input**: JSON with `mistakes` array (id, difficulty, added_date), `start_date`, `total_items`
**Output**: JSON with `daily_plan`, `retention_curve`, `statistics`
**Algorithm**: Hybrid Ebbinghaus forgetting curve + SM-2 ease factor adjustment

Run with:
```bash
python scripts/spaced_repetition.py --input mistakes.json --output schedule.json
```

### scripts/report_generator.py
Standalone Python script for generating dual-format reports.

**Input**: Complete analysis JSON (see `assets/analysis_template.json` for schema)
**Output**: `{output}.html` (interactive with Chart.js) + `{output}.md` (plain text)
**Dependencies**: None (Chart.js loaded via CDN in HTML)

Run with:
```bash
python scripts/report_generator.py --input analysis.json --output report_name
```

### scripts/progress_tracker.py
Quantitative progress analysis with trend computation and mastery forecasting.

**Commands**: trend, compare, summary, forecast
**Usage examples**:
```bash
python scripts/progress_tracker.py trend --collection collection.json --days 30
python scripts/progress_tracker.py compare --collection collection.json --baseline 2026-07-01 --current 2026-08-01
python scripts/progress_tracker.py summary --collection collection.json --period weekly
python scripts/progress_tracker.py forecast --collection collection.json --target-date 2026-09-01
```

## Asset Reference

### assets/analysis_template.json
Complete template for the analysis data structure. Use this as the schema reference
when building the analysis JSON in Phase 4. All fields are documented inline.

## Important Rules

1. **Always confirm stage (学段)** before starting analysis if the user has not provided it
2. **Never use emoji** in reports, labels, or any output -- use typography and color for visual hierarchy
3. **Keep analysis specific** -- avoid generic advice like "practice more"; instead say "practice factoring quadratic expressions where the coefficient of x^2 is not 1"
4. **Chart color convention**: Use the defined color palette for consistency across reports
5. **Knowledge point mapping priorities**: Match to the most specific knowledge point; use parent only as fallback
6. **Confidence**: Mark low-confidence error classifications (<0.5) with a note in the report
7. **Privacy**: Mistake data stays local in the workspace; never upload question content externally
8. **Chinese-first output** -- all generated artefacts (HTML, Markdown, charts,
   labels, axis titles, legends, buttons, tooltips) must be in Chinese, with the
   only exceptions being knowledge-point proper nouns, technical abbreviations
   (SM-2, Ebbinghaus, etc.), and code identifiers (Q1, ERR_METHOD, kp_id).
9. **Schedule Timeline is interactive** -- the HTML report's schedule must
   embed question/mistake data as JSON (see **Schedule Modal Spec** above) and
   each day must open a modal with that day's questions, analysis, knowledge
   points, and variant exercises. Plain bullet lists are not acceptable.
10. **Web UI management console** -- when the user wants to add, delete, or
    import mistakes visually, start `scripts/mistake_webui.py` on an available
    port. The server provides a browser-based management page with a form for
    adding mistakes, drag-and-drop file import, a mistake list with delete
    buttons, and a one-click report regeneration button. After the user finishes
    with the UI, regenerate the analysis report from the updated collection.
