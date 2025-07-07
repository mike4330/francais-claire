![francais claire logo](res/frenchapp.svg){ width=256 height=256 }
# 🇫🇷 French Listening Practice App

A sophisticated French news listening training system designed to bridge the gap between high school French and understanding authentic French media. Features professional-quality audio synthesis, difficulty-graded content, and intelligent caching for scalable learning.

## 🎯 Objective

**Primary Goal**: A "software toy" for French language learning - an endless, exploratory learning experience without artificial endpoints or completion states. Like SimCity for language acquisition, this app provides continuous discovery and growth through authentic French media content.

**Software Toy Philosophy**: 
- **No "End" State**: Learning continues indefinitely with ever-evolving content
- **Exploratory Learning**: Users discover language through authentic contexts
- **Continuous Content Evolution**: New questions, topics, and variations added regularly
- **Organic Growth**: Content expands based on user needs and linguistic gaps
- **Playful Engagement**: Learning feels like exploration rather than curriculum completion

**Target Focus**: 
- **A2-C2 levels** (A1 content minimal - focus is on media literacy, not basic language acquisition)
- **Authentic vocabulary** from French journalism, politics, and current affairs
- **Real-world contexts** encountered in French media consumption
- **Progressive difficulty** to build from elementary understanding to full media comprehension
- **Living Content**: Questions and vocabulary that evolve with contemporary French usage

This app bridges the gap between classroom French and the linguistic reality of French news media, preparing learners for genuine French content consumption through endless, engaging exploration.

## ✨ Features

### 🎧 Professional Audio Synthesis
- **AWS Polly Integration**: High-quality neural French voices (Léa, Rémi)
- **Browser TTS Fallback**: Works without AWS credentials
- **Variable Speed Control**: 0.75x, 1x, 1.25x playback speeds
- **SSML Support**: Enhanced speech synthesis for supported content

### 📊 CEFR-Based Difficulty System
- **A1 Beginner**: Simple phrases, basic vocabulary (max 9 words)
- **A2 Elementary**: Everyday expressions, personal topics (max 14 words)
- **B1 Intermediate**: Work, travel, familiar topics (max 25 words)
- **B2 Upper-Intermediate**: Abstract topics, complex ideas (max 38 words)
- **C1 Advanced**: Professional, academic content (max 60 words)
- **C2 - Proficiency**: French media, political discourse (max 90 words)

### 🎯 Question Types
- **Comprehension Questions** 📖: English questions testing French audio understanding
- **Listening Questions** 👂: "Qu'est-ce que vous avez entendu?" with French options
- **Fill-in-the-Blank Questions** ✏️: Listening questions where learners fill in a missing word from the audio text, testing specific vocabulary recall
- **Content Variety**: Politics, weather, healthcare, environment, celebrity news, food

### 🔄 Template Variation System
Questions can include semantic variations to prevent memorization:
- **Template Structure**: `"Une {political_person} a {reporting_verb} qu'elle pense {uncertainty}..."`
- **Weighted Selection**: More common vocabulary appears more frequently
- **60-Minute Caching**: Variations stay consistent during study sessions, auto-expire for freshness
- **Manual Regeneration**: "🎲 New Variations" button for immediate changes
- **Example Variations**:
  - "Une femme politique a dit qu'elle pense peut-être ne pas pouvoir participer aux élections."
  - "Une députée a déclaré qu'elle pense probablement ne pas pouvoir se présenter aux prochaines élections."

### ⚡ Redis Caching System
- **WebSocket Server**: Real-time cache management on port 8080
- **MD5 Hash Keys**: Efficient cache key generation
- **30-Day Expiration**: Automatic cache cleanup
- **Cache Operations**: Check, store, stats, clear, surgical eviction
- **Base64 Encoding**: Efficient audio storage in Redis

### 🎮 Interactive Features
- **Auto-play**: 500ms delay after question load
- **Auto-advance**: 1.5s advancement on correct answers
- **Skip Questions**: Skip difficult questions with separate scoring
- **Answer Randomization**: Fisher-Yates shuffle prevents pattern memorization
- **Settings Persistence**: localStorage for user preferences

### 🎯 Intelligent Question Selection
The app uses a revolutionary **pure intelligent selection** system that eliminates traditional question sequences in favor of adaptive, performance-driven question delivery.

#### **Pure Intelligent Selection Architecture** (July 2025 Redesign)

**Key Innovation**: Every question request goes through intelligent selection - no more filtered arrays or sequential navigation.

