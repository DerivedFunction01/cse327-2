#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_standard_evaluation.sh <kb|all>

kb:
  countries
  size200
  size300
  size400
  all

Environment:
  PYTHON_BIN  Python interpreter to use. Defaults to the repo .venv.
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

TARGET="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

run_one() {
  local kb_name="$1"
  local kb_dir=""
  local kb_path=""
  local data_dir=""

  case "$kb_name" in
    countries)
      kb_dir="$ROOT_DIR/countries/default"
      kb_path="$ROOT_DIR/countries/countries_kb.txt"
      data_dir="$ROOT_DIR/data/countries"
      ;;
    size200|size300|size400)
      kb_dir="$ROOT_DIR/$kb_name/default"
      kb_path="$ROOT_DIR/$kb_name/randomKB.txt"
      data_dir="$ROOT_DIR/data/random/$kb_name"
      ;;
    *)
      echo "Unknown KB: $kb_name" >&2
      exit 1
      ;;
  esac

  if [[ ! -f "$kb_path" ]]; then
    echo "Missing KB file: $kb_path" >&2
    exit 1
  fi
  if [[ ! -f "$data_dir/vocab.pkl" || ! -f "$data_dir/test_queries.txt" ]]; then
    echo "Missing shared init files in $data_dir. Run init_shared_data.py first." >&2
    exit 1
  fi

  mkdir -p "$kb_dir"
  ln -sfn "$data_dir/vocab.pkl" "$kb_dir/vocab.pkl"
  ln -sfn "$data_dir/test_queries.txt" "$kb_dir/test_queries.txt"

  echo "Running standard evaluation for $kb_name"
  (
    cd "$kb_dir"
    "$PYTHON_BIN" "$ROOT_DIR/evaluate.py" \
      --kb "$kb_path" \
      --qfile "$kb_dir/test_queries.txt" \
      --vocab_file "$kb_dir/vocab" \
      --standard
  )
}

case "$TARGET" in
  countries)
    run_one "countries"
    ;;
  size200|size300|size400)
    run_one "$TARGET"
    ;;
  all)
    run_one "countries"
    run_one "size200"
    run_one "size300"
    run_one "size400"
    ;;
  *)
    usage
    exit 1
    ;;
esac
