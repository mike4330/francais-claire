# French Language Learning System - Claude Code Assistant

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

**DO NOT add new questions to `questions.json` - this is the original/legacy file and should not be modified.**

### File Structure for New Questions:
- **`questions-a.json`** → A1 & A2 levels (ID range: 34-199)
- **`questions-b.json`** → B1 & B2 levels (ID range: 200-399)  
- **`questions-c.json`** → C1 & C2 levels (ID range: 400-499)

## 📋 Adding New Questions

### Step 1: Determine CEFR Level & Target File
- **A1 Beginner** (max 9 words) → `questions-a.json`
- **A2 Elementary** (max 14 words) → `questions-a.json`
- **B1 Intermediate** (max 25 words) → `questions-b.json`
- **B2 Upper-Intermediate** (max 38 words) → `questions-b.json`
- **C1 Advanced** (max 60 words) → `questions-c.json`
- **C2 Proficiency** (max 90 words) → `questions-c.json`

### Step 2: ID Assignment
**🛠️ Use the `getid` tool to automatically determine the next available ID:**

```bash
# Get next ID for A1/A2 levels (questions-a.json)
./getid a

# Get next ID for B1/B2 levels (questions-b.json) 
./getid b

# Get next ID for C1/C2 levels (questions-c.json)
./getid c
```

**Manual fallback** - Check existing IDs in target file and assign next available ID:
- **questions-a.json**: ID range 34-199
- **questions-b.json**: ID range 200-399
- **questions-c.json**: ID range 400-499

### Step 3: Question Structure Template

```json
{
    "id": [NEXT_AVAILABLE_ID],
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

### Step 4: Required Fields Validation

**✅ Mandatory Fields:**
- `id`: Unique integer in correct range
- `audioText`: French text within CEFR word limits
- `question`: Clear question in English or French
- `questionType`: One of the three valid types
- `options`: Array of exactly 4 options
- `correct`: Index (0-3) of correct answer
- `explanation`: Detailed explanation
- `difficulty`: Valid CEFR level
- `source`: Brief content source
- `tags`: Array of relevant tags
- `timeCreated`: Time of question creation in Unix time

**🎯 Optional Fields:**
- `parentQuestion`: ID of related comprehension question (for listening variants)
- `audioTemplate`: Template for variable content
- `templateVariables`: Variables for templates

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
- [ ] **Tags are CONTENT TOPICS only (no grammar/verb names/individual words)**
- [ ] Options are plausible but only one correct
- [ ] JSON syntax is valid

## 🛠️ Available Tools

### ID Assignment Tool
Get the next available ID for any CEFR level:
```bash
./getid [a|b|c]  # a=A1/A2, b=B1/B2, c=C1/C2
```

### Question Analysis
After adding questions, run analysis:
```bash
bash analyze-questions.sh
```

## 🚫 Common Mistakes to Avoid

1. **Never modify `questions.json`** - legacy file
2. **Don't exceed word limits** - breaks CEFR classification
3. **Don't reuse IDs** - causes conflicts
4. **Don't forget parentQuestion** - for listening variants
5. **🚨 CRITICAL: Don't use grammar/verb/word tags** - tags must be real-world content topics only
6. **Don't create implausible distractors** - reduces pedagogical value
7. **Always append the question json files** - don't try to parse and insert in the middle
8. **🚨 CRITICAL: Fill-in-the-blank `audioText` must contain complete sentences** - Never use literal underscores `______` in `audioText` field for fill-in-the-blank questions. The `audioText` must contain the complete French sentence with the correct word filled in for proper audio synthesis. Only the `question` field should show blanks to users.

## 🎯 Claude Code Specific Instructions

### Task Management
- Use TodoWrite/TodoRead tools to track multi-step tasks
- Mark todos as completed immediately after finishing each step
- Only have one task in_progress at a time

### Testing Commands
After making changes, run:
```bash
# Lint and validate JSON files
npm run lint

# Type checking (if applicable)
npm run typecheck

# Run question analysis
bash analyze-questions.sh
```

### Code Style
- Follow existing patterns in the codebase
- Maintain consistent JSON formatting
- Use appropriate French diacritical marks
- Ensure proper Unicode encoding for French characters