# French Language Learning System - Claude Code Assistant

## Base directory the project is /var/www/html/language/

## 🚨 CRITICAL: Tag Content Policy

**TAGS MUST DESCRIBE REAL-WORLD CONTENT TOPICS ONLY**

❌ **NEVER use these as tags:**
- Grammar terms (listening, conditional, imperfect, subjunctive)
- Verb names (aller, être, avoir, faire, dire, voir, parler, aimer)  
- Individual French words (peu, sûr, beau, seul, heureux, pauvre)
- Language mechanics (gender-agreement, exact-comprehension, tense-forms)

✅ **ALWAYS use these instead:**
- Real situations (restaurant, workplace, family, travel, news)
- Content themes (politics, technology, health, education, business)
- Context types (formal-discussion, casual-conversation, media-coverage)

**Think: "What real-world situation is this question about?" NOT "What grammar does it test?"**


## 🚨 CRITICAL: Question File Organization

**NEW QUESTIONS**: Add to individual `questions/source/q{ID}.json` files → Compile with `node compile-questions.js`

**File Structure**:
- **Compiled A**: A1 & A2 levels (ID: 1-199) → `questions/q-compiled-a.json`
- **Compiled B**: B1 & B2 levels (ID: 200-399) → `questions/q-compiled-b.json`  
- **Compiled C**: C1 & C2 levels (ID: 400-510) → `questions/q-compiled-c.json`

## 🎯 Strategic Question Creation

**Before adding questions, use data-driven analysis to identify the highest-priority vocabulary gaps.**

### Running Lemma Coverage Analysis

Use the comprehensive lemma analysis tool to identify coverage gaps:

```bash
cd util
python3 lemma-coverage.py --limit 20
```

**Target high-frequency lemmas with low coverage. Create questions addressing multiple gaps simultaneously.**



## 📋 Adding New Questions

**🔄 CORRECT SEQUENCE: Analyze → Generate → Classify → Pick ID → Write**

### Step 1: Generate Content & Question Type
- Create French `audioText` with target vocabulary/grammar
- Design appropriate question and 4 plausible options
- Choose question type: comprehension, listening, fill-in-the-blank, FIB-reading

### Step 2: Classify Difficulty Level
- Count words in `audioText` to determine CEFR level:
  - **A1 Beginner** (max 9 words) → `questions-a.json`
  - **A2 Elementary** (max 14 words) → `questions-a.json`
  - **B1 Intermediate** (max 25 words) → `questions-b.json`
  - **B2 Upper-Intermediate** (max 38 words) → `questions-b.json`
  - **C1 Advanced** (max 60 words) → `questions-c.json`
  - **C2 Proficiency** (max 90 words) → `questions-c.json`

### Step 3: Pick Correct ID
```bash
./getid [a|b|c]  # Get next ID (a=A1/A2, b=B1/B2, c=C1/C2)
[ ! -f "questions/source/q${ID}.json" ] && echo "✅ Available" || echo "❌ Exists"
```

### Step 4: Write Individual Question File
Create `questions/source/q{ID}.json` with all mandatory fields, then `node compile-questions.js`


**Mandatory Fields**: `id`, `audioText`, `question`, `questionType`, `options`, `correct`, `explanation`, `difficulty`, `source`, `tags`, `timeCreated`
**Writing Questions**: Add `correctAnswer`, `acceptedAnswers`

## 📝 Content Guidelines

### CEFR Word Limits (Strictly Enforced):
- **A1**: Maximum 9 words
- **A2**: Maximum 14 words  
- **B1**: Maximum 25 words
- **B2**: Maximum 38 words
- **C1**: Maximum 60 words
- **C2**: Maximum 90 words

### Question Types:

1. **comprehension**: English question testing understanding
   - Focus on main ideas, details, implications
   - 4 plausible options with clear correct answer

2. **listening**: French "Qu'est-ce que vous avez entendu?"
   - Test exact auditory comprehension
   - Options in French with subtle variations
   - Often paired with comprehension question via `parentQuestion`

3. **fill-in-the-blank**: Missing word completion
   - Question format: "Text with ______ gap"
   - Test vocabulary and grammar knowledge
   - **🚨 CRITICAL**: `audioText` must contain complete sentence with correct word, NOT underscores!
   - **Example**: ✅ `"audioText": "Tu aimes cette chose rouge ?"` ❌ `"audioText": "Tu ______ cette chose rouge ?"`

4. **writing**: Active vocabulary practice with text input
   - Question format: "Text with ______ gap"
   - User must type the correct French word
   - **🚨 CRITICAL**: `audioText` must contain complete sentence with correct word, NOT underscores!
   - **Fields**: `correctAnswer` (primary answer), `acceptedAnswers` (variations including capitalization)
   - **Options**: Empty array `[]`
   - **Correct**: Always `0` (placeholder)
   - **Example**: `"correctAnswer": "mardis"`, `"acceptedAnswers": ["mardis", "Mardis"]`

### Explanation Guidelines:

**🚨 CRITICAL: French Translation Requirement**
- **If question and options are in English**: The explanation MUST include the full French translation of the `audioText`
- **Purpose**: Ensures learners understand the French content even when the interface is in English
- **Format**: Include French text followed by " - " and English translation
- **French Text Styling**: All French text in explanations should be italicized using `<em>` tags
- **Example**: ✅ `"The text states '<em>Je mange une pomme rouge</em>' - I am eating a red apple."`

