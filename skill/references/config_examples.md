# Configuration Examples & Input Formats

This reference provides concrete examples of all input formats supported by AI Wrong Question Coach.

---

## 1. CSV Import Format

### Minimal CSV (required fields only)

```csv
question,subject
Solve x^2 - 5x + 6 = 0,Math
Calculate the force given mass=5kg and acceleration=2m/s^2,Physics
Balance the equation: Fe + O2 -> Fe2O3,Chemistry
```

### Full CSV (all supported fields)

```csv
question,subject,student_answer,correct_answer,difficulty,stage,error_types,knowledge_points,tags
Find the vertex of y = x^2 - 4x + 1,Math,(-2, 5),(2, -3),hard,Senior High,ERR_CALC,Quadratic Functions|Vertex Formula,期中考
Calculate current through 10 ohm resistor with 12V battery,Physics,0.83A,1.2A,medium,Junior High,ERR_METHOD,Ohm's Law|Series Circuits,电学
Translate: 'Despite the rain, the game continued',English,虽然下雨但游戏继续,尽管下雨比赛仍继续进行,medium,Senior High,ERR_CONCEPT,Conjunctions|Translation,英语翻译
```

### CSV Field Reference

| Field | Required | Type | Example |
|-------|----------|------|---------|
| `question` | Yes | String | "Solve 2x + 3 = 11" |
| `subject` | No | String | "Math", "Physics", "Chemistry", "Chinese", "English" |
| `student_answer` | No | String | "x = 5" |
| `correct_answer` | No | String | "x = 4" |
| `difficulty` | No | easy/medium/hard | "medium" |
| `stage` | No | String | "Junior High", "Senior High" |
| `error_types` | No | Pipe-separated codes | "ERR_CALC|ERR_READ" |
| `knowledge_points` | No | Pipe-separated names | "Newton's Laws|Force Diagrams" |
| `tags` | No | Pipe-separated | "期中考|重点" |

**Note:** Pipe `|` is the separator for multi-value fields in CSV. In JSON imports, these are arrays.

---

## 2. JSON Import Format

### Single mistake (inline in conversation)

```json
{
  "question": "Prove that the sum of interior angles of a triangle equals 180 degrees",
  "subject": "Math",
  "stage": "Junior High",
  "student_answer": "Used a protractor to measure each angle and added them up",
  "correct_answer": "Construct a line parallel to one side through the opposite vertex, then use alternate interior angles",
  "difficulty": "medium",
  "knowledge_points": ["Triangle Angle Sum Theorem", "Geometric Proof", "Parallel Lines"],
  "error_types": ["ERR_METHOD"],
  "tags": ["几何", "证明"]
}
```

### Batch import (JSON file)

```json
{
  "mistakes": [
    {
      "question": "Solve |2x - 4| = 6",
      "subject": "Math",
      "stage": "Senior High",
      "student_answer": "x = 5 or x = -1",
      "correct_answer": "x = 5 or x = -1",
      "difficulty": "medium",
      "knowledge_points": ["Absolute Value Equations"],
      "error_types": ["ERR_READ"]
    },
    {
      "question": "Find the derivative of f(x) = x^3 * sin(x)",
      "subject": "Math",
      "stage": "Senior High",
      "student_answer": "f'(x) = 3x^2 * sin(x)",
      "correct_answer": "f'(x) = 3x^2*sin(x) + x^3*cos(x)",
      "difficulty": "hard",
      "knowledge_points": ["Derivative Product Rule", "Trigonometric Derivatives"],
      "error_types": ["ERR_GAP", "ERR_METHOD"]
    }
  ]
}
```

---

## 3. Markdown Import Format

### Simple structure

