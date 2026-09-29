# Website Uptime Monitor

A command-line tool that checks whether websites are UP or DOWN, stores every
check in SQLite, and shows uptime history and statistics.

## Features
- Monitors multiple websites at the same time (multithreading)
- Records status code, response time, timestamp and error reason
- Stores full history in a local SQLite database (`uptime.db`)
- `--once` for a single check, `--watch` for continuous monitoring
- Handles timeouts, connection/DNS errors, SSL errors, invalid URLs and
  unexpected HTTP status codes
- `--report` shows the uptime of all websites in one table
- `--stats` and `--history` show details for a single website

## Setup
Requires Python 3.8+.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

## Usage
Add websites to `websites.txt` (one per line, with `https://`), then:

```bash
python main.py --once                        # check all sites one time
python main.py --once --report               # check, then show uptime table
python main.py --watch --interval 30         # check every 30 seconds (Ctrl+C to stop)
python main.py --report                      # uptime of ALL websites
python main.py --stats google.com            # detailed uptime for one website
python main.py --history google.com          # recent checks for one website
python main.py --history google.com --limit 25
python main.py --once --file other_list.txt  # use a different list
python main.py --help                        # all options
```

Example `--stats` output:
```
Website: https://google.com

Uptime:       99.42%
Checks:       1,250
Successful:   1,243
Failed:       7
Avg Response: 184ms
```

Example `--report` output:
```
WEBSITE                     NOW    UPTIME    CHECKS   FAILED   AVG SPEED
---------------------------------------------------------------------------
https://github.com          UP     100.00%   11       0        1242ms
https://google.com          UP     100.00%   11       0        2261ms
not-a-valid-url             DOWN   0.00%     11       11       -
```

## How a website is judged UP or DOWN
- UP: HTTP status 200-399 (redirects are followed)
- DOWN: status 400+, timeout, connection error, SSL error, invalid URL

## Project structure
```
monitor/
  checker.py   - checks one website
  database.py  - SQLite storage
  stats.py     - uptime calculations
  cli.py       - command-line interface
main.py        - entry point
websites.txt   - websites to monitor
```

## Design decisions
- Threads are used because checking websites is mostly waiting on the network.
- Only the main thread writes to SQLite, which avoids threading issues.
- Timestamps are stored in UTC and shown in local time.
- Average response time counts only successful checks.
- Database queries use placeholders, which prevents SQL injection. 
