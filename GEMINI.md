# Gemini CLI Agent Guidelines for French Language Learning App

This document outlines the specific instructions and conventions for the Gemini CLI agent when working on the French Language Learning App project. It consolidates critical information from `CLAUDE.md` and other project documentation to ensure consistent and correct operation.

## 🚨 CRITICAL: Tag Content Policy

**TAGS MUST DESCRIBE REAL-WORLD CONTENT TOPICS ONLY.**

-   **NEVER use as tags:** Grammar terms (e.g., listening, conditional), verb names (e.g., aller, être), individual French words (e.g., peu, sûr), or language mechanics (e.g., gender-agreement, tense-forms).
-   **ALWAYS use as tags:** Real situations (e.g., restaurant, workplace, family, travel, news), content themes (e.g., politics, technology, health), or context types (e.g., formal-discussion, casual-conversation).
-   **Core Principle**: Tags describe **WHAT THE SITUATION IS ABOUT** in the real world, not what grammar it tests.
-   Tags should always be in English and lowercase, separated by hyphens.

## 🚨 CRITICAL: Topic Coverage Guidelines

-   **AVOID OVER-COVERED TOPICS:** Minimize new questions about environmental themes.
-   **PRIORITIZE UNDER-COVERED TOPICS:** Focus on daily life situations, hobbies, sports, arts, entertainment, personal relationships, shopping, transportation, healthcare appointments, etc.

## 🚨 CRITICAL: Question File Organization

**DO NOT add new questions to `questions.json` or `questions/questions-{level}.json`.** These are legacy files and should not be modified directly.

### Source/Compile System Architecture:

-   **New Questions**: Must be added to individual source files: `questions/source/q{ID}.json`.
-   **Compilation**: After adding/modifying source files, run `node compile-questions.js` to update the auto-generated compiled files (`questions/q-compiled-{level}.json`).
-   **Application Usage**: The application reads from the compiled files.

### File Structure for New Questions:

-   **Source Files**: `questions/source/q{ID}.json`
-   **Compiled A**: `questions/q-compiled-a.json` (A1 & A2 levels, ID range: 1-199)
-   **Compiled B**: `questions/q-compiled-b.json` (B1 & B2 levels, ID range: 200-399)
-   **Compiled C**: `questions/q-compiled-c.json` (C1 & C2 levels, ID range: 400-999) - *Note: `config.json` defines the actual maxId, currently 999 for 'c' level.*

## 📋 Adding New Questions Workflow

**Correct Sequence: Generate Content & Question Type → Classify Difficulty → Pick ID → Write File.**

### Step 1: Generate Content & Question Type

-   Create French `audioText` with target vocabulary/grammar.
-   Design question and 4 plausible options.
-   Choose question type: `comprehension`, `listening`, `fill-in-the-blank`, `FIB-reading`, `writing`.

### Step 2: Classify Difficulty Level (CEFR Word Limits - Strictly Enforced)

-   Count words in `audioText` to determine CEFR level. Target between 75% and 100% of the max word length for the level:
    -   **A1 Beginner**: Max 9 words
    -   **A2 Elementary**: Max 14 words
    -   **B1 Intermediate**: Max 25 words
    -   **B2 Upper-Intermediate**: Max 38 words
    -   **C1 Advanced**: Max 60 words
    -   **C2 Proficiency**: Max 90 words

### Step 3: Pick Correct ID

-   **Use `util/getid` tool**:
    -   `util/getid a` (for A1/A2)
    -   `util/getid b` (for B1/B2)
    -   `util/getid c` (for C1/C2)
-   **ID Validation**: Always check if the ID returned by `getid` already exists in `questions/source/q{ID}.json`. If it does, increment and check again.

### Step 4: Write Individual Question File

-   Use the skeleton template (`questions/source/_skel.json`) as a guide.
-   Create `questions/source/q{ID}.json` with all mandatory fields.

### Mandatory Fields for Question JSON:

