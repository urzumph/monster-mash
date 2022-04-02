# monster-mash
Parses D&amp;D 3.5 stat blocks input as raw (copy/paste) text and exports them to other systems (Roll20)

## Getting Started:
Create a new virtual environment with

```
python -m venv .venv/mm
source .venv/mm/bin/activate
pip install -r requirements.txt
```

## Running one specific test:
python -m unittest parsers.parser_test.TestParser.test_parser_bam

## Usage

Run chromium with `chromium --remote-debugging-port=9222 --user-data-dir=remote-profile‘
