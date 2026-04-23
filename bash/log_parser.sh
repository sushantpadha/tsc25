#!/usr/bin/env bash
# log_parser.sh — parse app logs into CSV + print stats
#
# Log format:
#   [2025-04-23 14:05:32] [INFO]  login  user=alice duration=320ms
#   [2025-04-23 14:06:01] [ERROR] logout user=bob   duration=150ms
#
# Usage: ./log_parser.sh <logfile> [max_age_days]
#   logfile       path to log file
#   max_age_days  skip entries older than N days (default: 30)

# ── usage / arg check ──────────────────────────────────────────
usage() {
    echo "Usage: $0 <logfile> [max_age_days]" >&2
    exit 1
}

[[ $# -lt 1 ]]        && usage
[[ ! -f "$1" ]]       && { echo "Error: file '$1' not found" >&2; exit 1; }
[[ ! -r "$1" ]]       && { echo "Error: file '$1' not readable" >&2; exit 1; }

LOGFILE="$1"
MAX_AGE_DAYS="${2:-30}"
OUTFILE="output.csv"
CUTOFF_EPOCH=$(date -d "-${MAX_AGE_DAYS} days" +%s 2>/dev/null) \
    || { echo "Error: 'date' command failed" >&2; exit 1; }

# ── parse timestamp → unix epoch ──────────────────────────────
to_epoch() {
    local ts="$1"          # expects: "2025-04-23 14:05:32"
    date -d "$ts" +%s 2>/dev/null || { echo "0"; return 1; }
}

# ── check if entry is recent enough ───────────────────────────
is_recent() {
    local epoch="$1"
    (( epoch >= CUTOFF_EPOCH ))   # returns 0 (true) if recent
}

# ── parse a single log line into fields ───────────────────────
# sets globals: TS_RAW, EPOCH, LEVEL, EVENT, USER, DURATION_MS
parse_line() {
    local line="$1"
    local regex='^\[([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] \[([A-Z]+)\] +([a-z]+) +user=([^ ]+) +duration=([0-9]+)ms'

    [[ "$line" =~ $regex ]] || return 1

    TS_RAW="${BASH_REMATCH[1]}"
    LEVEL="${BASH_REMATCH[2]}"
    EVENT="${BASH_REMATCH[3]}"
    USER="${BASH_REMATCH[4]}"
    DURATION_MS="${BASH_REMATCH[5]}"
    EPOCH=$(to_epoch "$TS_RAW") || return 1
    return 0
}

# ── write CSV header ───────────────────────────────────────────
init_csv() {
    local outfile="$1"
    echo "timestamp,epoch,level,event,user,duration_ms" > "$outfile" \
        && echo "Initialized $outfile" \
        || { echo "Error: cannot write to $outfile" >&2; exit 1; }
}

# ── append one parsed entry to CSV ────────────────────────────
write_csv_row() {
    local outfile="$1"
    echo "${TS_RAW},${EPOCH},${LEVEL},${EVENT},${USER},${DURATION_MS}" >> "$outfile"
}

# ── print statistics ───────────────────────────────────────────
print_stats() {
    local total="$1" errors="$2" skipped="$3"
    local duration_sum="$4" duration_count="$5"

    echo ""
    echo "──────────────── stats ────────────────"
    echo "  entries parsed : $total"
    echo "  errors         : $errors"
    echo "  skipped (old)  : $skipped"

    if (( duration_count > 0 )); then
        local avg
        avg=$(echo "scale=1; $duration_sum / $duration_count" | bc)
        echo "  avg duration   : ${avg}ms  (over $duration_count entries)"
    fi
    echo "───────────────────────────────────────"
    echo "  output         : $OUTFILE"
}

# ── main ───────────────────────────────────────────────────────
main() {
    local total=0 errors=0 skipped=0
    local duration_sum=0 duration_count=0

    init_csv "$OUTFILE"

    while IFS= read -r line; do
        [[ -z "$line" ]] && continue                  # skip blank lines

        parse_line "$line" || { (( errors++ )); continue; }

        if ! is_recent "$EPOCH"; then
            (( skipped++ ))
            continue
        fi

        write_csv_row "$OUTFILE"
        (( total++ ))
        (( duration_sum  += DURATION_MS ))
        (( duration_count++ ))

    done < "$LOGFILE"

    print_stats "$total" "$errors" "$skipped" "$duration_sum" "$duration_count"
}

main