#!/bin/bash

python tests/sample_data.py
pytest
tail -f /dev/null