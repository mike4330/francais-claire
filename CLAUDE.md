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

**DO NOT add new questions to `questions.json` - this is the original/legacy file and should not be modified.**

### 🏗️ Source/Compile System Architecture

**NEW QUESTIONS MUST BE ADDED TO INDIVIDUAL SOURCE FILES:**

- **Individual Source Files**: `questions/source/q{ID}.json` (e.g., `q362.json`)
- **Compiled Files**: `questions/q-compiled-{level}.json` (auto-generated)
- **Legacy Files**: `questions/questions-{level}.json` (minimal placeholders)

### Workflow:
1. **Create**: Add new question to `questions/source/q{ID}.json`
2. **Compile**: Run `node compile-questions.js` to update compiled files
3. **App Usage**: Application reads from compiled files

### File Structure for New Questions:
- **Source Files**: `questions/source/q{ID}.json` → Individual question files
- **Compiled A**: `questions/q-compiled-a.json` → A1 & A2 levels (ID range: 1-199)
- **Compiled B**: `questions/q-compiled-b.json` → B1 & B2 levels (ID range: 200-399)  
- **Compiled C**: `questions/q-compiled-c.json` → C1 & C2 levels (ID range: 400-510)

## 🎯 Strategic Question Creation

**Before adding questions, use data-driven analysis to identify the highest-priority vocabulary gaps.**

### Running Lemma Coverage Analysis

Use the comprehensive lemma analysis tool to identify coverage gaps:

```bash
cd util
python3 lemma-coverage.py --limit 20
```

**This analysis provides:**
- **Verb Conjugation Gaps**: Missing conjugated forms of high-frequency verbs (sorted by Lexique frequency)
- **Adjective Coverage**: Adjectives needing attention based on questions-containing-lemma methodology  
- **Adverb Coverage**: High-frequency adverbs with low question bank representation
- **Noun Coverage**: Essential nouns below optimal coverage thresholds
- **Question Type Distribution**: Balance of comprehension vs listening vs fill-in-the-blank
- **CEFR Level Distribution**: Identify under-represented difficulty levels

### Strategic Targeting Methodology

**✅ PRIORITIZE: Questions that address multiple gaps simultaneously**

Create questions targeting:
1. **High-frequency lemmas** (top of analysis priority lists)
2. **Under-represented CEFR levels** (check statistics section)
3. **Imbalanced question types** (ensure variety)
4. **Cross-category synergies** (verb + adjective + noun + adverb combinations)

### Example Strategic Workflow:

```bash
# 1. Run analysis
python3 lemma-coverage.py --limit 15

# 2. Identify targets (example results):
#    - Verb: "rendrait" (conditional, missing)  
#    - Adjective: "normal" (0.2% coverage)
#    - Noun: "chance" (0.3% coverage)
#    - Adverb: "précisément" (0.001% coverage)

# 3. Create synergistic question:
#    "Cette formation normale rendrait précisément plus de chances..."
#    (Targets 4 vocabulary gaps in one question)

# 4. Verify improvements with follow-up analysis
```

### Coverage Improvement Tracking

The questions-containing-lemma methodology (used for nouns and adjectives) provides stable metrics:
- **Before**: "normal" in 3 questions (0.3% coverage)  
- **After**: "normal" in 4 questions (0.4% coverage)
- **Progress**: +33% improvement visible immediately

**Key Benefits:**
- **Immune to expanding denominator problem**: Coverage percentages remain meaningful as question bank grows
- **Pedagogically relevant**: Tracks actual learning opportunities, not just word frequency
- **Actionable targets**: Clear thresholds (e.g., "get this word to 2% coverage")

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
**🛠️ Use the `getid` tool to automatically determine the next available ID:**

```bash
# Get next ID for A1/A2 levels (questions-a.json)
./getid a

# Get next ID for B1/B2 levels (questions-b.json) 
./getid b

# Get next ID for C1/C2 levels (questions-c.json)
./getid c

# note: getid can be run with the switch '-a' to generate a simple oneline tuple output of available ranges for all levels
```