```markdown
# Math Mistakes

## Q1
**Question:** Solve the quadratic: x^2 - 6x + 8 = 0
**知识点:** Quadratic Equations, Factoring
**错误类型:** ERR_CALC
**分析:** Factored incorrectly as (x-2)(x-6) instead of (x-2)(x-4)

## Q2
**Question:** Find the domain of f(x) = sqrt(x - 3)
**知识点:** Function Domain, Inequalities
**错误类型:** ERR_CONCEPT
**分析:** 混淆了定义域 -- 忘记平方根内必须大于等于0而非大于0
```

### Detailed structure

```markdown
# Physics Mistakes - Week 12

---

## Q1: Newton's Second Law Application

**Subject:** Physics
**Stage:** Senior High
**Difficulty:** hard

**Question:**
A 2kg block is pulled with a force of 10N at an angle of 30 degrees
above the horizontal on a frictionless surface. Find the acceleration.

**Student Answer:** a = 5 m/s^2

**Correct Answer:** a = 4.33 m/s^2

**知识点:** Newton's Second Law, Force Decomposition, Vector Components
**错误类型:** ERR_METHOD, ERR_CALC
**分析:**
The student directly used F = ma with the full 10N force without decomposing
it into horizontal component (F_x = 10*cos(30) = 8.66N). This is both a
method error (missing decomposition step) and a calculation error since they
should have computed a = F_x/m = 8.66/2 = 4.33 m/s^2.

**Tags:** 力学, 矢量分解, 期中考

---
```

### Markdown Parsing Rules

The `mistake_manager.py` Markdown importer parses:

| Pattern | Extracts |
|---------|----------|
| `## Q<N>` or `### Q<N>` | New mistake block |
| `**Question:**` or `**题目:**` | Question text |
| `**知识点:**` or `**Knowledge Point:**` | Comma/pipe separated knowledge points |
| `**错误类型:**` or `**Error Type:**` | Comma/pipe separated error codes |
| `**分析:**` or `**Analysis:**` | Error analysis text |
| `**Subject:**` | Subject name |
| `**Stage:**` | Junior High / Senior High |
| `**Difficulty:**` | easy / medium / hard |
| `**Tags:**` | Comma separated tags |

---

## 4. Analysis JSON Structure (for Report Generation)

This is the intermediate format built by the skill before generating reports.
Full template at `assets/analysis_template.json`.

### Key Structure Fields

```json
{
  "title": "Mistake Analysis Report",
  "subject": "Math",
  "stage": "Senior High",
  "generated_at": "2026-07-16",
  "target_retention": 85,

  "statistics": {
    "items": [
      {"label": "Total Mistakes", "value": "15"},
      {"label": "Knowledge Points Involved", "value": "8"},
      {"label": "Review Sessions Scheduled", "value": "12"},
      {"label": "Mastery Rate", "value": "33.3%"}
    ]
  },

  "error_distribution": {
    "ERR_CALC": 5,
    "ERR_CONCEPT": 4,
    "ERR_GAP": 3,
    "ERR_READ": 2,
    "ERR_METHOD": 1
  },

  "kp_error_counts": {
    "Quadratic Functions": 4,
    "Trigonometric Functions": 3,
    "Sequences": 2,
    "Probability": 2,
    "Vectors": 2,
    "Derivatives": 1,
    "Complex Numbers": 1
  },

  "difficulty_distribution": {
    "easy": 3,
    "medium": 8,
    "hard": 4
  },

  "mistakes": [
    {
      "id": "Q001",
      "subject": "Math",
      "question": "Solve x^2 - 5x + 6 = 0",
      "analysis": "Factoring error: student wrote (x+2)(x+3) instead of (x-2)(x-3). Sign confusion when the constant term is positive but the linear coefficient is negative.",
      "knowledge_points": ["Quadratic Equations", "Factoring"],
      "error_types": ["ERR_CALC"],
      "difficulty": "medium",
      "variants": [
        "Solve x^2 + x - 6 = 0",
        "Find the roots of 2x^2 - 7x + 3 = 0"
      ]
    }
  ],

  "retention_curve": [
    {"day": 0, "retention": 1.0},
    {"day": 1, "retention": 0.97},
    {"day": 3, "retention": 0.93},
    {"day": 7, "retention": 0.85},
    {"day": 15, "retention": 0.74},
    {"day": 30, "retention": 0.58},
    {"day": 60, "retention": 0.32}
  ],

  "schedule_statistics": {
    "items": [
      {"label": "Total Review Sessions", "value": "12"},
      {"label": "Avg Daily Items", "value": "2.5"},
      {"label": "Coverage Period", "value": "2026-07-17 ~ 2026-10-15"}
    ]
  },

  "schedule_timeline": [
    {"date": "2026-07-17", "items": "Review Q001, Q003, Q007 (3 items)"},
    {"date": "2026-07-19", "items": "Review Q004, Q012 (2 items)"},
    {"date": "2026-07-21", "items": "Review Q002, Q005, Q008, Q015 (4 items)"}
  ],

  "suggestions": [
    {
      "title": "Focus on Quadratic Functions",
      "description": "4 out of 15 mistakes involve quadratic functions. Review factoring techniques and the vertex formula. Schedule a focused practice session on discriminants and root nature analysis.",
      "priority": "high"
    },
    {
      "title": "Reduce Calculation Errors",
      "description": "Calculation errors account for 33% of all mistakes. Practice verifying each step by substitution. Consider doing a 5-minute mental math warm-up before starting problem sets.",
      "priority": "high"
    },
    {
      "title": "Method Selection Drills",
      "description": "For sequence problems, practice distinguishing between arithmetic, geometric, and recursive sequences before solving. Create a decision flowchart for method selection.",
      "priority": "medium"
    }
  ]
}
```

