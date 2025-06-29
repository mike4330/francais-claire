![francais claire logo](res/frenchapp.svg){ width=256 height=256 }
# francais claire
## CEFR-Based Audio Learning Framework

### Overview
A systematic approach to classify French content by difficulty level using the Common European Framework of Reference for Languages (CEFR), specifically designed for listening comprehension training from beginner phrases to authentic French news media.

### Classification Levels

#### **A1 - Beginner** 🟢
- **Maximum Word Count**: **9 words**
- **Linguistic Features:**
  - Simple present tense dominance
  - Basic vocabulary (≤1000 most common words)
  - Short, declarative sentences
  - Concrete nouns and simple adjectives
- **Content Topics:**
  - Greetings, numbers, colors
  - Family members, basic objects
  - Simple daily activities
- **Example:** *"Je mange une pomme rouge."* (5 words)
- **Cognitive Load**: Minimal - students can hold entire phrase in working memory

#### **A2 - Elementary** 🟡  
- **Maximum Word Count**: **14 words**
- **Linguistic Features:**
  - Past and future tenses introduced
  - Personal pronouns and possessives
  - Simple connectors (et, mais, parce que)
  - Vocabulary: 1000-2000 words
- **Content Topics:**
  - Personal experiences and routine
  - Shopping, food, travel basics
  - Simple descriptions of people/places
- **Example:** *"Hier, j'ai acheté des légumes au marché avec ma mère."* (10 words)
- **Cognitive Load**: Low - familiar contexts help comprehension

#### **B1 - Intermediate** 🟠
- **Maximum Word Count**: **25 words**
- **Linguistic Features:**
  - Conditional and subjunctive moods
  - Complex sentence structures
  - Abstract vocabulary introduction
  - Vocabulary: 2000-4000 words
- **Content Topics:**
  - Work and professional life
  - Travel experiences and plans
  - Opinions on familiar topics
- **Example:** *"Si j'avais plus de temps libre, je voyagerais davantage pour découvrir d'autres cultures."* (16 words)
- **Cognitive Load**: Moderate - students can follow longer discourse

#### **B2 - Upper-Intermediate** 🔴
- **Maximum Word Count**: **38 words**
- **Linguistic Features:**
  - Sophisticated grammatical structures
  - Technical and specialized vocabulary
  - Complex argumentation patterns
  - Vocabulary: 4000-8000 words
- **Content Topics:**
  - Abstract concepts and ideas
  - Technical explanations
  - Debate and discussion topics
- **Example:** *"L'impact environnemental des nouvelles technologies soulève des questions éthiques complexes."* (11 words)
- **Cognitive Load**: High - requires advanced processing skills

#### **C1 - Advanced** 🟣
- **Maximum Word Count**: **60 words**
- **Linguistic Features:**
  - Advanced grammatical structures
  - Professional and academic register
  - Implicit meaning and inference
  - Vocabulary: 8000+ words
- **Content Topics:**
  - Professional and academic discourse
  - Complex social issues
  - Literary and cultural analysis
- **Example:** *"Les implications socio-économiques de cette réforme nécessitent une analyse approfondie des mécanismes redistributifs."* (14 words)
- **Cognitive Load**: Very High - native-like processing required

#### **C2 - Proficiency** ⚫
- **Maximum Word Count**: **90 words**
- **Linguistic Features:**
  - Native-level complexity
  - Idiomatic expressions and cultural references
  - Political and media discourse patterns
  - Specialized terminology across domains
- **Content Topics:**
  - French news media and journalism
  - Political commentary and analysis
  - Complex societal debates
- **Example:** *"L'Assemblée nationale examine actuellement les modalités d'application de cette directive européenne dans le contexte hexagonal."* (16 words)
- **Cognitive Load**: Expert - authentic native content

### Question Generation Framework

#### **Comprehension Questions** (English)
- Test overall understanding of content
- Multiple choice format with plausible distractors
- Focus on main ideas and key details
- Example: *"What is the main topic discussed in this audio?"*

#### **Listening Verification** (French)
- Test exact auditory comprehension
- "What did you hear?" format
- Options in French to verify listening accuracy
- Example: *"Qu'est-ce que vous avez entendu?"*

### Implementation Strategy

1. **Content Analysis:**
   - Vocabulary frequency analysis
   - Grammatical complexity assessment
   - Topic and register identification

2. **Automatic Classification:**
   - Sentence length and structure metrics
   - Vocabulary level scoring
   - Tense and mood complexity

3. **Quality Assurance:**
   - Manual review for edge cases
   - Native speaker validation
   - Learner feedback integration

### Progression Path

**Learning Journey:** A1 → A2 → B1 → B2 → C1 → C2

- **A1-A2:** Foundation building with familiar contexts
- **B1-B2:** Transition to authentic materials with support
- **C1-C2:** Native-level media consumption and analysis

### Word Length Guidelines

The following word count boundaries ensure appropriate cognitive load and pedagogical progression:

| CEFR Level | Maximum Words | Cognitive Load | Primary Focus |
|------------|---------------|----------------|---------------|
| **A1** | max 9 words | Minimal | Simple phrases, basic vocabulary |
| **A2** | max 14 words | Low | Everyday expressions, familiar contexts |
| **B1** | max 25 words | Moderate | Complex sentences, abstract concepts |
| **B2** | max 38 words | High | Technical vocabulary, argumentation |
| **C1** | max 60 words | Very High | Professional discourse, implicit meaning |
| **C2** | max 90 words | Expert | Authentic media, political discourse |

#### **Pedagogical Rationale:**

- **Maximum Word Limits**: Based on mean of original ranges to ensure concise, focused content
- **Working Memory**: Lower levels need shorter texts for complete processing
- **Vocabulary Load**: Unknown words dramatically increase cognitive burden
- **Syntax Complexity**: Embedded clauses require more mental resources
- **Cultural Context**: Implicit knowledge requirements increase with level

#### **Content Guidelines:**

- **Conciseness Principle**: Content should be as brief as possible while maintaining pedagogical value
- **Length vs. Complexity**: Higher levels prioritize linguistic/cultural complexity over pure length
- **Progressive Limits**: Each level has a clear maximum to prevent cognitive overload

### Assessment Criteria

- **Accuracy:** Correct difficulty level assignment
- **Consistency:** Reliable classification across similar content
- **Pedagogical Value:** Appropriate challenge level for learning
- **Authenticity:** Real-world French language usage
- **Length Appropriateness:** Word count within CEFR level boundaries

### Technology Integration

- **AWS Polly:** Neural voice synthesis for consistent audio quality
- **Redis Caching:** Performance optimization for repeated content
- **Randomization:** Prevent answer memorization through shuffling
- **Progress Tracking:** Individual learner advancement monitoring

### Classification Flow Diagram

```
French Text Input
       ↓
Content Analysis
       ↓
CEFR Classification
       ↓
┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│   A1    │   A2    │   B1    │   B2    │   C1    │   C2    │
│Beginner │Elementary│Intermed.│Upper-Int│Advanced │Proficiency│
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
       ↓
Question Generation
       ↓
Listening Exercise
• Audio synthesis
• Comprehension questions  
• Listening verification
```

### Real-World Application Examples

**A1 Example Question Bank:**
- Audio: *"Bonjour, je m'appelle Marie. J'ai vingt ans."*
- Question: "What is the speaker's name?"
- Options: A) Marie B) Anna C) Sophie D) Claire

**C2 Example Question Bank:**
- Audio: *"Le gouvernement français annonce des mesures d'austérité budgétaire..."*
- Question: "What type of measures is the French government announcing?"
- Options: A) Tax cuts B) Budget austerity C) Social programs D) Infrastructure spending

### Validation Metrics

- **Inter-rater Reliability:** Agreement between multiple French teachers
- **Learner Performance Correlation:** Difficulty matches actual student results
- **Progression Validation:** Students advance appropriately through levels
- **Content Authenticity:** Real French media accurately classified

---

*This framework transforms francais claire from traditional classroom exercises into authentic media consumption training, preparing learners for real-world French communication and news comprehension.*

## Current Implementation Status

### Question Bank Statistics (as of implementation):
- **A1:** 1 question
- **A2:** 0 questions  
- **B1:** 2 questions
- **B2:** 3 questions
- **C1:** 5 questions
- **C2:** 1 question
- **Total:** 12 questions across all levels

### Technical Architecture:
- **Frontend:** HTML5 + JavaScript with AWS SDK
- **Audio Cache:** Redis + WebSocket (Node.js)
- **Voice Synthesis:** Amazon Polly (Neural voices: Léa, Rémi)
- **Data Storage:** JSON file + localStorage for custom additions
- **Management Interface:** Planning dashboard with statistics

### Key Features Implemented:
- ✅ Real-time difficulty filtering
- ✅ Answer randomization (Fisher-Yates shuffle)
- ✅ Automatic audio caching with Redis
- ✅ Auto-play and auto-advance functionality
- ✅ Live cache statistics and monitoring
- ✅ Settings persistence across sessions

### Development Tools:
- ✅ **ID Assignment Tool (`util/getid`)**: Automatically determines next available ID for each CEFR level
- `./util/getid a` → Next ID for A1/A2 levels (questions-a.json, range 34-99)
- `./util/getid b` → Next ID for B1/B2 levels (questions-b.json, range 200-299)
- `./util/getid c` → Next ID for C1/C2 levels (questions-c.json, range 100-199)
- ✅ **Question Analysis (`analyze-questions.sh`)**: Validates question structure and distribution

### Question Creation Workflow:
1. **Determine CEFR level** based on content complexity and word count limits
2. **Get next available ID**: `./util/getid [a|b|c]` based on target level
3. **Choose target file**: 
   - A1/A2 → `questions-a.json`
   - B1/B2 → `questions-b.json`
   - C1/C2 → `questions-c.json`
4. **Create question** following the JSON structure template
5. **Validate**: Run `bash analyze-questions.sh` to check for errors
6. **Test**: Verify question appears correctly in the learning interface 