**🚨 CRITICAL: Avoid Meta-Commentary in Explanations**
- **Never reference the question bank**: Don't mention what's "missing from our question bank" or "completely missing from our question bank"
- **Never reference coverage analysis**: Don't mention lemma frequency, coverage percentages, or strategic targeting
- **Never reference difficulty levels**: Don't mention "C1-level text", "appropriate for B2 learners", "advanced C2 structure", etc.
- **Focus on the learning**: Explanations should teach the language, not discuss the question creation process or classification system
- **❌ FORBIDDEN**: "The adjective 'premier/première' was completely missing from our question bank despite being very frequent."
- **❌ FORBIDDEN**: "This C1-level text discusses complex economic concepts."
- **✅ CORRECT**: "The correct form is 'première' (first) - feminine form agreeing with 'fois' (time)."

### Tag Guidelines:
Use descriptive, lowercase tags separated by hyphens for **CONTENT TOPICS ONLY**:

**✅ GOOD TAGS (Real-world topics):**
- **Topics**: politics, weather, food, technology, health, business, travel, education
- **Context**: restaurant, workplace, family, news, conversation, formal-situation
- **Content type**: scientific-discussion, casual-chat, media-coverage

**❌ FORBIDDEN TAGS (Learning mechanics):**
- **Grammar terms**: listening, comprehension, fill-in-the-blank, conditional, imperfect, subjunctive
- **Verb names**: aller, avoir, être, faire, dire, voir, venir, parler, aimer
- **Individual words**: peu, beaucoup, sûr, vrai, beau, seul, heureux, pauvre
- **Language mechanics**: gender-agreement, verb-conjugation, tense-forms, exact-comprehension

**🎯 Core Principle**: Tags describe **WHAT THE SITUATION IS ABOUT** in the real world, not how the French language works.

**Examples**:
- ✅ "restaurant, service, politeness" (real situation)
- ❌ "conditional, parler, second-person" (grammar mechanics)

Tags should always be in English and focus on **content themes** that help learners find topics they're interested in.

## 🔍 Quality Checklist

Before adding a question:
- [ ] Word count within CEFR limits
- [ ] Correct file for difficulty level
- [ ] Unique ID in proper range
- [ ] All mandatory fields present
- [ ] Explanation references specific French phrases
- [ ] **If English question/options: Full French translation included in explanation**
- [ ] **Explanation avoids meta-commentary about question bank, coverage analysis, or difficulty levels**
- [ ] **Tags are CONTENT TOPICS only (no grammar/verb names/individual words)**
- [ ] Options are plausible but only one correct
- [ ] JSON syntax is valid

## 🛠️ Available Tools

```bash
./getid [a|b|c]                    # Get next available ID
./questions/source/rq <old> <new>  # Renumber questions safely  
node compile-questions.js          # Compile source files
python3 util/lemma-coverage.py     # Analyze vocabulary gaps
bash util/analyze-questions.sh     # Full question analysis
```

## 🚫 Common Mistakes to Avoid

2. **Don't exceed word limits** - breaks CEFR classification
3. **Don't reuse IDs** - causes conflicts
4. **Don't forget parentQuestion** - for listening variants
5. **🚨 CRITICAL: Don't use grammar/verb/word tags** - tags must be real-world content topics only
6. **Don't create implausible distractors** - reduces pedagogical value
7. **Always append the question json files** - don't try to parse and insert in the middle
8. **🚨 CRITICAL: Fill-in-the-blank `audioText` must contain complete sentences** - Never use literal underscores `______` in `audioText` field for fill-in-the-blank questions. The `audioText` must contain the complete French sentence with the correct word filled in for proper audio synthesis. Only the `question` field should show blanks to users.
9. **🚨 CRITICAL: Writing questions follow same audioText rule** - Like fill-in-the-blank, writing questions must have complete sentences in `audioText` field. The gap (`______`) only appears in the `question` field for user display.
10. **🚨 CRITICAL: Writing questions need correctAnswer and acceptedAnswers** - Don't forget to include both `correctAnswer` (primary answer) and `acceptedAnswers` (array with variations) for proper answer validation.
11. **🚨 CRITICAL: Avoid proper names in questions** - Never include specific people's names (like "Sophie Bauer", "Marie Dupont", etc.) in questions as they add unnecessary complexity without pedagogical value. Use generic references like "le médecin", "la femme", "l'homme", "le professeur" instead.
12. **🚨 CRITICAL: Don't include meta-commentary in explanations** - Never reference the question bank, coverage analysis, strategic targeting, or difficulty levels in explanations. Focus on teaching the language, not discussing the question creation process or classification system.
13. **🚨 CRITICAL: Level reclassification requires renumbering** - If you change a question's difficulty level (e.g., A2 → B1), the question MUST be renumbered to fit the correct ID range. Use `questions/source/rq <old_id> <new_id>` tool to safely renumber questions with automatic Redis data migration and parent question reference updates.

## 🎯 Claude Code Specific Instructions

### Task Management
- Use TodoWrite/TodoRead tools to track multi-step tasks
- Mark todos as completed immediately after finishing each step
- Only have one task in_progress at a time


## 🏗️ Architecture: Pure Intelligent Selection

**Added**: Direct question loading by ID, performance-driven selection for every question
**Result**: True intelligent progression with anti-repetition and timestamp tracking


## 🧠 Intelligent Question Selection System

**4-Tier Priority System**: Early intervention for struggling questions → Unattempted → Practice needed (<70% success) → Review mastered
**Performance Data**: WebSocket loads user performance from Redis for adaptive selection
**Anti-Repetition**: Timestamp filtering prevents cycling through recent questions