-   `id`: Unique integer in correct range.
-   `audioText`: French text within CEFR word limits.
-   `question`: Clear question in English or French.
-   `questionType`: One of `comprehension`, `listening`, `fill-in-the-blank`, `FIB-reading`, `writing`.
-   `options`: Array of exactly 4 options (empty array `[]` for writing questions).
-   `correct`: Index (0-3) of correct answer (always `0` for writing questions).
-   `explanation`: Detailed explanation following specific formatting guidelines.
-   `difficulty`: Valid CEFR level (e.g., "A1", "B2", "C1").
-   `source`: Brief content source description (e.g., "Gemini CLI").
-   `tags`: Array of relevant content-topic tags.
-   `timeCreated`: Unix timestamp of creation.
-   `parentQuestion`: (Optional) The ID of the original question this question was derived from (e.g., a listening version of a comprehension question).
-   `correctAnswer`: Primary correct answer (required for writing questions).
-   `acceptedAnswers`: Array of acceptable answer variations (required for writing questions).

### Specific `fill-in-the-blank` Rule:

-   **🚨 CRITICAL**: `audioText` must contain the complete sentence with the correct word filled in, NOT underscores (`______`). Only the `question` field should show blanks to users.

### Specific `writing` Question Rules:

-   **🚨 CRITICAL**: Same audioText rule as fill-in-the-blank - complete sentence with correct word, NOT underscores.
-   **Required Fields**: `correctAnswer` (primary answer) and `acceptedAnswers` (array with variations).
-   **Options**: Always empty array `[]`.
-   **Correct**: Always `0` (placeholder).
-   **Example**: `"correctAnswer": "mardis"`, `"acceptedAnswers": ["mardis", "Mardis"]`.
-   **Purpose**: Active vocabulary practice - users must type the correct French word.

### Writing Question Example:

```json
{
    "id": 349,
    "audioText": "Je vais au marché tous les mardis pour acheter des légumes frais.",
    "question": "Je vais au marché tous les ______ pour acheter des légumes frais.",
    "questionType": "writing",
    "options": [],
    "correct": 0,
    "correctAnswer": "mardis",
    "acceptedAnswers": ["mardis", "Mardis"],
    "explanation": "The correct answer is '<em>mardis</em>' (Tuesdays). The complete sentence is '<em>Je vais au marché tous les mardis pour acheter des légumes frais</em>' - I go to the market every Tuesday to buy fresh vegetables. Note that days of the week are plural when used with 'tous les' (every).",
    "difficulty": "A2",
    "source": "Gemini CLI - Writing practice",
    "tags": ["daily-routine", "food", "shopping"],
    "timeCreated": 1720656700
}
```

## 📝 Explanation Formatting Guidelines

**🚨 CRITICAL: All explanations must follow this exact format:**

### For English Questions/Options:
```
"explanation": "The text states '<em>French audioText here</em>' - English translation here. [Grammar explanation with verb conjugation details]."
```

### For French Questions/Options (listening, some fill-in-the-blank):
```
"explanation": "The text states '<em>French audioText here</em>' - English translation here. [Grammar explanation]. The distractors test [list what each distractor tests]."
```

### Key Requirements:
1. **Always start with**: "The text states"
2. **French text styling**: Use `<em>` tags around ALL French text
3. **Include full translation**: Complete English translation after the dash
4. **Grammar explanation**: Explain the specific conjugation, tense, or grammar point
5. **For listening questions ONLY**: Explain what each distractor tests
6. **American English**: Use American idiomatic expressions throughout
7. **🚨 NO distractor discussion**: For comprehension and fill-in-the-blank questions, do NOT explain what distractors test - focus only on the correct answer and grammar

### Examples:

**Good Explanation (Comprehension):**
```
"explanation": "The text states '<em>Elle mange une pomme rouge</em>' - She is eating a red apple. 'Mange' is the third person singular form of 'manger' (to eat), used in the present tense."
```

**Good Explanation (Fill-in-the-blank):**
```
"explanation": "The text states '<em>Je vais au marché</em>' - I am going to the market. 'Vais' is the first person singular form of 'aller' (to go), used in the present tense."
```

**Good Explanation (Listening - distractor discussion allowed):**
```
"explanation": "The text states '<em>Je vais au marché</em>' - I am going to the market. 'Vais' is the first person singular form of 'aller' (to go). The distractors test verb confusion (viens), location confusion (magasin), and tense confusion (allais)."
```

**Bad Explanation (Missing French text and translation):**
```
"explanation": "This tests the present tense conjugation of the verb 'manger'."
```

**Bad Explanation (Distractor discussion in comprehension question):**
```
"explanation": "The text states '<em>Elle mange une pomme rouge</em>' - She is eating a red apple. The distractors test color confusion (verte), fruit confusion (orange), and verb confusion (boit)."
```

## 🚫 Common Mistakes to Avoid

