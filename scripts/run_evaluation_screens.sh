#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_evaluation_screens.sh [--embed-size N] [--max-jobs N] [--start-index N]
                                    [--poll-interval SEC] [--timeout SEC]

Launch detached screen sessions for learned evaluation jobs.

The canonical job order is:
  countries/default
  countries/embed
  countries/mod
  size200/default
  size200/embed
  size200/mod
  size300/default
  size300/embed
  size300/mod
  size400/default
  size400/embed
  size400/mod

By default the script launches all jobs. Use --max-jobs 8 to start the first
8 jobs, then rerun with --start-index 8 --max-jobs 4 for the remaining jobs.

Environment:
  PYTHON_BIN   Python interpreter to use. Defaults to the repo .venv.
  EMBED_SIZE   Embedding size for the embed variant. Defaults to 75.
  GPU_IDS      Space-separated GPU ids for countries size200 size300 size400.
               Defaults to: 0 1 2 3
  POLL_INTERVAL Seconds between checks for expected files. Default: 30.
  TIMEOUT       Maximum seconds to wait for expected files. Default: 0 (no timeout).
  OMP_NUM_THREADS, MKL_NUM_THREADS, NUMEXPR_NUM_THREADS
               Thread caps passed into each screen session.
EOF
}

EMBED_SIZE="${EMBED_SIZE:-75}"
MAX_JOBS="${MAX_JOBS:-12}"
START_INDEX="${START_INDEX:-0}"
POLL_INTERVAL="${POLL_INTERVAL:-30}"
TIMEOUT="${TIMEOUT:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --embed-size)
      EMBED_SIZE="${2:?missing value for --embed-size}"
      shift 2
      ;;
    --max-jobs)
      MAX_JOBS="${2:?missing value for --max-jobs}"
      shift 2
      ;;
    --start-index)
      START_INDEX="${2:?missing value for --start-index}"
      shift 2
      ;;
    --poll-interval)
      POLL_INTERVAL="${2:?missing value for --poll-interval}"
      shift 2
      ;;
    --timeout)
      TIMEOUT="${2:?missing value for --timeout}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! [[ "$EMBED_SIZE" =~ ^[0-9]+$ && "$MAX_JOBS" =~ ^[0-9]+$ && "$START_INDEX" =~ ^[0-9]+$ && "$POLL_INTERVAL" =~ ^[0-9]+$ && "$TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo "EMBED_SIZE, MAX_JOBS, START_INDEX, POLL_INTERVAL, and TIMEOUT must be integers." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

if ! command -v screen >/dev/null 2>&1; then
  echo "screen is required but was not found in PATH." >&2
  echo "Install screen or run the evaluation jobs in separate terminals instead." >&2
  exit 1
fi

mkdir -p "$ROOT_DIR/logs"

read -r -a GPU_IDS <<< "${GPU_IDS:-0 1 2 3}"
if [[ ${#GPU_IDS[@]} -lt 1 ]]; then
  echo "Need at least one GPU id in GPU_IDS." >&2
  exit 1
fi

KBS=(countries size200 size300 size400)
JOBS=()
for kb_name in "${KBS[@]}"; do
  JOBS+=("${kb_name}:default")
  JOBS+=("${kb_name}:embed")
  JOBS+=("${kb_name}:mod")
done

if (( START_INDEX >= ${#JOBS[@]} )); then
  echo "START_INDEX ${START_INDEX} is past the end of the ${#JOBS[@]}-job queue." >&2
  exit 1
fi

END_INDEX=$(( START_INDEX + MAX_JOBS ))
if (( END_INDEX > ${#JOBS[@]} )); then
  END_INDEX=${#JOBS[@]}
fi

start_session() {
  local kb_name="$1"
  local variant="$2"
  local gpu_id="$3"
  local session_name="c327-${kb_name}-${variant}-eval"
  local log_file="$ROOT_DIR/logs/${session_name}.log"
  local work_dir="$ROOT_DIR/${kb_name}/${variant}"
  local kb_path=""
  local data_dir=""
  local eval_script=""
  local eval_cmd=""
  case "$kb_name" in
    countries)
      kb_path="$ROOT_DIR/countries/countries_kb.txt"
      data_dir="$ROOT_DIR/data/countries"
      ;;
    size200|size300|size400)
      kb_path="$ROOT_DIR/$kb_name/randomKB.txt"
      data_dir="$ROOT_DIR/data/random/$kb_name"
      ;;
    *)
      echo "Unknown KB: $kb_name" >&2
      exit 1
      ;;
  esac

  case "$variant" in
    default)
      eval_script="$ROOT_DIR/evaluate.py"
      ;;
    embed)
      eval_script="$ROOT_DIR/evaluate.py"
      ;;
    mod)
      eval_script="$ROOT_DIR/evaluate2.py"
      ;;
    *)
      echo "Unknown variant: $variant" >&2
      exit 1
      ;;
  esac

  if [[ ! -f "$kb_path" ]]; then
    echo "Missing KB file: $kb_path" >&2
    exit 1
  fi

  mkdir -p "$work_dir"
  ln -sfn "$data_dir/test_queries.txt" "$work_dir/test_queries.txt"
  ln -sfn "$data_dir/vocab.pkl" "$work_dir/vocab.pkl"

  if [[ ! -d "$work_dir" ]]; then
    echo "Missing work dir: $work_dir" >&2
    exit 1
  fi

  if screen -list | grep -qE "[.]${session_name}[[:space:]]"; then
    echo "Screen session already exists: ${session_name}" >&2
    return 1
  fi

  echo "Starting ${session_name} on GPU ${gpu_id}"
  screen -L -Logfile "$log_file" -dmS "$session_name" bash -lc "
    set -euo pipefail
    cd '$ROOT_DIR'
    export PYTHON_BIN='$PYTHON_BIN'
    export CUDA_VISIBLE_DEVICES='$gpu_id'
    export OMP_NUM_THREADS='${OMP_NUM_THREADS:-8}'
    export MKL_NUM_THREADS='${MKL_NUM_THREADS:-8}'
    export NUMEXPR_NUM_THREADS='${NUMEXPR_NUM_THREADS:-8}'
    echo 'Session: $session_name'
    echo 'KB:      $kb_name'
    echo 'Variant: $variant'
    echo 'GPU:     $gpu_id'
    echo 'Embed:   $EMBED_SIZE'
    exec '$ROOT_DIR/scripts/run_evaluation_job.sh' '$ROOT_DIR' '$kb_name' '$variant' '$EMBED_SIZE' '$PYTHON_BIN' '$POLL_INTERVAL' '$TIMEOUT'
  "

  echo "  log: $log_file"
  echo "  attach: screen -r $session_name"
}

echo "Launching jobs ${START_INDEX}..$((END_INDEX - 1)) out of ${#JOBS[@]}"
for idx in $(seq "$START_INDEX" $((END_INDEX - 1))); do
  job="${JOBS[$idx]}"
  kb_name="${job%%:*}"
  variant="${job##*:}"
  gpu_id="${GPU_IDS[$(( idx % ${#GPU_IDS[@]} ))]}"
  start_session "$kb_name" "$variant" "$gpu_id"
done

echo
echo "Use 'screen -ls' to list sessions and 'screen -r <session>' to attach."
