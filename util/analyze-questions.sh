#!/bin/bash

# French Question Bank Analyzer
# Analyzes word frequency and tag frequency from questions.json

echo "🇫🇷 French Question Bank Analyzer"
echo "=================================="

# Check if question files exist
if ! ls question*.json 1> /dev/null 2>&1; then
    echo "❌ Error: No question*.json files found"
    exit 1
fi

# French stop words to filter out
FRENCH_STOPWORDS="le la les un une des de du da dans sur pour avec sans par que qui quoi dont où comment quand pourquoi et ou mais donc car ni si même tout tous toute toutes ce cette ces cet son sa ses mon ma mes ton ta tes notre nos votre vos leur leurs il elle ils elles je tu nous vous on ne pas plus moins très bien mal beaucoup peu trop assez aussi encore déjà jamais toujours souvent parfois quelquefois avant après pendant depuis jusqu maintenant aujourd hui hier demain ici là bas haut sous dessus dessous devant derrière entre parmi vers chez contre malgré selon grâce"

# Common articles and short words (1-2 chars) to exclude
SHORT_WORDS="a à au aux en of or is it an as at be by do go he if in me my no of on so to up we d l n s t y"

echo ""
echo "📊 WORD FREQUENCY ANALYSIS"
echo "==========================="

# Extract all audioText and aggregate into word list
echo "Extracting French vocabulary from audioText fields..."

# Create temporary file for words
TEMP_WORDS=$(mktemp)

# Extract audioText content from all question files, clean and split into words
jq -r '.questions[].audioText' question*.json | \
    # Convert to lowercase
    tr '[:upper:]' '[:lower:]' | \
    # Remove punctuation and special characters
    sed 's/[«»""(),.!?;:—–-]/ /g' | \
    # Split into individual words
    tr ' ' '\n' | \
    # Remove empty lines
    grep -v '^$' | \
    # Remove words with 1-2 characters
    grep -v '^..$' | \
    grep -v '^.$' | \
    # Remove apostrophes and clean up
    sed "s/'//g" | \
    # Filter out French stop words and common short words
    grep -vwE "($(echo $FRENCH_STOPWORDS $SHORT_WORDS | tr ' ' '|'))" > $TEMP_WORDS

# Question Coverage Analysis for Top French Nouns
echo ""
    echo "📊 Top 50 Priority French Nouns - Coverage Report:"
    echo "=================================================="

# Check if Lexique noun frequency file exists
if [ ! -f "database/nouns.csv" ]; then
    echo "❌ Error: Lexique noun frequency file not found at database/nouns.csv"
    echo "Falling back to simple word frequency..."
    sort $TEMP_WORDS | uniq -c | sort -nr | head -50 | \
        awk '{printf "%2d. %-20s (%d occurrences)\n", NR, $2, $1}'