**ID Validation Workflow:**
Since the `getid` tool checks monolithic files (which may be outdated compared to source files), validate the ID before creating:

```bash
# Step 1: Get next ID quickly (token-efficient)
NEXT_ID=$(./util/getid b)

# Step 2: Quick validation to prevent conflicts
[ ! -f "questions/source/q${NEXT_ID}.json" ] && echo "✅ ID $NEXT_ID available" || echo "❌ ID $NEXT_ID exists, try $((NEXT_ID + 1))"
```

If conflict exists, increment ID and check again. This hybrid approach balances speed with safety.

**ID Ranges by Difficulty:**
- **questions-a.json**: ID range 1-199 (A1/A2)
- **questions-b.json**: ID range 200-399 (B1/B2)
- **questions-c.json**: ID range 400-499 (C1/C2)

### Step 4: Write Individual Question File

**🔧 Use the skeleton template for easier file creation:**

```bash
# Copy template and replace ID
cp questions/source/_skel.json questions/source/q{ID}.json
```

**Template file**: `questions/source/_skel.json` contains all required fields with placeholder values. This avoids Write tool restrictions and ensures consistent structure.

**Create file**: `questions/source/q{ID}.json`

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

**After creating source file, compile:**
```bash
node compile-questions.js
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

### Explanation Guidelines:

**🚨 CRITICAL: French Translation Requirement**
- **If question and options are in English**: The explanation MUST include the full French translation of the `audioText`
- **Purpose**: Ensures learners understand the French content even when the interface is in English
- **Format**: Include French text followed by " - " and English translation
- **French Text Styling**: All French text in explanations should be italicized using `<em>` tags
- **Example**: ✅ `"The text states '<em>Je mange une pomme rouge</em>' - I am eating a red apple."`

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
- [ ] **Tags are CONTENT TOPICS only (no grammar/verb names/individual words)**
- [ ] Options are plausible but only one correct
- [ ] JSON syntax is valid

## 🛠️ Available Tools

### ID Assignment Tool
Get the next available ID for any CEFR level (reads from `config.json`):
```bash
./util/getid [a|b|c]  # a=A1/A2, b=B1/B2, c=C1/C2
```
**Features**: Shows level description, ID range, and next available ID with enhanced output.

### Question Renumbering Tool
Rename source files and update IDs safely:
```bash
cd questions/source
./rq <old_id> <new_id>

# Example:
./rq 499 412  # Rename q499.json to q412.json and update ID field
```

**What it does:**
1. Renames `qOLD.json` to `qNEW.json`
2. Updates the `"id"` field inside the JSON file
3. Creates automatic backup files
4. Validates new ID doesn't already exist
5. Checks for parent question references that might need updating

**Safety Features**:
- Creates timestamped backups before changes
- Validates inputs and file existence
- Warns about parent question dependencies
- Provides clear next steps (recompile, check references)

### JSON Move Tool (jmv)
Extract individual questions from monolithic files to source files:
```bash
./jmv <question_id> <source_file>

