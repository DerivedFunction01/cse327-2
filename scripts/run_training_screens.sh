#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_training_screens.sh [--embed-size N] [--max-jobs N] [--start-index N]

Launch detached screen sessions for a batch of training jobs.

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
  OMP_NUM_THREADS, MKL_NUM_THREADS, NUMEXPR_NUM_THREADS
               Thread caps passed into each screen session.
EOF
}

EMBED_SIZE="${EMBED_SIZE:-75}"
MAX_JOBS="${MAX_JOBS:-12}"
START_INDEX="${START_INDEX:-0}"

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
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! [[ "$EMBED_SIZE" =~ ^[0-9]+$ && "$MAX_JOBS" =~ ^[0-9]+$ && "$START_INDEX" =~ ^[0-9]+$ ]]; then
  echo "EMBED_SIZE, MAX_JOBS, and START_INDEX must be integers." >&2
  exit 1
fi

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

if ! command -v screen >/dev/null 2>&1; then
  echo "screen is required but was not found in PATH." >&2
  echo "Install screen or run the four training jobs in separate terminals instead." >&2
  exit 1
fi

mkdir -p "$ROOT_DIR/logs"

read -r -a GPU_IDS <<< "${GPU_IDS:-0 1 2 3}"
KBS=(countries size200 size300 size400)
if [[ ${#GPU_IDS[@]} -lt 1 ]]; then
  echo "Need at least one GPU id in GPU_IDS." >&2
  exit 1
fi

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
  local session_name="c327-${kb_name}-${variant}"
  local log_file="$ROOT_DIR/logs/${session_name}.log"
  local pipeline_cmd=""

  case "$variant" in
    default)
      pipeline_cmd="bash '$ROOT_DIR/scripts/run_training_pipeline.sh' '$kb_name' default"
      ;;
    embed)
      pipeline_cmd="bash '$ROOT_DIR/scripts/run_training_pipeline.sh' '$kb_name' embed '$EMBED_SIZE'"
      ;;
    mod)
      pipeline_cmd="bash '$ROOT_DIR/scripts/run_training_pipeline.sh' '$kb_name' mod"
      ;;
    *)
      echo "Unknown variant: $variant" >&2
      exit 1
      ;;
  esac

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
    echo 'Variant:  $variant'
    echo 'GPU:      $gpu_id'
    echo 'Embed:    $EMBED_SIZE'
    $pipeline_cmd
    echo 'Completed $session_name'
    exec bash
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