**How It Works**:
- **No Question Arrays**: Removed the problematic `questions` array filtering system
- **Direct ID-based Loading**: `loadQuestion(questionId)` finds questions directly in `questionBank`
- **Every Question Optimized**: Each question request uses `findBestQuestionForLevel()` 
- **No Sequence Dependency**: Questions selected purely on learning objectives and performance

#### **Two UI Paths for Intelligent Selection**

**Path 1: Main Page Level Buttons** (`french_listening_app.html`)
- **Trigger**: User clicks difficulty level buttons (A1, A2, B1, B2, C1, C2)
- **Process**: Asynchronously loads performance data via WebSocket, then applies intelligent selection
- **Flow**: `selectDifficulty()` → `loadUserPerformanceDataThenStart()` → `findBestQuestionForLevel()`

**Path 2: Student Dashboard Level Cards** (`student.html`)
- **Trigger**: User clicks pre-calculated level progress cards  
- **Process**: Performance data already loaded, best question pre-calculated during card rendering
- **Flow**: `launchQuizWithLevel()` → redirects to main app with `?start={questionId}`

#### **3-Tier Priority Algorithm** (Used by Both Paths)
1. **Priority 1 - New Learning**: Selects unattempted questions (lowest ID first)
   - Reasoning: "Student has never attempted this question - perfect for new learning"

2. **Priority 2 - Targeted Practice**: Focuses on questions with <70% success rate
   - Sorts by lowest success rate first, then by question ID
   - Reasoning: "Student struggling with this question - targeted practice needed"

3. **Priority 3 - Mastery Review**: When all questions are mastered (≥70% success)
   - Returns lowest ID for spaced repetition review
   - Reasoning: "Maintaining mastery through spaced repetition"

#### **Performance Tracking with Timestamps**
- **`lastAnswered` Field**: Every performance record includes when question was last answered
- **Time-Aware Debug Logs**: Console shows "Question 403 last answered 2 days 3 hours ago"
- **Anti-Repetition Logic**: Uses timestamps to avoid recently answered questions
- **Future-Ready**: Enables spaced repetition and forgetting curve algorithms

#### **Technical Implementation**
- **Performance Data Source**: Redis WebSocket connection with real-time user statistics
- **Data Structure**: `questionPerformances` array with success rates, attempt counts, timestamps
- **Direct Question Loading**: `loadQuestion(questionId)` bypasses array indexing entirely
- **Dynamic User Answers**: `userAnswers.push()` tracks questions by ID, not array position
- **Async Loading**: WebSocket retry logic for connection delays
- **Debug Visibility**: Comprehensive console logging for selection process and timing

#### **Major Architectural Changes** (July 2025)
- **🚫 Removed Question Filtering**: Eliminated `filterQuestionsByDifficulty()` and `questions[]` array
- **🚫 Removed Sequential Navigation**: No more `currentQuestion` index or `nextQuestionSequential()`
- **✅ Pure Intelligent Selection**: Every question request uses performance-driven algorithms
- **✅ ID-Based Architecture**: Questions loaded directly by ID from `questionBank`
- **✅ Timestamp Tracking**: Added `lastAnswered` field to performance data
- **✅ Simplified Flow**: Removed 100+ lines of array management code
- **✅ Enhanced Debugging**: Time-aware console logs for question selection analysis

## 🚀 Quick Start

### Prerequisites
- Web server (Apache, Nginx, or development server)
- Redis server (for caching functionality)
- Node.js (for cache server)
- AWS Account (optional, for Polly integration)

### Installation
1. Clone or download the project files
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start Redis server:
   ```bash
   redis-server
   ```
4. Start the cache server:
   ```bash
   ./start-cache-server.sh
   ```
5. Serve the HTML files via web server
6. Open `french_listening_app.html` in browser

### AWS Polly Setup (Optional)
1. Create AWS account and get Access Key/Secret Key
2. Open app settings (⚙️ icon)
3. Enable "Use Amazon Polly"
4. Enter AWS credentials and select region
5. Choose French voice (Céline, Mathieu, or Léa)

**🔒 Security Note**: For shared deployments, AWS credentials are stored server-side in `tts-proxy.php` for security. Voice settings are accessible through the hamburger menu (🔊 Voice Settings) with a clean, credential-free interface for family use.

## 📁 File Structure

