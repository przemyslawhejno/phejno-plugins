#!/usr/bin/env bash
export LC_NUMERIC=C

# Hard dependency: jq is used throughout to parse the JSON piped in via stdin.
# Fail loud (in the status line itself, since stderr isn't shown) rather than
# silently producing an empty/garbled line.
if ! command -v jq >/dev/null 2>&1; then
  printf "\033[31mstatusline plugin: 'jq' not found on PATH - install it (e.g. apt/brew/snap install jq)\033[0m"
  exit 0
fi

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // "?"')
model=$(echo "$input" | jq -r '.model.display_name // "?"')
effort=$(echo "$input" | jq -r '.effort.level // empty')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
session_id=$(echo "$input" | jq -r '.session_id // empty')
session=$(echo "$input" | jq -r '.session_name // empty')
session_cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
rl5_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
rl5_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
rl7_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
rl7_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
fast_mode=$(echo "$input" | jq -r '.fast_mode // false')
cache_hit_ratio=$(echo "$input" | jq -r '.prompt_cache.hit_ratio // empty')
cache_warm=$(echo "$input" | jq -r '.prompt_cache.warm | if . == null then empty else tostring end')

# Shorten home directory to ~
home="$HOME"
cwd="${cwd/#$home/\~}"

# Context usage - just percentage
if [ -n "$used" ]; then
  used_int=${used%.*}
  ctx_str="ctx:${used_int}%"
else
  ctx_str="ctx:--"
fi

# Rate limits - 5h
rl_str=""
if [ -n "$rl5_pct" ]; then
  rl5_int=${rl5_pct%.*}
  rl5_reset_str=""
  if [ -n "$rl5_reset" ]; then
    now=$(date +%s)
    diff=$(( rl5_reset - now ))
    if [ "$diff" -gt 0 ]; then
      mins=$(( diff / 60 ))
      rl5_reset_str=" (~${mins}m)"
    fi
  fi
  rl_str=" | \033[35mrl5h:${rl5_int}%${rl5_reset_str}\033[0m"
fi

# Rate limits - weekly
if [ -n "$rl7_pct" ]; then
  rl7_int=${rl7_pct%.*}
  rl7_reset_str=""
  if [ -n "$rl7_reset" ]; then
    now=$(date +%s)
    diff=$(( rl7_reset - now ))
    if [ "$diff" -gt 0 ]; then
      days=$(( diff / 86400 ))
      hrs=$(( (diff % 86400) / 3600 ))
      rl7_reset_str=" (~${days}d${hrs}h)"
    fi
  fi
  rl_str="${rl_str} | \033[35mrl7d:${rl7_int}%${rl7_reset_str}\033[0m"
fi

# Session cost
cost_str=""
if [ -n "$session_cost" ] && [ "$session_cost" != "0" ]; then
  cost_str=" | \033[33m\$$(printf '%.2f' "$session_cost")\033[0m"
fi

# Monthly + daily cost tracking
monthly_cost_str=""
daily_cost_str=""
if [ -n "$session_id" ] && [ -n "$session_cost" ]; then
  cost_dir="$HOME/.claude/monthly-costs"
  mkdir -p "$cost_dir"
  month_file="$cost_dir/$(date +%Y-%m).tsv"
  touch "$month_file"

  # Update current session cost in the file
  if grep -q "^${session_id}	" "$month_file" 2>/dev/null; then
    sed -i "s/^${session_id}	.*/${session_id}	${session_cost}/" "$month_file"
  else
    echo "${session_id}	${session_cost}" >> "$month_file"
  fi

  # Sum all session costs for the month
  monthly_total=$(awk -F'\t' '{s+=$2} END {printf "%.2f", s}' "$month_file")
  monthly_cost_str=" | \033[33mmo:\$${monthly_total}\033[0m"

  # Daily tracking: reuse the month file, keyed by day, filtered by today's date prefix
  day_dir="$HOME/.claude/daily-costs"
  mkdir -p "$day_dir"
  day_file="$day_dir/$(date +%Y-%m-%d).tsv"
  touch "$day_file"

  if grep -q "^${session_id}	" "$day_file" 2>/dev/null; then
    sed -i "s/^${session_id}	.*/${session_id}	${session_cost}/" "$day_file"
  else
    echo "${session_id}	${session_cost}" >> "$day_file"
  fi

  daily_total=$(awk -F'\t' '{s+=$2} END {printf "%.2f", s}' "$day_file")
  daily_cost_str=" | \033[33md:\$${daily_total}\033[0m"
fi

# Resolve cwd to an absolute path for git commands
if [[ "$cwd" == \~* ]]; then
  abs_cwd="$HOME/${cwd/#\~\//}"
else
  abs_cwd="$cwd"
fi

# Git branch
git_str=""
git_branch=$(git -C "$abs_cwd" branch --show-current 2>/dev/null)
if [ -n "$git_branch" ]; then
  dirty=$(git -C "$abs_cwd" status --short 2>/dev/null | wc -l | tr -d ' ')
  [ "$dirty" -gt 0 ] && git_branch="${git_branch}*"
  git_str=" | \033[32m${git_branch}\033[0m"
fi

# Session name
if [ -n "$session" ]; then
  session_str=" [$session]"
else
  session_str=""
fi

# Model + effort
if [ -n "$effort" ]; then
  model_str="${model}/${effort}"
else
  model_str="$model"
fi

# Fast mode indicator
fast_str=""
if [ "$fast_mode" = "true" ]; then
  fast_str=$' \033[31m\xe2\x9a\xa1\033[0m'
fi

# Cache hit ratio
cache_str=""
if [ -n "$cache_hit_ratio" ]; then
  cache_pct=$(awk -v r="$cache_hit_ratio" 'BEGIN { printf "%.0f", r * 100 }')
  cache_color="\033[32m"
  [ "$cache_pct" -lt 80 ] && cache_color="\033[33m"
  [ "$cache_pct" -lt 50 ] && cache_color="\033[31m"
  cache_str=" | ${cache_color}cache:${cache_pct}%%\033[0m"
elif [ "$cache_warm" = "false" ]; then
  cache_str=" | \033[31mcache:cold\033[0m"
fi

printf "\033[33m%s\033[0m${fast_str} | \033[36m%s\033[0m${cache_str}${rl_str}${cost_str}${daily_cost_str}${monthly_cost_str}%s${git_str} | \033[34m%s\033[0m" \
  "$model_str" "$ctx_str" "$session_str" "$cwd"
