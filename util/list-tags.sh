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
if [ -f "questions.json" ]; then
    PATH_PREFIX=""
else
    PATH_PREFIX="../"
fi

# Set files to process
if [ -n "$SPECIFIC_FILE" ]; then
    if [ ! -f "$SPECIFIC_FILE" ]; then
        echo "❌ File $SPECIFIC_FILE not found"
        exit 1
    fi
    QUESTION_FILES=("$SPECIFIC_FILE")
else
    QUESTION_FILES=("${PATH_PREFIX}questions.json" "${PATH_PREFIX}questions-a.json" "${PATH_PREFIX}questions-b.json" "${PATH_PREFIX}questions-c.json")
fi

echo "🏷️  Tag Analysis Report"
echo "======================="

# Function to extract all tags from files
extract_all_tags() {
    for file in "${QUESTION_FILES[@]}"; do
        if [ -f "$file" ]; then
            jq -r '.questions[]?.tags[]?' "$file" 2>/dev/null
        fi
    done
}

# Function to count tag usage
count_tag_usage() {
    local tag="$1"
    local count=0
    for file in "${QUESTION_FILES[@]}"; do
        if [ -f "$file" ]; then
            local file_count=$(jq -r ".questions[] | select(.tags[]? == \"$tag\") | .id" "$file" 2>/dev/null | wc -l)
            count=$((count + file_count))
        fi
    done
    echo "$count"
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
    
    # Create a temporary file for sorting by count
    temp_file=$(mktemp)
    
    while IFS= read -r tag; do
        if [ -n "$tag" ]; then
            count=$(count_tag_usage "$tag")
            echo "$count|$tag" >> "$temp_file"
        fi
    done <<< "$ALL_TAGS"
    
    # Sort by count (descending) and display
    sort -t'|' -k1,1nr "$temp_file" | while IFS='|' read -r count tag; do
        printf "  %-3s %s\n" "$count" "$tag"
    done
    
    rm -f "$temp_file"
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