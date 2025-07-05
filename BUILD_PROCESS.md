# Question Build/Compile Process

## Overview

This document outlines the recommended build process for managing French language learning questions as individual JSON files instead of large monolithic files. This approach improves maintainability, version control, and collaboration.

## Current State vs. Proposed State

### Current Structure
```
questions/
├── questions.json          # Legacy file (31 questions)
├── questions-a.json        # A1/A2 levels (78+ questions)
├── questions-b.json        # B1/B2 levels (111+ questions)
└── questions-c.json        # C1/C2 levels (69+ questions)
```

### Proposed Structure
```
src/
├── questions/
│   ├── a1/
│   │   ├── 034.json
│   │   ├── 035.json
│   │   └── ...
│   ├── a2/
│   │   ├── 067.json
│   │   ├── 068.json
│   │   └── ...
│   ├── b1/
│   │   ├── 200.json
│   │   ├── 201.json
│   │   └── ...
│   ├── b2/
│   │   ├── 250.json
│   │   ├── 251.json
│   │   └── ...
│   ├── c1/
│   │   ├── 400.json
│   │   ├── 401.json
│   │   └── ...
│   └── c2/
│       ├── 450.json
│       ├── 451.json
│       └── ...
├── build/
│   ├── questions-a.json    # Compiled A1+A2
│   ├── questions-b.json    # Compiled B1+B2
│   └── questions-c.json    # Compiled C1+C2
└── tools/
    ├── build.js            # Main build script
    ├── validate.js         # Question validation
    └── split.js            # Migration tool
```

## Benefits of Individual Files

### 1. **Version Control**
- Clear diff history for each question
- Easy to track changes and authorship
- Reduced merge conflicts
- Granular rollback capabilities

### 2. **Collaboration**
- Multiple contributors can work simultaneously
- Easy to assign specific questions to team members
- Clear ownership and responsibility
- Simplified code review process

### 3. **Maintainability**
- Easier to find and edit specific questions
- Reduced risk of JSON syntax errors affecting entire sets
- Individual validation and testing
- Modular organization by difficulty level

### 4. **Development Workflow**
- Automated validation per question
- Build-time error checking
- Flexible deployment options
- Easy A/B testing of individual questions

## Individual Question File Format

Each question file follows this structure:

```json
{
  "id": 123,
  "audioText": "French text for audio synthesis",
  "question": "English comprehension question or French listening prompt",
  "questionType": "comprehension|listening|fill-in-the-blank",
  "options": [
    "Option A",
    "Option B", 
    "Option C",
    "Option D"
  ],
  "correct": 0,
  "explanation": "Detailed explanation in English",
  "difficulty": "A1|A2|B1|B2|C1|C2",
  "source": "Content source description",
  "tags": ["tag1", "tag2", "tag3"],
  "timeCreated": 1234567890,
  "parentQuestion": 456,
  "metadata": {
    "wordCount": 12,
    "estimatedDuration": 30,
    "lastModified": 1234567890,
    "author": "contributor-id",
    "reviewStatus": "approved|pending|draft"
  }
}
```

## Build Process

### 1. **Validation Phase**
```bash
npm run validate        # Validate all individual questions
npm run validate:a1     # Validate specific level
npm run validate:123    # Validate specific question ID
```

**Validation Checks:**
- JSON syntax validity
- Required fields presence
- CEFR word count limits
- Tag content policy compliance
- ID uniqueness and range compliance
- Audio text character limits
- Option array length (exactly 4)
- Correct answer index validity (0-3)

### 2. **Compilation Phase**
```bash
npm run build           # Build all compiled files
npm run build:dev       # Build with development metadata
npm run build:prod      # Build optimized for production
```

**Compilation Process:**
1. Read all individual question files by difficulty level
2. Sort by ID within each level
3. Validate cross-references (parentQuestion links)
4. Generate compiled JSON files
5. Create build metadata and statistics
6. Generate analysis reports

### 3. **Deployment Phase**
```bash
npm run deploy:staging  # Deploy to staging environment
npm run deploy:prod     # Deploy to production
```

## Migration Strategy

### Phase 1: Setup Build System
1. Create directory structure
2. Implement build scripts
3. Set up validation rules
4. Create migration tools

### Phase 2: Split Existing Questions
1. Run migration script to split current files
2. Preserve all existing metadata
3. Maintain ID assignments and ranges
4. Verify compiled output matches original

### Phase 3: Parallel Development
1. Continue using compiled files in production
2. Edit individual files for new questions
3. Test build process thoroughly
4. Train contributors on new workflow

### Phase 4: Full Migration
1. Switch production to use compiled files from build
2. Archive old monolithic files
3. Update documentation and tooling
4. Establish continuous integration

## Build Scripts Implementation

