# Gemini Assistant - Core Task Instructions

This document contains the essential instructions for managing questions in this application, derived from `CLAUDE.md` and `README.md`.

## 🚨 Core Workflow: Adding a New Question

The system uses a source/compile model. New questions are added to individual source files, then compiled into application-ready files.

**🔄 Sequence: Generate → Classify → Pick ID → Write → Compile**

### Step 1: Classify Difficulty Level
Classification is based on the word count in the `audioText`.

| CEFR Level | Max Words | ID Range  | Target Compiled File |
|------------|-----------|-----------|----------------------|
| A1/A2      | 9 / 14    | 1-199     | `q-compiled-a.json`  |
| B1/B2      | 25 / 38   | 200-399   | `q-compiled-b.json`  |
| C1/C2      | 60 / 90   | 400-510   | `q-compiled-c.json`  |

### Step 2: Pick Correct ID
Use the `getid` tool to find the next available ID for the target level.

```bash
# For A1/A2 levels
./util/getid a

# For B1/B2 levels 
./util/getid b

# For C1/C2 levels
./util/getid c
```
Before creating the file, quickly validate the chosen ID does not already exist in the source directory: `ls questions/source/q{ID}.json`.

### Step 3: Write Individual Question File
Create a new file in `questions/source/q{ID}.json`, replacing `{ID}` with the number from Step 2.

### Step 4: Populate JSON Content
The file must contain a JSON object with the following structure:

```json
{
    "id": [ID_FROM_STEP_2],
    "audioText": "[French text - must respect CEFR word limits]",
    "question": "[English comprehension question OR 'Qu'est-ce que vous avez entendu?' for listening]",
    "questionType": "comprehension" | "listening" | "fill-in-the-blank",
    "options": [
        "[Option A]",
        "[Option B]", 
        "[Option C]",
        "[Option D]"
    ],
    "correct": [0-3],
    "explanation": "[Detailed explanation in English]",
    "difficulty": "[A1|A2|B1|B2|C1|C2]",
    "source": "[Content source description]",
    "tags": ["tag1", "tag2", "tag3"],
    "timeCreated": [Unix timestamp]
}
```

### Step 5: Compile Changes
After creating the source file, run the compilation script:
```bash
node compile-questions.js
```

## 📋 Critical Policies & Guidelines

### 1. Tagging Policy
**TAGS MUST DESCRIBE REAL-WORLD CONTENT TOPICS ONLY.**

- ✅ **GOOD TAGS (Real-world topics):**
  - **Topics**: politics, weather, food, technology, health, business, travel, education
  - **Context**: restaurant, workplace, family, news, conversation, formal-situation

- ❌ **FORBIDDEN TAGS (Learning mechanics):**
  - **Grammar terms**: listening, conditional, imperfect, subjunctive
  - **Verb names**: aller, avoir, être, faire, dire, voir
  - **Individual words**: peu, sûr, beau, seul, heureux
  - **Language mechanics**: gender-agreement, tense-forms

### 2. File Editing Policy
- **NEVER** directly modify `questions.json`, `questions-a.json`, `questions-b.json`, `questions-c.json`, or `q-compiled-*.json`.
- **ALWAYS** add new questions by creating new files in the `questions/source/` directory.

### 3. "Fill-in-the-Blank" `audioText` Rule
- For `fill-in-the-blank` questions, the `audioText` field **MUST** contain the complete, correct sentence.
- The `question` field should contain the text with the blank (e.g., `Tu ______ cette chose rouge ?`).
- **Correct `audioText`**: `"Tu aimes cette chose rouge ?"`
- **Incorrect `audioText`**: `"Tu ______ cette chose rouge ?"`
