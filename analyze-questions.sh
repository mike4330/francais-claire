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

# Count word frequency
echo ""
echo "Top 50 Rarest French Nouns:"
echo "-----------------------------------"

# Check if French noun dictionary exists
if [ ! -f "res/french_nouns.tsv" ]; then
    echo "❌ Error: French noun dictionary not found at res/french_nouns.tsv"
    echo "Falling back to simple word frequency..."
    sort $TEMP_WORDS | uniq -c | sort -n | head -50 | \
        awk '{printf "%2d. %-20s (%d occurrences)\n", NR, $2, $1}'
else
    echo "Using French noun dictionary for accurate identification..."
    echo ""
    
    # Create temporary file for dictionary lookup
    TEMP_DICT_WORDS=$(mktemp)
    
    # Extract just the noun column from dictionary (skip header and comment lines)
    tail -n +2 res/french_nouns.tsv | grep -v '^#' | cut -f1 | sort -u > $TEMP_DICT_WORDS
    
    # Create temporary file for filtered results
    TEMP_NOUN_RESULTS=$(mktemp)
    
    # Get word frequency counts and filter only nouns from dictionary
    sort $TEMP_WORDS | uniq -c | sort -n | \
        while read count word; do
            # Check if word exists in noun dictionary
            if grep -qx "$word" $TEMP_DICT_WORDS; then
                echo "$count $word"
            fi
        done > $TEMP_NOUN_RESULTS
    
    # Display results
    if [ -s "$TEMP_NOUN_RESULTS" ]; then
        head -60 $TEMP_NOUN_RESULTS | \
            awk '{printf "%2d. %-20s (%d occurrences)\n", NR, $2, $1}'
        
        echo ""
        echo "📊 Noun Analysis Summary:"
        TOTAL_NOUNS=$(wc -l < $TEMP_NOUN_RESULTS)
        echo "  Found $TOTAL_NOUNS nouns in audioText content"
        echo "  Showing rarest 50 (least frequent first)"
        
        # Show some statistics about noun gender if possible
        if [ $TOTAL_NOUNS -gt 0 ]; then
            echo ""
            echo "🚻 Gender Distribution (from dictionary):"
                         # Join with dictionary to get gender info for found nouns
             head -50 $TEMP_NOUN_RESULTS | \
                 while read count word; do
                     grep -w "^$word" res/french_nouns.tsv | grep -v '^#' | head -1
                 done | \
                cut -f2 | sort | uniq -c | \
                awk '{
                    gender = $2
                    count = $1
                    if (gender == "m") desc = "masculine"
                    else if (gender == "f") desc = "feminine"
                    else desc = "unknown"
                    printf "  %-9s: %2d nouns\n", desc, count
                }'
        fi
    else
        echo "  No nouns found that match the dictionary."
        echo "  This might indicate the text contains mostly verbs, adjectives, or uncommon words."
    fi
    
    # Clean up temp files
    rm $TEMP_DICT_WORDS $TEMP_NOUN_RESULTS
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
echo "Content Tags by Frequency:"
echo "--------------------------"
sort $TEMP_TAGS | uniq -c | sort -nr | \
    awk '{printf "%2d. %-20s (%d questions)\n", NR, $2, $1}'

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