# Usage Guide: AI Wrong Question Coach

This guide provides end-to-end usage scenarios and step-by-step instructions for common workflows with the AI Wrong Question Coach skill.

---

## Scenario 1: First-Time Setup -- Creating a Mistake Collection

A student just finished a math exam and wants to start tracking mistakes.

### Step 1: Initialize a collection

```bash
python scripts/mistake_manager.py init --output math_collection.json
```

This creates an empty collection file. The skill will automatically detect the subject and stage.

### Step 2: Add mistakes via text input

Provide mistakes in conversation, and the skill will analyze each one. Example user message:

> Here are my mistakes from the quadratic functions test:
>
> 1. Solve x^2 - 5x + 6 = 0. I wrote x = 2, 3. But the answer says x = 2, 3...
>    Wait, I did get it right? [Actually the student wrote "x = 2 or 3" but the
>    correct format was "x1=2, x2=3" -- format error]
>
> 2. Find the vertex of y = x^2 - 4x + 1. I got (-2, 5). Correct is (2, -3).
>    I used x = -b/2a wrong -- forgot the negative sign.
>
> 3. Determine the range of y = -x^2 + 6x - 5. I wrote y <= 4. Correct is y <= 4.
>    Wait... [actually the domain was restricted to [1, 5], so the range
>    is [0, 4] -- missed the domain constraint]

### Step 3: The skill analyzes each

For each mistake, the skill:
- Classifies the error type using `references/error_patterns.md`
- Maps to knowledge points in `references/knowledge_points.md`
- Assesses difficulty
- Generates variant exercises

### Step 4: Build the analysis data

The skill assembles a complete `analysis.json` following the template in `assets/analysis_template.json`.

### Step 5: Generate the schedule

```bash
python scripts/spaced_repetition.py --input mistakes_for_schedule.json --output schedule.json
```

### Step 6: Produce reports

```bash
python scripts/report_generator.py --input analysis.json --output math_report
```

Produces `math_report.html` and `math_report.md`.

---

## Scenario 2: Batch Import from CSV

A teacher exported test mistakes from a grading system as CSV.

### CSV Format

```csv
question,subject,student_answer,correct_answer,difficulty
Solve 2x + 3 = 11,Math,x = 5,x = 4,medium
Find sin(30 degrees),Math,0.5,0.5,easy
```

### Import command

```bash
python scripts/mistake_manager.py import --collection collection.json --source test_mistakes.csv --format csv
```

### Post-import

After import, the skill should:
1. Confirm the import count
2. Ask: "Should I analyze these mistakes now? (y/n)"
3. If yes, proceed with Phase 2-6 of the workflow

---

## Scenario 3: Import from Markdown

A student keeps a simple Markdown mistake journal.

### Markdown Format

```markdown
# Math Mistakes - Week 3

## Q1: Quadratic Equations
**Question:** Solve x^2 - 7x + 12 = 0
**知识点**: Quadratic Equations, Factoring
**错误类型:** ERR_CALC
**分析:** 符号错误 -- (x-3)(x-4) 写成了 (x+3)(x+4)

## Q2: Trigonometric Identities
**Question:** Prove sin^2(x) + cos^2(x) = 1
**知识点**: Trigonometric Identities
**错误类型:** ERR_CONCEPT
**分析:** 混淆了 sin^2(x) 和 sin(x^2) 的定义
```

### Import command

```bash
python scripts/mistake_manager.py import --collection collection.json --source mistakes.md --format md
```

---

## Scenario 4: Tracking Progress

A student has been using the system for 4 weeks and wants to know if they're improving.

### Daily trend

```bash
python scripts/progress_tracker.py trend --collection collection.json --days 30
```

Output includes daily activity counts and error type trends with direction indicators.

### Period comparison

```bash
python scripts/progress_tracker.py compare --collection collection.json --baseline 2026-06-15 --current 2026-07-15
```

Output shows mastery rate change, total growth, and top knowledge points in each period.

### Weekly summary

```bash
python scripts/progress_tracker.py summary --collection collection.json --period weekly
```

### Mastery forecast

```bash
python scripts/progress_tracker.py forecast --collection collection.json --target-date 2026-09-01
```

Output shows estimated completion date and whether the student is on track.

---

## Scenario 5: Filtering and Searching

### Search by keyword

```bash
python scripts/mistake_manager.py search --collection collection.json --query "quadratic"
```

### Filter by error type

```bash
python scripts/mistake_manager.py filter --collection collection.json --error-type ERR_CALC
```

### Filter by subject and difficulty

```bash
python scripts/mistake_manager.py filter --collection collection.json --subject Math --difficulty hard
```

### Filter unmastered items

For finding what still needs work -- note: filter by `mastered` requires the JSON field, so use:

```bash
# Get all non-mastered math mistakes
python scripts/mistake_manager.py filter --collection collection.json --subject Math
```

Then the skill can filter for `mastered: false` in the JSON output.

---

## Scenario 6: Stage Summary (Monthly Review)

A student wants a monthly summary to show their parents/tutor.

### Steps

1. Load the collection
2. Run `progress_tracker.py summary --period monthly`
3. Run `progress_tracker.py compare` for current month vs previous month
4. Run `progress_tracker.py trend --days 30`
5. Build an analysis JSON with summary-level data
6. Generate the report:
   ```bash
   python scripts/report_generator.py --input monthly_analysis.json --output monthly_report
   ```

The monthly report HTML focuses on:
- Before/after comparison (trend charts)
- Top 3 improved knowledge points
- Top 3 areas still needing attention
- Mastery forecast for next month

---

## Scenario 7: Editing and Managing Mistakes

### Edit a mistake's analysis

```bash
python scripts/mistake_manager.py edit --collection collection.json --id Q005 --field analysis --value "The student correctly identified the method but made a sign error in step 3 when distributing the negative sign."
```

### Mark as mastered

```bash
python scripts/mistake_manager.py edit --collection collection.json --id Q005 --field mastered --value true
```

### Add tags for organization

```bash
python scripts/mistake_manager.py edit --collection collection.json --id Q005 --field tags --value "期中考,重点,二次函数"
```

### Delete a mistake

```bash
python scripts/mistake_manager.py delete --collection collection.json --id Q005
```

---

## Complete Script Reference

| Script | Purpose | Key Commands |
|--------|---------|-------------|
| `mistake_manager.py` | CRUD + import | init, add, list, search, filter, edit, delete, import, stats |
| `spaced_repetition.py` | Review scheduling | Computes hybrid Ebbinghaus+SM-2 intervals |
| `report_generator.py` | Report output | Generates HTML + Markdown with Chart.js |
| `progress_tracker.py` | Progress analysis | trend, compare, summary, forecast |

## Typical Session Flow

```
User: "Here are my physics mistakes from this week..."

[Skill does Phase 1-4: analysis, knowledge point mapping, variant generation]

Skill: "Analysis complete. Would you like to generate the review plan?"

User: "Yes"

[Skill runs spaced_repetition.py and report_generator.py]

Skill: "Here's your report." [presents HTML + MD]
      "Top 3 findings:
       1. 3 out of 5 mistakes are Calculation Errors in Mechanics (ERR_CALC)
       2. Knowledge point 'Newton's Second Law' has 4 errors -- highest weakness
       3. Suggested: practice unit conversion before force calculations

      First review session: 2026-07-17 (3 items)"

User: "Add 2 more mistakes from chemistry..."

[Skill iterates from Phase 1, regenerates reports]
```
