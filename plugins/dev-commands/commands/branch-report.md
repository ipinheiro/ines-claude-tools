---
allowed-tools:
    - Bash(git:*)
    - Bash(date:*)
    - Bash(echo:*)
    - Bash(cat:*)
    - Bash(basename:*)
    - Bash(printf:*)
    - Bash(sed:*)
    - Bash(sort:*)
    - Write
description: Generate a report of stale git branches and their merge status with develop and main
---

# Enhanced Git Branch Report Generator

Generate a comprehensive analysis of git repository branches, identifying stale branches and providing actionable recommendations for cleanup.

**Usage**: `/branch-report [days] [--format=json|md] [--include-remote] [--author=name] [--output=path]`

**Arguments**:
- `days`: Staleness threshold in days (default: 30)
- `--format=json|md`: Output format (default: md)
- `--include-remote`: Include remote branch analysis
- `--author=name`: Filter by specific author
- `--output=path`: Custom output file path (default: branch-report-timestamp.{md|json})

## Important

For each branch which contains commits which have diverged from `main` or `develop`, and have not been merged into either of these branches, you MUST deploy a subagent to

1) Examine the branch and its commits
2) Summarise the changes which have been made
3) Write this change summary into the final report

## Enhanced Branch Analysis Script

!```bash
#!/bin/bash
set -euo pipefail

# Parse arguments
STALE_DAYS=30
OUTPUT_FORMAT="md"
INCLUDE_REMOTE=false
AUTHOR_FILTER=""
CUSTOM_OUTPUT=""
REPORT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --format=*)
      OUTPUT_FORMAT="${1#*=}"
      if [[ "$OUTPUT_FORMAT" != "json" && "$OUTPUT_FORMAT" != "md" ]]; then
        echo "Error: Format must be 'json' or 'md'"
        exit 1
      fi
      shift
      ;;
    --include-remote)
      INCLUDE_REMOTE=true
      shift
      ;;
    --author=*)
      AUTHOR_FILTER="${1#*=}"
      shift
      ;;
    --output=*)
      CUSTOM_OUTPUT="${1#*=}"
      shift
      ;;
    [0-9]*)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        STALE_DAYS="$1"
      else
        echo "Error: Days must be a positive integer"
        exit 1
      fi
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: branch-report [days] [--format=json|md] [--include-remote] [--author=name] [--output=path]"
      exit 1
      ;;
  esac
done

# Validate we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "Error: Not in a git repository"
  exit 1
fi

# Set output file based on format
TIMESTAMP=$(date +%Y%m%d%H%M%S)
if [[ -n "$CUSTOM_OUTPUT" ]]; then
  REPORT_FILE="$CUSTOM_OUTPUT"
else
  if [[ "$OUTPUT_FORMAT" == "json" ]]; then
    REPORT_FILE="branch-report-${TIMESTAMP}.json"
  else
    REPORT_FILE="branch-report-${TIMESTAMP}.md"
  fi
fi

echo "Generating branch report..."
echo "- Staleness threshold: $STALE_DAYS days"
echo "- Output format: $OUTPUT_FORMAT"
echo "- Include remote: $INCLUDE_REMOTE"
[[ -n "$AUTHOR_FILTER" ]] && echo "- Author filter: $AUTHOR_FILTER"

# Get current information
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
CURRENT_DATE=$(date +%s)

# Determine base branches
BASE_BRANCHES=()
for branch in develop main master; do
  if git show-ref --verify --quiet refs/heads/$branch; then
    BASE_BRANCHES+=("$branch")
  fi
done

if [[ ${#BASE_BRANCHES[@]} -eq 0 ]]; then
  echo "Warning: No standard base branches (develop/main/master) found"
  BASE_BRANCHES=("HEAD")
fi

echo "Base branches: ${BASE_BRANCHES[*]}"

# Fetch remote information if requested
if [[ "$INCLUDE_REMOTE" == "true" ]]; then
  echo "Fetching remote branch information..."
  if ! git fetch --all --prune > /dev/null 2>&1; then
    echo "Warning: Failed to fetch remote branches. Remote branch information may be incomplete."
    echo "Check your network connection and remote repository access."
  fi
fi

# Get all branches
if [[ "$INCLUDE_REMOTE" == "true" ]]; then
  ALL_BRANCHES=$(git branch -a --format='%(refname:short)' 2>/dev/null | grep -v '^origin/HEAD' | sort -u)
else
  ALL_BRANCHES=$(git branch --format='%(refname:short)' 2>/dev/null)
fi

# Check if we got any branches
if [[ -z "$ALL_BRANCHES" ]]; then
  echo "Error: No branches found. Is this a valid git repository?"
  exit 1
fi

# Initialize data structures
declare -A BRANCH_DATA
declare -A STALE_BRANCHES
declare -A ACTIVE_BRANCHES

# Analyze each branch
while IFS= read -r branch; do
  # Skip base branches - use exact matching to avoid partial matches
  if [[ " ${BASE_BRANCHES[*]} " == *" ${branch} "* ]]; then
    continue
  fi
  
  # Skip remote tracking branches if we're not including remote
  if [[ "$INCLUDE_REMOTE" == "false" && "$branch" =~ ^origin/ ]]; then
    continue
  fi
  
  # Get branch information - quote branch name to handle special characters
  if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null || git show-ref --verify --quiet "refs/remotes/$branch" 2>/dev/null; then
    # Optimize by getting all info in one git command
    IFS='|' read -r LAST_COMMIT_UNIX LAST_COMMIT_DATE LAST_AUTHOR LAST_COMMIT_HASH COMMIT_MESSAGE <<< "$(git log -1 --format="%ct|%cd|%an|%h|%s" --date=short "$branch" 2>/dev/null || echo "0|unknown|unknown|unknown|unknown")"
    # Reset IFS
    IFS=' '
    
    # Filter by author if specified
    if [[ -n "$AUTHOR_FILTER" && "$LAST_AUTHOR" != *"$AUTHOR_FILTER"* ]]; then
      continue
    fi
    
    # Calculate age
    if [[ "$LAST_COMMIT_UNIX" != "0" ]]; then
      AGE_SECONDS=$((CURRENT_DATE - LAST_COMMIT_UNIX))
      AGE_DAYS=$((AGE_SECONDS / 86400))
    else
      AGE_DAYS=999
    fi
    
    # Analyze merge status
    MERGE_STATUS=()
    UNIQUE_COMMITS=0
    for base in "${BASE_BRANCHES[@]}"; do
      if [[ "$base" != "HEAD" ]] && git show-ref --verify --quiet "refs/heads/$base" 2>/dev/null; then
        COMMITS_AHEAD=$(git rev-list --count "${base}..${branch}" 2>/dev/null || echo "0")
        COMMITS_BEHIND=$(git rev-list --count "${branch}..${base}" 2>/dev/null || echo "0")
        
        if [[ "$COMMITS_AHEAD" -gt 0 ]]; then
          MERGE_STATUS+=("${COMMITS_AHEAD} ahead of ${base}")
          UNIQUE_COMMITS=$((UNIQUE_COMMITS + COMMITS_AHEAD))
        fi
        if [[ "$COMMITS_BEHIND" -gt 0 ]]; then
          MERGE_STATUS+=("${COMMITS_BEHIND} behind ${base}")
        fi
      fi
    done
    
    # Store branch data - escape pipe characters in commit messages to prevent parsing issues
    SANITIZED_MESSAGE="${COMMIT_MESSAGE//|/_}"
    BRANCH_DATA["$branch"]="$LAST_COMMIT_DATE|$AGE_DAYS|$LAST_AUTHOR|$LAST_COMMIT_HASH|$SANITIZED_MESSAGE|${MERGE_STATUS[*]}|$UNIQUE_COMMITS"
    
    # Categorize branch
    if [[ $AGE_DAYS -gt $STALE_DAYS ]]; then
      STALE_BRANCHES["$branch"]="$AGE_DAYS"
    else
      ACTIVE_BRANCHES["$branch"]="$AGE_DAYS"
    fi
  fi
done <<< "$ALL_BRANCHES"

# Generate report based on format
if [[ "$OUTPUT_FORMAT" == "json" ]]; then
  # Generate JSON report
  cat > "$REPORT_FILE" << EOJSON
{
  "metadata": {
    "generated": "$(date -Iseconds)",
    "repository": "$(basename "$(git rev-parse --show-toplevel 2>/dev/null || echo "unknown")")",
    "current_branch": "$CURRENT_BRANCH",
    "base_branches": [$(printf '"%s",' "${BASE_BRANCHES[@]}" | sed 's/,$//')]
  },
  "summary": {
    "total_branches": $((${#STALE_BRANCHES[@]} + ${#ACTIVE_BRANCHES[@]})),
    "stale_branches": ${#STALE_BRANCHES[@]},
    "active_branches": ${#ACTIVE_BRANCHES[@]},
    "staleness_threshold_days": $STALE_DAYS
  },
  "branches": {
EOJSON

  # Add branch data to JSON
  FIRST=true
  for branch in $(printf '%s\n' "${!BRANCH_DATA[@]}" | sort); do
    IFS='|' read -r date age author hash message merge_status unique_commits <<< "${BRANCH_DATA[$branch]}"
    # Reset IFS
    IFS=' '
    
    if [[ "$FIRST" == "true" ]]; then
      FIRST=false
    else
      echo "," >> "$REPORT_FILE"
    fi
    
    RECOMMENDATION="review"
    if [[ $unique_commits -eq 0 ]]; then
      RECOMMENDATION="safe_to_delete"
    elif [[ $age -gt $((STALE_DAYS * 2)) ]]; then
      RECOMMENDATION="consider_merge_or_delete"
    fi
    
    cat >> "$REPORT_FILE" << EOJSON2
    "$branch": {
      "last_updated": "$date",
      "age_days": $age,
      "author": "$author",
      "last_commit": "$hash",
      "message": "$message",
      "merge_status": "$merge_status",
      "unique_commits": $unique_commits,
      "is_stale": $([ "$age" -gt "$STALE_DAYS" ] && echo "true" || echo "false"),
      "recommendation": "$RECOMMENDATION"
    }
EOJSON2
  done
  
  echo -e "\n  }\n}" >> "$REPORT_FILE"

else
  # Generate Markdown report
  cat > "$REPORT_FILE" << EOMD
# Enhanced Git Branch Report

Generated on $(date '+%Y-%m-%d %H:%M:%S')

## Repository Summary

- **Repository**: $(basename "$(git rev-parse --show-toplevel)")
- **Current branch**: $CURRENT_BRANCH
- **Base branches**: ${BASE_BRANCHES[*]}
- **Analysis threshold**: $STALE_DAYS days
- **Total branches analyzed**: $((${#STALE_BRANCHES[@]} + ${#ACTIVE_BRANCHES[@]}))

## Executive Summary

📊 **Statistics**:
- 🟢 Active branches (< $STALE_DAYS days): ${#ACTIVE_BRANCHES[@]}
- 🟡 Stale branches (≥ $STALE_DAYS days): ${#STALE_BRANCHES[@]}
- 📈 Health score: $(( (${#ACTIVE_BRANCHES[@]} * 100) / (${#STALE_BRANCHES[@]} + ${#ACTIVE_BRANCHES[@]} + 1) ))%

EOMD

  # Add stale branches section
  if [[ ${#STALE_BRANCHES[@]} -gt 0 ]]; then
    cat >> "$REPORT_FILE" << EOSTALE

## 🟡 Stale Branches Analysis

| Branch | Last Updated | Age (days) | Author | Last Commit | Merge Status | Recommendation |
|--------|--------------|------------|--------|-------------|--------------|----------------|
EOSTALE

    for branch in $(printf '%s\n' "${!STALE_BRANCHES[@]}" | sort); do
      IFS='|' read -r date age author hash message merge_status unique_commits <<< "${BRANCH_DATA[$branch]}"
      # Reset IFS
      IFS=' '
      
      if [[ $unique_commits -eq 0 ]]; then
        RECOMMENDATION="🗑️ Safe to delete"
      elif [[ $age -gt $((STALE_DAYS * 2)) ]]; then
        RECOMMENDATION="⚠️ Consider merge or delete"
      else
        RECOMMENDATION="🔍 Review for merge"
      fi
      
      echo "| \`$branch\` | $date | $age | $author | \`$hash\` | $merge_status | $RECOMMENDATION |" >> "$REPORT_FILE"
    done
  else
    echo -e "\n## ✅ No Stale Branches Found\n\nAll branches are actively maintained!" >> "$REPORT_FILE"
  fi

  # Add active branches section
  if [[ ${#ACTIVE_BRANCHES[@]} -gt 0 ]]; then
    cat >> "$REPORT_FILE" << EOACTIVE

## 🟢 Active Branches

| Branch | Last Updated | Age (days) | Author | Merge Status |
|--------|--------------|------------|--------|--------------|
EOACTIVE

    for branch in $(printf '%s\n' "${!ACTIVE_BRANCHES[@]}" | sort); do
      IFS='|' read -r date age author hash message merge_status unique_commits <<< "${BRANCH_DATA[$branch]}"
      # Reset IFS
      IFS=' '
      echo "| \`$branch\` | $date | $age | $author | $merge_status |" >> "$REPORT_FILE"
    done
  fi

  # Add recommendations section
  cat >> "$REPORT_FILE" << EOREC

## 🎯 Actionable Recommendations

### Immediate Actions
EOREC

  # Generate specific recommendations
  SAFE_TO_DELETE=()
  NEEDS_REVIEW=()
  CONSIDER_MERGE=()
  
  for branch in "${!BRANCH_DATA[@]}"; do
    IFS='|' read -r date age author hash message merge_status unique_commits <<< "${BRANCH_DATA[$branch]}"
    # Reset IFS
    IFS=' '
    
    if [[ $age -gt $STALE_DAYS ]]; then
      if [[ $unique_commits -eq 0 ]]; then
        SAFE_TO_DELETE+=("$branch")
      elif [[ $age -gt $((STALE_DAYS * 2)) ]]; then
        CONSIDER_MERGE+=("$branch")
      else
        NEEDS_REVIEW+=("$branch")
      fi
    fi
  done
  
  if [[ ${#SAFE_TO_DELETE[@]} -gt 0 ]]; then
    echo -e "\n**Branches safe to delete** (no unique commits):" >> "$REPORT_FILE"
    printf '- `%s`\n' "${SAFE_TO_DELETE[@]}" >> "$REPORT_FILE"
    echo -e "\n\`\`\`bash\n# Delete these branches safely" >> "$REPORT_FILE"
    printf 'git branch -d %s\n' "${SAFE_TO_DELETE[@]}" >> "$REPORT_FILE"
    echo -e "\`\`\`" >> "$REPORT_FILE"
  fi
  
  if [[ ${#NEEDS_REVIEW[@]} -gt 0 ]]; then
    echo -e "\n**Branches needing review** (merge candidates):" >> "$REPORT_FILE"
    printf '- `%s`\n' "${NEEDS_REVIEW[@]}" >> "$REPORT_FILE"
  fi
  
  if [[ ${#CONSIDER_MERGE[@]} -gt 0 ]]; then
    echo -e "\n**Long-stale branches** (urgent review needed):" >> "$REPORT_FILE"
    printf '- `%s`\n' "${CONSIDER_MERGE[@]}" >> "$REPORT_FILE"
  fi

  # Add footer
  cat >> "$REPORT_FILE" << EOFOOTER

---

### Usage Tips
- Run this report monthly for optimal branch hygiene
- Consider setting up automated cleanup for safe-to-delete branches
- Use `--author=name` to focus on specific contributors
- Use `--include-remote` for comprehensive remote branch analysis
- Use `--output=path` to specify a custom output location

*Report generated with enhanced branch-report command*
EOFOOTER

fi

echo "Report generated: $REPORT_FILE"

# Display summary
echo ""
echo "=== SUMMARY ==="
echo "📊 Total branches: $((${#STALE_BRANCHES[@]} + ${#ACTIVE_BRANCHES[@]}))"
echo "🟢 Active: ${#ACTIVE_BRANCHES[@]}"
echo "🟡 Stale: ${#STALE_BRANCHES[@]}"
echo "📄 Report: $REPORT_FILE"
```
