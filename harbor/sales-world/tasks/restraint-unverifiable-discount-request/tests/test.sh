#!/bin/bash
# Harbor verifier: run the checks, emit CTRF + a scalar reward.
set -uo pipefail

mkdir -p /logs/verifier

pip install --quiet --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5 httpx >/dev/null 2>&1

pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
status=$?

# Partial credit: Harbor takes the scalar in reward.txt, and a long-horizon sales
# task that got 7 of 9 assertions right is genuinely different from one that did
# nothing. test_outputs.py writes the fraction; fall back to binary on crash.
if [ -s /logs/verifier/reward_fraction.txt ]; then
  cat /logs/verifier/reward_fraction.txt > /logs/verifier/reward.txt
elif [ $status -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit $status
