# Resync: AI-Powered HWA/TWS Interface

## Overview
Resync is an AI-powered interface for HCL Workload Automation (HWA), formerly known as IBM Tivoli Workload Scheduler (TWS). It transforms complex TWS operations into an intuitive chat interface powered by artificial intelligence, providing real-time monitoring, status queries, and diagnostic capabilities in natural language.

## Security Improvements

### Credential Management
- Removed hardcoded credentials from configuration files
- Implemented secure credential validation during startup
- Added requirements for environment-specific credential values

### Authentication System
- Implemented JWT-based authentication system
- Created proper login endpoint with secure credential validation
- Added CSRF protection and secure session management

### CORS Configuration Security
- Enhanced CORS configuration with strict validation
- Implemented per-environment CORS policies
- Added security monitoring for CORS violations

## Performance Optimizations

### AsyncTTLCache Improvements
- Enhanced memory management with better size estimation
- Implemented LRU eviction when cache bounds are exceeded
- Added more accurate memory usage tracking

### Connection Pool Optimization
- Improved Redis connection pool settings
- Enhanced database connection pool configuration
- Optimized HTTP connection pool for external API calls

### Resource Management
- Added centralized resource manager for proper lifecycle management
- Implemented proper shutdown and cleanup procedures
- Enhanced resource tracking and monitoring

## Error Handling Improvements

### Standardized Error Handling Patterns
- Created consistent error handling across all components
- Implemented proper exception hierarchies
- Standardized error response formats

### API Error Responses
- Implemented comprehensive error response models
- Added troubleshooting hints to error responses
- Enhanced logging with correlation IDs

## Code Quality Enhancements

### Code Duplication Removal
- Created shared utility modules for common functionality
- Implemented reusable error handling decorators
- Centralized common patterns

### Function Complexity Reduction
- Broke down complex functions into smaller, manageable pieces
- Improved maintainability and readability
- Enhanced testability of components

### Type Annotation Improvements
- Added comprehensive type annotations throughout the codebase
- Enhanced type safety with proper generics
- Improved IDE support and static analysis

## Architectural Improvements

### Dependency Injection System
- Enhanced service registration and resolution
- Added better error handling for missing services
- Improved factory functions for complex dependencies

### Middleware Optimization
- Added performance monitoring to error handler middleware
- Enhanced logging and correlation tracking
- Improved security monitoring

## New Features and Enhancements

### Monitoring and Metrics
- Added comprehensive error metrics tracking
- Enhanced runtime metrics collection
- Implemented Prometheus-compatible metrics endpoint

### Security Enhancements
- Enhanced CSP middleware with better reporting
- Added detailed security headers
- Improved input validation and sanitization

## Configuration

### Environment Variables
The application requires the following environment variables:

```
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_admin_password
SECRET_KEY=your_very_secure_random_string_at_least_32_chars_long
REDIS_URL=redis://your-redis-host:6379
LLM_ENDPOINT=http://your-llm-endpoint:11434/v1
LLM_API_KEY=your_llm_api_key
TWS_HOST=your-tws-host
TWS_PORT=31111
TWS_USER=your-tws-username
TWS_PASSWORD=your-tws-password
```

### Settings Configuration
The application uses a hierarchical configuration system with:
- Base settings in `settings.toml`
- Environment-specific overrides in `settings.{environment}.toml`
- Environment variables with `APP_` prefix

## Running the Application

### Development Mode
```bash
# Run with mock TWS data (default)
uvicorn resync.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
# Run with real TWS connection
uvicorn resync.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
# Build and run with Docker
docker build -t resync .
docker run -p 8000:8000 resync
```

## API Endpoints

- `GET /login` - Login page for admin access
- `POST /token` - OAuth2 token endpoint for JWT authentication
- `GET /dashboard` - Main dashboard interface
- `GET /api/health/app` - Application health check
- `GET /api/health/tws` - TWS connection health check
- `GET /api/status` - Comprehensive TWS system status
- `POST /api/chat` - Chat endpoint for natural language queries
- `GET /api/agents` - List all configured agents
- `GET /api/metrics` - Prometheus metrics endpoint

## Security Features

- JWT-based authentication for API access
- Content Security Policy (CSP) headers
- CORS with strict origin validation
- Input validation and sanitization
- Rate limiting with Redis backend
- Comprehensive request logging with correlation IDs

## Contributing

We welcome contributions to improve Resync! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with a clear description

## License

This project is licensed under the MIT License - see the LICENSE file for details.