---

## 5. Schedule Input Format (for spaced_repetition.py)

```json
{
  "mistakes": [
    {"id": "Q001", "difficulty": "hard", "added_date": "2026-07-16"},
    {"id": "Q002", "difficulty": "medium", "added_date": "2026-07-16"},
    {"id": "Q003", "difficulty": "easy", "added_date": "2026-07-15"},
    {"id": "Q004", "difficulty": "hard", "added_date": "2026-07-16"},
    {"id": "Q005", "difficulty": "medium", "added_date": "2026-07-14"}
  ],
  "start_date": "2026-07-17",
  "total_items": 5
}
```

**Difficulty impact on scheduling:**
- `easy` (EF=2.8): Longer intervals, fewer review sessions
- `medium` (EF=2.5): Standard intervals
- `hard` (EF=2.2): Shorter intervals, more review sessions

---

## 6. Error Type Codes Reference

| Code | Chinese Label | English Label |
|------|---------------|---------------|
| `ERR_CONCEPT` | 概念混淆 | Concept Confusion |
| `ERR_CALC` | 计算失误 | Calculation Error |
| `ERR_READ` | 审题不清 | Misreading Question |
| `ERR_METHOD` | 方法错误 | Method Error |
| `ERR_GAP` | 知识盲区 | Knowledge Gap |
| `ERR_FORMAT` | 解题不规范 | Non-standard Solution |
| `ERR_PSYCH` | 考试心理因素 | Test-taking Factors |

---

## 7. Knowledge Point ID Convention

Knowledge point IDs follow the pattern: `{SUBJECT}_{STAGE}_{NN}`

Examples:
- `MATH_JH_05` -- Math, Junior High, #05 (Quadratic Equations)
- `PHYS_SH_10` -- Physics, Senior High, #10 (Electrostatics)
- `CHEM_JH_06` -- Chemistry, Junior High, #06 (Acids, Bases, Salts)
- `CN_04` -- Chinese, #04 (Classical Chinese vocabulary)
- `EN_03` -- English, #03 (Modal Verbs)

When matching mistakes to knowledge points, prefer the most specific `kp_id`.
If a new knowledge point is needed, suggest an ID following this convention
and note it for taxonomy expansion.