else
    echo "Using Lexique frequency data - showing 50 nouns that need attention..."
    echo "(Filtering out well-represented nouns with >0.1% frequency)"
    echo ""
    
    # Create temporary files
    TEMP_TOP_NOUNS=$(mktemp)
    TEMP_COVERAGE=$(mktemp)
    
    # Extract all nouns from Lexique data (skip header, get lemme column)
    tail -n +2 database/nouns.csv | cut -d',' -f1 | \
        # Remove quotes if present
        sed 's/"//g' | \
        # Convert to lowercase for matching
        tr '[:upper:]' '[:lower:]' > $TEMP_TOP_NOUNS
    
    # Check coverage for each top noun
    COVERED=0
    
    echo "Coverage Status (✅ = found in questions, ❌ = missing):"
    echo "--------------------------------------------------------"
    
         # Get total word count for frequency calculation
     TOTAL_WORD_INSTANCES=$(wc -l < $TEMP_WORDS)
     
     DISPLAYED=0
     while IFS= read -r noun && [ $DISPLAYED -lt 50 ]; do
         
         # Check if this noun appears in our word list
         if grep -qx "$noun" $TEMP_WORDS; then
             # Count occurrences and calculate frequency percentage
             COUNT=$(grep -cx "$noun" $TEMP_WORDS)
             FREQUENCY=$(echo "scale=2; $COUNT * 100 / $TOTAL_WORD_INSTANCES" | bc)
             
             # Skip if frequency > 0.1%
             if (( $(echo "$FREQUENCY > 0.1" | bc -l) )); then
                 continue
             fi
             
             STATUS="✅"
             COVERED=$((COVERED + 1))
             DISPLAYED=$((DISPLAYED + 1))
             printf "%2d. %-15s %s (%s%%)\n" $DISPLAYED "$noun" "$STATUS" "$FREQUENCY"
         else
             STATUS="❌"
             DISPLAYED=$((DISPLAYED + 1))
             printf "%2d. %-15s %s (not found)\n" $DISPLAYED "$noun" "$STATUS"
         fi
     done < $TEMP_TOP_NOUNS
    
    # Calculate coverage statistics  
    COVERAGE_PERCENT=$(echo "scale=1; $COVERED * 100 / 50" | bc)
    
    echo ""
    echo "📈 Coverage Statistics:"
    echo "  Top 50 priority nouns covered: $COVERED/50 ($COVERAGE_PERCENT%)"
    echo "  Missing high-frequency nouns: $((50 - $COVERED))"
    
    # Show top missing nouns (important gaps)
    echo ""
    echo "🎯 Priority Nouns Missing from Question Bank:"
    echo "--------------------------------------------"
    MISSING_COUNT=0
    while IFS= read -r noun && [ $MISSING_COUNT -lt 10 ]; do
        if ! grep -qx "$noun" $TEMP_WORDS; then
            MISSING_COUNT=$((MISSING_COUNT + 1))
                         # Get frequency info from CSV (take only first match)
             FREQ=$(tail -n +2 database/nouns.csv | grep "^$noun," | head -1 | cut -d',' -f7 | tr -d '\n\r')
             if [ -z "$FREQ" ]; then
                 FREQ=$(tail -n +2 database/nouns.csv | grep "\"$noun\"," | head -1 | cut -d',' -f7 | tr -d '\n\r')
             fi
             # Ensure FREQ is a valid number before printf
             if [ -n "$FREQ" ] && [ "$FREQ" != "" ]; then
                 printf "%2d. %-15s (frequency: %.0f)\n" $MISSING_COUNT "$noun" "$FREQ"
             else
                 printf "%2d. %-15s (frequency: unknown)\n" $MISSING_COUNT "$noun"
             fi
        fi
    done < $TEMP_TOP_NOUNS
    
    # Show gender distribution of covered nouns
    echo ""
    echo "🚻 Gender Distribution of Covered Nouns:"
    echo "---------------------------------------"
    
    # Get gender info for covered nouns
    MASCULINE=0
    FEMININE=0
    UNKNOWN=0
    
    while IFS= read -r noun; do
        if grep -qx "$noun" $TEMP_WORDS; then
            # Get gender from CSV
            GENDER=$(tail -n +2 database/nouns.csv | grep "^$noun," | cut -d',' -f3)
            if [ -z "$GENDER" ]; then
                GENDER=$(tail -n +2 database/nouns.csv | grep "\"$noun\"," | cut -d',' -f3)
            fi
            
            case "$GENDER" in
                "m") MASCULINE=$((MASCULINE + 1)) ;;
                "f") FEMININE=$((FEMININE + 1)) ;;
                *) UNKNOWN=$((UNKNOWN + 1)) ;;
            esac
        fi
    done < $TEMP_TOP_NOUNS
    
    echo "  Masculine: $MASCULINE nouns"
    echo "  Feminine:  $FEMININE nouns" 
    echo "  Unknown:   $UNKNOWN nouns"
    
    # Clean up temp files
    rm $TEMP_TOP_NOUNS $TEMP_COVERAGE
fi

