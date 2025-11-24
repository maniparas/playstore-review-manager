# Google Play Reviews Explorer

A lightweight FastAPI + Bootstrap framework that fetches Google Play Store reviews via the [Google Play Developer Reviews API](https://developers.google.com/android-publisher/api-ref/rest/v3/reviews). It exposes configurable filters (date range, star rating, translation language, paging) and renders insights, keywords, and optional AI notes in an interactive dashboard.

## Features

- **Backend**: FastAPI service that wraps the `reviews.list` and `reviews.get` endpoints with typed schemas and mock-mode support.
- **Filtering**: Query parameters for timeframe, rating bounds, locales, and rolling "recent activity" buckets.
- **Insights**: Basic sentiment buckets, keyword surfacing, and optional AI summaries (OpenAI integration).
- **Frontend**: Vanilla HTML with Bootstrap 5, providing a Google Play Console-inspired table and filter form.
- **Mock data**: Local JSON payload (`sample_data/mock_reviews.json`) allows UI exploration without live credentials.
- **Comprehensive Logging**: Pretty-printed logs for all API requests/responses (Client ↔ Server ↔ Google Play API).

## Getting Started

### Quick Start (Recommended)

```bash
cd google-reviews
./run.sh
```

The script will:
- Create a virtual environment if needed
- Install dependencies
- Copy `.env.example` to `.env` if missing
- Start the server at `http://127.0.0.1:8000`

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/google-reviews.git
   cd google-reviews
   ```

2. **Install dependencies**
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env` and update values:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your settings:
     - `GOOGLE_SERVICE_ACCOUNT_FILE`: Path to your service-account JSON that has *Google Play Android Developer API* access.
     - `DEFAULT_PACKAGE_NAME`: Your app's package name from Play Console.
     - `ENABLE_MOCK_MODE`: Set to `true` for testing with sample data, `false` for real API calls.
     - `AI_PROVIDER` / `OPENAI_API_KEY`: Optional AI summary hook (currently OpenAI only).
   - You may also export variables directly in your shell.

4. **Google Cloud prerequisites**
   - Enable the *Google Play Android Developer API* for your Play Console project.
   - Generate a service account, grant it the *View app information and reply to reviews* role (or broader if needed), and download the JSON.
   - Link the service account email inside Play Console (Setup → API access) and grant the target app permission to read reviews.

5. **Run the server**
   ```bash
   .venv/bin/uvicorn app.main:app --reload
   ```
   Visit `http://127.0.0.1:8000`.

## Workflow

- The UI submits filter values to `/api/reviews`.
- `GooglePlayReviewClient` pages through `reviews.list` (max 100 per call) and hydrates Pydantic models.
- Filters (date range, min/max rating) are applied server-side, followed by summary generation (`app/ai/insights.py`).
- Optional: `/api/reviews/{id}` fetches an individual review using `reviews.get`.

## Enabling AI brief (optional)

- Set `AI_PROVIDER=openai` and provide `OPENAI_API_KEY`.
- The helper grabs up to 20 recent snippets and requests a short summary from `gpt-4o-mini`. Replace the model/provider if desired.
- If the SDK/key is missing, the app silently disables the AI card.

## Extending

- **Additional filters**: Add query params in `app/api/routes.py` and surface in `templates/index.html`.
- **Caching**: Wrap `GooglePlayReviewClient.list_reviews` with your preferred cache (Redis/Memcached).
- **Persistence**: Pipe API responses into your warehouse (BigQuery, Snowflake) for longer-term analytics.
- **CI/CD**: Containerize with Uvicorn/Gunicorn for deployment; add tests targeting mock data.

## Testing with mock data

Leave `ENABLE_MOCK_MODE=true` to skip Google API calls. Modify `sample_data/mock_reviews.json` to simulate new scenarios.

## Logging

The application includes comprehensive logging that tracks all requests and responses:

- **HTTP Layer**: Logs incoming requests from clients (browser, curl, etc.) to the FastAPI server
- **Google API Layer**: Logs outgoing requests from server to Google Play API with response details
- **Pretty Formatting**: Color-coded symbols (🌍 🌐 📦 📤) for easy visual parsing

See **[LOGGING.md](docs/LOGGING.md)** for complete documentation.

Quick examples:
```bash
# Run server and see logs in real-time
.venv/bin/uvicorn app.main:app --reload

# Test logging with demo script
./test_logging.sh

# Filter specific log types
.venv/bin/uvicorn app.main:app --reload 2>&1 | grep "🌐"  # Google API calls only
```

## Testing

The project includes a comprehensive test suite with unit and integration tests.

### Quick Start Testing

```bash
# Run all tests with coverage
./run_tests.sh

# Run only unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration

# Run without coverage (faster)
./run_tests.sh fast

# Run with verbose output
./run_tests.sh verbose

# Generate detailed coverage report
./run_tests.sh coverage

# Run specific test file
./run_tests.sh specific tests/unit/test_schemas.py
```

### Manual Testing

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Run specific test markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_schemas.py      # Pydantic model tests
│   ├── test_google_play_client.py  # Client wrapper tests
│   └── test_ai_insights.py  # AI/insights module tests
└── integration/             # Integration tests
    └── test_api_routes.py   # API endpoint tests
```

### Coverage Reports

After running tests with coverage, open the HTML report:

```bash
open htmlcov/index.html
```

### Test Features Covered

- ✅ **Pydantic Schemas**: Model validation, datetime conversion, property getters
- ✅ **Google Play Client**: Mock mode, real API (mocked), pagination, error handling
- ✅ **AI Insights**: Sentiment analysis, keyword extraction, review summarization
- ✅ **API Routes**: All endpoints (health, list, get, single reply, bulk reply)
- ✅ **Filters**: Rating, date range, translation language, keyword filters
- ✅ **Frontend**: HTML/CSS/JS loading
- ✅ **Validation**: Input validation, error responses

### Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```bash
# Example CI command
pytest tests/ -v --cov=app --cov-report=xml --cov-report=term
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/google-reviews/issues)
- 💬 [Discussions](https://github.com/yourusername/google-reviews/discussions)

## Roadmap

- [ ] Add authentication layer (OAuth, JWT)
- [ ] Support additional AI providers (Vertex AI, Azure OpenAI)
- [ ] Add caching layer (Redis/Memcached)
- [ ] Export reviews to CSV/JSON
- [ ] Dashboard analytics and charts
- [ ] Email notifications for new reviews