1.  **Never modify `questions.json`, `questions/questions-{level}.json`, or `config.json` unless specifically instructed.**
2.  **Do not exceed CEFR word limits** in `audioText`.
3.  **Do not reuse IDs**.
4.  **Do not use grammar terms, verb names, or individual words as tags**. Tags must be real-world content topics only.
5.  **For fill-in-the-blank questions, `audioText` must contain the complete, correct sentence (no underscores)**.
6.  **Explanation formatting violations**: Missing French text in `<em>` tags, missing English translations, or incomplete grammar explanations.
7.  Always append new question JSON files; do not try to parse and insert in the middle.

## 🛠️ Available Tools (Summary)

-   `util/getid [a|b|c]`: Get the next available question ID.
-   `util/analyze-conjugations.py`: Analyze conjugation coverage.
-   `util/analyze-adjectives.py`: Analyze adjective coverage.
-   `util/analyze-adverbs.py`: Analyze adverb coverage.
-   `util/analyze-questions.sh`: Comprehensive question analysis.
-   `node compile-questions.js`: Compile individual source files into app-ready files.
-   `util/renumber-questions.js` (or `rq` alias): Rename source files and update IDs safely.
-   `jmv` (or `node jmv.js`): Extract individual questions from monolithic files to source files.

## 🧠 System Architecture & Intelligent Selection (High-Level Context)

The application uses a "Pure Intelligent Selection System" for question delivery, eliminating traditional sequential question flows.

-   **No Fixed Sequences**: Questions are selected dynamically based on user performance and learning objectives.
-   **Performance-Driven**: Every question request goes through `findBestQuestionForLevel()`, prioritizing unattempted questions, then questions needing practice (success rate < 70%), then well-practiced questions for review.
-   **Redis for Performance Data**: User performance data is stored in Redis with TTL (Time To Live) settings for automatic expiration, ensuring data freshness and efficient cleanup.
-   **WebSocket Communication**: Performance data is loaded asynchronously via WebSockets.
-   **Repetition Avoidance**: The system tracks recently answered questions to prevent immediate repetition within a session.

## 🎯 Strategic Question Generation Best Practices

### Before Creating Questions:
1. **Run lemma coverage analysis** to identify priority vocabulary gaps:
   ```bash
   python3 util/lemma-coverage.py --limit 20
   ```

2. **Target multiple vocabulary gaps simultaneously** in each question for maximum pedagogical efficiency

3. **Create authentic, compelling scenarios** - avoid generic daily life contexts when possible

### Quality-Focused Generation Prompts:

**Strategic Context-First Approach:**
```
Generate a French [LEVEL] question targeting these priority words: [list].
CONTEXT: Create a realistic scenario where all target words naturally appear
REQUIREMENT: Use compelling story situation, not generic daily life
TECHNICAL: Complete audioText (no blanks), natural French phrasing
```

**Naturalness Test:**
- Would a native French speaker use this exact phrasing?
- Does the scenario feel authentic and believable?
- Are all vocabulary choices contextually appropriate?

**Pedagogical Value Check:**
- Does it test multiple vocabulary gaps efficiently?
- Are distractors pedagogically valuable (not just random)?
- Does the explanation teach beyond just the answer?

### Common Generation Issues to Avoid:
- **Awkward word cramming**: Don't force vocabulary together unnaturally
- **Generic contexts**: "Traffic," "weather" - use specific, interesting scenarios
- **Single-word focus**: Target 2-3 priority words per question when possible
- **Temporal confusion**: Especially with adverbs like "précédemment"

## 🔍 Quality Checklist (Before Finalizing Changes)

-   Word count within CEFR limits.
-   Correct file for difficulty level.
-   Unique ID in proper range.
-   All mandatory fields present.
-   **Explanation follows exact formatting**: Starts with "The text states", includes French text in `<em>` tags, complete English translation, and detailed grammar explanation.
-   **Tags are CONTENT TOPICS only (no grammar/verb names/individual words)**.
-   Options are plausible but only one correct.
-   **Natural French phrasing**: Would native speakers use this exact sentence?
-   **Strategic vocabulary targeting**: Multiple priority words in natural context.
-   JSON syntax is valid.
-   Run `node compile-questions.js` after any question changes.
-   Run `python3 util/analyze-conjugations.py`, `python3 util/analyze-adjectives.py`, `python3 util/analyze-adverbs.py`, and `bash util/analyze-questions.sh` to verify coverage.