# Count total unique words
TOTAL_WORDS=$(wc -l < $TEMP_WORDS)
UNIQUE_WORDS=$(sort $TEMP_WORDS | uniq | wc -l)

echo ""
echo "📈 Vocabulary Statistics:"
echo "  Total word instances: $TOTAL_WORDS"
echo "  Unique vocabulary: $UNIQUE_WORDS words"
echo "  Vocabulary richness: $(echo "scale=2; $UNIQUE_WORDS * 100 / $TOTAL_WORDS" | bc)%"

# Clean up temp file
rm $TEMP_WORDS

echo ""
echo "🏷️  TAG FREQUENCY ANALYSIS"
echo "=========================="

# Extract all tags and count frequency
echo "Analyzing content tags..."

# Create temporary file for tags
TEMP_TAGS=$(mktemp)

# Extract all tags from all question files
jq -r '.questions[].tags[]' question*.json > $TEMP_TAGS

# Count tag frequency
echo ""
echo "Content Tags by Frequency (Top 20 & Bottom 20):"
echo "-----------------------------------------------"

# Create temporary files for top and bottom tags
TEMP_TAG_COUNTS=$(mktemp)
sort $TEMP_TAGS | uniq -c | sort -nr > $TEMP_TAG_COUNTS

# Show top 20 tags
echo "🔥 TOP 20 MOST FREQUENT TAGS:"
head -20 $TEMP_TAG_COUNTS | \
    awk '{printf "%2d. %-20s (%d questions)\n", NR, $2, $1}'

echo ""
echo "🔻 BOTTOM 20 LEAST FREQUENT TAGS:"
tail -20 $TEMP_TAG_COUNTS | sort -n | \
    awk 'BEGIN{total=0} {tags[++total] = $0} END {
        for(i=total; i>=1; i--) {
            split(tags[i], parts)
            printf "%2d. %-20s (%d questions)\n", total-i+1, parts[2], parts[1]
        }
    }'

# Clean up temp file
rm $TEMP_TAG_COUNTS

# Count total tags
TOTAL_TAGS=$(wc -l < $TEMP_TAGS)
UNIQUE_TAGS=$(sort $TEMP_TAGS | uniq | wc -l)

echo ""
echo "📈 Tag Statistics:"
echo "  Total tag instances: $TOTAL_TAGS"
echo "  Unique tags: $UNIQUE_TAGS"
echo "  Average tags per question: $(echo "scale=1; $TOTAL_TAGS / $(jq '.questions | length' question*.json | paste -sd+ | bc)" | bc)"

# Clean up temp file
rm $TEMP_TAGS

echo ""
echo "🎯 DIFFICULTY DISTRIBUTION"
echo "=========================="

# Count questions by difficulty level
echo "Questions by CEFR Level:"
echo "------------------------"
jq -r '.questions[].difficulty' question*.json | sort | uniq -c | sort -k2 | \
    awk '{
        level = $2
        count = $1
        if (level == "A1") desc = "Beginner"
        else if (level == "A2") desc = "Elementary" 
        else if (level == "B1") desc = "Intermediate"
        else if (level == "B2") desc = "Upper-Intermediate"
        else if (level == "C1") desc = "Advanced"
        else if (level == "C2") desc = "C2 - Proficiency"
        else desc = "Unknown"
        printf "  %-3s %-18s %2d questions\n", level, desc, count
    }'

echo ""
echo "📝 QUESTION TYPE DISTRIBUTION"
echo "============================="

# Count questions by type
echo "Questions by Type:"
echo "------------------"
jq -r '.questions[].questionType' question*.json | sort | uniq -c | sort -nr | \
    awk '{
        type = $2
        count = $1
        if (type == "comprehension") desc = "English comprehension"
        else if (type == "listening") desc = "French listening"
        else desc = "Other"
        printf "  %-13s %-20s %2d questions\n", type, desc, count
    }'

echo ""
echo "✅ Analysis complete!"
echo "" 