# Waymore - Copilot Instructions

## Project Overview

Waymore is a reconnaissance tool that extracts URLs from multiple archived sources and downloads historical responses. It aggregates data from Wayback Machine, Common Crawl, Alien Vault OTX, URLScan, VirusTotal, and Intelligence X to provide comprehensive coverage for bug bounty and security research.

## Architecture & Core Components

### Single Module Design
- **`waymore/waymore.py`**: The entire application is a single ~4000-line module containing all functionality
- **`waymore/__init__.py`**: Simple version declaration (`__version__="6.1"`)
- **`config.yml`**: YAML configuration with filtering rules, API keys, and output settings

### Operating Modes
The tool operates in three distinct modes:
- **Mode U**: URLs only - retrieves links from all sources
- **Mode R**: Responses only - downloads archived content from Wayback/URLScan  
- **Mode B**: Both URLs and responses (default for domain-only inputs)

### Data Source Integration
Each source has dedicated processing functions:
- `getWaybackUrls()` + `processWayBackPage()` - Wayback Machine CDX API
- `getCommonCrawlUrls()` + `processCommonCrawlCollection()` - Common Crawl indexes  
- `getAlienVaultUrls()` + `processAlienVaultPage()` - OTX passive DNS
- `getURLScanUrls()` + `processURLScanUrl()` - URLScan.io search + DOM retrieval
- `getVirusTotalUrls()` + `processVirusTotalUrl()` - VirusTotal domain reports
- `getIntelxUrls()` + `processIntelxUrl()` - Intelligence X phonebook search

## Key Development Patterns

### Global State Management
Heavy use of global variables for application state:
```python
global args, linksFound, linkMimes, successCount, failureCount, stopProgram
```
All major functions operate on shared global state rather than passing parameters.

### Rate Limiting & Resilience
- Built-in retry logic with configurable delays (`-wrlr`, `-urlr` arguments)
- Memory monitoring with threshold-based termination (`-m` argument, default 95%)
- Graceful handling of API rate limits with pause/retry mechanisms
- Signal handling for clean termination (SIGINT)

### Filtering System
Multi-layered filtering via config.yml and CLI arguments:
- **URL filters**: `FILTER_URL` - file extensions and paths to exclude
- **MIME filters**: `FILTER_MIME` - content types to exclude  
- **Status code filters**: `FILTER_CODE` - HTTP responses to exclude
- **Keyword filters**: `FILTER_KEYWORDS` - regex patterns for inclusion

### Output Management
- **URLs**: Saved to `waymore.txt` (or custom `-oU` path)
- **Responses**: Individual files with hash-based names + `waymore_index.txt` mapping
- **Directory structure**: `~/.config/waymore/results/{domain}/`

## Critical Developer Workflows

### Setup & Installation
```bash
# Install with config file creation
python setup.py install
# Creates ~/.config/waymore/config.yml with defaults

# Docker workflow
docker build -t waymore .
docker run -v $PWD/results:/app/results waymore -i example.com
```

### Configuration Management
Config loading happens in `getConfig()` - always check this when adding new settings:
```python
# Loads from ~/.config/waymore/config.yml or -c specified path
# Falls back to hardcoded defaults if config missing
```

### Adding New Data Sources
Follow the established pattern:
1. Add URL constant at top of file
2. Create `get{Source}Urls()` function for API interaction
3. Create `process{Source}Url()` function for individual URL processing
4. Add exclusion argument (`-x{xx}`) in argument parser
5. Integrate into main loop with `if not args.x{xx}` check

### Testing & Debugging
```bash
# Check mode - estimate requests without execution  
waymore -i domain.com --check-only

# Verbose output for debugging
waymore -i domain.com -v

# Memory monitoring
waymore -i domain.com -m 80  # Stop at 80% memory usage
```

## Important Constraints

### API Dependencies
- URLScan requires API key for full functionality (`URLSCAN_API_KEY`)
- VirusTotal needs API key (`VIRUSTOTAL_API_KEY`) 
- Intelligence X requires paid subscription (`INTELX_API_KEY`)
- Missing keys result in source exclusion, not failure

### Performance Considerations
- **No parallel source processing** - sources run sequentially by design
- Common Crawl can be extremely slow - default limit is 1 collection (`-lcc 1`)
- Wayback Machine requests can reach millions for large domains
- Use `-lr` to limit requests per source for large targets

### File Handling
- Responses use hash-based filenames to deduplicate content
- Extensions derived from MIME types or URL paths
- Special handling for inline JavaScript extraction (`-oijs` flag)
- Continuation support for interrupted downloads via `.tmp` files

## Project-Specific Conventions

### Error Handling
Errors use colored terminal output via `termcolor`:
```python
writerr(colored('ERROR main 1: ' + str(e), 'red'))
```

### Progress Indication  
Custom progress bar implementation for long-running operations:
```python
printProgressBar(iteration, total, prefix='Progress:', suffix='Complete')
```

### Input Validation
Extensive input validation with custom type functions:
- `validateArgInput()` - domain/file validation with punycode conversion
- `validateArgStatusCodes()` - HTTP status code validation  
- `validateArgMimeTypes()` - MIME type validation

When modifying waymore, maintain the single-file architecture, preserve global state patterns, and ensure all new features integrate with the existing filtering and rate limiting systems.