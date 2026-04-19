#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_training_pipeline.sh <kb> <variant> [embed_size]

kb:
  countries
  size200
  size300
  size400

variant:
  default   Default size-50 training run
  embed     Alternate embedding-size run
  mod       Modified scoring-model run

embed_size:
  Optional, defaults to 50. Used for the embed variant and passed through to
  the training commands.

Environment:
  PYTHON_BIN  Python interpreter to use. Defaults to `python`.
EOF
}

if [[ $# -lt 2 || $# -gt 3 ]]; then
  usage
  exit 1
fi

KB_NAME="$1"
VARIANT="$2"
EMBED_SIZE="${3:-50}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

case "$KB_NAME" in
  countries)
    KB_DIR="$ROOT_DIR/countries"
    KB_PATH="$KB_DIR/countries_kb.txt"
    DATA_DIR="$ROOT_DIR/data/countries"
    ;;
  size200|size300|size400)
    KB_DIR="$ROOT_DIR/$KB_NAME"
    KB_PATH="$KB_DIR/randomKB.txt"
    DATA_DIR="$ROOT_DIR/data/random/$KB_NAME"
    ;;
  *)
    echo "Unknown KB: $KB_NAME" >&2
    usage
    exit 1
    ;;
esac

case "$VARIANT" in
  default)
    WORK_DIR="$KB_DIR/default"
    EMBED_MODEL_PATH="$WORK_DIR/rKB_model.pth"
    GUIDANCE_MODEL_PATH="$WORK_DIR/uni_mr_model.pt"
    REASONER_SCRIPT="$ROOT_DIR/nnreasoner.py"
    ;;
  embed)
    WORK_DIR="$KB_DIR/embed"
    EMBED_MODEL_PATH="$WORK_DIR/rKB_model_${EMBED_SIZE}.pth"
    GUIDANCE_MODEL_PATH="$WORK_DIR/uni_mr_model_${EMBED_SIZE}.pt"
    REASONER_SCRIPT="$ROOT_DIR/nnreasoner.py"
    ;;
  mod)
    WORK_DIR="$KB_DIR/mod"
    EMBED_MODEL_PATH="$WORK_DIR/rKB_model.pth"
    GUIDANCE_MODEL_PATH="$WORK_DIR/uni_mr_model_mod.pt"
    REASONER_SCRIPT="$ROOT_DIR/nnreasoner2.py"
    ;;
  *)
    echo "Unknown variant: $VARIANT" >&2
    usage
    exit 1
    ;;
esac

if [[ ! -f "$KB_PATH" ]]; then
  echo "Missing KB file: $KB_PATH" >&2
  exit 1
fi

if [[ ! -f "$DATA_DIR/vocab.pkl" ]]; then
  echo "Missing shared data files in $DATA_DIR. Run init_shared_data.py first." >&2
  exit 1
fi

if [[ ! -f "$DATA_DIR/train_queries.txt" || ! -f "$DATA_DIR/test_queries.txt" ]]; then
  echo "Missing shared query files in $DATA_DIR. Run init_shared_data.py first." >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/kbencoder.py" ]]; then
  echo "Missing kbencoder.py in repo root: $ROOT_DIR" >&2
  exit 1
fi

if [[ ! -f "$REASONER_SCRIPT" ]]; then
  echo "Missing reasoner script: $REASONER_SCRIPT" >&2
  exit 1
fi

mkdir -p "$WORK_DIR"
ln -sfn "$DATA_DIR/train_queries.txt" "$WORK_DIR/train_queries.txt"
ln -sfn "$DATA_DIR/test_queries.txt" "$WORK_DIR/test_queries.txt"

cd "$WORK_DIR"

echo "Work dir: $WORK_DIR"
echo "KB:       $KB_PATH"
echo "Variant:  $VARIANT"
echo "Embed:    $EMBED_SIZE"
echo "Python:   $PYTHON_BIN"
echo

"$PYTHON_BIN" "$ROOT_DIR/kbencoder.py" \
  --kb_path "$KB_PATH" \
  --train_unification_model \
  --vocab_file "$DATA_DIR/vocab" \
  --embed_size "$EMBED_SIZE" \
  --embed_model_path "$EMBED_MODEL_PATH"

"$PYTHON_BIN" "$REASONER_SCRIPT" \
  --embed_type unification \
  --training_file "$DATA_DIR/mr_train_examples.csv" \
  --vocab_file "$DATA_DIR/vocab" \
  --embed_size "$EMBED_SIZE" \
  --embed_model_path "$EMBED_MODEL_PATH" \
  --save_model "$GUIDANCE_MODEL_PATH"
