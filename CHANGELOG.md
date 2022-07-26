## Changelog

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
