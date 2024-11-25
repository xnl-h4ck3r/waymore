<center><img src="https://github.com/xnl-h4ck3r/waymore/blob/main/waymore/images/title.png"></center>

## About - v4.6

The idea behind **waymore** is to find even more links from the Wayback Machine than other existing tools.

👉 The biggest difference between **waymore** and other tools is that it can also **download the archived responses** for URLs on wayback machine so that you can then search these for even more links, developer comments, extra parameters, etc. etc.
👉 Also, other tools do not currenrtly deal with the rate limiting now in place by the sources, and will often just stop with incomplete results and not let you know they are incomplete.

Anyone who does bug bounty will have likely used the amazing [waybackurls](https://github.com/tomnomnom/waybackurls) by @TomNomNoms. This tool gets URLs from [web.archive.org](https://web.archive.org) and additional links (if any) from one of the index collections on [index.commoncrawl.org](http://index.commoncrawl.org/).
You would have also likely used the amazing [gau](https://github.com/lc/gau) by @hacker\_ which also finds URL's from wayback archive, Common Crawl, but also from Alien Vault and URLScan.
Now **waymore** gets URL's from ALL of those sources too (with ability to filter more to get what you want):

- Wayback Machine (web.archive.org)
- Common Crawl (index.commoncrawl.org)
- Alien Vault OTX (otx.alienvault.com)
- URLScan (urlscan.io)
- Virus Total (virustotal.com)

👉 It's a point that many seem to miss, so I'll just add it again :) ... The biggest difference between **waymore** and other tools is that it can also **download the archived responses** for URLs on wayback machine so that you can then search these for even more links, developer comments, extra parameters, etc. etc.

👉 **PLEASE READ ALL OF THE INFORMATION ON THIS PAGE TO MAKE THE MOST OF THIS TOOL, AND ESPECIALLY BEFORE RAISING ANY ISSUES** 🤘

👉 **THIS TOOL CAN BE VERY SLOW, BUT IT IS MEANT FOR COVERAGE, NOT SPEED**

⚠️ **A common mistake that is made is passing a file of subdomains to get everything for a domain. DON'T DO IT! Just pass the domain only to get all subs for that domain. It will be SO much quicker, and you won't miss anything.**

## Installation

**NOTE: If you already have a `config.yml` file, it will not be overwritten. The file `config.yml.NEW` will be created in the same directory. If you need the new config, remove `config.yml` and rename `config.yml.NEW` back to `config.yml`.**

`waymore` supports **Python 3**.

Install `waymore` in default (global) python environment.

```bash
pip install waymore
```

OR

```bash
pip install git+https://github.com/xnl-h4ck3r/waymore.git -v
```

You can upgrade with

```bash
pip install --upgrade waymore
```

### pipx

Quick setup in isolated python environment using [pipx](https://pypa.github.io/pipx/)

```bash
pipx install git+https://github.com/xnl-h4ck3r/waymore.git
```

## Usage

| Arg           | Long Arg                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -i            | --input                    | The target domain (or file of domains) to find links for. This can be a domain only, or a domain with a specific path. If it is a domain only to get everything for that domain, don't prefix with `www.`. You can also specify a TLD only by prefixing with a period, e.g. `.mil`, which will get all subs for all domains with that TLD (NOTE: The Alien Vault OTX source is excluded if searching for a TLD because it requires a full domain). **NOTE: Any scheme, port number, query string, or URL fragment will be removed from the input values. However, if you provide a path, this will be specifically searched for, so will limit your results.** |
| -mode         |                            | The mode to run: `U` (retrieve URLs only), `R` (download Responses only) or `B` (Both). If `-i` is a domain only, then `-mode` will default to `B`. If `-i` is a domain with path then `-mode` will default to `R`.                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -oU           | --output-urls              | The file to save the Links output to, including path if necessary. If the `-oR` argument is not passed, a `/results` directory will be created in the path specified by the `DEFAULT_OUTPUT_DIR` key in `config.yml` file (typically defaults to `~/.config/waymore/`). Within that, a directory will be created with target domain (or domain with path) passed with `-i` (or for each line of a file passed with `-i`). For example: `-oU ~/Recon/Redbull/waymoreUrls.txt`                                                                                                                                                                                   |
| -oR           | --output-responses         | The directory to save the response output files to, including path if necessary. If the argument is not passed, a `/results` directory will be created in the path specified by the `DEFAULT_OUTPUT_DIR` key in `config.yml` file (typically defaults to `~/.config/waymore/`). Within that, a directory will be created with target domain (or domain with path) passed with `-i` (or for each line of a file passed with `-i`). For example: `-oR ~/Recon/Redbull/waymoreResponses`                                                                                                                                                                          |
| -n            | --no-subs                  | Don't include subdomains of the target domain (only used if input is not a domain with a specific path).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -f            | --filter-responses-only    | The initial links from sources will not be filtered, only the responses that are downloaded, e.g. it maybe useful to still see all available paths from the links, even if you don't want to check the content.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| -fc           |                            | Filter HTTP status codes for retrieved URLs and responses. Comma separated list of codes (default: the `FILTER_CODE` values from `config.yml`). Passing this argument will override the value from `config.yml`                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| -ft           |                            | Filter MIME Types for retrieved URLs and responses. Comma separated list of MIME Types (default: the `FILTER_MIME` values from `config.yml`). Passing this argument will override the value from `config.yml`. **NOTE: This will NOT be applied to Alien Vault OTX and Virus Total because they don't have the ability to filter on MIME Type. Sometimes URLScan does not have a MIME Type defined - these will always be included. Consider excluding sources if this matters to you.**.                                                                                                                                                                      |
| -mc           |                            | Only Match HTTP status codes for retrieved URLs and responses. Comma separated list of codes. Passing this argument overrides the config `FILTER_CODE` and `-fc`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| -mt           |                            | Only MIME Types for retrieved URLs and responses. Comma separated list of MIME types. Passing this argument overrides the config `FILTER_MIME` and `-ft`. **NOTE: This will NOT be applied to Alien Vault OTX and Virus Total because they don't have the ability to filter on MIME Type. Sometimes URLScan does not have a MIME Type defined - these will always be included. Consider excluding sources if this matters to you.**.                                                                                                                                                                                                                           |
| -l            | --limit                    | How many responses will be saved (if `-mode R` or `-mode B` is passed). A positive value will get the **first N** results, a negative value will get the **last N** results. A value of 0 will get **ALL** responses (default: 5000)                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -from         | --from-date                | What date to get responses from. If not specified it will get from the earliest possible results. A partial value can be passed, e.g. `2016`, `201805`, etc.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -to           | --to-date                  | What date to get responses to. If not specified it will get to the latest possible results. A partial value can be passed, e.g. `2021`, `202112`, etc.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| -ci           | --capture-interval         | Filters the search on archive.org to only get at most 1 capture per hour (`h`), day (`d`) or month (`m`). This filter is used for responses only. The default is `d` but can also be set to `none` to not filter anything and get all responses.                                                                                                                                                                                                                                                                                                                                                                                                               |
| -ra           | --regex-after              | RegEx for filtering purposes against links found from all sources of URLs AND responses downloaded. Only positive matches will be output.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| -url-filename |                            | Set the file name of downloaded responses to the URL that generated the response, otherwise it will be set to the hash value of the response. Using the hash value means multiple URLs that generated the same response will only result in one file being saved for that response.                                                                                                                                                                                                                                                                                                                                                                            |
| -xwm          |                            | Exclude checks for links from Wayback Machine (archive.org)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -xcc          |                            | Exclude checks for links from commoncrawl.org                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| -xav          |                            | Exclude checks for links from alienvault.com                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -xus          |                            | Exclude checks for links from urlscan.io                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -xvt          |                            | Exclude checks for links from virustotal.com                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -lcc          |                            | Limit the number of Common Crawl index collections searched, e.g. `-lcc 10` will just search the latest `10` collections (default: 1). As of November 2024 there are currently 106 collections. Setting to `0` will search **ALL** collections. If you don't want to search Common Crawl at all, use the `-xcc` option.                                                                                                                                                                                                                                                                                                                                        |
| -lcy          |                            | Limit the number of Common Crawl index collections searched by the year of the index data. The earliest index has data from 2008. Setting to 0 (default) will search collections or any year (but in conjuction with `-lcc`). For example, if you are only interested in data from 2015 and after, pass `-lcy 2015`. This will override the value of `-lcc` if passed. If you don't want to search Common Crawl at all, use the `-xcc` option.                                                                                                                                                                                                                 |
| -t            | --timeout                  | This is for archived responses only! How many seconds to wait for the server to send data before giving up (default: 30)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -p            | --processes                | Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes (threads) used (default: 1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -r            | --retries                  | The number of retries for requests that get connection error or rate limited (default: 1).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| -m            | --memory-threshold         | The memory threshold percentage. If the machines memory goes above the threshold, the program will be stopped and ended gracefully before running out of memory (default: 95)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| -ko           | --keywords-only            | Only return links and responses that contain keywords that you are interested in. This can reduce the time it takes to get results. If you provide the flag with no value, Keywords are taken from the comma separated list in the `config.yml` file (typically in `~/.config/waymore/`) with the `FILTER_KEYWORDS` key, otherwise you can pass a specific Regex value to use, e.g. `-ko "admin"` to only get links containing the word `admin`, or `-ko "\.js(\?\|$)"` to only get JS files. The Regex check is NOT case sensitive.                                                                                                                           |
| -lr           | --limit-requests           | Limit the number of requests that will be made when getting links from a source (this doesn\'t apply to Common Crawl). Some targets can return a huge amount of requests needed that are just not feasible to get, so this can be used to manage that situation. This defaults to 0 (Zero) which means there is no limit.                                                                                                                                                                                                                                                                                                                                      |
| -ow           | --output-overwrite         | If the URL output file (default `waymore.txt`, or specified by `-oU`) already exists, it will be overwritten instead of being appended to.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| -nlf          | --new-links-file           | If this argument is passed, a `waymore.new` file (or if `-oU` is used it will be the name of that file suffixed with `.new`) will also be written, and will contain links for the latest run. This can be used for continuous monitoring of a target (only for `mode U`, not `mode R`).                                                                                                                                                                                                                                                                                                                                                                        |
| -c            | --config                   | Path to the YML config file. If not passed, it looks for file `config.yml` in the default directory, typically `~/.config/waymore`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -wrlr         | --wayback-rate-limit-retry | The number of minutes the user wants to wait for a rate limit pause on Wayback Machine (archive.org) instead of stopping with a `429` error (default: 3).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| -urlr         | --urlscan-rate-limit-retry | The number of minutes the user wants to wait for a rate limit pause on URLScan.io instead of stopping with a `429` error (default: 1).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| -co           | --check-only               | This will make a few minimal requests to show you how many requests, and roughly how long it could take, to get URLs from the sources and downloaded responses from Wayback Machine.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -nd           | --notify-discord           | Whether to send a notification to Discord when waymore completes. It requires `WEBHOOK_DISCORD` to be provided in the `config.yml` file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| -oijs         | --output-inline-js         | Whether to save combined inline javascript of all relevant files in the response directory when `-mode R` (or `-mode B`) has been used. The files are saved with the name `combinedInline{}.js` where `{}` is the number of the file, saving 1000 unique scripts per file. The file `combinedInlineSrc.txt` will also be created, containing the `src` value of all external scripts referenced in the files.                                                                                                                                                                                                                                                  |
| -v            | --verbose                  | Verbose output                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|             | --print-only                  | Prints output directly to the shell                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|               | --version                  | Show current version number.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -h            | --help                     | Show the help message and exit.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

## Run with docker

Install [docker](https://docs.docker.com/get-docker/)

```bash
git clone https://github.com/xnl-h4ck3r/waymore.git
cd waymore
```

Build image:

```bash
docker build -t waymore .
```

Run waymore with this command:

```bash
docker run -it --rm -v $PWD/results:/app/results waymore:latest waymore -i example.com -oU example.com.links -oR results/example.com/
```

## Input and Mode

The input `-i` can either be a domain only, e.g. `redbull.com` or a specific domain and path, e.g. `redbull.com/robots.txt`. You can also pass a file of domains/URLs to process (or pass values in by piping from another program on the command line). **NOTE: Any scheme, port number, query string, or URL fragment will be removed from the input values. However, if you provide a path, this will be specifically searched for, so will limit your results.**

There are different modes that can be run for waymore. The `-mode` argument can be 3 different value:

- `U` - URLs will be retrieved from archive.org (if `-xwm` is not passed), commoncrawl.org (if `-xcc` is not passed), otx.alienvault.com (if `-xvv` is not passed) and urlscan.io (if `-xus` is not passed)
- `R` - Responses will be downloaded from archive.org
- `B` - Both URLs and Responses will be retrieved

If the input was a specific URL, e.g. `redbull.com/robots.txt` then the `-mode` defaults to `R`. Only responses will be downloaded. You cannot change the mode to `U` or `B` for a domain with path because it isn't necessary to retrieve URLs for a specific URL.

If the input is just a domain, e.g. `redbull.com` then the `-mode` defaults to `B`. It can be changed to `U` or `R` if required. When a domain only is passed then all URLs/responses are retrieved for that domain (and sub domains unless `-n` is passed). If the no sub domain option `-n` is passed then the `www` sub domain is still included by default.

## config.yml

The `config.yml` file (typically in `~/.config/waymore/`) have values that can be updated to suit your needs. Filters are all provided as comma separated lists:

- `FILTER_CODE` - Exclusions used to exclude responses we will try to get from web.archive.org, and also for file names when `-i` is a directory, e.g. `301,302`. This can be overridden with the `-fc` argument. Passing the `-mc` (to match status codes instead of filter) will override any value in `FILTER_CODE` or `-fc`.
- `FILTER_MIME` - MIME Content-Type exclusions used to filter links and responses from web.archive.org through their API, e.g. `'text/css,image/jpeg`. This can be overridden with the `-ft` argument. . Passing the `-mt` (to match MIME types instead of filter) will override any value in `FILTER_MIME` or `-ft`.
- `FILTER_URL` - Response code exclusions we will use to filter links and responses from web.archive.org through their API, e.g. `.css,.jpg`
- `FILTER_KEYWORDS` - Only links and responses will be returned that contain the specified keywords if the `-ko`/`--keywords-only` argument is passed (without providing an explicit value on the command line), e.g. `admin,portal`
- `URLSCAN_API_KEY` - You can sign up to [urlscan.io](https://urlscan.io/user/signup) to get a **FREE** API key (there are also paid subscriptions available). It is recommended you get a key and put it into the config file so that you can get more back (and quicker) from their API. NOTE: You will get rate limited unless you have a full paid subscription.
- `CONTINUE_RESPONSES_IF_PIPED` - If retrieving archive responses doesn't complete, you will be prompted next time whether you want to continue with the previous run. However, if `stdout` is piped to another process it is assumed you don't want to have an interactive prompt. A value of `True` (default) will determine assure the previous run will be continued. if you want a fresh run every time then set to `False`.
- `WEBHOOK_DISCORD` - If the `--notify-discord` argument is passed, `knoxnl` will send a notification to this Discord wehook when a successful XSS is found.
- `DEFAULT_OUTPUT_DIR` - This is the default location of any output files written if the `-oU` and `-oR` arguments are not used. If the value of this key is blank, then it will default to the location of the `config.yml` file.

  **NOTE: The MIME types cannot be filtered for Alien Vault OTX and Virus Total because they don't have the ability to filter on MIME Type. Sometimes URLScan does not have a MIME Type defined for a URL. In these cases, URLs will be included regardless of filter or match. Bear this in mind and consider excluding certain providers if this is important.**

## Output

In the default output directory specificed in the `config.yml` file with `DEFAULT_OUTPUT_DIR` (if that is blank, it will default to the location of the `config.yml` file itself, typically `~/.config/waymore/`), a `results` directory will be created. Within that, a directory will be created with target domain (or domain with path) passed with `-i` (or for each line of a file passed with `-i`). You can alternatively use argument `-oU` to specify where the URL links file will be output (and the name of the file). You can also use argument `-oR` to specify a directory (or path) where the archived responses will be output.
When run, the following files are created in the target directory:

- `waymore.txt` - If `-mode` is `U` or `B`, this file will contain links from selected sources. Links will be retrieved from archive.org Wayback Machine (unless `-xwm` was passed), commoncrawl.org (unless `-xcc` was passed), otx.alienvault.com (unless `-xav` was passed) and urlscan.io (unless `-xus` was passed). If the `-ow` option was also passed, any existing `waymore.txt` file in the target results directory will be overwritten, otherwise new links will be appended and duplicates removed.
- `index.txt` - If `-mode` is `R` or `B`, and `-url-filname` was not passed then archived responses will be downloaded and hash values will be used for the saved file names. This file contains a comma separated list of `<hash>,<archive URL>,<timestamp>` in case you need to know which URLs produced which response.
- `ALL OTHER FILES` - These archived response files will be created if `-mode` was `R` or `B`. If `-url-filename` was passed the the file names will be the archive URL that generated the response, e.g. `https--example.com-robots.txt`, otherwise the file name will be a hash value, e.g. `7960113391501.{EXT}` where `{EXT}` will be the extension derived from the path, otherwise it will be derived from the response `content-type`. Sometimes a general extesions will be given, e.g. `.js` for any content type containing the word `javascript`, otherwise it may be set to the last part of the type (e.g. if it's `application/java-archive` the file will be `7960113391501.java-archive`). Using hash values mean that less files will be written as there will only be one file per unique response. These archived responses are edited, before being saved, to remove any reference to `web.archive.org`.

## Info and Suggestions

The number of links found, and then potentially the number of files archived responses you will download could potentially be **HUGE** for many domains. This tool isn't about speed, it's about finding more, so be patient.

There is a `-p` option to increase the number of processes (used when retrieving links from all sources, and downloading archived responses from archive.org). However, although it may not be as fast as you'd like, I would suggest leaving `-p` at the default of 3 because I personally found issues with getting responses with higher values. We don't want to cause these services any problems, so be sensible!

I often use the `-f` option because I want `waymore.txt` to contain ALL possible links. Even though I don't care about images, fonts, etc. it could still be useful to see all possible paths and maybe parameters. Any filters will always be applied to downloading archived responses though. You don't want to waste time downloading thousands of images!

Using the `-v` option can help see what is happening behind the scenes and could help you if you aren't getting the output you are expecting.

All the MIME Content Types of URL's found (by all sources except Alien Vault) will be displayed when `-v` is used. This may help to add further exclusions if you find you still get back things you don't want to see. If you spot a MIME type that is being included but you don't want that going forward, add it to the `FILTER_MIME` in `config.yml`.
It should be noted that sometimes the MIME type on archive.org is stored as `unk` and `unknown` instead of the real MIME so the filter won't necessarily remove it from their results. The `FILTER_URL` config settings can be used to remove these afterwards. For example, if a GIF has MIME type `unk` instead of `image/gif` (and that's in `FILTER_MIME`) then it won't get filtered, but if the url is `https://target.com/assets/logo.gif` and `.gif` is in `FILTER_URL` it won't get requested.

If `config.yml` doesn't exist, or the entries for filters, aren't in the file, then default filters are used. It's better to have the file and review these to ensure you are getting what you need.

There can potentially be millions of responses so make sure you set filters, but also the Limit (`-l`), From Date (`-from`), To Date (`-to`) and/or Capture Interval (`-ci`) if you need to. The limit defaults to 5000, but say you wanted to get the latest 20,000 responses from 2015 up until January 2018... you would pass `-l -20000 -from 2015 -to 201801`. The Capture Interval determines how many responses will get downloaded for a particular URL within a specified period, e.g. if you set to `m` you will only get one response per month for a URL. The default `d` will likely greatly reduce the number of responses and unlikely to miss many unique responses unless a target changed something more than once in a given day.

Another useful argument is `-mc` that will only get results where the HTTP status code matches the comma separated list passed, e.g. `-mc 200` or `-mc 200,403`.

You can also greatly reduce the number (and therefore reduce the execution time) of links and responses by only returning ones that contain keywords you are interested in. You can list these keywords in `config.yml` with the `FILTER_KEYWORDS` key and then pass argument `-ko`/`--keywords-only` to use these, or you can pass `-ko`/`--keywords-only` with a specific Regex, e.g. `-ko "\.js(\?|$)"` to only get JS files.

As mentioned above, sign up to [urlscan.io](https://urlscan.io/user/signup) to get a **FREE** API key (there are also paid subscriptions available). It is recommended you get a key and put it into the `config.yml` file so that you can get more back (and quicker) from their API. NOTE: You will get rate limited unless you have a full paid subscription.

The archive.org Wayback Machine CDX API can sometimes can sometimes require a huge amount of requests to get all the links. For example, if you run **waymore** for `-i twitter.com` it says there are **28,903,799** requests to archive.org that need to be made (that could take almost 1000 days for some people!!!). The argument `-lr` can be used to limit the number of requests made per source (although it's usually archive.org that is the problem). The default value for the argument is 0 (Zero) which will apply no limit.

There is also a problem with the Wayback Machine CDX API where the number of pages returned is not correct when filters are applied and can cause issues (see https://github.com/internetarchive/wayback/issues/243). Until that issue is resolved, setting the `-lr` argument to a sensible value can help with that problem in the short term.

The Common Crawl API has had a lot of issues for a long time. Including this source could make waymore take a lot longer to run and may not yield any extra results. You can check if tere is an issue by visiting http://index.commoncrawl.org/collinfo.json and seeing if this is successful. Consider excluding Common Crawl altogether using the `--providers` argument and not including `commoncrawl`, or using the `-xcc` argument.

**The provider API servers aren't designed to cope with huge volumes, so be sensible and considerate about what you hit them with!**

When downloading archived responses, this can take a long time and can sometimes be killed by the machine for some reason, or manually killed by the user.
In the targets `results` directory, a file called `responses.tmp` is created at the start of the process and contains all the response URLs that will be retrieved. There will also be a file called `continueResp.tmp` that stores the index of the latest response retrieved. If `waymore` is run to get responses (`-mode R` or `-mode B`), and these files exist, it means there was a previous incomplete run, and you will be asked if you want to continue with that one instead. It will then continue from where it stopped before.

## Some Basic Examples

### Example 1

Just get the URLs from all sources for `redbull.com` (`-mode U` is just for URLs, so no responses are downloaded):

<center><img src="https://github.com/xnl-h4ck3r/waymore/blob/main/waymore/images/example1.png"></center>

The URLs are saved in the same path as `config.yml` (typically `~/.config/waymore`) under `results/redbull.com/waymore.txt`

### Example 2

Get ALL the URLs from Wayback for `redbull.com` (no filters are applied in `mode U` with `-f`, and no URLs are retrieved from Commone Crawl, Alien Vault, URLScan and Virus Total, because `-xcc`, `-xav`, `-xus`, `-xvt` are passed respectively. This can also be achieved by passing `--providers wayback` instead of the exclude arguments).
Save the FIRST 200 responses that are found starting from 2022 (`-l 200 -from 2022`):

<center><img src="https://github.com/xnl-h4ck3r/waymore/blob/main/waymore/images/example2.png"></center>

The `-mode` wasn't explicitly set so defaults to `B` (Both - retrieve URLs AND download responses).
A file will be created for each unique response and also saved in `results/redbull.com/`:

<center><img src="https://github.com/xnl-h4ck3r/waymore/blob/main/waymore/images/example3.png"></center>

There will also be a file `results/redbull.com/index.txt` that will contain a reference to what URLs gave the response for what file, e.g.

```
4847147712618,https://web.archive.org/web/20220426044405/https://www.redbull.com/additional-services/geo ,2022-06-24 20:07:50.603486
```

where `4847147712618` is the hash value of the response in `4847147712618.xnl`, the 2nd value is the Wayback Machine URL where you can view the actual page that was archived, and the 3rd is a time stamp of when the response was downloaded.

## Example 3

You can pipe waymore to other tools. Any errors are sent to `stderr` and any links found are sent to `stdout`. The output file is still created in addition to the links being piped to the next program. However, archived responses are not piped to the next program, but they are still written to files. For example:

```
waymore -i redbull.com -mode U | unfurl keys | sort -u
```

You can also pass the input through `stdin` instead of `-i`.

```
cat redbull_subs.txt | waymore
```

## Example 4

Sometimes you may just want to check how many request, and how long `waymore` is likely to take if you ran it for a particular domain. You can do a quick check by using the `-co`/`--check-only` argument. For example:

```
waymore -i redbull.com --check-only
```

<center><img src="https://github.com/xnl-h4ck3r/waymore/blob/main/waymore/images/example4.png"></center>

## Finding Way More URLs!

So now you have lots of archived responses and you want to find extra links? Easy! Why not use [xnLinkFinder](https://github.com/xnl-h4ck3r/xnLinkFinder)?
For example:

```
xnLinkFinder -i ~/Tools/waymore/results/redbull.com -sp https://www.redbull.com -sf redbull.com -o redbull.txt
```

Or run other tools such as [trufflehog](https://github.com/trufflesecurity/trufflehog) or [gf](https://github.com/tomnomnom/gf) over the directory of responses to find even more from the archived responses!

## Issues

If you come across any problems at all, or have ideas for improvements, please feel free to raise an issue on Github. If there is a problem, it will be useful if you can provide the exact command you ran and a detailed description of the problem. If possible, run with `-v` to reproduce the problem and let me know about any error messages that are given.

## TODO

- Add an `-oss` argument that accepts a file of Out Of Scope subdomains/URLs that will not be returned in the output, or have any responses downloaded

## References

- [Wayback CDX Server API - BETA](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server)
- [Common Crawl Index Server](https://index.commoncrawl.org/)
- [Alien Vault OTX API](https://otx.alienvault.com/assets/static/external_api.html)
- [URLScan API](https://urlscan.io/docs/api/)
- [VirusTotal API (v2)](https://docs.virustotal.com/v2.0/reference/getting-started)

Good luck and good hunting!
If you really love the tool (or any others), or they helped you find an awesome bounty, consider [BUYING ME A COFFEE!](https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

🤘 /XNL-h4ck3r