# Examples:
./jmv 132 questions-a.json         # Move question 132 to questions/source/q132.json
./jmv 250 questions-b.json         # Move question 250 to questions/source/q250.json
node jmv.js 400 questions-c.json   # Alternative: use node directly
```

**What it does:**
1. Finds the question with specified ID in the source file
2. Creates `questions/source/q{id}.json` with that question
3. Removes the question from the original file
4. Preserves JSON formatting and structure

**Use cases:**
- Migrating questions from monolithic files to individual source files
- Moving questions you want to edit individually
- Converting legacy structure to new individual file workflow

### Question Compilation
Compile individual source files into app-ready files:
```bash
node compile-questions.js
```

**Features**: 
- Reads level ranges from `config.json`
- Combines source files into compiled files by difficulty
- Shows detailed statistics and conflict detection

### Question Analysis
After adding questions, run comprehensive analysis:
```bash
bash util/analyze-questions.sh
```

**Enhanced Features**:
- Uses compiled files as primary source
- Analyzes vocabulary coverage against Lexique frequency data
- Tag frequency analysis with source file support
- CEFR difficulty distribution
- Question type breakdown

## 🚫 Common Mistakes to Avoid

1. **Never modify `questions.json`** - legacy file
2. **Don't exceed word limits** - breaks CEFR classification
3. **Don't reuse IDs** - causes conflicts
4. **Don't forget parentQuestion** - for listening variants
5. **🚨 CRITICAL: Don't use grammar/verb/word tags** - tags must be real-world content topics only
6. **Don't create implausible distractors** - reduces pedagogical value
7. **Always append the question json files** - don't try to parse and insert in the middle
8. **🚨 CRITICAL: Fill-in-the-blank `audioText` must contain complete sentences** - Never use literal underscores `______` in `audioText` field for fill-in-the-blank questions. The `audioText` must contain the complete French sentence with the correct word filled in for proper audio synthesis. Only the `question` field should show blanks to users.
9. **🚨 CRITICAL: Avoid proper names in questions** - Never include specific people's names (like "Sophie Bauer", "Marie Dupont", etc.) in questions as they add unnecessary complexity without pedagogical value. Use generic references like "le médecin", "la femme", "l'homme", "le professeur" instead.

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

## 🏗️ Architecture Changes (July 2025)

### Pure Intelligent Selection System
The app has been completely redesigned to eliminate traditional question sequences in favor of adaptive, performance-driven question delivery.

#### **Key Architectural Changes:**

**🚫 Removed Components:**
- `questions[]` array (filtered by difficulty)
- `currentQuestion` index tracking
- `filterQuestionsByDifficulty()` function
- `nextQuestionSequential()` function
- Array shuffling logic
- Index-based question navigation

**✅ New Components:**
- `currentQuestionData` - holds current question object directly
- `loadQuestion(questionId)` - loads questions by ID from `questionBank`
- Pure intelligent selection for every question request
- `userAnswers.push()` - dynamic tracking by question ID
- Enhanced performance tracking with `lastAnswered` timestamps

#### **How It Works:**
1. **Every Question Request**: Goes through `findBestQuestionForLevel()`
2. **Direct Loading**: `loadQuestion(questionId)` finds questions in `questionBank` by ID
3. **No Sequences**: Questions selected purely on learning objectives and performance
4. **Dynamic Progress**: Score based on `userAnswers.length`, not array position

#### **Benefits:**
- 🎯 **True intelligent selection** for every question
- 🚫 **No array/index mismatches** 
- 🧹 **Cleaner code** - removed 100+ lines of array management
- ⚡ **Better performance** - no shuffling or filtering overhead
- 🔄 **Consistent behavior** - same selection logic everywhere

#### **Performance Tracking Enhancements:**
- **`lastAnswered` Field**: Every performance record includes timestamp
- **Time-Aware Debugging**: Console logs show "Question 403 last answered 2 days 3 hours ago"
- **Anti-Repetition Logic**: Uses timestamps to avoid recently answered questions
- **Future-Ready**: Enables spaced repetition and forgetting curve algorithms

### Configuration System
Level ranges are now centralized in `config.json`:

```json
{
    "levelRanges": {
        "a": { "levels": ["A1", "A2"], "minId": 1, "maxId": 199 },
        "b": { "levels": ["B1", "B2"], "minId": 200, "maxId": 399 },
        "c": { "levels": ["C1", "C2"], "minId": 400, "maxId": 510 }
    }
}
```

**Tools Updated to Use Config:**
- `getid` - reads ranges from config.json
- `compile-questions.js` - dynamic range loading
- All ID validation uses centralized ranges

## 🧠 Intelligent Question Selection System

### Overview
The system uses intelligent question selection to provide personalized learning experiences based on user performance data stored in Redis via WebSocket connections.

### Two UI Paths for Level Selection

#### Path 1: Main Page Level Buttons (`french_listening_app.html`)
- **Trigger**: User clicks difficulty level buttons (A1, A2, B1, B2, C1, C2)
- **Function**: `selectDifficulty(level)` → `loadUserPerformanceDataThenStart(level)`
- **Process**: 
  1. Loads user performance data via WebSocket
  2. Waits for data to load asynchronously
  3. Calls `findBestQuestionForLevel(level)` with loaded performance data
  4. Starts quiz with intelligently selected question

#### Path 2: Student Dashboard Level Cards (`student.html`)
- **Trigger**: User clicks pre-calculated level progress cards
- **Function**: `launchQuizWithLevel(level, questionId)` 
- **Process**:
  1. Performance data already loaded when cards are rendered
  2. Best question pre-calculated during card generation
  3. Redirects to main app with `?start=${questionId}` parameter

### Intelligent Selection Algorithm (`findBestQuestionForLevel`)

**Priority 1: Unattempted Questions**
- Selects questions the user has never attempted
- Chooses lowest ID for consistent progression
- Reason: New learning opportunities

**Priority 2: Questions Needing Practice**
- Selects questions with success rate < 70%
- Chooses lowest ID needing practice
- Reason: Reinforce weak areas

**Priority 3: Review Well-Practiced Questions**
- When all questions are mastered (≥70% success rate)
- Selects lowest ID for systematic review
- Reason: Maintain proficiency

### WebSocket Performance Data Structure
```javascript
{
  type: "user_question_performance_result",
  uuid: "user-uuid",
  questionPerformances: [
    {
      questionId: 201,
      successRate: 83,
      totalAttempts: 6,
      correctAttempts: 5,
      avgResponseTime: 30478
    }
  ],
  totalQuestionsAttempted: 146
}
```

### Redis Data Expiration Settings

Performance data is automatically expired using Redis TTL (Time To Live) settings in `redis-cache-server.js`:

#### Expiration Parameters (redis-cache-server.js)

| Data Type | Redis Key Pattern | Duration | Line | Purpose |
|-----------|------------------|----------|------|---------|
| **Individual Responses** | `response:uuid:questionId:timestamp` | 90 days (7,776,000 sec) | 463 | Detailed response tracking |
| **User Question Stats** | `user_question:uuid:questionId` | 1 year (31,536,000 sec) | 518 | Per-user question performance |
| **Global Question Stats** | `question_stats:questionId` | 1 year (31,536,000 sec) | 488 | Overall question analytics |
| **Audio Cache** | `audio:cacheKey` | 30 days (2,592,000 sec) | N/A | TTS/Polly audio files |

#### Implementation Details
```javascript
// Individual responses (90 days)
await redisClient.setEx(responseKey, 7776000, JSON.stringify(responseData));

