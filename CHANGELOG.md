## Changelog

- v8.2

  - Changed

    - **Reliable Config Creation**: Improved the configuration file creation logic to ensure it works across all installation methods (e.g., `pipx`). The config file is now created robustly at runtime if it doesn't already exist.
    - Improved platform-specific path detection for Windows, Linux, and macOS.
    - Fixed a bug where providing a relative path via `-c` would fail to create the default config if the directory was not already present.
    - Removed redundant and fragile install-time config copying logic from `setup.py`.

- v8.1

  - New

    - **Auto-create config.yml**: If the `config.yml` file is not found in the default location when `waymore` runs, it will now be automatically created with default values. This fixes issues where the config file was not created during installation for some users.

- v8.0

  - New

    - **GhostArchive Source**: Added [GhostArchive](https://ghostarchive.org/) as a new URL source for `-mode U` AND `-mode R`. This source doesn't have an API, so waymore crawls the HTML pages directly to extract archived URLs. The source paginates automatically until no more results are found. For `-mode R` it will download the WARC files and extract the HTTP Responses and extra URLs from them.
    - Added `-xga` argument to exclude checks for links from ghostarchive.org.
    - Updated `--providers` argument to accept `ghostarchive` as a valid provider value.
    - Added `.avif` to `FILTER_URL` and `image/avif` to `FILTER_MIME` in `config.yml` and default values in `DEFAULT_FILTER_URL` and `DEFAULT_FILTER_MIME`.

  - Changed

    - Remove `application/pdf` from `FILTER_MIME` in `config.yml` and default values in `DEFAULT_FILTER_MIME`. These files can contain valuable information and should not be filtered out.

- v7.7

  - New

    - Add a few more audio and video extensions to `FILTER_URL` in `config.yml` and default values in `DEFAULT_FILTER_URL`
    - Add few more audio and video MIME type to `FILTER_MIME` in `config.yml` and default values in `DEFAULT_FILTER_MIME`
    - Added extar debug info to show the file being processed so if waymore seems to freeze on a specific file I can investigate.

  - Changed

    - **Binary File Download Fix**: Fixed critical bug where binary files (`.zip`, `.pdf`, `.gz`, images, etc.) downloaded (with `-mode R`) were corrupted. The issue was that all responses were being handled as text (`resp.text`) and written in text mode with UTF-8 encoding, which mangles binary data during the encoding/decoding cycle.
    - Added `BINARY_EXTENSIONS` constant containing 50+ binary file extensions (`.zip`, `.gz`, `.pdf`, `.exe`, `.png`, `.mp4`, fonts, archives, etc.)
    - Added `BINARY_MIME_TYPES` constant containing 40+ binary MIME types (`application/zip`, `application/pdf`, `image/*`, `audio/*`, `video/*`, etc.)
    - Replaced `isBinaryFile()` with improved `isBinaryContent()` function that now checks actual content bytes for file signatures. This ensures HTML error pages are correctly treated as text even if the URL has a binary extension like `.pdf`. Priority order: (1) content inspection for file magic bytes, (2) Content-Type header, (3) URL extension as fallback.
    - Binary files are now downloaded using `resp.content` (raw bytes) and written using binary mode (`"wb"`), preserving the original file data
    - Text files continue to use decoded bytes with UTF-8 encoding and Wayback cleanup regex processing
    - Binary files that cannot determine an extension will use `.bin` instead of `.unknown`
    - **Raw Wayback Downloads (`id_` modifier)**: For binary files, the Wayback Machine URL now includes the `id_` modifier (e.g., `/web/20090315210455id_/http://...`) which retrieves the raw original file without any Wayback Machine modifications. This fixes corruption of media files like `.wmv`, `.mp4`, etc.
    - Added `isLikelyBinaryUrl()` helper to pre-check if a URL has a binary extension before making the request
    - Added `addRawModifier()` helper to insert the `id_` modifier into Wayback URLs
    - Added comprehensive binary file magic bytes signatures
    - The `--source-ip` option is now only displayed in verbose (`-v`) output when it's explicitly configured. Previously, it always showed a default message even when not set.

- v7.6

  - New
  
    - **Source IP Binding**: Added `--source-ip` / `--bind-ip` CLI argument and `SOURCE_IP` config option to bind outbound HTTP/HTTPS requests to a specific source IP address. Useful for multi-homed hosts where you need to use a specific whitelisted IP. Thanks to [fbettag](https://github.com/fbettag) for PR [#79](https://github.com/xnl-h4ck3r/waymore/pull/79).
  
  - Changed

    - Fixed `notifyDiscord()` and `notifyTelegram()` functions to use the HTTP adapter for source IP binding consistency.
    - Added null checks for `HTTP_ADAPTER` in `chooseIntelxBase()` and webhook functions for robustness.

- v7.5

  - New

    - **IntelX Fallback Mechanism**: Added automatic fallback between paid (`2.intelx.io`) and free (`free.intelx.io`) Intelligence X endpoints. The tool now probes endpoints in order and automatically switches to the free endpoint if the paid one returns 401/402/403 errors, improving reliability for users with different API key types.
    - Added thread-local storage for IntelX URL configuration to support concurrent operations.
    - Change the README to note that Intelligence X is now an academia or paid tier only source, not just paid.
    - Thanks to the [aleister1102](https://github.com/aleister1102) for PR [#78](https://github.com/xnl-h4ck3r/waymore/pull/78) for this improvement.

- v7.4

  - BUG FIX: The source specific totals were showing as 0 when running `-mode U` and the error `ERROR processIntelxUrl 1: name 'linksFoundIntelx' is not defined` was shown. This has been fixed.

- v7.3

- Changed

  - The v7.2 changes were not correct to provide support for Telegram notifications. A new optional argument `-nt`/`--notify-telegram` can be used to send a notification to a Telegram webhook when waymore completes. This requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to be provided in the `config.yml` file.

- v7.2

  - New

    - Added support for **Telegram notifications**. A new optional argument `-nt`/`--notify-telegram` can be used to send a notification to a Telegram webhook when waymore completes. This requires `WEBHOOK_TELEGRAM` to be provided in the `config.yml` file.

- v7.1

  - New

    - Add `/_incapsula_resource` to `FILTER_URL` in `config.yml` (and the default constant if the config file is not found) to exclude this common response that is not part of the original target. The response also causes regex "catastrophic backtracking" in `xnLinkFinder` so I am excluding here aswell as looking into solving that problem.
     
- v7.0

  - New

    - **Async Concurrent Source Fetching**: Implemented asynchronous concurrent fetching from all URL sources (Wayback Machine, Common Crawl, AlienVault OTX, URLScan, VirusTotal, Intelligence X) for **significantly improved performance (2-4x faster** for multi-source runs).
    - Added `asyncio` orchestration layer to manage concurrent execution while maintaining backward compatibility with existing synchronous code.
    - Added `aiohttp` dependency to requirements for async HTTP support.
    - Added thread-safe locks (`threading.Lock`) to protect shared global state (`linksFound`, `linkMimes`, `urlscanRequestLinks`) from race conditions during concurrent operations.

  - Changed

    - Sources are now fetched **concurrently** instead of sequentially, with proper error handling to ensure one source failure doesn't stop others.
    - Properly initialized `linksFound` and `linkMimes` as global variables to prevent `NoneType` errors during concurrent access.
    - Removed local reassignments of global variables in source functions (`getURLScanUrls`, `getCommonCrawlUrls`, `getVirusTotalUrls`) that were causing race conditions.
    - All `.add()` operations on shared sets are now protected with locks for thread safety.
    - **Minimum Python version**: Now requires **Python 3.7+** for `async/await` support.
    - Ensure the default value for `-lcc`/`--limit-common-crawl` is set to 1.
    - Set the default value for `-p`/`--processes` to 2. This will speed things if people don't specify a value, and shouldn't cause any issues.
    - Fixed duplicate rate limit messages from AlienVault when using parallel processes by checking `stopSource` before printing the 429 error message.
    - Fixed issue where AlienVault would show an "Unexpected response" error after a "Rate limit reached" error.
    - **Wayback streaming improvements**: Wayback Machine requests now use `stream=True` to retrieve results as they arrive. If the connection is interrupted (`Response ended prematurely` error), all URLs processed before the error are still saved instead of losing everything. Error messages now show how many URLs were saved before the connection failed.
    - **Ctrl-C interrupt for streaming requests (2025-12-03)**: Fix SIGINT handling so a live streaming response is closed when Ctrl-C is pressed, allowing blocking `session.get(..., stream=True)` requests to be interrupted and stop faster. This exposes the active response to the SIGINT handler and closes it to cancel blocking network I/O.
    - **Session-level interrupt fix (2025-12-03T11:36:18.961Z)**: Also expose and close the active requests.Session when SIGINT is received to more reliably abort blocking streaming requests on some platforms/environments.
    - **Interruptible rate-limit waits (2025-12-03T12:04:37.195Z)**: Replaced blocking time.sleep() calls used when rate-limited with an interruptible wait driven by a global threading.Event (interrupt_event). The SIGINT handler now sets interrupt_event so rate-limit waits wake early when Ctrl-C is pressed.
    - **Unique Link Counting**: The link count displayed for each source (Wayback, Common Crawl, etc.) now represents the number of **unique** URLs found from that source, rather than the total number of URLs found (which included duplicates). The final total still shows the unique URLs found across all sources.
    - **Memory Optimization**: Significant reduction in memory usage by preventing duplicate storage of links. Links are now stored only in source-specific sets during processing and merged into the main set at the end, with source sets being cleared immediately to free up memory.
    - **Link Counting Consistency**: Fixed a discrepancy where source-specific link counts could be higher than the final total. All link counting now uses the same normalization (removing ports 80/443) and filtering logic to ensure consistency.
    - **Source-Specific Link Counting**: Added separate link counts for each source (Wayback, Common Crawl, etc.) to provide more detailed information about the number of unique links found from each source.
    
    
- v6.6

  - Changed

    - The `-from`/`--from-date` and `-to`/`--to-date` arguments were not used for getting URLs from Wayback Archive, only for responses. These have been changed to apply to both mode `U` and mode `R` for Wayback. They will not be used for URLs if the `-f`/`--filter-responses-only` argument is passed.
    - The `-lcy` argument will be removed and the `-from`/`--from-date` and `-to`/`--to-date` arguments will now determine which Common Crawl indexes to get and which records from the files will be returned if filtering is required.
    - The `-from`/`--from-date` and `-to`/`--to-date` arguments were also not used for getting URLs from Common Crawl, Alien Vault and Virus Total within the date limits. **IMPORTANT: There are some exceptions with sources unable to get URLs within date limits: Virus Total - all known sub domains will still be returned; Intelligence X - all URLs will still be returned.**

- v6.5

  - New

    - Added GitHub Actions CI workflow with automated linting (ruff), formatting checks (black), and testing (pytest) across Python 3.9-3.12
    - Added `pyproject.toml` with modern Python project configuration and tool settings
    - Added basic test suite with import test
    - Added `docker-entrypoint.sh` for proper permission handling in Docker containers

  - Changed

    - **Docker improvements**: Upgraded to multi-stage build using Python 3.12-slim for smaller image size and better security
    - **Docker security**: Container now runs as non-root user (appuser) with proper permission handling via gosu
    - **Docker build**: Now uses `python -m build --wheel` instead of deprecated `setup.py install`
    - Fixed circular import issue in `setup.py` by adding `get_version()` function to read version via regex
    - Simplified Docker usage command in README (removed redundant `waymore` command from entrypoint)
    - Applied black and ruff formatting to `setup.py` and `pyproject.toml`

  - Thanks

    - Thanks to [@Donovoi](https://github.com/Donovoi) for PR [#70](https://github.com/xnl-h4ck3r/waymore/pull/70)

- v6.4

  - New

    - Add `.ruff_cache` and `.pytest_cache` to `.gitignore` now required after v6.3 changes.

  - Changed

    - BUG FIX: The version was now being shown as outdated because of changes made in v6.3. The version just needed white space stripped now.

- v6.3

  - Changed

    - Code quality improvements: Fixed all bare `except:` statements to use `except Exception:` for better error handling practices.
    - Fixed undefined variable issue by properly declaring `process` as a global variable.
    - Removed unused variable assignments to clean up the codebase.
    - Applied consistent code formatting (black) and linting (ruff) across all Python files.
    - All changes are code quality improvements with no functional impact.

- v6.2

  - New

    - Add argument `--stream`. Using it will output URLs to STDOUT as soon as they are found (duplicates will be shown). Only works with `-mode U`. All other output is suppressed, so use `-v` to see any errors. Use `-oU` to explicitly save results to file (wil be deduplicated). [Issue 54](https://github.com/xnl-h4ck3r/waymore/issues/54)

  - Changed

    - Change the `--version` argument to show the version and whether it is outdated or not, in the same way as the banner.

- v6.1

  - INFO: v6.0 was skipped because there was an error in the version uploaded to PyPi and it cannot be replaced

  - New

    - Get archived responses from URLScan in addition to wayback machine. The same processing to get the links will be done, but the `_id` values will be stored and then the DOM for each response can be retrieved from `https://urlscan.io/dom/{UUID}`. Sometimes the API may not have saved the DOM, so these are just skipped.
    - BUG FIX: The `-from`/`--from-date` and `-to`/`--to-date` values can take the format `YYYYMMDDhhmmss` (or part of) but wasn't validated that it was a valid date/time. Validation now added.
    - BUG FIX: The search for links on URLScan wasn't taking into account the `-from` or `-to` fields. These are now used to format the `{DATERANGE}` section in `URLSCAN_URL`.
    - BUG FIX: If a URL is passed as input, then the links from URLScan would just match the domain, not the URL.

  - Changed

    - Pass the waymore version in the User-Agent when making requests to URLScan.
    - Rename `index.txt` to `waymore_index.txt` instead, to allow `xnLinKFinder` identify a `waymore` response directory better.

- v5.1

  - BUG FIX: When calling URLScan API, it would sometimes return a 429 response straight away. It was assumed this was just to do with the API rate limiting, but it seemed to been related to the User-Agent and was a WAF 429 rather than a specific API 429. It now sets a specific user agent of `waymore by xnl-h4ck3r` which always works for now.

- v5.0

  - New

    - Add source **Intelligence X - intelx.io**. It requires a paid API key to do the `/phonebook/search` through their API (as of 2024-09-01, the Phonebook service has been restricted to paid users due to constant abuse by spam accounts).
    - Add argument `-xix` to exclude checks for links from Intelligence X (intelx.io).
    - Add `INTELX_API_KEY` to `config.yml`.

- v4.9

  - Changed

    - BUG FIX: The error `ERROR combineInlineJS 1: local variable 'fileNumber' referenced before assignment` is raised when there are external javascript files provided via `src` but no inline javascript sections. The correct message will be displayed now without an error being raised.
    - BUG FIX: If a status code filter does not include `404` (whether specified in `config.yml` or changed via `-fc` or `-mc`) then the logic was causing a response to not be downloaded.
    - BUG FIX: When downloading responses, the URL needs to all be in lower case, regardless of the URL that the API returns that may have uppercase characters. This resulted in some responses not being found and failing to download.

- v4.8

  - Changed

    - BUG FIX: When downloading responses and creating the file name, sometimes the file extension is incorrectly derived and has `/` in it, e.g. `5146045725697.well-known/openid-configuration`, and this causes the writing of the file to fail. If the derived extension does contain `/` then it will be reset to blank, and determined a different way.

- v4.7

  - New

    - BUG FIX: If an input domain has unicode in, e.g `xñl.uk`, then it will be converted to the punycode version, e.g. `xn--xl-zja.uk` to use that as the input instead. This will ensure the URLs and responses are correctly retrieved from the archive sources.

- v4.6

  - New

    - Add argument `-ft` to specify a list of MIME Types to filter. This will override the `FILTER_MIME` list in `config.yml`. **NOTE: This will NOT be applied to Alien Vault OTX and Virus Total because they don't have the ability to filter on MIME Type. Sometimes URLScan does not have a MIME Type defined - these will always be included. Consider excluding sources if this matters to you.**.
    - Add argument `-mt` to specify a list of MIME Types to match. This will be used instead of the default filtering using `FILTER_MIME` list in `config.yml`, or filtering using `-ft`. **NOTE: This will NOT be applied to Alien Vault OTX and Virus Total because they don't have the ability to filter on MIME Type. Sometimes URLScan does not have a MIME Type defined - these will always be included. Consider excluding sources if this matters to you.**.
    - Add argument `--providers` in the same way as `gau`. A comma separated list of source providers that you want to get URLs from. The values can be `wayback`,`commoncrawl`,`otx`,`urlscan` and `virustotal`. Passing this will override any exclude arguments (e.g. `-xwm`,`-xcc`, etc.) passed to exclude sources, and reset those based on what was passed with this argument.

  - Changed

    - When argument `--verbose` has been used and the options are shown, show the name of providers that will be searched instead of the exclude arguments, e.g.`-xwm`, `-xcc`, etc.
    - Change `HTTP_ADAPTER_CC` used for Common Crawl requests to use `retries+3` instead of `reties+20`. This was originally suggested by Common Crawl, but there are so many issues it can just take forever to get anything from their API, and often fail anyway.
    - Change the default of `-lcc` to 1 instead of 3 because of so many problems with Common Crawl.
    - BUG FIX: If a connection error occurs when getting the Common Crawl index file, then error `ERROR getCommonCrawlUrls 1: object of type 'NoneType' has no len()` is displayed. This will now be suppressed.
    - BUG FIX: If arg `-mc` was not passed and `-ft` was, when options were shown to the user (in `showOptions` function), the value of `-mc` was shown for `-ft`.
    - BUG FIX: When a MIME type is used in a filter for Wayback Machine that has a `+` in it (e.g. `image/svg+xml`), then the `+` was replaced because that'#s the only way Wayback recognises it. However, it was being escaped first and was being converted to `image/svg\.xml` instead of `image/svg.xml` so was not recognised in the filter.

- v4.5

  - Change

    - BUG FIX: When `-f`/`--filter-responses-only` is used, and retrieving Wayback Archive links, the links were still being filtered for URL exclusions, e.g. the extensions. This has been fixed and should return more links in that situation.
    - BUG FIX: If there is an invalid response from Alien Vault, then the error `ERROR: getAlienVaultUrls 1: Expecting value: line 1 column 1 (char 0)` is raised. This will be handled properly.
    - BUG FIX: If there is an invalid response from URLScan, then the error `ERROR getURLScanUrls 1: local variable 'jsonResp' referenced before assignment` is raised. This will be handled properly.
    - BUG FIX: If there is an invalid response from Virus Total, then the error `ERROR getVirusTotalUrls 1: Expecting value: line 1 column 1 (char 0)` is raised. This will be handled properly.
    - BUG FIX: When retrieving links from the Wayback Archive, and the user presses Ctrl-C to cancel the program, the error `[ ERR ] Error getting response for page  - local variable 'resp' referenced before assignment` was displayed. This will no longer be shown.

- v4.4

  - New

    - When using `-mode R`, if input was used that does find results, but then those reults don't match the input given, then display a message. For example, if input is `www.hackerone.com/xnl` then wayback machine returns links for `http://hackerone.com/xnl` (without the `www.`). These don't match so aren't returned, but a message will give the user and clue as to what to change the input to if they did want those.

  - Changed

    - BUG FIX:Rewrite the logic in `linksFoundAdd` and correct a typo that always made a runtime error occur and always add a link, without doing the check to see if the domain matches what was searched for (it's rare other URLs are included anyway). Also use new `linksFoundResponseAdd` with similar logic, but remove the prefixed timestamp which occurs with response links.
    - BUG FIX: If a URL is passed (instead of just a domain) as input for `-mode R` to download archived responses, it would not download anything because it would check the result contains the input, but the default port number is included in wayback results, but not included in the input. This has been corrected.
    - Remove `argparse` from `setup.py` and `requirements.txt` because it is a standard Python module.

- v4.3

  - Changed

    - Wayback Machine seemed to have made some changes to their CDX API without any notice or documentation. This caused problems getting URLs for `-mode U` because the API pagination no longer worked. If a number of pages cannot be returned, then all links will be retrieved in one request. However, if they "fix" the problem and pagination starts working again, it will revert to previous code that will get results a page at a time.
    - Although the bug fix for [Github Issue #45](https://github.com/xnl-h4ck3r/waymore/issues/45) appeared to be working fine since the last version, the "changes" made by Wayback machine seemed to have broken that too. The code had to be refactored to work (i.e. don't include the `collapse` parameter at all if `none`), but also no longer works with multiple fields.
    - When `-co` is used, there is no way to tell how long the results will take from Wayback machine now because all the data is retrieved in one request. While pagination is broken, this will just return `Unknown` but will revert back to previous functionality if pagination is fixed.

- v4.2

  - Changed

    - BUG FIX: [Github Issue #45](https://github.com/xnl-h4ck3r/waymore/issues/45) - When getting archived responses from wayback machine, by default it is supposed to get one capture per day per URL (this interval can be changed with `-ci`). But, it was only getting one response per day, not for all the different URLs per day. Thanks to @zakaria_ounissi for raising this.
    - BUG FIX: [Github Issue #46](https://github.com/xnl-h4ck3r/waymore/issues/46) - The config `FILTER_URL` list was being applied to links found from all sources, except wayback machine. So if the MIME type wasn't correct, it was possible that links that matched `FILTER_URL` were still included in the output. Thanks to @brutexploiter for raising this.

- v4.1

  - Changed

    - Removed line `from tqdm import tqdm` as it is not needed and will cause errors if not installed.

- v4.0

  - New

    - Add argument `-oijs`/`--output-inline-js`. If passed, and archived responses are requested, all unique scripts from the responses (excluding `.js`, `.csv`, `.xls`, `.xslx`, `.doc`, `.docx`, `.pdf`, `.msi`, `.zip`, `.gzip`, `.gz`, `.tar`, `.rar`, `.json`) will be extracted and written to files `combinedInline{}.js` (in the same response directory) where `{}` will be the number of the file for every 1000 unique scripts. There will also be a file `combinedInlineSrc.txt` written that will contain the `src` value for all inline external scripts.
    - Exclude SOME downloaded custom 404 responses for `-mode R` if 404 status is to be excluded. The custom 404 pages will be identified by the regex `<title>[^\<]*(404|not found)[^\<]*</title>`.
    - Add `long_description_content_type` to `setup.py` to upload to PyPi
    - Add `waymore` to `PyPi` so can be installed with `pip install waymore`

  - Changed

    - When getting the `DEFAULT_OUTPUT_DIR`, use the `os.path.expanduser` to ensure that the full path is used.

- v3.7

  - Changed

    - Fix a big that can occur in some situations where error `ERROR processResponses 1: [Errno 2] No such file or directory: 'testing/responses.tmp'` shown. The required directories weren't being created correctly.
    - Remove a debug print line I left in!
    - Remove this script from downloaded responses that's now being included by archive.org:
      `<script>window.RufflePlayer=window.RufflePlayer||{};window.RufflePlayer.config={"autoplay":"on","unmuteOverlay":"hidden"};</script>`
    - Remove the comment `<!-- End Wayback Rewrite JS Include -->` from the downloaded responses.
    - Clarify that `-nlf` argument is only relevant to `mode U`.

- v3.6

  - Changed

    - Added `-ko` to the suggestions displayed for Responses when the `-co`/`--check-only` option is used, and there a huge amount of requests to be made.
    - Remove `-ko` from the suggestion displayed for Urls when the `-co`/`--check-only` option is used, because this doesn't affect this. The `-ko` is applied after the links are retrieved.
    - Add a statement to `setup.py` to show where `config.yml` is created if it doesn't already exist. This is to help in figuring out Issue #41.

- v3.5

  - Changed

    - Change `README` descriptions of `-oU` and `-oR` to reference recent `DEFAULT_OUTPUT_DIR`.
    - Change description of `-ra` arg in code and on `README` to say all sources.
    - Other small improvements to `README`.

- v3.4

  - New

    - Add `DEFAULT_OUTPUT_DIR` to the `config.yml` file. This will be used to specify the default directory where output will be written if the `-oU` and `-oR` options aren't used. If blank, this defaults to the directory where `config.yml` is stored (typically `~/.config/waymore/`).

- v3.3

  - New

    - Add `WEBHOOK_DISCORD` to `config.yml` to provide a webhook to be notified when `waymore` has finished, because in some cases it can take a looooooong time!
    - Add arg `-nd`/`--notify-discord` to send a notification to the specified Discord webhook in `config.yml` when `waymore` completes. This is useful when because `waymore` can take a looooong time to complete for some targets.

- v3.2

  - New

    - When getting the Common Crawl index file, if the response is 503, then let the user know it's unavailable. If anything other than 429 or 403, then print an error.

  - Changed

    - Don't show the coffee link if the output is piped out to something else.
    - Remove the `mimetypes` library as it turned out to be quite inaccurate compared to just getting the path extension and using content type of response. Also improve the extension logic.
    - If the input has a path, then make sure it is treated as if no subdomains are wanted, i.e. don't prefix with `*.`. This stopped links coming back from archive.org
    - Change the messaging to make more sense when multiple sources are used, showing `Links found...` for the first, but `Extra links found...` for the rest.

- v3.1

  - Changed

    - Make the identification of extension type better when creating the archived hash files. First try the `mimetypes` library that guesses the extension based on the mimetype. If that doesn't work, try to get the extension from the path. If the extension cannot be retrieved from the path, it will be derived from the `content-type` header. If a generic type still can't be obtained, it will be set to the 2nd part of the `content-type` after the `/`. If still unknown, it will be set to `.unknown`. There will be no more `.xnl` extensions by default.
    - Updated `README` and images to reflect the most recent version.

- v3.0

  - New

    - Allow `waymore` to be installed using `pip` or `pipx` so it can be run from any directory.
    - Show the current version of the tool in the banner, and whether it is the latest, or outdated.
    - When installing `waymore`, if the `config.yml` already exists then it will keep that one and create `config.yml.NEW` in case you need to replace the old config.
    - Add reference to VirusTotal v2 API in `README.md`.
    - Fix a big where the `results/target` folder was being created every time, even if the `-oU` and `-oR` arguments were passed.
    - Include "Buy Me a Coffee" link at the end of output.

  - Changed

    - Change installation instructions in `README.md`.
    - If `--check-only` was passed and it looks like it will take a long time. include the `-ko` argument in the message description of arguments to consider.

- v2.6

  - New

    - Use `tldextract` library to determine whether the input is a subdomain, or just a domain.
    - Include `tldextract` in `setup.py`

  - Changed

    - Fix a bug that causes Alien Vault to not return any links if a subdomain is passed as input. This happens because the api is called with `/indicators/domain/`. If a URL is passed, it will use `/indicators/hostname/` instead and return links successfully.
    - Fix a bug that causes URLScan to fail with error `[ 400 ] Unable to get links from urlscan.io`. This happens when a URL is sent as input because URLScan.io can only retrieve information for hosts. Also, if a host is sent with a trailing `/` then it will be stripped for URLScan.io so it doesn't think there is a path.
    - Fix a bug that causes Alien Vault to fail with runtime error `ERROR getAlienVaultUrls 1: 'full_size'`. This happens when a URL is sent as input. This will now successfully return links for passed URLs.

- v2.5

  - New

    - Show a warning if the user may be passing a sub domain. The chances are that they want all subs if a domain, so should just call for the domain only.

- v2.4

  - New

    - Add lots of extra search terms to the `DEFAULT_FILTER_KEYWORDS` and `FILTER_KEYWORDS` in `config.yml`

  - Changed

    - The Common Crawl HTTPAdaptor for retry strategy will just be applied for code 503. There was an issue with 504 errors happening, and then waymore effectively freezes because of the retry strategy. The Common Crawl documentation (https://commoncrawl.org/blog/oct-nov-2023-performance-issues) just says to retry on 503.

- v2.3

  - New

    - Add `jira` as a search term to the `DEFAULT_FILTER_KEYWORDS` and `FILTER_KEYWORDS` in `config.yml`

- v2.2

  - New

    - Add `-lcy` argument. This lets you limit the number of Common Crawl index collections searched by the year of the index data. The earliest index has data from 2008. Setting to 0 (default) will search collections or any year (but in conjuction with `-lcc`). For example, if you are only interested in data from 2015 and after, pass `-lcy 2015`. This will override the value of `-lcc` if passed.

- v2.1

  - New

    - When the responses are downloaded from archive.org they include some archive.orf code such as scripts and stylesheets. This is usually removed but they may have changed this so was being included again. This change will ensure the new code is removed so the response doesn't include the archive.org code.

- v2.0

  - New

    - Add VirusTotal as a source for URLs. We will get URLs from the v2 API domain report. This can include sub domains, detected URLs, and undetected URLs in the response. It does not give you the status code or MIME type of the links, so we will just check against extension.
    - Show a specific message for Wayback Machine if there is a Connection Refused error. This happens when they have blocked the users IP.
    - Add some pointless celebration messages to the banner for a few different dates!

- v1.37

  - New

    - Add argument `-co`/`--check-only`. If passed, then it will just get the count of requests that need to be made to get URLs from the sources, and how many archived responses will be downloaded. It will try to give an idea of the time the tool could take with the settings given.

- v1.36

  - New

    - Add argument `-wrlr`/`--wayback-rate-limit-retry` which is the number of minutes the user wants to wait for a rate limit pause on Wayback Machine (archive.org) instead of stopping with a `429` error. This defaults to 3 minutes which is a time that seems to work for a while after.
    - Add some additional User-Agents to use when making requests to the API providers.
    - Add new MIME exclusions `video/x-ms-wmv`,`image/x-png`,`video/quicktime`,`image/x-ms-bmp`,`font/opentype`,`application/x-font-opentype`,`application/x-woff` and `audio/aiff`.

  - Changed

    - Change the default `-p`/`--processes` to 1 instead of 3. This is to help with the rate limiting now put in place by web.archive.org. If set to 1 we can also ensure that the pages are processed in order and save where we stopped.
    - Change the `backoff_factor` on `HTTP_ADAPTER` from 1 to 1.1 to help with the rate limiting now put in place by web.archive.org.
    - Change the `pages` set to a list to ensure pages are processed in order (only does if `--processes` is 1).

- v1.35

  - New

    - I had a specific problem with my ISP blocking archive.org for adult content (!) which resulted in a large and confusing error message. This has been replaced by a more useful message if this happens for anyone else.

- v1.34

  - Changed

    - Any scheme, port number, query string, or URL fragment will be removed from the input values.
    - Only show the warning `No value for "URLSCAN_API_KEY" in config.yml - consider adding (you can get a FREE api key at urlscan.io)` if the `-xus` argument wasn't passed.
    - If the input has a domain AND path, then it will still be searched for links, and the mode will not be forced to R.
    - When input value is validated and `<stdin>` is used, just assume one line is a domain/url, and multiple lines are treated as a file (so the correct description is shown).

- v1.33

  - Changed

    - A bug existed that would cause any site that had only had one page of links to not be completely retrieved. Change the processing for Wayback Machine that gets the number of pages. If the total number of pages is 1, then don't pass page number at all.
    - In the `getSPACER` function, add 5 to the length instead of taking 1 away, to text artifacts aren't left.

- v1.32

  - Changed

    - Changes to prevent `SyntaxWarning: invalid escape sequence` errors when Python 3.12 is used.

- v1.31

  - New

    - Add new argument `-urlr`/`--urlscan-rate-limit-retry` to pass the number of minutes that you want to wait between each rate-limit pause from URLScan.
    - Add new MIME exclusions `application/x-msdownload` and `application/x-ms-application`.

  - Changed

    - When getting URLs from the results of URLScsn, also get the `[task][url]` values. Thanks to @Ali45598547 for highlighting this!
    - When the URLScan rate limits, it says how many seconds you need to wait until you can try again. If less than 1 minute, the program will wait automatically to get more results. If more than 1 minute, then the code will wait for the length of time specified by the `-urlr`/`--urlscan-rate-limit-retry` argument, if passed.
    - For CommonCrawl, do at least 20 retires. This helps reduce the problem of `503`` errors and doing many retries was suggested by CommonCrawl them selves to deal with the problem.

- v1.30

  - Changed

    - If there any `+` in the MIME types, e.g. `image/svg+xml`, then replace the `+` with a `.` otherwise the wayback API does not recognise it.
    - Add `application/font-otf` to the `FILTER_MIME` value in `config.yml`.

- v1.29

  - New

    - Check for specific text in response code of 503 (which usually means the site is down for maintenance or not available) and return a specific message instead of the full response.

- v1.28

  - New

    - Added `application/font-otf` to `DEFAULT_FILTER_MIME`

  - Changed

    - Fix a bug that overwrites the output URLs file if the input is a file that contains different hosts.

- v1.27

  - Changed

    - Set the default for `-lcc` to 3 instead of 0 to only search the 3 latest indexes for Common Crawl instead of all of them.

- v1.26

  - Changed

    - Allow an input value of just a TLD, e.g. `.mil`. If a TLD is passed then resources for all domains with that TLD will be retrieved. NOTE: If a TLD is passed then the Alien Vault OTX source is excluded because it needs a full domain.

- v1.25

  - Changed

    - Fix a bug that always strips the port number from URLs found. It should only remove the port if it is :80 or :443

- v1.24

  - Changed

    - Handle errors with the config file better. Display specific message to say if the file isn't found or if there is a formatting error. If there is any other kind of error, the error message will be displayed. THe default values will be used in the case of any of these errors.

- v1.23

  - Changed

    - The `-ko`/`--keywords-only` argument can now be passed without a value, which will use the `FILTER_KEYWORDS` in `config.yml` as before, or passed with a Regex value that will be used instead. For example, `-ko "admin"` to only get links containing the word `admin`, or `-ko "\.js(\?\|$)"` to only get JS files. The Regex check is NOT case sensitive.

- v1.22

  - Changed

    - Fix issue https://github.com/xnl-h4ck3r/waymore/issues/23. If a file is passed as input, an error would occur if any of the domains in the file contained a capital letter or ended with a full stop. The regex in `validateArgInput` has been amended to fix this, adn any `.` on the end of a domain is stripped and domain converted to lowercase before processing.

- v1.21

  - Changed

    - Fix issue https://github.com/xnl-h4ck3r/waymore/issues/24. If the `FILTER_CODE` in `config.yml` is set to one status code then it is needs to be explicitly set to a string in `getConfig()`

- v1.20

  - New

    - Add argument `-fc` for filtering HTTP status codes. Using this will override the `FILTER_CODE` value from `config.yml`. This is for specifying HTTP status codes you want to exclude from the results, and are provided in a comma separated list.
    - Add argument `-mc` for matching HTTP status codes. Using this will override the `FILTER_CODE` value from `config.yml` AND the `-fc` argument. This is for specifying HTTP status codes you want to match from the results, and are provided in a comma separated list.

  - Changed

    - Changed how filters are specified in the request to the Common Crawl API. Removes the regex negative lookahead which is not needed if you use `filter=!`

- v1.19

  - Changed

    - Bug fix - ignore any blank lines in the input file when validating if input is in the correct format

- v1.18

  - Changed

    - Cache the Common Crawl `collinfo.json` file locally. The file is only updated a few times per year so there is no point in requesting it every time **waymore** is run. Common Crawl can struggle with volume against it's API which can cause timeouts, and currently, about 10% of all requests they get are for the `collinfo.json`!
    - Add a HTTPAdapter specifically for Common Crawl to have `retries` and `backoff_factor` increased which seems to reduce the errors and maximize the results found.

- v1.17

  - Changed
    - If an input file has a sub domain starting with \_ or - then an error was raised, but these are valid. This bug has been fixed.
    - In addition to the fix above, the error message will show what line was flagged in error so the user can raise an issue on Github about it if they believe it is an error.

- v1.16

  - Changed
    - Fix a bug that raises `ERROR processURLOutput 6: [Errno 2] No such file or directory: ''` if the value passed to `-oU` has no directory specified as part of the file name.

- v1.15

  - Changed
    - Fix bug that shows an error when `-v` is passed and `-oU` does not specify a directory, just a filename

- v1.14

  - Changed
    - Fix a bug with the `-c`/`--config` option

- v1.13

  - New

    - Added argument `-oU`/`--output-urls` to allow the user to specify a filename (including path) for the URL links file when `-mode U` (or `B`oth) is used. If not passed, then the file `waymore.txt` will be created in the `results/{target.domain}` directory as normal. If a path is passed with the file, then any directories will be created. For example: `-oU ~/Recon/Redbull/waymoreUrls.txt`
    - Added argument `-oR`/`--output-responses` to allow the user to specify a directory (or path) where the archived responses and `index.txt` file is written when `-mode R` (or `B`oth) is used. If any directories in the path do not exist they will be created. For example: `-oR ~/Recon/Redbull/waymoreResponses`

  - Changed
    - When removing all web archive references in the downloaded archived response, there were a few occasions this wasn't working so the regex has been changed to be more specific to ensure this works.

- v1.12

  - New
    - Added argument `-c` / `--config` to specify the full path of a YML config file. If not passed, it looks for file `config.yml` in the same directory as runtime file `waymore.py`

- v1.11

  - New
    - Added argument `-nlf`/`--new-links-file`. If passed, and you run `-mode U` or `-mode B` to get URLs more than once for the same target, the `waymore.txt` will still be appended with new links (unless `-ow` is passed), but a new output file called `waymore.new` will also be written. If there are no new links, the empty file will still be created. This can be used for continuous monitoring of a target.
    - Added a `waymore` folder containing a new `__init__.py` file that contains the `__version__` value.
    - Added argument `--verison` to display the current version.
    - Show better error messages if the archive.org site returns a `Blocked Site Error`.
  - Changed
    - If a file of domains is passed as input, make sure spaces are stripped from the lines.
    - Change `.gitignore` to include `__pycache__`.
    - Move images to `waymore/images` folder.

- v1.10

  - New
    - If `-mode U` is run for the same target again, by default new links found will be added to the `waymore.txt` file and duplicates removed.
    - Added argument `-ow`/`--output-overwrite` that can be passed to force the `waymore.txt` file to be overwritten with newly found links instead of being appended.
  - Changed
    - Change the README.md to reflect new changes

- v1.9

  - New
    - Add functionality to continue downloading archived responses if it does not complete for any reason. When downloading archived responses, a file called `responses.tmp` will be created with the links of all responses that will be downloaded. There will also be a `continueresp.tmp` that will store the index of the current response being saved. If these files exist when run again, the user will be prompted whether to continue a previous run (so new filters will be ignored) or start a new one.
    - Add `CONTINUE_RESPONSES_IF_PIPED` to `config.yml`. If `stdin` or `stdout` is piped from another process, the user is not prompted whether they want a previous run of downloading responses. This value will determine whether to continue a previous run, or start a new one, in that situation.
  - Changed
    - Corrected the total pages shown when getting wayback URLs
    - Included missing packages in the `requirements.txt` document.
    - Fix Issue #16 (https://github.com/xnl-h4ck3r/waymore/issues/16)

- v1.8

  - Changed
    - When archived responses are saved as files, the extension `.xnl` will no longer be used if `-url-filename` is passed. If `-url-filename` is not passed then the filename is represented by a hash value. The extension of these files will be set to `.xnl` only of the original file type cannot be derived from the original URL.

- v1.7

  - New
    - Added `-xwm` parameter to exclude getting URL's from Wayback Machine (archive.org)
    - Added `-lr`/`--limit-requests` that can be used to limit the number of requests made per source (excluding Common Crawl) when getting URL's. For example, if you run **waymore** for `-i twitter.com` it says there are 28,903,799 requests to archive.org that need to be made (that could take almost 1000 days for some people!!!). The default value for the argument is 0 (Zero) which will apply no limit as before. There is also an problem with the Wayback Machine CDX API where the number of pages returned is not correct when filters are applied and can cause issues. Setting this parameter to a sensible value can relieve that issue (it may take a while for archive.org to address the problem).
  - Changed
    - Make sure that filters in API URL's are escaped correctly
    - Add error handling to `getMemory()` to avoid any errors if `psutil` is not installed

- v1.6

  - New
    - Add a docker option to run `waymore`. Include instructions in `README.md` and a new `DockerFile`
  - Changed
    - If multiple domain/URLs are passed by file or STDIN, remove `*.` from the start of any input values.
    - Change the default `FILTER_KEYWORDS` to include more useful words.
    - If a link found from an API has port 80 or 443 specified, e.g. `https://exmaple.com:80/example` then remove the `:80`. Many links have this in archive.org so this could reduce the number of similar links reported.
    - Amend `setup.py` to include `urlparse3` that is now used to get the domain and port of links found

- v1.5

  - New
    - Add argument `-ko`/`--keywords-only` which if passed, will only get Links (unless `-f` is passed) that have a specified keyword in the URL, and will only download responses (regardless of `-f`) where the keyword is in the URL. These multiple keywords can be specified in `config.yml` in a comma separated list.
    - Add a `FILTER_KEYWORDS` key/pair to `config.yml` (and default value in code) initially set to `admin,login,logon,signin,register,dashboard,portal,ftp,cpanel`
  - Changed
    - Only add to the MIME type list if the `-v` option is used because they are not displayed otherwise.
    - Warn the user if there is a value missing from the config.yml file
    - Fixed small bug in `getURLScanUrls` that raised an error for `getSPACER`

- v1.4

  - New
    - Added `-m /--memory-threshold` argument to set memory threshold percentage. If the machines memory goes above the threshold, the program will be stopped and ended gracefully before running out of memory (default: 95)
    - If `-v` verbose output was used, memory stats will be output at the end, and also shown on teh progress bar downloading responses.
    - Included `psutil` in `setup.py`
  - Changed
    - Fix some display issues not completely done in v1.3, regarding trailing spaces when errors are displayed.
    - Remove line `os.kill(os.getpid(),SIGINT)` from `processArchiveUrl` which isn't needed and just causes more error if a user does press Ctrl-C.

- v1.3

  - New
    - Added functionality to allow output Links output to be piped to another program (the output file will still be written). Errors and progress bar are written to STDERR. No information about archived responses will be piped.
    - Added functionality to allow input to be piped to waymore. This will be the same as passing to `-i` argument.
  - Changed
    - Use a better way to add trailing spaces to strings to cover up other strings (like progress bar), regardless of terminal width.
    - Change the README to mention `-xus` argument and how to get a URLScan API key to add to the config file.

- v1.2

  - Changed
    - Removed User-Agent `Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1` because it caused problems on some domains in `xnLinkFinder` tool, so removing from here too.
    - Base the length of the progress bar (show when downloading archived responses) on the width of the terminal so it displays better and you don't get multiple lines on smaller windows.
    - Amend `.gitignore` to include other unwanted files

- v1.1

  - New
    - Allow a file of domains/URL's to be passed as input with `-i` instead of just one.
  - Changed
    - Remove version numbers from `requirements.txt` as these aren't really needed and may cause some issues.

- v1.0

  - New
    - Added URLScan as a source of URL's. Waymore now has all the same sources for URLs as [gau](https://github.com/lc/gau)
    - Added `-xus` parameter to exclude URLScan when getting URL's.
    - Added `-r` parameter to specify the number of times requests are retried if they return 429, 500, 502, 503 or 504 (default: 1).
    - Made requests use a retry strategy using `-r` value, and also a `backoff_factor` of 1 for Too Many Redirect (429) responses.
    - General bug fixes.
  - Changed
    - Fixed a bug with was preventing HTTP Status Code filtering from working on Alien Vaults requests.
    - Fixed a bug that was preventing MIME type filtering from working on Common Crawl requests.
    - Correctly escape all characters is strings compared in regex with re.escape instead of just changing `.` to `\.`
    - Changed default MIME type filter to include: video/webm,video/3gpp,application/font-ttf,audio/mp3,audio/x-wav,image/pjpeg,audio/basic
    - Changed default URL filter to include:/jquery,/bootstrap
    - If Ctrl-C is used to end the program, try to ensure that results at that point are still saved before ending.

- v0.3

  - New
    - Added Alien Vault OTX as a source of URL's. Results cannot be checked against MIME filters though because that info is not available in the API response.
    - Added `-xav` parameter to exclude Alien Vault when getting URL's.
  - Changed
    - Improved regex for the `-i` input value to ensure it's a valid domain, with or without sub domains and path, but no query string or fragments.
    - General tidying up and improvements

- v0.2

  - New
    - Added to the TODO list on README.md of changes coming soon
  - Changed
    - When getting URl's from archive.org it now uses pagination. Instead of one API call (how waybackurls does it), it makes one call per page of URL's (how gau does it). This actually results in a lot more URL's being returned even though the archive.org API docs seem to imply it should be the same. So in comparison to gau it now returns the same number of URL's from archive.org
    - Ensure input domain/path is URL encoded when added to the API call URL's

- v0.1 - Initial release
