# Ralph Agent Configuration

## Build Instructions

```bash
# Install dependencies
pip install -r requirements.txt
```

## Test Instructions

```bash
# Run all tests
python main.py

# Run K-line tests only
python main.py --kline

# Run indicator tests only
python main.py --indicator

# Run with custom service URL
python main.py --url http://localhost:8080

# Run with verbose output
python main.py --verbose
```

## Run Instructions

```bash
# Start the market-data-service first (if running locally)
# Then run the test suite
python main.py
```

## Environment Variables

- `MARKET_DATA_SERVICE_URL`: Base URL for the service (default: http://localhost:8000)
- `REPORT_DIR`: Directory for test reports (default: ./reports)
- `VERBOSE`: Enable verbose logging (default: true)

## Test Reports

Reports are generated in the `./reports` directory:
- JSON format: `test_report_YYYYMMDD_HHMMSS.json`
- HTML format: `test_report_YYYYMMDD_HHMMSS.html`

## Notes
- The test framework is designed to be extensible for future interface testing
- Configuration can be modified in `config.py`
- New exchanges, indicators, and intervals can be added to the config
