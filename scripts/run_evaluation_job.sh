#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_evaluation_job.sh <root_dir> <kb> <variant> <embed_size> <python_bin> <poll_interval> <timeout>

This waits for the expected model/input files, then runs the learned evaluation
for one job.
EOF
}

if [[ $# -ne 7 ]]; then
  usage
  exit 1
fi

ROOT_DIR="$1"
KB_NAME="$2"
VARIANT="$3"
EMBED_SIZE="$4"
PYTHON_BIN="$5"
POLL_INTERVAL="$6"
TIMEOUT="$7"

case "$KB_NAME" in
  countries)
    KB_PATH="$ROOT_DIR/countries/countries_kb.txt"
    DATA_DIR="$ROOT_DIR/data/countries"
    ;;
  size200|size300|size400)
    KB_PATH="$ROOT_DIR/$KB_NAME/randomKB.txt"
    DATA_DIR="$ROOT_DIR/data/random/$KB_NAME"
    ;;
  *)
    echo "Unknown KB: $KB_NAME" >&2
    exit 1
    ;;
esac

WORK_DIR="$ROOT_DIR/$KB_NAME/$VARIANT"
mkdir -p "$WORK_DIR"
ln -sfn "$DATA_DIR/test_queries.txt" "$WORK_DIR/test_queries.txt"
ln -sfn "$DATA_DIR/vocab.pkl" "$WORK_DIR/vocab.pkl"

case "$VARIANT" in
  default)
    EVAL_SCRIPT="$ROOT_DIR/evaluate.py"
    EVAL_ARGS=(
      --unifier
      --embed_model_path "$WORK_DIR/rKB_model.pth"
      --scoring_model_path "$WORK_DIR/uni_mr_model.pt"
    )
    EXPECTED_FILES=(
      "$WORK_DIR/rKB_model.pth"
      "$WORK_DIR/uni_mr_model.pt"
    )
    ;;
  embed)
    EVAL_SCRIPT="$ROOT_DIR/evaluate.py"
    EVAL_ARGS=(
      --unifier
      --embed_size "$EMBED_SIZE"
      --embed_model_path "$WORK_DIR/rKB_model_${EMBED_SIZE}.pth"
      --scoring_model_path "$WORK_DIR/uni_mr_model_${EMBED_SIZE}.pt"
    )
    EXPECTED_FILES=(
      "$WORK_DIR/rKB_model_${EMBED_SIZE}.pth"
      "$WORK_DIR/uni_mr_model_${EMBED_SIZE}.pt"
    )
    ;;
  mod)
    EVAL_SCRIPT="$ROOT_DIR/evaluate2.py"
    EVAL_ARGS=(
      --unifier
      --embed_model_path "$WORK_DIR/rKB_model.pth"
      --scoring_model_path "$WORK_DIR/uni_mr_model_mod.pt"
    )
    EXPECTED_FILES=(
      "$WORK_DIR/rKB_model.pth"
      "$WORK_DIR/uni_mr_model_mod.pt"
    )
    ;;
  *)
    echo "Unknown variant: $VARIANT" >&2
    exit 1
    ;;
esac

EXPECTED_FILES+=("$KB_PATH" "$DATA_DIR/vocab.pkl" "$DATA_DIR/test_queries.txt")

start_ts="$(date +%s)"
while true; do
  missing=()
  for file in "${EXPECTED_FILES[@]}"; do
    [[ -e "$file" ]] || missing+=("$file")
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    break
  fi
  if (( TIMEOUT > 0 )); then
    now_ts="$(date +%s)"
    if (( now_ts - start_ts >= TIMEOUT )); then
      echo "Timed out waiting for expected files:" >&2
      printf '  %s\n' "${missing[@]}" >&2
      exit 1
    fi
  fi
  echo "WAIT ${KB_NAME}/${VARIANT}: ${missing[*]}"
  sleep "$POLL_INTERVAL"
done

cd "$WORK_DIR"
exec "$PYTHON_BIN" "$EVAL_SCRIPT" --kb "$KB_PATH" --qfile "$WORK_DIR/test_queries.txt" --vocab_file "$WORK_DIR/vocab" "${EVAL_ARGS[@]}"
