## Technical Approach

### 1. Reverse Engineering the Voyager REST API
Rather than rendering heavy DOM elements in a headless browser, this service issues raw HTTPS GET requests directly to LinkedIn's private REST API endpoint:
`GET https://www.linkedin.com/voyager/api/identity/dash/profiles`

### 2. Required Protocol Headers & Security Matching
LinkedIn enforces Anti-CSRF verification by pairing HTTP headers with session cookies:
* **`csrf-token`**: Must equal the value of the `JSESSIONID` cookie with surrounding double quotes removed (e.g., `JSESSIONID="ajax:1234"` requires `csrf-token: ajax:1234`).
* **`x-restli-protocol-version`**: Enforces `2.0.0` REST.li protocol rules.
* **`accept`**: Set to `application/vnd.linkedin.normalized+json+2.1` to request flat graph objects.

### 3. Concurrency Optimization
By avoiding browser engines, memory requirements drop from ~500 MB per tab to ~2 MB per active task coroutine. Outbound connections are pooled with keep-alive enabled and bounded using `asyncio.Semaphore(30)` to protect process socket handles and upstream resource limits.

## Requirements & Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```ini
# Application Configuration
ENVIRONMENT=production
PORT=8000
WORKERS=4

# Bearer Token for Protecting API Endpoints
API_AUTH_TOKEN=your_secure_random_api_token_here

# LinkedIn Backend Credentials (Extracted from Active Browser Session)
LINKEDIN_LI_AT=AQEDAQ...
LINKEDIN_JSESSIONID="ajax:8473920194857204938"

# Optional Proxy DSN (Use socks5h:// for Remote DNS Resolution)
PROXY_DSN=

# Concurrency Controls
MAX_CONCURRENT_REQUESTS=30
REQUEST_TIMEOUT_SECONDS=15.0
