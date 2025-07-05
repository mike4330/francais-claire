# Utility Scripts for French Language Learning System

This directory contains analyzer and utility scripts for managing the French question bank.

## 📊 Analysis Scripts

### `analyze-questions.sh`
**Main question bank analyzer**
- Analyzes word frequency, noun coverage, tag distribution
- Shows CEFR level and question type statistics
- Provides strategic insights for content development
- Usage: `bash analyze-questions.sh`

### `analyze-conjugations.py`
**Verb conjugation coverage analyzer**
- Analyzes coverage of French verb conjugations
- Shows missing forms for top 25 most frequent verbs
- Provides priority targets for new questions
- Usage: `python3 analyze-conjugations.py`

### `analyze-adjectives.py`
**Adjective coverage analyzer**
- Analyzes coverage of French adjectives (all forms: m/f/s/p)
- Shows missing adjectives from top 30 most frequent adjectives
- Identifies high-frequency adjectives completely missing from question bank
- Provides priority targets for adjective-focused questions
- Usage: `python3 analyze-adjectives.py`

## 🛠️ Utility Scripts

### `getid`
**Next available ID generator**
- Gets next available question ID for specific CEFR levels
- Supports A1/A2 (a), B1/B2 (b), C1/C2 (c) levels
- Usage: `./getid [a|b|c]`

### `delete-tag.sh`
**Tag deletion tool**
- Safely removes tags from question bank with backups
- Supports multiple tag removal in single operation
- Keeps only last 5 backups per file
- Usage: `./delete-tag.sh <tag1> [tag2] [tag3] ...`

### `list-tags.sh`
**Tag listing utility**
- Lists all tags used across question files
- Shows frequency and usage statistics
- Helps identify tag inconsistencies
- Usage: `bash list-tags.sh`

## 📝 Usage Examples

```bash
# Analyze question bank
bash util/analyze-questions.sh

# Analyze verb conjugations  
python3 util/analyze-conjugations.py

# Analyze adjective coverage
python3 util/analyze-adjectives.py

# Get next ID for A2 level question
./util/getid a

# Remove multiple tags
./util/delete-tag.sh grammar verb-conjugation B2

# List all tags
bash util/list-tags.sh
```

## 🔗 Integration

These utilities integrate with the compiled question files:
- `questions/q-compiled-a.json` (A1/A2 levels)
- `questions/q-compiled-b.json` (B1/B2 levels) 
- `questions/q-compiled-c.json` (C1/C2 levels)
- Individual source files: `questions/source/q*.json`

## 📋 Dependencies

- **jq** - JSON processing (for most scripts)
- **bc** - Basic calculator (for statistics)
- **python3** - For conjugation and adjective analysis
- **res/adj.csv** - Adjective frequency data (for adjective analysis)
- **Standard Unix tools** - awk, sed, grep, sort, etc. 