// User question performance (1 year) 
await redisClient.expire(userQuestionKey, 31536000);

// Global question statistics (1 year)
await redisClient.expire(questionStatsKey, 31536000);
```

**Automatic Cleanup**: Redis handles expiration automatically - no cron jobs needed. Each time a user answers a question, the expiration timer resets, keeping active users' data fresh while inactive data expires naturally.

### Key Implementation Details

#### WebSocket Response Handler
```javascript
// Correct field name is 'questionPerformances', not 'performances'
userPerformanceData = data.questionPerformances || [];
```

#### Async Flow Management
- Uses `window.pendingLevelStart` to store level selection until data loads
- Implements retry mechanism for WebSocket connection delays
- Falls back to random selection if performance data unavailable

#### Debug Output
Enable debug logging to monitor intelligent selection:
```javascript
console.log(`[DEBUG-2] 📊 Loaded ${userPerformanceData.length} user performance records`);
console.log(`[DEBUG-2] 📈 User has performance data for: ${performanceCount} questions in ${level} level`);
```

### Recent Fixes Applied

1. **Fixed WebSocket Data Loading**: Main page level buttons now properly load performance data before question selection
2. **Corrected Data Field Name**: Changed from `data.performances` to `data.questionPerformances` 
3. **Added Retry Logic**: Handles WebSocket connection timing issues
4. **Enhanced Debug Logging**: Better visibility into selection process
5. **🆕 MAJOR: Intelligent Question Progression**: Every question now uses intelligent selection, not just the first one

### Intelligent Progression System

**Previous Behavior**: Intelligent selection only for first question → sequential/random progression
**New Behavior**: Intelligent selection for every question with repetition avoidance

#### Algorithm Enhancements
- **Exclusion Logic**: Prevents immediate repetition by excluding recently answered questions
- **Session Memory**: Tracks last 3 questions to avoid cycling
- **Fallback Safety**: Falls back to sequential if intelligent selection fails
- **Performance Driven**: Every question choice considers user's learning needs

#### Function Changes
- `findBestQuestionForLevel(level, excludeQuestions = [])` - Added exclusion parameter
- `nextQuestion()` - Now uses intelligent selection instead of `currentQuestion++`
- `nextQuestionSequential()` - Fallback function for edge cases
- `window.recentlyAnsweredQuestions` - Session-based repetition avoidance

Both UI paths now use identical intelligent selection logic with proper performance data loading and smart progression.

## 🧠 Intelligent Question Priority System

The system uses a **4-tier priority system** with timestamp-based anti-repetition logic to optimize learning effectiveness:

### Priority Levels (in order of execution):

#### 🔥 Priority 0: Early Intervention (NEW)
**Condition**: Questions at ≥75% through cooldown threshold AND success rate <70%
- **Bypass**: Normal timestamp filtering for struggling questions
- **Selection**: Lowest success rate first, then lowest ID
- **Pedagogical Logic**: Don't wait for full cooldown when students are struggling with concepts
- **Example**: Question answered 3 hours ago (75% of 4-hour threshold) with 45% success rate → immediate practice
- **Debug**: `🔥 PRIORITY 0: Early intervention`

#### ✨ Priority 1: Unattempted Questions
**Condition**: Questions never attempted (after timestamp filtering)
- **Selection**: Lowest ID among unattempted questions
- **Pedagogical Logic**: Prioritize new learning opportunities
- **Debug**: `✨ PRIORITY 1: Found X unattempted questions`

#### 📈 Priority 2: Questions Needing Practice
**Condition**: Questions with success rate <70% (after timestamp filtering)
- **Selection**: Lowest success rate first, then lowest ID
- **Pedagogical Logic**: Target weak areas for reinforcement
- **Debug**: `📈 PRIORITY 2: Found X questions needing practice`

#### 🏆 Priority 3: Review/Mastery Maintenance
**Condition**: All questions mastered (≥70% success rate)
- **Selection**: Lowest ID for systematic review
- **Pedagogical Logic**: Spaced repetition to maintain proficiency
- **Debug**: `🏆 PRIORITY 3: All questions mastered`

### Key Features:

#### Anti-Repetition Logic:
- **Timestamp Filtering**: Excludes questions answered within `recentAnswerThresholdMinutes` (default: 10 minutes)
- **Priority 0 Override**: Bypasses timestamp filtering for struggling questions at ≥75% through threshold
- **Session Memory**: Tracks recently answered questions to prevent cycling

#### Performance-Driven Selection:
- **User Performance Data**: Loaded via WebSocket from Redis cache
- **Success Rate Tracking**: Based on `correctAttempts / totalAttempts`
- **Timestamp Tracking**: Uses `lastAnswered` field for cooldown calculations
- **Adaptive Thresholds**: Configurable via `appConfig.intelligentSelection.recentAnswerThresholdMinutes`

#### Educational Benefits:
- **Responsive Learning**: Doesn't make students wait full cooldown for struggling concepts
- **Balanced Progression**: New content → Struggling areas → Review
- **Consistent Selection**: Uses lowest ID as tiebreaker for predictable progression
- **Individual Adaptation**: Tailors to each user's performance patterns

This system ensures optimal learning experiences by balancing new content introduction, targeted practice for weak areas, and systematic review - all while preventing repetitive question cycling.
