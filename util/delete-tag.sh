#!/bin/bash

# Surgical tag deletion tool for French language learning question bank
# Usage: ./delete-tag.sh <tag1> [tag2] [tag3] ...

if [ $# -eq 0 ]; then
    echo "Usage: $0 <tag1> [tag2] [tag3] ..."
    echo "Examples:"
    echo "  $0 grammar                           # Remove single tag"
    echo "  $0 grammar verb-conjugation B2       # Remove multiple tags"
    echo "  $0 listening exact-comprehension     # Remove related tags"
    exit 1
fi

# Determine path based on current directory
if [ -f "questions/q-compiled-a.json" ]; then
    PATH_PREFIX="questions/"
elif [ -f "../questions/q-compiled-a.json" ]; then
    PATH_PREFIX="../questions/"
else
    PATH_PREFIX=""
fi

TAGS_TO_REMOVE=("$@")

# Function to find question IDs containing tags using compiled files (faster)
find_questions_with_tags() {
    local compiled_files=(
        "${PATH_PREFIX}q-compiled-a.json"
        "${PATH_PREFIX}q-compiled-b.json" 
        "${PATH_PREFIX}q-compiled-c.json"
    )
    
    for tag in "${TAGS_TO_REMOVE[@]}"; do
        for file in "${compiled_files[@]}"; do
            if [ -f "$file" ]; then
                jq -r ".questions[] | select(.tags[]? == \"$tag\") | .id" "$file" 2>/dev/null
            fi
        done
    done | sort -n | uniq
}

# Get list of question IDs that contain any of the target tags
echo "🔍 Pre-scanning compiled files for efficiency..."
AFFECTED_IDS=($(find_questions_with_tags))

if [ ${#AFFECTED_IDS[@]} -eq 0 ]; then
    echo "ℹ️  No questions found containing any of the specified tags: ${TAGS_TO_REMOVE[*]}"
    echo "   No files need to be processed."
    exit 0
fi

echo "📋 Found ${#AFFECTED_IDS[@]} questions potentially containing target tags"
echo "   Only processing relevant source files for efficiency"

# Build list of source files to process based on affected IDs
QUESTION_FILES=()
for id in "${AFFECTED_IDS[@]}"; do
    source_file="${PATH_PREFIX}source/q${id}.json"
    if [ -f "$source_file" ]; then
        QUESTION_FILES+=("$source_file")
    fi
done
TOTAL_REMOVED=0
TAGS_PROCESSED=()
TAGS_FOUND=()

echo "🔍 Searching for ${#TAGS_TO_REMOVE[@]} tag(s) across all question files..."
echo "   Tags to remove: ${TAGS_TO_REMOVE[*]}"
echo

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed. Please install jq first."
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
    exit 1
fi

# Function to clean up old backups, keeping only the last 5
cleanup_old_backups() {
    local file="$1"
    local backup_pattern="${file}.backup.*"
    
    # Find all backup files for this file, sort by modification time (newest first)
    local backup_files=($(ls -t ${backup_pattern} 2>/dev/null))
    local backup_count=${#backup_files[@]}
    
    if [ $backup_count -gt 5 ]; then
        echo "🧹 Cleaning up old backups for $file (keeping last 5 of $backup_count)" >&2
        # Remove backups beyond the 5 newest
        for ((i=5; i<backup_count; i++)); do
            echo "   Removing: ${backup_files[i]}" >&2
            rm -f "${backup_files[i]}"
        done
    fi
}

# Function to count tag occurrences in a file
count_tag_occurrences() {
    local file="$1"
    local tag="$2"
    if [ ! -f "$file" ]; then
        echo "0"
        return
    fi
    # Handle both individual source files and monolithic files
    if jq -e '.questions' "$file" >/dev/null 2>&1; then
        # Monolithic format: {questions: [...]}
        jq -r ".questions[] | select(.tags[]? == \"$tag\") | .id" "$file" 2>/dev/null | wc -l
    else
        # Individual source format: single question object
        jq -r "select(.tags[]? == \"$tag\") | .id" "$file" 2>/dev/null | wc -l
    fi
}

# Function to remove tag from a file
remove_tag_from_file() {
    local file="$1"
    local tag="$2"
    
    if [ ! -f "$file" ]; then
        echo "⚠️  File $file not found, skipping..." >&2
        echo "0"
        return
    fi
    
    # Count before removal
    local before_count=$(count_tag_occurrences "$file" "$tag")
    
    if [ "$before_count" -eq 0 ]; then
        echo "✅ $file: No instances of '$tag' found" >&2
        echo "0"
        return
    fi
    
    # Show which questions will be affected
    echo "📝 $file: Found '$tag' in questions:" >&2
    if jq -e '.questions' "$file" >/dev/null 2>&1; then
        # Monolithic format
        jq -r ".questions[] | select(.tags[]? == \"$tag\") | \"   ID \(.id): \(.audioText[0:50])...\"" "$file" 2>/dev/null >&2
    else
        # Individual source format
        jq -r "select(.tags[]? == \"$tag\") | \"   ID \(.id): \(.audioText[0:50])...\"" "$file" 2>/dev/null >&2
    fi
    
    # Create backup
    cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Clean up old backups, keeping only the last 5
    cleanup_old_backups "$file"
    
    # Remove the tag using jq
    if jq -e '.questions' "$file" >/dev/null 2>&1; then
        # Monolithic format
        jq "(.questions[] | .tags) |= map(select(. != \"$tag\"))" "$file" > "${file}.tmp"
    else
        # Individual source format
        jq ".tags |= map(select(. != \"$tag\"))" "$file" > "${file}.tmp"
    fi
    
    # Check if jq succeeded
    if [ $? -eq 0 ]; then
        mv "${file}.tmp" "$file"
        echo "✅ $file: Removed $before_count instances of '$tag'" >&2
        echo "💾 Backup created: ${file}.backup.$(date +%Y%m%d_%H%M%S)" >&2
        echo "$before_count"  # Only the count goes to stdout
    else
        rm -f "${file}.tmp"
        echo "❌ $file: Error processing file" >&2
        echo "0"  # Only the count goes to stdout
    fi
}

# Process each tag
for tag in "${TAGS_TO_REMOVE[@]}"; do
    echo "=========================================="
    echo "🏷️  Processing tag: '$tag'"
    echo "=========================================="
    
    tag_found=false
    tag_total=0
    
    # Process each file for this tag
    for file in "${QUESTION_FILES[@]}"; do
        echo "----------------------------------------"
        removed_count=$(remove_tag_from_file "$file" "$tag")
        if [ "$removed_count" -gt 0 ]; then
            tag_found=true
            tag_total=$((tag_total + removed_count))
        fi
        TOTAL_REMOVED=$((TOTAL_REMOVED + removed_count))
        echo
    done
    
    # Track which tags were processed and found
    TAGS_PROCESSED+=("$tag")
    if [ "$tag_found" = true ]; then
        TAGS_FOUND+=("$tag")
        echo "✅ Tag '$tag' removed from $tag_total question(s)"
    else
        echo "ℹ️  Tag '$tag' not found in any questions"
    fi
    echo
done

echo "=========================================="
echo "🎯 FINAL SUMMARY:"
echo "   Tags processed: ${#TAGS_PROCESSED[@]} (${TAGS_PROCESSED[*]})"
echo "   Tags found & removed: ${#TAGS_FOUND[@]} (${TAGS_FOUND[*]})"
echo "   Total questions affected: $TOTAL_REMOVED"
echo "   Backup files created for safety"
echo

if [ $TOTAL_REMOVED -gt 0 ]; then
    echo "🔄 Recompiling question files to update compiled versions..."
    
    # Determine compilation command based on current directory
    if [ -f "compile-questions.js" ]; then
        node compile-questions.js >/dev/null 2>&1
    elif [ -f "../compile-questions.js" ]; then
        (cd .. && node compile-questions.js >/dev/null 2>&1)
    else
        echo "⚠️  Could not find compile-questions.js for automatic recompilation"
        echo "💡 TIP: Run 'node compile-questions.js' manually to update compiled files"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Compiled files updated successfully"
    else
        echo "⚠️  Compilation may have failed - check manually"
    fi
    echo
    
    echo "💡 TIP: Run 'bash analyze-questions.sh' to see updated statistics"
    echo "💡 TIP: Use 'git diff' to review changes before committing"
else
    echo "ℹ️  No changes made - none of the specified tags were found"
fi 