### Core Build Script (`tools/build.js`)
```javascript
const fs = require('fs');
const path = require('path');

class QuestionBuilder {
  constructor(srcDir, buildDir) {
    this.srcDir = srcDir;
    this.buildDir = buildDir;
    this.questions = new Map();
  }

  async build() {
    await this.loadQuestions();
    await this.validateQuestions();
    await this.compileByLevel();
    await this.generateReports();
  }

  async loadQuestions() {
    // Load all individual question files
    // Organize by difficulty level
    // Validate basic structure
  }

  async validateQuestions() {
    // Run comprehensive validation
    // Check ID uniqueness and ranges
    // Verify CEFR compliance
    // Validate tag policies
  }

  async compileByLevel() {
    // Group questions by CEFR level pairs
    // Sort by ID within each group
    // Generate compiled JSON files
    // Preserve original structure
  }

  async generateReports() {
    // Create build statistics
    // Generate coverage reports
    // Update analysis data
  }
}
```

### Validation Rules (`tools/validate.js`)
```javascript
const VALIDATION_RULES = {
  requiredFields: ['id', 'audioText', 'question', 'questionType', 'options', 'correct', 'explanation', 'difficulty', 'source', 'tags', 'timeCreated'],
  
  wordLimits: {
    'A1': 9,
    'A2': 14,
    'B1': 25,
    'B2': 38,
    'C1': 60,
    'C2': 90
  },

  idRanges: {
    'A1': [34, 199],
    'A2': [34, 199],
    'B1': [200, 399],
    'B2': [200, 399],
    'C1': [400, 499],
    'C2': [400, 499]
  },

  forbiddenTags: [
    // Grammar terms
    'listening', 'comprehension', 'conditional', 'imperfect', 'subjunctive',
    // Verb names  
    'aller', 'être', 'avoir', 'faire', 'dire', 'voir', 'parler', 'aimer',
    // Individual words
    'peu', 'sûr', 'beau', 'seul', 'heureux', 'pauvre'
  ]
};
```

## Package.json Scripts

```json
{
  "scripts": {
    "validate": "node tools/validate.js",
    "validate:level": "node tools/validate.js --level",
    "validate:id": "node tools/validate.js --id",
    "build": "node tools/build.js",
    "build:dev": "node tools/build.js --dev",
    "build:prod": "node tools/build.js --prod",
    "split": "node tools/split.js",
    "analyze": "npm run build && bash util/analyze-questions.sh",
    "watch": "nodemon --watch src/ --exec 'npm run build:dev'",
    "test": "npm run validate && npm run build && npm run analyze"
  }
}
```

## Git Workflow

### Adding New Questions
```bash
# Create new question file
cp template.json src/questions/b1/312.json
# Edit the question
vim src/questions/b1/312.json
# Validate
npm run validate:312
# Build and test
npm run build:dev
# Commit individual file
git add src/questions/b1/312.json
git commit -m "Add question 312: workplace technology topic"
```

### Updating Existing Questions
```bash
# Edit existing question
vim src/questions/a2/089.json
# Validate changes
npm run validate:89
# Build and test
npm run build:dev
# Commit changes
git add src/questions/a2/089.json
git commit -m "Update question 89: fix audio text word count"
```

## Integration with Existing Tools

### Analysis Tools
- Update `analyze-questions.sh` to read from build directory
- Modify `analyze-conjugations.py` to accept source directory
- Enhance `analyze-tag-network.py` for individual file processing

### ID Management
- Update `getid` tool to check source directory structure
- Add validation for ID availability across all levels
- Implement ID reservation system for concurrent development

### Question Loading
- Maintain backward compatibility with existing `loadQuestionBank()` function
- Add development mode to load from source files directly
- Implement hot-reload for development workflow

## Timeline and Milestones

### Week 1: Foundation
- [ ] Create directory structure
- [ ] Implement basic build script
- [ ] Set up validation framework
- [ ] Create migration tool

### Week 2: Migration
- [ ] Split existing questions into individual files
- [ ] Verify compiled output matches original
- [ ] Update analysis tools
- [ ] Test integration with existing system

### Week 3: Enhancement
- [ ] Add advanced validation rules
- [ ] Implement watch mode and hot-reload
- [ ] Create contributor documentation
- [ ] Set up CI/CD pipeline

### Week 4: Production
- [ ] Deploy build system to production
- [ ] Train team on new workflow
- [ ] Archive legacy files
- [ ] Monitor and optimize performance

## Next Steps

1. **Review and approve** this build process design
2. **Create initial tooling** for validation and compilation
3. **Run migration** on existing question bank
4. **Test thoroughly** with current application
5. **Deploy incrementally** with fallback options

This build process will significantly improve the maintainability and scalability of the French language learning question system while preserving all existing functionality.