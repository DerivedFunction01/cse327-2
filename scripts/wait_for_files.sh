#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: wait_for_files.sh [--poll-interval N] [--timeout N] -- file1 file2 -- command...

Wait until all listed files exist, then exec the command.

Environment:
  POLL_INTERVAL  Seconds between checks. Default: 30.
  TIMEOUT        Maximum seconds to wait. Default: 0 (no timeout).
EOF
}

POLL_INTERVAL="${POLL_INTERVAL:-30}"
TIMEOUT="${TIMEOUT:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --poll-interval)
      POLL_INTERVAL="${2:?missing value for --poll-interval}"
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:?missing value for --timeout}"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! [[ "$POLL_INTERVAL" =~ ^[0-9]+$ && "$TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo "POLL_INTERVAL and TIMEOUT must be integers." >&2
  exit 1
fi

expected_files=()
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--" ]]; then
    shift
    break
  fi
  expected_files+=("$1")
  shift
done

if [[ ${#expected_files[@]} -eq 0 ]]; then
  echo "At least one expected file is required." >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "A command to exec is required after the file list." >&2
  exit 1
fi

start_ts="$(date +%s)"
while true; do
  missing=()
  for file in "${expected_files[@]}"; do
    [[ -e "$file" ]] || missing+=("$file")
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    break
  fi
  if (( TIMEOUT > 0 )); then
    now_ts="$(date +%s)"
    if (( now_ts - start_ts >= TIMEOUT )); then
      echo "Timed out waiting for files:" >&2
      printf '  %s\n' "${missing[@]}" >&2
      exit 1
    fi
  fi
  echo "Waiting for files:"
  printf '  %s\n' "${missing[@]}"
  sleep "$POLL_INTERVAL"
done

exec "$@"