```
language/
├── french_listening_app.html    # Main application
├── planning.html               # Question management interface
├── questions.json              # Question database (legacy, do not modify)
├── questions-a.json            # A1/A2 level questions 
├── questions-b.json            # B1/B2 level questions
├── questions-c.json            # C1/C2 level questions
├── redis-cache-server.js       # WebSocket cache server
├── start-cache-server.sh       # Cache server startup script
├── cache-monitor.html          # Cache monitoring dashboard
├── util/                       # Utility scripts directory
│   ├── analyze-questions.sh    # Question bank analyzer
│   ├── analyze-conjugations.py # Verb conjugation analyzer
│   ├── getid                   # ID generator utility
│   ├── delete-tag.sh           # Tag deletion tool
│   ├── list-tags.sh            # Tag listing utility
│   └── README.md              # Utilities documentation
├── package.json               # Node.js dependencies
├── CEFR_Classification_Framework.md  # Content guidelines
└── README.md                  # This file
```

## 🎯 Usage Guide

### Basic Workflow
1. **Select Difficulty**: Choose CEFR level (A1-C2)
2. **Configure Audio**: Set up AWS Polly or use browser TTS
3. **Practice Listening**: Questions auto-play with 500ms delay
4. **Answer Questions**: Select from multiple choice options
5. **Review Results**: See score with skipped questions tracked separately

### Advanced Features

#### Template Variations
Questions with `audioTemplate` field generate semantic variations:
- Variations cached for 60 minutes during study sessions
- Use "🎲 New Variations" to generate fresh content immediately
- Console logs show selected variables for debugging

#### Cache Management
- **Pre-Cache All**: Download all audio files to Redis in advance
- **Clear Cache**: Remove all cached audio (requires re-download)
- **Cache Stats**: Real-time display of cached files and storage usage
- **Surgical Eviction**: Remove specific questions from cache (e.g., `evictQuestion9()`)

#### Skip Functionality
- Skip difficult questions without penalty
- Final scores calculated on attempted questions only
- Skipped questions tracked and reported separately

## 🔧 Technical Details

### Audio Caching Strategy
- Cache keys: MD5 hash of `audioText + voiceId`
- Storage: Base64-encoded MP3 data in Redis
- Expiration: 30 days for audio files, 60 minutes for template variations
- Fallback: Direct Polly synthesis on cache miss

### Question Tracking & Data Retention
The app tracks detailed performance analytics with automatic Redis expiration configured in `redis-cache-server.js`:

#### Individual Question Responses
- **Retention**: 90 days (7,776,000 seconds)
- **Purpose**: Detailed response tracking (response time, correctness, timestamps)
- **Key Format**: `response:{uuid}:{questionId}:{timestamp}`
- **Implementation**: `redis-cache-server.js:463` - `setEx(responseKey, 7776000, ...)`

#### User Question Performance
- **Retention**: 1 year (31,536,000 seconds)
- **Purpose**: Per-user, per-question statistics for CEFR level progress
- **Key Format**: `user_question:{uuid}:{questionId}`
- **Used For**: 70% mastery threshold calculations in student dashboard
- **Implementation**: `redis-cache-server.js:518` - `expire(userQuestionKey, 31536000)`

#### Global Question Statistics
- **Retention**: 1 year (31,536,000 seconds)
- **Purpose**: Overall question analytics (success rates, average response times)
- **Key Format**: `question_stats:{questionId}`
- **Implementation**: `redis-cache-server.js:488` - `expire(questionStatsKey, 31536000)`

#### Audio Cache
- **Retention**: 30 days (2,592,000 seconds)
- **Purpose**: TTS/Polly generated audio files
- **Key Format**: `audio:{cacheKey}`
- **Implementation**: Automatic Redis TTL on audio storage

#### Template Variations
- **Retention**: 60 minutes (in-memory cache)
- **Purpose**: Generated content variations during study sessions
- **Behavior**: Auto-regenerates after expiry for content freshness

**Note**: All expiration timers reset when data is updated, keeping active users' data fresh while automatically cleaning up inactive data.

### Question Bank Format
```json
{
  "id": 18,
  "audioText": "Static fallback text",
  "audioTemplate": "Une {political_person} a {reporting_verb}...",
  "templateVariables": {
    "political_person": {
      "options": ["femme politique", "députée", "candidate"],
      "weights": [0.4, 0.3, 0.3]
    }
  },
  "question": "What did you hear?",
  "questionType": "listening",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "explanation": "Detailed explanation...",
  "difficulty": "B1",
  "source": "News Source",
  "tags": ["politics", "listening"]
}
```

### CEFR Word Count Guidelines
Questions are classified by maximum word counts based on pedagogical research:
- **A1**: 5-12 words (avg 9)
- **A2**: 8-20 words (avg 14)  
- **B1**: 15-35 words (avg 25)
- **B2**: 25-50 words (avg 38)
- **C1**: 40-80 words (avg 60)
- **C2**: 60-120 words (avg 90)

