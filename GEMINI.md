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
-   Choose question type: `comprehension`, `listening`, `fill-in-the-blank`, `FIB-reading`.

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
-   `questionType`: One of `comprehension`, `listening`, `fill-in-the-blank`, `FIB-reading`.
-   `options`: Array of exactly 4 options.
-   `correct`: Index (0-3) of correct answer.
-   `explanation`: Detailed explanation following specific formatting guidelines.
-   `difficulty`: Valid CEFR level (e.g., "A1", "B2", "C1").
-   `source`: Brief content source description (e.g., "Gemini CLI").
-   `tags`: Array of relevant content-topic tags.
-   `timeCreated`: Unix timestamp of creation.

### Specific `fill-in-the-blank` Rule:

-   **🚨 CRITICAL**: `audioText` must contain the complete sentence with the correct word filled in, NOT underscores (`______`). Only the `question` field should show blanks to users.

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
5. **For listening questions**: Explain what each distractor tests
6. **American English**: Use American idiomatic expressions throughout

### Examples:

**Good Explanation (Comprehension):**
```
"explanation": "The text states '<em>Elle mange une pomme rouge</em>' - She is eating a red apple. 'Mange' is the third person singular form of 'manger' (to eat), used in the present tense."
```

**Good Explanation (Listening):**
```
"explanation": "The text states '<em>Je vais au marché</em>' - I am going to the market. 'Vais' is the first person singular form of 'aller' (to go). The distractors test verb confusion (viens), location confusion (magasin), and tense confusion (allais)."
```

**Bad Explanation (Missing French text and translation):**
```
"explanation": "This tests the present tense conjugation of the verb 'manger'."
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

## 🔍 Quality Checklist (Before Finalizing Changes)

-   Word count within CEFR limits.
-   Correct file for difficulty level.
-   Unique ID in proper range.
-   All mandatory fields present.
-   **Explanation follows exact formatting**: Starts with "The text states", includes French text in `<em>` tags, complete English translation, and detailed grammar explanation.
-   **Tags are CONTENT TOPICS only (no grammar/verb names/individual words)**.
-   Options are plausible but only one correct.
-   JSON syntax is valid.
-   Run `node compile-questions.js` after any question changes.
-   Run `python3 util/analyze-conjugations.py`, `python3 util/analyze-adjectives.py`, `python3 util/analyze-adverbs.py`, and `bash util/analyze-questions.sh` to verify coverage.