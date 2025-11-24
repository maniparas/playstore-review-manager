# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-24

### Added
- Initial release of Google Play Reviews Explorer
- FastAPI backend with Google Play Developer API integration
- Bootstrap 5 frontend with responsive dashboard
- Mock mode for testing without credentials
- Sentiment analysis and keyword extraction
- Optional OpenAI integration for AI summaries
- Comprehensive logging system
- Complete test suite with 69 tests and 80% coverage
- Environment-based configuration
- API endpoints for listing and fetching reviews
- Filter support (date range, ratings, language)
- Pagination handling
- Documentation (README, QUICKSTART, API_ENDPOINTS, LOGGING, TESTING)
- MIT License
- Contributing guidelines
- Code of Conduct

### Features
- **Reviews Listing**: Fetch and filter Google Play reviews
- **Individual Review**: Get detailed review information
- **Filters**: Date range, star ratings, translation language
- **Summary Metrics**: Total reviews, average rating, sentiment split
- **Keywords**: Auto-extracted from review text
- **AI Summaries**: Optional OpenAI-powered insights
- **Mock Mode**: Test without real Google credentials
- **Comprehensive Logging**: Track all API requests and responses
- **Test Suite**: Full unit and integration tests

### Documentation
- Detailed README with setup instructions
- Quick start guide for fast deployment
- API endpoints documentation
- Logging documentation
- Testing guide with coverage reports
- Contributing guidelines for open source contributors
- MIT License

## [Unreleased]

### Planned Features
- [ ] Authentication layer (OAuth, JWT)
- [ ] Additional AI providers (Vertex AI, Azure OpenAI)
- [ ] Caching layer (Redis/Memcached)
- [ ] Export reviews to CSV/JSON
- [ ] Dashboard analytics and charts
- [ ] Email notifications for new reviews
- [ ] Reply to reviews feature
- [ ] Bulk operations support
- [ ] Webhook support for new reviews

---

For a complete list of changes, see the [commit history](https://github.com/yourusername/google-reviews/commits/main).

