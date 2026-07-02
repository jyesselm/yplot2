#!/usr/bin/env bash
# One-command regen for a paper's figures + the yplot2 plot catalog.
#
# Pin the environment first — see requirements.lock.template for guidance.
# "Raw data" here means an analysis-ready dataframe; the fastq/BAM pipeline
# is OUT of scope for this script.
#
# Usage: bash figures/build.sh
set -euo pipefail

# 1. Regenerate every figure (scripts AND notebooks, clean kernel):
python -m yplot2.build figures

# 2. Regenerate the plot catalog (static json + blocking style gate + gallery):
python -m yplot2.catalog_build.build --out-dir catalog
