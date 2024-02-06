## Changelog

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
