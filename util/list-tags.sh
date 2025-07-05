#!/bin/bash

# List all tags across French language learning question files
# Usage: ./list-tags.sh [--count] [--file filename]

SHOW_COUNT=false
SPECIFIC_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --count|-c)
            SHOW_COUNT=true
            shift
            ;;
        --file|-f)
            SPECIFIC_FILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --count, -c     Show usage count for each tag"
            echo "  --file, -f      Show tags from specific file only"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # List all unique tags"
            echo "  $0 --count           # List tags with usage counts"
            echo "  $0 --file questions-a.json  # List tags from A-level file only"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed. Please install jq first."
    echo "   sudo apt-get install jq  # Ubuntu/Debian"
    echo "   brew install jq          # macOS"
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

# Set files to process
if [ -n "$SPECIFIC_FILE" ]; then
    if [ ! -f "$SPECIFIC_FILE" ]; then
        echo "❌ File $SPECIFIC_FILE not found"
        exit 1
    fi
    QUESTION_FILES=("$SPECIFIC_FILE")
else
    # Use compiled files for much faster execution
    COMPILED_FILES=(
        "${PATH_PREFIX}q-compiled-a.json"
        "${PATH_PREFIX}q-compiled-b.json"
        "${PATH_PREFIX}q-compiled-c.json"
    )
    
    # Check if compiled files exist, fallback to source files
    QUESTION_FILES=()
    for file in "${COMPILED_FILES[@]}"; do
        if [ -f "$file" ]; then
            QUESTION_FILES+=("$file")
        fi
    done
    
    # If no compiled files found, use source files
    if [ ${#QUESTION_FILES[@]} -eq 0 ]; then
        echo "⚠️  No compiled files found, using source files (slower)"
        QUESTION_FILES=($(find "${PATH_PREFIX}questions/source" -name "q*.json" 2>/dev/null | sort))
    fi
fi

echo "🏷️  Tag Analysis Report"
echo "======================="

# Function to extract all tags from files
extract_all_tags() {
    for file in "${QUESTION_FILES[@]}"; do
        if [ -f "$file" ]; then
            # Handle both individual source files and monolithic files
            if jq -e '.questions' "$file" >/dev/null 2>&1; then
                # Monolithic format
                jq -r '.questions[]?.tags[]?' "$file" 2>/dev/null
            else
                # Individual source format
                jq -r '.tags[]?' "$file" 2>/dev/null
            fi
        fi
    done
}

# Function to get all tags with counts efficiently
get_tags_with_counts() {
    for file in "${QUESTION_FILES[@]}"; do
        if [ -f "$file" ]; then
            # Handle both individual source files and monolithic files
            if jq -e '.questions' "$file" >/dev/null 2>&1; then
                # Monolithic format - extract all tags at once
                jq -r '.questions[]?.tags[]?' "$file" 2>/dev/null
            else
                # Individual source format - extract all tags at once
                jq -r '.tags[]?' "$file" 2>/dev/null
            fi
        fi
    done | sort | uniq -c | sort -nr
}

# Get all unique tags
ALL_TAGS=$(extract_all_tags | sort | uniq)
TOTAL_UNIQUE=$(echo "$ALL_TAGS" | wc -l)

if [ -z "$ALL_TAGS" ]; then
    echo "ℹ️  No tags found in the specified files"
    exit 0
fi

echo "📊 Found $TOTAL_UNIQUE unique tags across question files"
echo

if [ "$SHOW_COUNT" = true ]; then
    echo "Tag Usage Counts:"
    echo "-----------------"
    
    # Use the efficient count function
    get_tags_with_counts | while read -r count tag; do
        if [ -n "$tag" ]; then
            printf "  %-3s %s\n" "$count" "$tag"
        fi
    done
else
    echo "All Tags (alphabetical):"
    echo "------------------------"
    echo "$ALL_TAGS" | while IFS= read -r tag; do
        if [ -n "$tag" ]; then
            echo "  $tag"
        fi
    done
fi

echo
echo "💡 TIP: Use './delete-tag.sh <tag>' to remove a single tag"
echo "💡 TIP: Use './delete-tag.sh <tag1> <tag2> <tag3>' to remove multiple tags"
echo "💡 TIP: Use '$0 --count' to see tag usage frequency" 