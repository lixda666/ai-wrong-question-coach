# Error Pattern Classification

This reference defines the error pattern taxonomy. Each wrong question must be classified into one or more error types. This classification drives the analysis report, remediation suggestions, and review plan optimization.

---

## Primary Error Types

### 1. Concept Confusion (概念混淆) [ERR_CONCEPT]

The student understands some of the relevant concepts but mixes them up with similar ideas.

**Examples:**
- Confusing similar-sounding formulas or theorems
- Mixing up definitions (e.g., median vs altitude in a triangle)
- Applying a concept from one domain in another domain incorrectly
- Confusing "necessary condition" vs "sufficient condition"
- Mixing up similar vocabulary or grammatical rules in languages

**Remediation Strategy:**
- Generate side-by-side comparison of the confused concepts
- Create distinguishing-feature questions
- Recommend concept mapping exercise

---

### 2. Calculation Error (计算失误) [ERR_CALC]

The student understood the approach but made an arithmetic, algebraic, or numerical mistake during execution.

**Examples:**
- Sign errors (dropping or adding a negative sign)
- Arithmetic mistakes in multi-step calculations
- Misplacing decimal points
- Unit conversion errors
- Exponent or log rule misapplication

**Remediation Strategy:**
- Highlight the exact step where the error occurred
- Generate similar-calculation drill exercises
- Recommend "verify by substitution" habit training

---

### 3. Misreading the Question (审题不清) [ERR_READ]

The student failed to correctly interpret the question's requirements, constraints, or key information.

**Examples:**
- Missing a conditional constraint ("x > 0" overlooked)
- Answering a different question than what was asked
- Ignoring implicit assumptions in word problems
- Misunderstanding the question's scope
- Reading the question too fast and skipping key details

**Remediation Strategy:**
- Deconstruct the question step by step
- Highlight the key phrases and what they imply
- Generate "trap" variants that test careful reading

---

### 4. Method Error (方法错误) [ERR_METHOD]

The student chose an incorrect or suboptimal problem-solving approach.

**Examples:**
- Using a formula that doesn't apply to the given conditions
- Taking a needlessly complex route and getting lost
- Incorrect solution template for the problem type
- Missing a prerequisite step before applying a standard method
- Using a brute-force approach where a shortcut exists

**Remediation Strategy:**
- Show the correct method step by step
- Explain *why* the chosen method was wrong and when it would be right
- Generate method-selection drill (which method for which problem?)

---

### 5. Knowledge Gap (知识盲区) [ERR_GAP]

The student lacks the foundational knowledge required to solve the problem.

**Examples:**
- Never learned the underlying concept or formula
- Missing prerequisite knowledge from earlier chapters
- The knowledge point was taught but the student was absent or didn't retain it
- Cannot recall the relevant theorem when needed

**Remediation Strategy:**
- Link to foundational material that must be mastered first
- Generate scaffolding exercises leading up to the target problem
- Prioritize this knowledge point in the review plan

---

### 6. Non-standard Solution (解题不规范) [ERR_FORMAT]

The student got the right approach but lost points due to incomplete or non-standard presentation.

**Examples:**
- Missing required proof steps in geometry or deduction problems
- Skipping "required" intermediate steps that carry scoring weight
- Not writing the final answer in the requested format
- Missing units or significant figures
- Poor handwriting causing grading errors

**Remediation Strategy:**
- Provide a fully written-out model solution
- Highlight scoring rubric expectations
- Generate format-awareness exercises

---

### 7. Psychological / Test-taking Factors (考试心理因素) [ERR_PSYCH]

Errors caused by test anxiety, time pressure, or mental fatigue rather than knowledge gaps.

**Examples:**
- Blanking out on known material under pressure
- Rushing through early questions and making careless mistakes
- Spending too long on one question and panicking
- Second-guessing and changing correct answers

**Remediation Strategy:**
- Recommend timed practice with similar problem sets
- Suggest test-taking strategy (question ordering, time allocation)
- Note in report: this may not be a knowledge issue

---

## Classification Rules

1. **Always classify into one primary type first**, then add secondary types if applicable.
2. **Concept Confusion** and **Knowledge Gap** are mutually exclusive for the primary classification - determine whether the student has partial knowledge (confusion) or no knowledge (gap).
3. **Calculation Error** should only be primary if the method and understanding were correct.
4. Each error gets an `error_types` array: `["primary", "secondary_1", ...]`

## Confidence Scoring

When assigning error types, the AI analysis should include a confidence score (0.0-1.0):

- **>= 0.8**: High confidence - clear indicators in the student's work
- **0.5-0.8**: Medium confidence - reasonable inference
- **< 0.5**: Low confidence - multiple possible explanations; acknowledge uncertainty in the report
