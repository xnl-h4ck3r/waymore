## Changelog

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