## 🛠️ Development

### Software Toy Architecture for Continuous Content Creation

The "software toy" approach drives all development decisions, prioritizing endless content evolution over traditional feature completion:

#### Content-First Development
- **Continuous Addition**: New questions, vocabulary, and contexts added regularly
- **Living Vocabulary**: Content adapts to contemporary French usage and current events
- **Gap Analysis**: Tools identify linguistic gaps for targeted content creation
- **Organic Growth**: Content expands based on learner discovery patterns

#### Adding New Questions
The process for adding new questions involves providing French text to the assistant. The assistant will then:
1. **Classify the Text**: Determine the CEFR difficulty level based on word count and content complexity.
2. **Generate Questions**: Create both comprehension (English) and listening (French) question types with appropriate options, correct answers, and explanations.
3. **Populate Fields**: Fill in all necessary fields such as `id`, `audioText`, `question`, `questionType`, `options`, `correct`, `explanation`, `difficulty`, `source`, and `tags`.
4. **Insert into File**: Place the new questions into the appropriate question file (e.g., `questions-a.json`, `questions-b.json`, or `questions-c.json`) based on difficulty or content category, ensuring unique IDs and logical organization.

This method ensures that new content is seamlessly integrated into the existing question bank with minimal manual intervention.

#### Content Evolution Tools
- **`lemma-coverage.py`**: Unified analysis tool for identifying vocabulary gaps across adjectives, adverbs, verbs, and nouns
- **Template System**: Semantic variations prevent stagnation and enable exponential content growth
- **Tag Analysis**: Content discovery through thematic clustering
- **Performance Analytics**: User data drives content prioritization

### Template Question Creation
```javascript
// Template-enabled question
addQuestion({
  audioText: "Fallback text",
  audioTemplate: "Une {subject} a {verb} que...",
  templateVariables: {
    "subject": {
      "options": ["femme", "députée", "ministre"],
      "weights": [0.5, 0.3, 0.2]
    },
    "verb": {
      "options": ["dit", "déclaré", "affirmé"],
      "weights": [0.4, 0.3, 0.3]
    }
  },
  // ... other fields
});
```

### Cache Operations
```javascript
// Evict specific question from cache
evictQuestionFromCache(questionId);

// Get cache statistics
updateCacheStats();

// Clear all template variations
regenerateVariations();
```

## 📈 Performance

### Optimizations
- **Parallel Tool Calls**: Multiple operations execute simultaneously
- **WebSocket Caching**: Sub-second cache lookups
- **Audio Compression**: Efficient MP3 storage
- **Smart Pre-loading**: Cache commonly accessed content

### Scalability
- **Unlimited Audio Storage**: Redis-based caching system
- **Template System**: Exponential content variation (e.g., 1,024 combinations from 5 variables)
- **Modular Architecture**: Easy to extend with new question types

## 🎓 Educational Philosophy

### Software Toy Learning Paradigm

Inspired by Will Wright's description of SimCity as a "software toy," this app abandons traditional educational constraints in favor of endless exploration:

#### Core Principles
- **No Completion**: Learning continues indefinitely - there's always more to discover
- **Emergent Understanding**: Knowledge builds naturally through authentic content exposure
- **Playful Discovery**: Exploration feels like play, not curriculum
- **Authentic Content**: Real French news and media language
- **Graduated Difficulty**: CEFR-based progression without artificial endpoints
- **Comprehension Focus**: Understanding over production
- **Cultural Context**: Exposure to French society and current events
- **Semantic Variation**: Prevents rote memorization through intelligent content variation

#### Software Toy Benefits
- **Sustainable Engagement**: No "graduation" means no loss of momentum
- **Personal Pace**: Users explore at their own speed without external pressure
- **Living Content**: Questions evolve with contemporary French usage
- **Organic Mastery**: Proficiency develops through authentic practice
- **Continuous Challenge**: New content prevents skill stagnation

## 🤝 Contributing

The app accepts new content through:
1. Manual question entry via console helpers
2. AI assistant integration for content generation
3. Direct JSON file editing
4. Template system for semantic variations

## 📄 License

This project is part of francais claire. See individual file headers for specific licensing information.

## 🔗 Related Files

- **[CEFR Classification Framework](CEFR_Classification_Framework.md)**: Detailed content guidelines
- **[Planning Interface](planning.html)**: Question management and statistics
- **[Cache Monitor](cache-monitor.html)**: Real-time cache monitoring

---

*Built with ❤️ for French language learners who want to understand authentic French media and news.* 