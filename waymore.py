#!/usr/bin/env python
# Python 3
# waymore - by @Xnl-h4ck3r: Find way more from the Wayback Machine
# Full help here: https://github.com/xnl-h4ck3r/waymore/blob/main/README.md
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

from urllib.parse import urlparse
import requests
from requests.exceptions import ConnectionError
from requests.utils import quote
from requests.adapters import HTTPAdapter, Retry
import argparse
from signal import SIGINT, signal
import multiprocessing.dummy as mp
from termcolor import colored
from datetime import datetime
from pathlib import Path
import yaml
import os
import json
import re
import random
import sys
import math
import enum
import pickle

# Try to import psutil to show memory usage
try:
    import psutil
except:
    currentMemUsage = -1
    maxMemoryUsage = -1
    currentMemPercent = -1
    maxMemoryPercent = -1

# Creating stopProgram enum
class StopProgram(enum.Enum):
    SIGINT = 1
    WEBARCHIVE_PROBLEM = 2
    MEMORY_THRESHOLD = 3
stopProgram = None

# Global variables
linksFound = set()
linkMimes = set()
inputValues = set()
argsInput = ''
isInputFile = False
stopProgramCount = 0
stopSource = False
successCount = 0
failureCount = 0
fileCount = 0
totalResponses = 0
totalPages = 0
indexFile = None
continueRespFile = None
inputIsDomainANDPath = False
subs = '*.'
path = ''
waymorePath = ''
terminalWidth = 120
maxMemoryUsage = 0
currentMemUsage = 0
maxMemoryPercent = 0
currentMemPercent = 0
HTTP_ADAPTER = None

# Source Provider URLs
WAYBACK_URL = 'https://web.archive.org/cdx/search/cdx?url={DOMAIN}&collapse={COLLAPSE}&fl=timestamp,original,mimetype,statuscode,digest'
CCRAWL_INDEX_URL = 'https://index.commoncrawl.org/collinfo.json'
ALIENVAULT_URL = 'https://otx.alienvault.com/api/v1/indicators/domain/{DOMAIN}/url_list?limit=500'
URLSCAN_URL = 'https://urlscan.io/api/v1/search/?q=domain:{DOMAIN}&size=10000'

# User Agents to use when making requests, chosen at random
USER_AGENT  = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
]

# The default maximum number of responses to download
DEFAULT_LIMIT = 5000

# The default timeout for archived responses to be retrieved in seconds
DEFAULT_TIMEOUT = 30

# Exclusions used to exclude responses we will try to get from web.archive.org
DEFAULT_FILTER_URL = '.css,.jpg,.jpeg,.png,.svg,.img,.gif,.mp4,.flv,.ogv,.webm,.webp,.mov,.mp3,.m4a,.m4p,.scss,.tif,.tiff,.ttf,.otf,.woff,.woff2,.bmp,.ico,.eot,.htc,.rtf,.swf,.image,/image,/img,/css,/wp-json,/wp-content,/wp-includes,/theme,/audio,/captcha,/font,node_modules,/jquery,/bootstrap'

# MIME Content-Type exclusions used to filter links and responses from web.archive.org through their API
DEFAULT_FILTER_MIME = 'text/css,image/jpeg,image/jpg,image/png,image/svg+xml,image/gif,image/tiff,image/webp,image/bmp,image/vnd,image/x-icon,image/vnd.microsoft.icon,font/ttf,font/woff,font/woff2,font/x-woff2,font/x-woff,font/otf,audio/mpeg,audio/wav,audio/webm,audio/aac,audio/ogg,audio/wav,audio/webm,video/mp4,video/mpeg,video/webm,video/ogg,video/mp2t,video/webm,video/x-msvideo,video/x-flv,application/font-woff,application/font-woff2,application/x-font-woff,application/x-font-woff2,application/vnd.ms-fontobject,application/font-sfnt,application/vnd.android.package-archive,binary/octet-stream,application/octet-stream,application/pdf,application/x-font-ttf,application/x-font-otf,video/webm,video/3gpp,application/font-ttf,audio/mp3,audio/x-wav,image/pjpeg,audio/basic'

# Response code exclusions we will use to filter links and responses from web.archive.org through their API
DEFAULT_FILTER_CODE = '404,301,302'

# Keywords 
DEFAULT_FILTER_KEYWORDS = 'admin,login,logon,signin,register,dashboard,portal,ftp,cpanel,panel,.js,api,robots.txt,graph,gql'

# Yaml config values
FILTER_URL = ''
FILTER_MIME = ''
FILTER_CODE = ''
FILTER_KEYWORDS = ''
URLSCAN_API_KEY = ''
CONTINUE_RESPONSES_IF_PIPED = True

# Define colours
class tc:
    NORMAL = '\x1b[39m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'

# Get memory usage for 
def getMemory():

    global currentMemUsage, currentMemPercent, maxMemoryUsage, maxMemoryPercent, stopProgram

    try:
        currentMemUsage = process.memory_info().rss
        currentMemPercent = math.ceil(psutil.virtual_memory().percent)
        if currentMemUsage > maxMemoryUsage:
            maxMemoryUsage = currentMemUsage
        if currentMemPercent > maxMemoryPercent:
            maxMemoryPercent = currentMemPercent
        if currentMemPercent > args.memory_threshold:
            stopProgram = StopProgram.MEMORY_THRESHOLD
    except:
        pass

# Convert bytes to human readable form
def humanReadableSize(size, decimal_places=2):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size < 1024.0 or unit == "PB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

# Display stats if -v argument was chosen
def processStats():
    if maxMemoryUsage > 0:
        write("MAX MEMORY USAGE: " + humanReadableSize(maxMemoryUsage))
    elif maxMemoryUsage < 0:
        write('MAX MEMORY USAGE: To show memory usage, run "pip install psutil"')
    if maxMemoryPercent > 0:
        write(
            "MAX TOTAL MEMORY: "
            + str(maxMemoryPercent)
            + "% (Threshold "
            + str(args.memory_threshold)
            + "%)"
        )
    elif maxMemoryUsage < 0:
        write('MAX TOTAL MEMORY: To show total memory %, run "pip install psutil"')
    write()
            
def write(text='',pipe=False):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or if the tool has been piped and the pipe parameter is True
    if sys.stdout.isatty() or (not sys.stdout.isatty() and pipe):
        # If it has carriage return in the string, don't add a newline
        if text.find('\r') > 0:
            sys.stdout.write(text)
        else:
            sys.stdout.write(text+'\n')

def writerr(text='',pipe=False):
    # Only send text to stdout if the tool isn't piped to pass output to something else, 
    # or If the tool has been piped to output the send to stderr
    if sys.stdout.isatty():
        # If it has carriage return in the string, don't add a newline
        if text.find('\r') > 0:
            sys.stdout.write(text)
        else:
            sys.stdout.write(text+'\n')
    else:
        # If it has carriage return in the string, don't add a newline
        if text.find('\r') > 0:
            sys.stderr.write(text)
        else:
            sys.stderr.write(text+'\n')
            
def showBanner():
    write()
    write(tc.RED+" _ _ _       _   _ "+tc.NORMAL+"____                    ")
    write(tc.RED+"| | | |_____| | | "+tc.NORMAL+"/    \  ___   ____ _____ ")
    write(tc.RED+"| | | (____ | | | "+tc.NORMAL+"| | | |/ _ \ / ___) ___ |")
    write(tc.RED+"| | | / ___ | |_| "+tc.NORMAL+"| | | | |_| | |   | |_| |")
    write(tc.RED+" \___/\_____|\__  "+tc.NORMAL+"|_|_|_|\___/| |   | ____/")
    write(tc.RED+"            (____/ "+tc.MAGENTA+"  by Xnl-h4ck3r "+tc.NORMAL+" \_____)")
    write()

def verbose():
    """
    Functions used when printing messages dependant on verbose option
    """
    return args.verbose

def handler(signal_received, frame):
    """
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    """
    global stopSource, stopProgram, stopProgramCount

    if stopProgram is not None:
        stopProgramCount = stopProgramCount + 1
        if stopProgramCount == 1:
            writerr(colored(getSPACER(">>> Please be patient... Trying to save data and end gracefully!"),'red'))
        elif stopProgramCount == 2:
            writerr(colored(getSPACER(">>> SERIOUSLY... YOU DON'T WANT YOUR DATA SAVED?!"), 'red'))
        elif stopProgramCount == 3:
            writerr(colored(getSPACER(">>> Patience isn't your strong suit eh? ¯\_(ツ)_/¯"), 'red'))
            sys.exit()
    else:
        stopProgram = StopProgram.SIGINT
        stopSource = True
        writerr(colored(getSPACER('>>> "Oh my God, they killed Kenny... and waymore!" - Kyle'), "red"))
        writerr(colored(getSPACER('>>> Attempting to rescue any data gathered so far...'), "red"))

def showOptions():
    """
    Show the chosen options and config settings
    """
    global inputIsDomainANDPath, argsInput, isInputFile
                
    try:
        write(colored('Selected config and settings:', 'cyan'))
        
        if isInputFile:
            inputArgDesc = '-i <FILE: current line>: '
        else:
            inputArgDesc = '-i: '
        if inputIsDomainANDPath:
            write(colored(inputArgDesc + argsInput, 'magenta')+colored(' The target URL to download responses for.','white'))
        else: # input is a domain
            write(colored(inputArgDesc + argsInput, 'magenta')+colored(' The target domain to find links for.','white'))
        
        if args.mode == 'U':
            write(colored('-mode: ' + args.mode, 'magenta')+colored(' Only URLs will be retrieved for the input.','white'))
        elif args.mode == 'R':
            write(colored('-mode: ' + args.mode, 'magenta')+colored(' Only Responses will be downloaded for the input.','white'))
        elif args.mode == 'B':
            write(colored('-mode: ' + args.mode, 'magenta')+colored(' URLs will be retrieved AND Responses will be downloaded for the input.','white'))

        if args.config is not None:
            write(colored('-c: ' + args.config, 'magenta')+colored(' The path of the config.yml file.','white'))
            
        if not inputIsDomainANDPath:
            if args.no_subs:
                write(colored('-n: ' +str(args.no_subs), 'magenta')+colored(' Sub domains are excluded in the search.','white'))
            else:
                write(colored('-n: ' +str(args.no_subs), 'magenta')+colored(' Sub domains are included in the search.','white'))
            
            write(colored('-xwm: ' +str(args.xwm), 'magenta')+colored(' Whether to exclude checks for links from Wayback Machine (archive.org)','white'))    
            write(colored('-xcc: ' +str(args.xcc), 'magenta')+colored(' Whether to exclude checks for links from commoncrawl.org','white'))
            if not args.xcc:
                if args.lcc == 0:
                    write(colored('-lcc: ' +str(args.lcc), 'magenta')+colored(' Search ALL Common Crawl index collections.','white'))
                else:
                    write(colored('-lcc: ' +str(args.lcc), 'magenta')+colored(' The number of latest Common Crawl index collections to be searched.','white'))
            write(colored('-xav: ' +str(args.xav), 'magenta')+colored(' Whether to exclude checks for links from alienvault.com','white'))
            write(colored('-xus: ' +str(args.xus), 'magenta')+colored(' Whether to exclude checks for links from urlscan.io','white'))
            if URLSCAN_API_KEY == '':
                write(colored('URLScan API Key:', 'magenta')+colored(' {none} - You can get a FREE or paid API Key at https://urlscan.io/user/signup which will let you get more bac, and quicker.','white'))
            else:
                write(colored('URLScan API Key: ', 'magenta')+colored(URLSCAN_API_KEY))
        
        if args.mode in ['U','B']:
            write(colored('-ow: ' +str(args.output_overwrite), 'magenta')+colored(' Whether the URL output file (waymore.txt) will be overwritten if it already exists. If False (default), it will be appended to, and duplicates removed.','white'))
            write(colored('-nlf: ' +str(args.new_links_file), 'magenta')+colored(' Whether the URL output file waymore.new will also be written. It will include only new links found for the same target on subsequent runs. This can be used for continuous monitoring of a target.','white'))
            
        if args.mode in ['R','B']:
            if args.limit == 0:
                write(colored('-l: ' +str(args.limit), 'magenta')+colored(' Save ALL responses found.','white'))
            else:
                if args.limit > 0:
                    write(colored('-l: ' +str(args.limit), 'magenta')+colored(' Only save the FIRST ' + str(args.limit) + ' responses found.','white'))
                else:
                    write(colored('-l: ' +str(args.limit), 'magenta')+colored(' Only save the LAST ' + str(abs(args.limit)) + ' responses found.','white'))
                    
            if args.from_date is not None:
                write(colored('-from: ' +str(args.from_date), 'magenta')+colored(' The date/time to get responses from.','white'))
            if args.to_date is not None:
                write(colored('-to: ' +str(args.to_date), 'magenta')+colored(' The date/time to get responses up to.','white'))
            
            if args.capture_interval == 'h': 
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' Get at most 1 archived response per hour from archive.org','white'))
            elif args.capture_interval == 'd':
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' Get at most 1 archived response per day from archive.org','white'))
            elif args.capture_interval == 'm':
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' Get at most 1 archived response per month from archive.org','white'))
            elif args.capture_interval == 'none':
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' There will not be any filtering based on the capture interval.','white'))
                    
            if args.url_filename:
                write(colored('-url-filename: ' +str(args.url_filename), 'magenta')+colored(' The filenames of downloaded responses wil be set to the URL rather than the hash value of the response.','white'))

        write(colored('-f: ' +str(args.filter_responses_only), 'magenta')+colored(' If True, the initial links from wayback machine will not be filtered, only the responses that are downloaded will be filtered. It maybe useful to still see all available paths even if you don\'t want to check the file for content.','white'))
        write(colored('-ko: ' +str(args.keywords_only), 'magenta')+colored(' If True, we will only get results that contain the given keywords.','white'))
        write(colored('-lr: ' +str(args.limit_requests), 'magenta')+colored(' The limit of requests made per source when getting links. A value of 0 (Zero) means no limit is applied.','white'))
        write(colored('MIME Type exclusions: ', 'magenta')+colored(FILTER_MIME))
        write(colored('Response Code exclusions: ', 'magenta')+colored(FILTER_CODE))      
        write(colored('Response URL exclusions: ', 'magenta')+colored(FILTER_URL))  
        if args.keywords_only:
            if FILTER_KEYWORDS == '':
                write(colored('Keywords only: ', 'magenta')+colored('It looks like no keywords have been set in config.yml file.','red'))
            else: 
                write(colored('Keywords only: ', 'magenta')+colored(FILTER_KEYWORDS))
                
        if args.regex_after is not None:
            write(colored('-ra: ' + args.regex_after, 'magenta')+colored(' RegEx for filtering purposes against found links from archive.org AND responses downloaded. Only positive matches will be output.','white'))
        if args.mode in ['R','B']:
            write(colored('-t: ' + str(args.timeout), 'magenta')+colored(' The number of seconds to wait for a an archived response.','white'))
        if args.mode in ['R','B'] or (args.mode == 'U' and not args.xcc):
            write(colored('-p: ' + str(args.processes), 'magenta')+colored(' The number of parallel requests made.','white'))
        write(colored('-r: ' + str(args.retries), 'magenta')+colored(' The number of retries for requests that get connection error or rate limited.','white'))
        
        write()

    except Exception as e:
        writerr(colored('ERROR showOptions: ' + str(e), 'red'))

def getConfig():
    """
    Try to get the values from the config file, otherwise use the defaults
    """
    global FILTER_CODE, FILTER_MIME, FILTER_URL, FILTER_KEYWORDS, URLSCAN_API_KEY, CONTINUE_RESPONSES_IF_PIPED, subs, path, waymorePath, inputIsDomainANDPath, HTTP_ADAPTER, argsInput, terminalWidth
    try:
        
        # Set terminal width
        try:
            terminalWidth = os.get_terminal_size().columns
        except:
            terminalWidth = 120
        
        # If the input doesn't have a / then assume it is a domain rather than a domain AND path
        if str(argsInput).find('/') < 0:
            path = '/*'
            inputIsDomainANDPath = False
        else:
            # If the input is a URL then -mode will have to be R (Responses only)
            inputIsDomainANDPath = True
            args.mode = 'R'
            
        # If the -no-subs argument was passed, OR the input is a path, don't include subs
        if args.no_subs or inputIsDomainANDPath:
            subs = ''
        
        # Set up an HTTPAdaptor for retry strategy when making requests
        try:
            retry= Retry(
                total=args.retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                raise_on_status=False,
                respect_retry_after_header=False
            )
            HTTP_ADAPTER = HTTPAdapter(max_retries=retry)
        except Exception as e:
            writerr(colored('ERROR getConfig 2: ' + str(e), 'red'))
            
        # Try to get the config file values
        try:
            # Get the path of the config file. If -c / --config argument is not passed, then it defaults to config.yml in the same directory as the run file
            if args.config is None:        
                waymorePath = Path(
                    os.path.dirname(os.path.realpath(__file__))
                )
                waymorePath.absolute
                if waymorePath == '':
                    configPath = 'config.yml'
                else:
                    configPath = Path(waymorePath / 'config.yml')
            else:
                try:
                    waymorePath = args.config
                    configPath = Path(waymorePath)
                except Exception as e:
                    print(str(e))
            config = yaml.safe_load(open(configPath))
            try:
                FILTER_URL = config.get('FILTER_URL')
                if str(FILTER_URL) == 'None':
                    writerr(colored('No value for "FILTER_URL" in config.yml - default set', 'yellow'))
                    FILTER_URL = ''
            except Exception as e:
                writerr(colored('Unable to read "FILTER_URL" from config.yml - default set', 'red'))
                FILTER_URL = DEFAULT_FILTER_URL

            try:
                FILTER_MIME = config.get('FILTER_MIME')
                if str(FILTER_MIME) == 'None':
                    writerr(colored('No value for "FILTER_MIME" in config.yml - default set', 'yellow'))
                    FILTER_MIME = ''
            except Exception as e:
                writerr(colored('Unable to read "FILTER_MIME" from config.yml - default set', 'red'))
                FILTER_MIME = DEFAULT_FILTER_MIME
            
            try:
                FILTER_CODE = config.get('FILTER_CODE')
                if str(FILTER_CODE) == 'None':
                    writerr(colored('No value for "FILTER_CODE" in config.yml - default set', 'yellow'))
                    FILTER_CODE = ''
            except Exception as e:
                writerr(colored('Unable to read "FILTER_CODE" from config.yml - default set', 'red'))
                FILTER_CODE = DEFAULT_FILTER_CODE
                
            try:
                URLSCAN_API_KEY = config.get('URLSCAN_API_KEY')
                if str(URLSCAN_API_KEY) == 'None':
                    writerr(colored('No value for "URLSCAN_API_KEY" in config.yml - consider adding (you can get a FREE api key at urlscan.io)', 'yellow'))
                    URLSCAN_API_KEY = ''
            except Exception as e:
                writerr(colored('Unable to read "URLSCAN_API_KEY" from config.yml - consider adding (you can get a FREE api key at urlscan.io)', 'red'))
                URLSCAN_API_KEY = ''
            
            try:
                FILTER_KEYWORDS = config.get('FILTER_KEYWORDS')
                if str(FILTER_KEYWORDS) == 'None':
                    writerr(colored('No value for "FILTER_KEYWORDS" in config.yml - default set', 'yellow'))
                    FILTER_KEYWORDS = ''
            except Exception as e:
                writerr(colored('Unable to read "FILTER_KEYWORDS" from config.yml - default set', 'red'))
                FILTER_KEYWORDS = ''
            
            try:
                CONTINUE_RESPONSES_IF_PIPED = config.get('CONTINUE_RESPONSES_IF_PIPED')
                if str(CONTINUE_RESPONSES_IF_PIPED) == 'None':
                    writerr(colored('No value for "CONTINUE_RESPONSES_IF_PIPED" in config.yml - default set', 'yellow'))
                    CONTINUE_RESPONSES_IF_PIPED = True
            except Exception as e:
                writerr(colored('Unable to read "FILTER_KEYWORDS" from config.yml - default set', 'red'))
                CONTINUE_RESPONSES_IF_PIPED = True
                
        except:
            if args.config is None:
                writerr(colored('WARNING: Cannot find file "config.yml", so using default values', 'yellow'))
            else:
                writerr(colored('WARNING: Cannot find file "' + args.config + '", so using default values', 'yellow'))
            FILTER_URL = DEFAULT_FILTER_URL
            FILTER_MIME = DEFAULT_FILTER_MIME
            FILTER_CODE = DEFAULT_FILTER_CODE
            URLSCAN_API_KEY = ''
            FILTER_KEYWORDS = ''
            CONTINUE_RESPONSES_IF_PIPED = True
            
    except Exception as e:
        writerr(colored('ERROR getConfig 1: ' + str(e), 'red'))

# Print iterations progress - copied from https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters?noredirect=1&lq=1
def printProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    try:
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        ).rjust(5)
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        # If the program is not piped with something else, write to stdout, otherwise write to stderr
        if sys.stdout.isatty():
            write(colored(f"\r{prefix} |{bar}| {percent}% {suffix}\r", "green"))
        else:
            writerr(colored(f"\r{prefix} |{bar}| {percent}% {suffix}\r", "green"))
        # Print New Line on Complete
        if iteration == total:
            # If the program is not piped with something else, write to stdout, otherwise write to stderr
            if sys.stdout.isatty():
                write()
            else: 
                writerr()
    except Exception as e:
        if verbose():
            writerr(colored("ERROR printProgressBar: " + str(e), "red"))

def filehash(text):
    """
    Generate a hash value for the passed string. This is used for the file name of a downloaded archived response
    """
    hash=0
    for ch in text:
        hash = (hash*281 ^ ord(ch)*997) & 0xFFFFFFFFFFF
    return str(hash)    

class WayBackException(Exception):
    """
    A custom exception to raise if archive.org respond with specific text in the response that indicate there is a problem on their side
    """
    def __init__(self):
         message = f"WayBackException"
         super().__init__(message)

def fixArchiveOrgUrl(url):
    """
    Sometimes archive.org returns a URL that has %0A at the end followed by other characters. If you try to reach the archive URL with that it will fail, but remove from the %0A (newline) onwards and it succeeds, so it doesn't seem intentionally included. In this case, strip anything from %0A onwards from the URL
    """
    newline = url.find('%0A')
    if newline > 0:
        url = url[0:newline]
    else:
        newline = url.find('%0a')
        if newline > 0:
            url = url[0:newline]
    return url

# Add a link to the linksFound collection
def linksFoundAdd(link):
    global linksFound
    # If the link specifies port 80 or 443, e.g. http://example.com:80, then remove the port 
    try:
        parsed = urlparse(link.strip())
        if parsed.netloc.find(':80') or parsed.netloc.fnd(':443'):
            newNetloc = parsed.netloc.split(':')[0]
            parsed = parsed._replace(netloc=newNetloc).geturl()
        linksFound.add(parsed)
    except:
        linksFound.add(link)
    
def processArchiveUrl(url):
    """
    Get the passed web archive response
    """
    global stopProgram, successCount, failureCount, fileCount, waymorePath, totalResponses, indexFile, argsInput, continueRespFile
    try:
        if stopProgram is None:
            
            archiveUrl = 'https://web.archive.org/web/' + fixArchiveOrgUrl(url)
            hashValue = ''
        
            # Get memory usage every 100 responses
            if (successCount + failureCount) % 100 == 0:
                try:
                    getMemory()
                except:
                    pass
                
            # Make a request to the web archive
            try:
                try:
                    # Choose a random user agent string to use for any requests
                    userAgent = random.choice(USER_AGENT)

                    session = requests.Session()
                    session.mount('https://', HTTP_ADAPTER)
                    session.mount('http://', HTTP_ADAPTER)
                    resp = session.get(url = archiveUrl, headers={"User-Agent":userAgent}, allow_redirects = False)
                    archiveHtml = str(resp.text)
                    
                    # Only create a file if there is a response
                    if len(archiveHtml) != 0:
                        
                        # Add the URL as a comment at the start of the response
                        if args.url_filename:
                            archiveHtml = '/* Original URL: ' + archiveUrl + ' */\n' + archiveHtml
                        
                        # Remove all web archive references in the response
                        archiveHtml = re.sub(r'\<head\>.*\<\!-- End Wayback Rewrite JS Include --\>','<head>',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                        archiveHtml = re.sub(r'\<script src=\"\/\/archive\.org.*\<\!-- End Wayback Rewrite JS Include --\>','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                        archiveHtml = re.sub(r'\<\!-- BEGIN WAYBACK TOOLBAR INSERT --\>.*\<\!-- END WAYBACK TOOLBAR INSERT --\>','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                        archiveHtml = re.sub(r'FILE ARCHIVED ON.*108\(a\)\(3\)\)\.','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                        archiveHtml = re.sub(r'(\<\!--|\/\*)\nplayback timings.*(--\>|\*\/)','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                        archiveHtml = re.sub(r'((https:)?\/\/web\.archive\.org)?\/web\/[0-9]{14}([A-Za-z]{2}\_)?\/','',archiveHtml,flags=re.IGNORECASE)
                        archiveHtml = re.sub(r'((https:)?\\\/\\\/web\.archive\.org)?\\\/web\\\/[0-9]{14}([A-Za-z]{2}\_)?\\\/','',archiveHtml,flags=re.IGNORECASE)
                        archiveHtml = re.sub(r'((https:)?%2F%2Fweb\.archive\.org)?%2Fweb%2F[0-9]{14}([A-Za-z]{2}\_)?%2F','',archiveHtml,flags=re.IGNORECASE)
                        archiveHtml = re.sub(r'((https:)?\\u002F\\u002Fweb\.archive\.org)?\\u002Fweb\\u002F[0-9]{14}([A-Za-z]{2}\_)?\\u002F','',archiveHtml,flags=re.IGNORECASE)
                       
                        # If there is a specific Wayback error in the response, raise an exception 
                        if archiveHtml.lower().find('wayback machine has not archived that url') > 0 or archiveHtml.lower().find('snapshot cannot be displayed due to an internal error') > 0:
                            raise WayBackException
                        
                        # Create file name based on url or hash value of the response, depending on selection. Ensure the file name isn't over 255 characters 
                        if args.url_filename:
                            fileName = url.replace('/','-').replace(':','')
                            fileName = fileName[0:254]
                        else:
                            hashValue = filehash(archiveHtml)
                            fileName = hashValue
                            
                            # Determine extension of file from the file name
                            extension = ''
                            try:
                                path = url[url.rindex(argsInput)+len(argsInput):]
                                if path.find('?') > 0:
                                    path = path[:path.index('?')]
                                extension = path[path.rindex('.')+1:]
                            except:
                                pass
                            # If the extension is blank, numeric, longer than 6 characters or not alphanumeric - then it's not a valid file type so set to default of xnl
                            if extension == '' or extension.isnumeric() or len(extension) > 6 or not extension.isalnum():
                                extension = 'xnl'
                            fileName = fileName + '.' + extension
                        
                        filePath = (
                                waymorePath
                                / 'results'
                                / str(argsInput).replace('/','-')
                                / f'{fileName}'
                        )

                        # Write the file
                        try:
                            responseFile = open(filePath, 'w', encoding='utf8')
                            responseFile.write(archiveHtml)
                            responseFile.close()
                            fileCount = fileCount + 1
                        except Exception as e:
                            writerr(colored(getSPACER('[ ERR ] Failed to write file ' + filePath + ': '+ str(e)), 'red'))
                            
                        # Write the hash value and URL to the index file
                        if not args.url_filename:
                            try:
                                timestamp = str(datetime.now())
                                indexFile.write(hashValue+','+archiveUrl+' ,'+timestamp+'\n')
                                indexFile.flush()
                            except Exception as e:
                                writerr(colored(getSPACER('[ ERR ] Failed to write to index.txt for "' + archiveUrl + '": '+ str(e)), 'red'))

                        # FOR DEBUGGING PURPOSES
                        try:
                            if archiveHtml.find('archive.org') > 0 and os.environ.get('USER') == 'xnl':
                                writerr(colored(getSPACER('"' + fileName + '" CONTAINS ARCHIVE.ORG - CHECK ITS A VALID REFERENCE'), 'yellow'))
                        except:
                            pass
                            
                    successCount = successCount + 1
                
                except WayBackException as wbe:
                    failureCount = failureCount + 1
                    if verbose():
                        writerr(colored(getSPACER('[ ERR ] archive.org returned a problem for "' + archiveUrl + '"'), 'red'))
                except ConnectionError as ce:
                    failureCount = failureCount + 1
                    if verbose():
                        writerr(colored(getSPACER('[ ERR ] archive.org connection error for "' + archiveUrl + '"'), 'red'))
                except Exception as e:
                    failureCount = failureCount + 1
                    if verbose():
                        try:
                            writerr(colored(getSPACER('[ ' + str(resp.status_code) +' ] Failed to get response for "' + archiveUrl + '"'), 'red'))
                        except:
                            writerr(colored(getSPACER('[ ERR ] Failed to get response for "' + archiveUrl + '": '+ str(e)), 'red'))
                
                # Show progress bar
                fillTest = (successCount + failureCount) % 2
                fillChar = "o"
                if fillTest == 0:
                    fillChar = "O"
                suffix="Complete "
                # Show memory usage if -v option chosen, and check memory every 25 responses (or if its the last)
                if (successCount + failureCount) % 25 == 1 or (successCount + failureCount) == totalResponses:
                    try:
                        getMemory()
                        if verbose():
                            suffix = (
                                "Complete (Mem Usage "
                                + humanReadableSize(currentMemUsage)
                                + ", Total Mem "
                                + str(currentMemPercent)
                                + "%)   "
                            )
                    except:
                        if verbose():
                            suffix = 'Complete (To show mem use, run "pip install psutil")'
                printProgressBar(
                    successCount + failureCount,
                    totalResponses,
                    prefix="Downloading " + str(totalResponses) + " responses:",
                    suffix=suffix,
                    length=getProgressBarLength(),
                    fill=fillChar
                )
                
                # Write the total count to the continueResp.tmp file
                try:
                    continueRespFile.seek(0)
                    continueRespFile.write(str(successCount + failureCount)+'\n')
                except Exception as e:
                    if verbose():
                        writerr(colored(getSPACER('ERROR processArchiveUrl 2:  ' + str(e)), 'red'))
                
            except Exception as e:
                if verbose():
                    writerr(colored(getSPACER('Error for "'+url+'": ' + str(e)), 'red'))
            
    except Exception as e:
        writerr(colored('ERROR processArchiveUrl 1:  ' + str(e), 'red'))

def processURLOutput():
    """
    Show results of the URL output, i.e. getting URLs from archive.org and commoncrawl.org and write results to file
    """
    global linksFound, subs, path, argsInput

    try:
            
        linkCount = len(linksFound)
        write(getSPACER(colored('Links found for ' + subs + argsInput + ': ', 'cyan')+colored(str(linkCount) + ' 🤘','white'))+'\n')
        
        # Create 'results' and domain directory if needed
        createDirs()
        
        fullPath = str(waymorePath) + '/results/' + str(argsInput).replace('/','-') + '/'
                
        # If the -ow / --output_overwrite argument was passed and the file exists already, get the contents of the file to include
        appendedUrls = False
        if not args.output_overwrite:
            try:
                existingLinks = open(fullPath + 'waymore.txt','r',)
                for link in existingLinks.readlines():
                    linksFound.add(link.strip())
                appendedUrls = True
            except Exception as e:
                pass
        
        # If the -nlf / --new-links-file argument is passes, rename the old waymore.txt file if it exists
        try:
            if args.new_links_file: 
                if os.path.exists(fullPath + 'waymore.txt'):
                    os.rename(fullPath + 'waymore.txt', fullPath + 'waymore.old')    
        except Exception as e:
            if verbose():
                writerr(colored('ERROR processURLOutput 5: ' + str(e), 'red'))
                    
        try:
            # Open the output file
            outFile = open(fullPath + 'waymore.txt','w')
        except Exception as e:
            if verbose():
                writerr(colored('ERROR processURLOutput 2: ' + str(e), 'red'))
                sys.exit()

        # Go through all links, and output what was found
        # If the -ra --regex-after was passed then only output if it matches
        outputCount = 0
        for link in linksFound:
            try:
                if args.regex_after is None or re.search(args.regex_after, link, flags=re.IGNORECASE):
                    # Don't write it if the link does not contain the requested domain (this can sometimes happen)
                    if link.find(argsInput) >= 0:
                        outFile.write(link + "\n")
                        # If the tool is piped to pass output to something else, then write the link
                        if not sys.stdout.isatty():
                            write(link,True)
                        outputCount = outputCount + 1
            except Exception as e:
                if verbose():
                    writerr(colored('ERROR processURLOutput 3: ' + str(e), 'red'))

        # If there are less links output because of filters, show the new total
        if args.regex_after is not None and linkCount > 0 and outputCount < linkCount:
            write(colored('Links found after applying filter "' + args.regex_after + '": ','cyan')+colored(str(outputCount) + ' 🤘\n','white'))
        
        # Close the output file
        try:
            outFile.close()
        except Exception as e:
            if verbose():
                writerr(colored('ERROR processURLOutput 4: ' + str(e), 'red'))

        if verbose():
            if outputCount == 0:
                write(colored('No links were found so nothing written to file.\n', 'cyan'))
            else:   
                if appendedUrls:
                    write(
                        colored('Links successfully appended to file ', 'cyan')+colored(fullPath + 'waymore.txt',
                        'white')+colored(' and duplicates removed.\n','cyan'))
                else:
                    write(
                        colored('Links successfully written to file ', 'cyan')+colored(fullPath + 'waymore.txt\n',
                        'white'))

        try:
            # If the -nlf / --new-links-file argument is passes, create the waymore.new file
            if args.new_links_file:
                
                # If waymore.old and waymore.txt exists then get the difference to write to waymore.new
                if os.path.exists(fullPath + 'waymore.old') and os.path.exists(fullPath + 'waymore.txt'):
                    
                    # Get all the old links
                    with open(fullPath + 'waymore.old','r') as oldFile:
                        oldLinks=set(oldFile.readlines())

                    # Get all the new links
                    with open(fullPath + 'waymore.txt','r') as newFile:
                        newLinks=set(newFile.readlines())

                    # Create a file with most recent new links
                    with open(fullPath + 'waymore.new','w') as newOnly:
                        for line in list(newLinks-oldLinks):
                            newOnly.write(line)

                    # Delete the old file
                    os.remove(fullPath + 'waymore.old')
                
        except Exception as e:
            if verbose():
                writerr(colored("ERROR processURLOutput 6: " + str(e), "red"))
                
    except Exception as e:
        if verbose():
            writerr(colored("ERROR processURLOutput 1: " + str(e), "red"))

def processResponsesOutput():
    """
    Show results of the archive responses saved
    """
    global successCount, failureCount, subs, fileCount, argsInput
    try:
        if failureCount > 0:
            write(colored('\nResponses saved for ' + subs + argsInput + ': ', 'cyan')+colored(str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘','white')+colored(' (' + str(failureCount) + ' failed)\n','red'))
        else:
            write(colored('\nResponses saved for ' + subs + argsInput + ': ', 'cyan')+colored(str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘\n','white'))
    except Exception as e:
        if verbose():
            writerr(colored("ERROR processResponsesOutput 1: " + str(e), "red"))    

def validateArgProcesses(x):
    """
    Validate the -p / --processes argument 
    Only allow values between 1 and 5 inclusive
    """
    x = int(x) 
    if x < 1 or x > 5:
        raise argparse.ArgumentTypeError('The number of processes must be between 1 and 5. Be kind to archive.org and commoncrawl.org! :)')     
    return x

def validateArgInput(x):
    """
    Validate the -i / --input argument.
    Ensure it is a domain only, or a URL, but with no schema or query parameters or fragment
    """
    global inputValues, isInputFile
    
    # If the input was given through STDIN (piped from another program) then 
    if x == '<stdin>':
        stdinFile = sys.stdin.readlines()
        count = 1
        for line in stdinFile:
            # Remove newline characters, and also *. if the domain starts with this
            inputValues.add(line.rstrip('\n').lstrip('*.'))
            count = count + 1
        if count > 1:
            isInputFile = True
    else:
        # Determine if a single input was given, or a file
        if os.path.isfile(x):
            isInputFile = True
            # Open file and put all values in input list
            inputFile = open(x, 'r')
            lines = inputFile.readlines()          
            # Check if any lines start with a *. and replace without the *.
            for line in lines:
                inputValues.add(line.lstrip('*.'))
        else:
            # Just add the input value to the input list
            inputValues.add(x)
    
    for i in inputValues:        
        if isInputFile:
            # Check if input seems to be valid domain or URL
            match = re.search(r"^((?!-))(xn--)?([a-z0-9][a-z0-9\-\_]{0,61}[a-z0-9]{0,1}\.)+(xn--)?([a-z0-9\-]{1,61}|[a-z0-9\-]{1,30}\.[a-z]{2,})(/[^\n|?#]*)?$", i.strip().rstrip('\n'))
            if match is None:
                error = 'Each line of the input file must contain a domain only (with no schema) to search for all links, or a domain and path (with no schema) to just get archived response for that URL. Do not pass a query string or fragment in any lines.'
                if x == '<stdin>':
                    writerr(colored(error,'red'))
                    sys.exit()
                else:
                    raise argparse.ArgumentTypeError(error)
        else:
            # Check if input seems to be valid domain or URL
            match = re.search(r"^((?!-))(xn--)?([a-z0-9][a-z0-9\-\_]{0,61}[a-z0-9]{0,1}\.)+(xn--)?([a-z0-9\-]{1,61}|[a-z0-9\-]{1,30}\.[a-z]{2,})(/[^\n|?#]*)?$", i.strip().rstrip('\n'))
            if match is None:
                error = 'Pass a domain only (with no schema) to search for all links, or pass a domain and path (with no schema) to just get archived responses for that URL. Do not pass a query string or fragment.'
                if x == '<stdin>':
                    writerr(colored(error,'red'))
                    sys.exit()
                else:
                    raise argparse.ArgumentTypeError(error)
    return x

def processAlienVaultPage(url):
    """
    Get URLs from a specific page of otx.alienvault.org API for the input domain
    """
    global totalPages, linkMimes, linksFound, stopSource, argsInput
    try:
        # Get memory in case it exceeds threshold
        getMemory()
        
        if not stopSource:
            try:             
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                page = url.split('page=')[1]
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER)
                session.mount('http://', HTTP_ADAPTER)
                resp = session.get(url, headers={"User-Agent":userAgent})  
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] alienvault.org connection error for page ' + page), 'red'))
                resp = None
                return
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Error getting response for page ' + page + ' - ' + str(e)),'red'))
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                        # If a status other of 429, then stop processing Alien Vault
                        if resp.status_code == 429:
                            writerr(colored(getSPACER('[ 429 ] Alien Vault rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                            stopSource = True
                            return
                        # If the response from alienvault.com is empty then skip
                        if resp.text == '' and totalPages == 0:
                            if verbose():
                                writerr(colored(getSPACER('[ ERR ] '+url+' gave an empty response.'),'red'))
                            return
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose():
                                writerr(colored(getSPACER('[ '+str(resp.status_code)+' ] Error for '+url),'red'))
                            return
                except:
                    pass
            
            # Get the JSON response
            jsonResp = json.loads(resp.text.strip())

            # Go through each URL in the list
            for urlSection in jsonResp['url_list']:
                # Get the URL
                try:
                    foundUrl = urlSection['url']
                except:
                    foundUrl = ''

                # If a URL was found
                if foundUrl != '':    
                    # If filters are not required and subs are wanted then just add the URL to the list
                    if args.filter_responses_only and not args.no_subs:
                        linksFoundAdd(foundUrl)
                    else:
                        addLink = True
                        
                        # If the user requested -n / --no-subs then we don't want to add it if it has a sub domain (www. will not be classed as a sub domain)
                        if args.no_subs:
                            match = re.search(r'\:\/\/(www\.)?'+re.escape(argsInput), foundUrl, flags=re.IGNORECASE)
                            if match is None:
                                addLink = False
                        
                        # If the user didn't requested -f / --filter-responses-only then check http code
                        # Note we can't check MIME filter because it is not returned by Alien Vault API
                        if addLink and not args.filter_responses_only: 
                            # Get the HTTP code
                            try:
                                httpCode = str(urlSection['httpcode'])
                            except:
                                httpCode = ''
                            
                            # If we have a HTTP Code, compare against the Code exclusions
                            if httpCode != '':
                                match = re.search(r'('+re.escape(FILTER_CODE).replace(',','|')+')', httpCode, flags=re.IGNORECASE)
                                if match is not None:
                                    addLink = False
                            
                            # Check the URL exclusions
                            if addLink:
                                match = re.search(r'('+re.escape(FILTER_URL).replace(',','|')+')', foundUrl, flags=re.IGNORECASE)
                                if match is not None:
                                    addLink = False            
                            
                            # Set keywords filter if -ko argument passed
                            if addLink and args.keywords_only:
                                match = re.search(r'('+re.escape(FILTER_KEYWORDS).replace(',','|')+')', foundUrl, flags=re.IGNORECASE)
                                if match is None:
                                    addLink = False
                
                        # Add link if it passed filters        
                        if addLink:
                            linksFoundAdd(foundUrl)
        else:
            pass                    
    except Exception as e:
        if verbose():
            writerr(colored("ERROR processLAlienVaultPage 1: " + str(e), "red"))
    
def getAlienVaultUrls():
    """
    Get URLs from the Alien Vault OTX, otx.alienvault.com
    """
    global linksFound, waymorePath, subs, path, stopProgram, totalPages, stopSource, argsInput
    
    # Write the file of URL's for the passed domain/URL
    try:
        stopSource = False
        originalLinkCount = len(linksFound)
        
        url = ALIENVAULT_URL.replace('{DOMAIN}',quote(argsInput))+'&page='
        
        # Get the number of pages (i.e. separate requests) that are going to be made to alienvault.com
        totalPages = 0
        try:
            write(colored('\rGetting the number of alienvault.com pages to search...\r','cyan'))
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
            resp = session.get(url+'&showNumPages=True', headers={"User-Agent":userAgent}) 
        except Exception as e:
            writerr(colored(getSPACER('[ ERR ] unable to get links from alienvault.com: ' + str(e)), 'red'))
            return
        
        # If the rate limit was reached end now
        if resp.status_code == 429:
            writerr(colored(getSPACER('[ 429 ] Alien Vault rate limit reached so unable to get links.'),'red'))
            return
        
        if verbose():
            write(getSPACER(colored('The Alien Vault URL requested to get links: ','magenta')+colored(url,'white'))+'\n')
        
        # Carry on if something was found
        if resp.text.lower().find('"error": "') < 0:

            # Get the JSON response
            jsonResp = json.loads(resp.text.strip())
            
            # Try to get the number of results
            totalUrls = jsonResp['full_size']
            
            # If there are results, carry on
            if  totalUrls > 0:
                
                # Get total pages 
                totalPages = math.ceil(totalUrls / 500)
                
                # If the argument to limit the requests was passed and the total pages is larger than that, set to the limit
                if args.limit_requests != 0 and totalPages > args.limit_requests:
                    totalPages = args.limit_requests

                # if the page number was found then display it, but otherwise we will just try to increment until we have everything       
                write(colored('\rGetting links from ' + str(totalPages) + ' alienvault.com API requests (this can take a while for some domains)...\r','cyan'))

                # Get a list of all the page URLs we need to visit
                pages = set()
                for page in range(1, totalPages + 1):
                    pages.add(url+str(page))

                # Process the URLs from alien vault 
                if stopProgram is None:
                    p = mp.Pool(args.processes)
                    p.map(processAlienVaultPage, pages)
                    p.close()
                    p.join()
        else:
            if verbose():
                writerr(colored(getSPACER('[ ERR ] An error was returned in the alienvault.com response.')+'\n', 'red'))
                
        linkCount = len(linksFound) - originalLinkCount
        write(getSPACER(colored('Extra links found on alienvault.com: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
        
    except Exception as e:
        writerr(colored('ERROR getAlienVaultUrls 1: ' + str(e), 'red'))

def processURLScanUrl(url, httpCode, mimeType):
    """
    Process a specific URL from urlscan.io to determine whether to save the link
    """
    global argsInput
    
    addLink = True
    
    try:      
        # If filters are required then test them
        if not args.filter_responses_only:
            
            # If the user requested -n / --no-subs then we don't want to add it if it has a sub domain (www. will not be classed as a sub domain)
            if args.no_subs:
                match = re.search(r'^[A-za-z]*\:\/\/(www\.)?'+re.escape(argsInput), url, flags=re.IGNORECASE)
                if match is None:
                    addLink = False
        
            # If the user didn't requested -f / --filter-responses-only then check http code
            # Note we can't check MIME filter because it is not returned by URLScan API
            if addLink and not args.filter_responses_only: 
                
                # If we have a HTTP Code, compare against the Code exclusions
                if httpCode != '':
                    match = re.search(r'('+re.escape(FILTER_CODE).replace(',','|')+')', httpCode, flags=re.IGNORECASE)
                    if match is not None:
                        addLink = False
                
                # Check the URL exclusions
                if addLink:
                    match = re.search(r'('+re.escape(FILTER_URL).replace(',','|')+')', url, flags=re.IGNORECASE)
                    if match is not None:
                        addLink = False            
                
                # Set keywords filter if -ko argument passed
                if addLink and args.keywords_only:
                    match = re.search(r'('+re.escape(FILTER_KEYWORDS).replace(',','|')+')', url, flags=re.IGNORECASE)
                    if match is None:
                        addLink = False
                                    
                # Check the MIME exclusions
                if mimeType != '':
                    match = re.search(r'('+re.escape(FILTER_MIME).replace(',','|')+')', mimeType, flags=re.IGNORECASE)
                    if match is not None:
                        addLink = False
                    else:
                        # Add MIME Types if --verbose option was selected
                        if verbose():
                            linkMimes.add(mimeType)            
                    
        # Add link if it passed filters        
        if addLink:
            # Just get the domain of the url found by removing anything after ? and then from 3rd / 
            domainOnly = url.split('?',1)[0]
            domainOnly = '/'.join(domainOnly.split('/',3)[:3])

            # URLScan can return URLs that aren't for the domain passed so we need to check for those and not process them
            # Check the URL
            match = re.search(r'^[A-za-z]*\:\/.*(\/|\.)'+re.escape(argsInput)+'$', domainOnly, flags=re.IGNORECASE)
            if match is not None:
                linksFoundAdd(url)  
            
    except Exception as e:
        writerr(colored('ERROR processURLScanUrl 1: ' + str(e), 'red'))
        
def getURLScanUrls():
    """
    Get URLs from the URLSCan API, urlscan.io
    """
    global URLSCAN_API_KEY, linksFound, linkMimes, waymorePath, subs, stopProgram, stopSource, argsInput
    
    # Write the file of URL's for the passed domain/URL
    try:
        requestsMade = 0
        stopSource = False
        linkMimes = set()
        originalLinkCount = len(linksFound)
        
        url = URLSCAN_URL.replace('{DOMAIN}',quote(argsInput))
        
        if verbose():
            write(colored('The URLScan URL requested to get links: ','magenta')+colored(url+'\n','white'))
                   
        write(colored('\rGetting links from urlscan.io API (this can take a while for some domains)...\r','cyan'))
       
        # Get the first page from urlscan.io
        try:
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
             # Pass the API-Key header too. This can change the max endpoints per page, depending on URLScan subscription
            resp = session.get(url, headers={'User-Agent':userAgent, 'API-Key':URLSCAN_API_KEY})
            requestsMade = requestsMade + 1
        except Exception as e:
            write(colored(getSPACER('[ ERR ] unable to get links from urlscan.io: ' + str(e)), 'red'))
            return
        
        # If the rate limit was reached or if a 401 (which likely means the API key isn't valid), try without API key
        if resp.status_code in (401,429): 
            if URLSCAN_API_KEY != '':
                try:
                    if resp.status_code == 429:
                        writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached so trying without API Key...'),'red'))
                    else:
                        writerr(colored(getSPACER('The URLScan API Key is invalid so trying without API Key...'),'red'))
                    # Set key to blank for further requests
                    URLSCAN_API_KEY = ''
                    resp = requests.get(url, headers={'User-Agent':userAgent}) 
                except Exception as e:
                    writerr(colored(getSPACER('[ ERR ] unable to get links from urlscan.io: ' + str(e)), 'red'))
                    return
                
                # If the rate limit was reached end now
                if resp.status_code == 429:
                    writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached without API Key so unable to get links.'),'red'))
                    return
            else:
                writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached so unable to get links.'),'red'))
                return
        elif resp.status_code != 200:
            writerr(colored(getSPACER('[ ' + str(resp.status_code) + ' ] unable to get links from urlscan.io'),'red'))
            return
        
        # Get the JSON response
        jsonResp = json.loads(resp.text.strip())
  
        # Get the number of results
        totalUrls = jsonResp['total']
        
        # Carry on if something was found
        if int(totalUrls) > 0:
            
            while not stopSource:
                
                searchAfter = ''
                
                # Get memory in case it exceeds threshold
                getMemory()
        
                # Go through each URL in the list
                for urlSection in jsonResp['results']:
                    
                    # Get the URL
                    try:
                        foundUrl = urlSection['page']['url']
                    except:
                        foundUrl = ''
                    
                    # Also get the "ptr" field which can also be a url we want
                    try:
                        pointer = urlSection['page']['ptr']
                        if not pointer.startswith('http'):
                            pointer = 'http://' + pointer
                    except:
                        pointer = ''

                    # Get the sort value used for the search_after parameter to get to the next page later
                    try:
                        sort = urlSection['sort']
                    except:
                        sort = ''
                    searchAfter = '&search_after='+str(sort[0])+','+str(sort[1])
                    
                    # Get the HTTP code
                    try:
                        httpCode = str(urlSection['page']['status'])
                    except:
                        httpCode = ''
                    
                    # Get the MIME type
                    try:
                        mimeType = urlSection['page']['mimeType']
                    except:
                        mimeType = ''
                    
                    # If a URL was found the process it
                    if foundUrl != '':    
                        processURLScanUrl(foundUrl, httpCode, mimeType)
                    
                    # If a pointer was found the process it
                    if pointer != '':    
                        processURLScanUrl(pointer, httpCode, mimeType)
                
                # If we have the field value to go to the next page...
                if searchAfter != '':
                
                    # Get the next page from urlscan.io
                    try:
                        # Choose a random user agent string to use for any requests
                        userAgent = random.choice(USER_AGENT)
                        session = requests.Session()
                        session.mount('https://', HTTP_ADAPTER)
                        session.mount('http://', HTTP_ADAPTER)
                        # Pass the API-Key header too. This can change the max endpoints per page, depending on URLScan subscription
                        resp = session.get(url+searchAfter, headers={'User-Agent':userAgent, 'API-Key':URLSCAN_API_KEY}) 
                        requestsMade = requestsMade + 1
                    except Exception as e:
                        writerr(colored(getSPACER('[ ERR ] unable to get links from urlscan.io: ' + str(e)), 'red'))
                        pass
                    
                    # If the rate limit was reached end now
                    if resp.status_code == 429:
                        writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                        stopSource = True
                        pass
                    elif resp.status_code != 200:
                        writerr(colored(getSPACER('[ ' + str(resp.status_code) + ' ] unable to get links from urlscan.io'),'red'))
                        stopSource = True
                        pass

                    if not stopSource:
                        # Get the JSON response
                        jsonResp = json.loads(resp.text.strip())
                        
                        # If there are no more results, or if the requests limit was specified and has been exceeded, then stop
                        if len(jsonResp['results']) == 0 or (args.limit_requests != 0 and requestsMade > args.limit_requests):
                            stopSource = True
        
        # Show the MIME types found (in case user wants to exclude more)
        if verbose() and len(linkMimes) > 0:
            linkMimes.discard('warc/revisit')
            write(getSPACER(colored('MIME types found: ','magenta')+colored(str(linkMimes),'white'))+'\n')
                    
        linkCount = len(linksFound) - originalLinkCount
        write(getSPACER(colored('Extra links found on urlscan.io: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
        
    except Exception as e:
        writerr(colored('ERROR getURLScanUrls 1: ' + str(e), 'red'))
        
def processWayBackPage(url):
    """
    Get URLs from a specific page of archive.org CDX API for the input domain
    """
    global totalPages, linkMimes, linksFound, stopSource
    try:
        # Get memory in case it exceeds threshold
        getMemory()
        
        if not stopSource:
            try:             
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                page = url.split('page=')[1]
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER)
                session.mount('http://', HTTP_ADAPTER)
                resp = session.get(url, headers={"User-Agent":userAgent})  
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] archive.org connection error for page ' + page), 'red'))
                resp = None
                return
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Error getting response for page ' + page + ' - ' + str(e)),'red'))
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                         # If a status other of 429, then stop processing Alien Vault
                        if resp.status_code == 429:
                            writerr(colored(getSPACER('[ 429 ] Archive.org rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                            stopSource = True
                            return
                        # If the response from archive.org is empty then skip
                        if resp.text == '' and totalPages == 0:
                            if verbose():
                                writerr(colored(getSPACER('[ ERR ] '+url+' gave an empty response.'),'red'))
                            return
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose():
                                writerr(colored(getSPACER('[ '+str(resp.status_code)+' ] Error for '+url),'red'))
                            return
                except:
                    pass
            
            # Get the URLs and MIME types. Each line is a separate JSON string
            for line in resp.iter_lines():
                results = line.decode("utf-8")
                # Only get MIME Types if --verbose option was selected
                if verbose():
                    try:
                        linkMimes.add(str(results).split(' ')[2])
                    except Exception as e:
                        if verbose():
                            writerr(colored(getSPACER('ERROR processWayBackPage 2: Cannot get MIME type from line: ' + str(line)),'red'))
                            write(resp.text)
                try:
                    foundUrl = fixArchiveOrgUrl(str(results).split(' ')[1])
                    linksFoundAdd(foundUrl)
                except Exception as e:
                    if verbose():
                        writerr(colored(getSPACER('ERROR processWayBackPage 3: Cannot get link from line: ' + str(line)),'red'))         
                        write(resp.text)       
        else:
            pass
    except Exception as e:
        if verbose():
            writerr(colored("ERROR processWayBackPage 1: " + str(e), "red"))
    
def getWaybackUrls():
    """
    Get URLs from the Wayback Machine, archive.org
    """
    global linksFound, linkMimes, waymorePath, subs, path, stopProgram, totalPages, stopSource, argsInput
    
    # Write the file of URL's for the passed domain/URL
    try:
        stopSource = False
        filterMIME = '&filter=!mimetype:warc/revisit|' + re.escape(FILTER_MIME).replace(',','|') 
        filterCode = '&filter=!statuscode:' + re.escape(FILTER_CODE).replace(',','|')
        
        # Set keywords filter if -ko argument passed
        filterKeywords = ''
        if args.keywords_only:
            filterKeywords = '&filter=original:.*(' + re.escape(FILTER_KEYWORDS).replace(',','|') + ').*'
            
        if args.filter_responses_only:
            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(argsInput) + path).replace('{COLLAPSE}','') + '&page='
        else:
            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(argsInput) + path).replace('{COLLAPSE}','') + filterMIME + filterCode + filterKeywords + '&page='
        
        # Get the number of pages (i.e. separate requests) that are going to be made to archive.org
        totalPages = 0
        try:
            write(colored('\rGetting the number of archive.org pages to search...\r','cyan'))
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
            resp = session.get(url+'&showNumPages=True', headers={"User-Agent":userAgent}) 
            totalPages = int(resp.text.strip())+1
            
            # If the argument to limit the requests was passed and the total pages is larger than that, set to the limit
            if args.limit_requests != 0 and totalPages > args.limit_requests:
                totalPages = args.limit_requests
        except Exception as e:
            try:
                if resp.text.lower().find('blocked site error') > 0:
                    writerr(colored(getSPACER('[ ERR ] unable to get links from archive.org: Blocked Site Error (they block the target site)'), 'red'))
                else:
                    writerr(colored(getSPACER('[ ERR ] unable to get links from archive.org: ' + str(resp.text.strip())), 'red'))
            except:
                writerr(colored(getSPACER('[ ERR ] unable to get links from archive.org: ' + str(e)), 'red'))
            return
        
        # If the rate limit was reached end now
        if resp.status_code == 429:
            writerr(colored(getSPACER('[ 429 ] Archive.org rate limit reached so unable to get links.'),'red'))
            return
        
        if verbose():
            write(colored('The archive URL requested to get links: ','magenta')+colored(url+'\n','white'))
         
        # if the page number was found then display it, but otherwise we will just try to increment until we have everything       
        write(colored('\rGetting links from ' + str(totalPages) + ' archive.org API requests (this can take a while for some domains)...\r','cyan'))

        # Get a list of all the page URLs we need to visit
        pages = set()
        for page in range(0, totalPages):
            pages.add(url+str(page))
        
        # Process the URLs from web archive        
        if stopProgram is None:
            p = mp.Pool(args.processes)
            p.map(processWayBackPage, pages)
            p.close()
            p.join()
               
        # Show the MIME types found (in case user wants to exclude more)
        if verbose() and len(linkMimes) > 0 :
            linkMimes.discard('warc/revisit')
            write(getSPACER(colored('MIME types found: ','magenta')+colored(str(linkMimes),'white'))+'\n')
            linkMimes = None
        
        if not args.xwm:
            linkCount = len(linksFound)
            write(getSPACER(colored('Links found on archive.org: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
            
    except Exception as e:
        writerr(colored('ERROR getWaybackUrls 1: ' + str(e), 'red'))

def processCommonCrawlCollection(cdxApiUrl):
    """
    Get URLs from a given Common Crawl index collection
    """
    global subs, path, linksFound, linkMimes, stopSource, argsInput
    
    try:
        # Get memory in case it exceeds threshold
        getMemory()
        
        if not stopSource:
            # Set mime content type filter
            filterMIME = '&filter=~mime:^(?!warc/revisit|' 
            if FILTER_MIME.strip() != '':
                filterMIME = filterMIME + re.escape(FILTER_MIME).replace(',','|')
            filterMIME = filterMIME + ')'
            
            # Set status code filter
            filterCode = ''
            if FILTER_CODE.strip() != '':
                filterCode = '&filter=~status:^(?!' + re.escape(FILTER_CODE).replace(',','|') + ')'
            
            # Set keywords filter if -ko argument passed
            filterKeywords = ''
            if args.keywords_only:
                filterKeywords = '&filter=~url:.*(' + re.escape(FILTER_KEYWORDS).replace(',','|') + ').*'
                
            commonCrawlUrl = cdxApiUrl + '?output=json&fl=timestamp,url,mime,status,digest&url=' 
               
            if args.filter_responses_only:
                url = commonCrawlUrl + subs + quote(argsInput) + path
            else:
                url = commonCrawlUrl + subs + quote(argsInput) + path + filterMIME + filterCode + filterKeywords
            
            try:
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER)
                session.mount('http://', HTTP_ADAPTER)
                resp = session.get(url, stream=True, headers={"User-Agent":userAgent})   
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] Common Crawl connection error'), 'red'))
                resp = None
                return
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Error getting response - ' + str(e)),'red'))
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                        # If a status other of 429, then stop processing Common Crawl
                        if resp.status_code == 429:
                            writerr(colored(getSPACER('[ 429 ] Common Crawl rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                            stopSource = True
                            return
                        # If the response from commoncrawl.org says nothing was found...
                        if resp.text.lower().find('no captures found') > 0:
                            # Don't output any messages, just exit function
                            return
                        # If the response from commoncrawl.org is empty, then stop
                        if resp.text == '':
                            if verbose():
                                writerr(colored(getSPACER('[ ERR ] '+url+' gave an empty response.'),'red'))
                            return
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose(): 
                                writerr(colored(getSPACER('[ '+str(resp.status_code)+' ] Error for '+url),'red'))
                            return
                except:
                    pass
                
            # Get the URLs and MIME types
            for line in resp.iter_lines():
                results = line.decode("utf-8")
                try:
                    data = json.loads(results)
                    # Get MIME Types if --verbose option was seletced
                    if verbose():
                        try:
                            linkMimes.add(data['mime'])
                        except:
                            pass
                    linksFoundAdd(data['url'])
                except Exception as e:
                    if verbose():
                        writerr(colored('ERROR processCommonCrawlCollection 2: Cannot get URL and MIME type from line: ' + str(line),'red'))
        else:
            pass
    except Exception as e:
        writerr(colored('ERROR processCommonCrawlCollection 1: ' + str(e), 'red'))
            
def getCommonCrawlUrls():
    """
    Get all Common Crawl index collections to get all URLs from each one
    """
    global linksFound, linkMimes, waymorePath, subs, path, stopSource, argsInput
    
    try:
        stopSource = False
        linkMimes = set()
        originalLinkCount = len(linksFound)
        
        # Set mime content type filter
        filterMIME = '&filter=~mime:^(?!warc/revisit|' 
        if FILTER_MIME.strip() != '':
            filterMIME = filterMIME + re.escape(FILTER_MIME).replace(',','|')
        filterMIME = filterMIME + ')'
        
        # Set status code filter
        filterCode = ''
        if FILTER_CODE.strip() != '':
            filterCode = '&filter=~status:^(?!' + re.escape(FILTER_CODE).replace(',','|') + ')'
    
        if verbose():
            if args.filter_responses_only:
                url = '{CDX-API-URL}?output=json&fl=timestamp,url,mime,status,digest&url=' + subs + quote(argsInput) + path
            else:
                url = '{CDX-API-URL}?output=json&fl=timestamp,url,mime,status,digest&url=' + subs + quote(argsInput) + path + filterMIME + filterCode  
            write(colored('The commoncrawl index URL requested to get links (where {CDX-API-URL} is from ' + CCRAWL_INDEX_URL + '): ','magenta')+colored(url+'\n','white'))
        
        write(colored('\rGetting commoncrawl.org index collections list...\r','cyan'))
                  
        # Get all the Common Crawl index collections
        try:
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
            indexes = session.get(CCRAWL_INDEX_URL, headers={"User-Agent":userAgent})
        except ConnectionError as ce:
            writerr(colored(getSPACER('[ ERR ] Common Crawl connection error'), 'red'))
            return
        except Exception as e:
            writerr(colored(getSPACER('[ ERR ] Error getting Common Crawl index collection - ' + str(e)),'red'))
            return
        
        # If the rate limit was reached end now
        if indexes.status_code == 429:
            writerr(colored(getSPACER('[ 429 ] Common Crawl rate limit reached so unable to get links.'),'red'))
            return
        
        # Get the API URLs from the returned JSON
        jsonResp = indexes.json()
        cdxApiUrls = set()
        collection = 0
        for values in jsonResp:
            for key in values:
                if key == 'cdx-api':
                    cdxApiUrls.add(values[key])
            collection = collection + 1
            if collection == args.lcc: break
        
        write(colored('\rGetting links from the latest ' + str(len(cdxApiUrls)) + ' commoncrawl.org index collections (this can take a while for some domains)...\r','cyan'))
             
        # Process the URLs from common crawl        
        if stopProgram is None:
            p = mp.Pool(args.processes)
            p.map(processCommonCrawlCollection, cdxApiUrls)
            p.close()
            p.join()
                           
        # Show the MIME types found (in case user wants to exclude more)
        if verbose() and len(linkMimes) > 0:
            linkMimes.discard('warc/revisit')
            write(getSPACER(colored('MIME types found: ','magenta')+colored(str(linkMimes),'white'))+'\n')
        
        linkCount = len(linksFound) - originalLinkCount
        write(getSPACER(colored('Extra links found on commoncrawl.org: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
                    
    except Exception as e:
        writerr(colored('ERROR getCommonCrawlUrls 1: ' + str(e), 'red'))

def processResponses():
    """
    Get archived responses from archive.org
    """
    global linksFound, subs, path, indexFile, totalResponses, stopProgram, argsInput, continueRespFile, successCount, fileCount
    try:
       
        # Create 'results' and domain directory if needed
        createDirs()
            
        # Check if a continueResp.tmp and responses.tmp files exists
        runPrevious = 'n'
        if os.path.exists(waymorePath
                / 'results'
                / str(argsInput).replace('/','-')
                / 'continueResp.tmp') and os.path.exists(waymorePath
                / 'results'
                / str(argsInput).replace('/','-')
                / 'responses.tmp'):
            
            # Load the links into the set
            with open(
                waymorePath
                / 'results'
                / str(argsInput).replace('/','-')
                / 'responses.tmp',
                'rb',
            ) as fl:
                linkRequests = pickle.load(fl)
            totalPrevResponses = len(linkRequests)        
               
            # Get the previous end position to start again at this point
            try:
                with open(waymorePath
                    / 'results'
                    / str(argsInput).replace('/','-')
                    / 'continueResp.tmp',
                    'r') as fc:
                        successCount = int(fc.readline().strip())
            except Exception as e:
                successCount = 0
                
            # Ask the user if we should continue with previous run if the current starting position is greater than 0 and less than the total
            if successCount > 0 and successCount < totalPrevResponses:
                 # If the program is not piped from or to another process, then ask whether to continue with previous run
                if sys.stdout.isatty() and sys.stdin.isatty():
                    write(colored('The previous run to get archived responses for ' + argsInput  + ' was not completed.\nYou can start from response ' + str(successCount) + ' of ' + str(totalPrevResponses) + ' for the previous run, or you can start a new run with your specified arguments.', 'yellow'))
                    runPrevious = input('Continue with previous run? y/n: ')
                else:
                    if CONTINUE_RESPONSES_IF_PIPED:
                        runPrevious = 'y'
                        writerr(colored('The previous run to get archived responses for ' + argsInput  + ' was not completed. Starting from response ' + str(successCount) + ' of ' + str(totalPrevResponses) + '... ', 'yellow'))
                    else:
                        runPrevious = 'n'
        
        # If we are going to run a new run
        if runPrevious.lower() == 'n':
            
            # Set start point
            successCount = 0
            
            # Set up filters
            filterLimit = '&limit=' + str(args.limit)
            if args.from_date is None:
                filterFrom = ''
            else:
                filterFrom = '&from=' + str(args.from_date)
            if args.to_date is None:
                filterTo = ''
            else:
                filterTo = '&to=' + str(args.to_date)
            
            # Set keywords filter if -ko argument passed
            filterKeywords = ''
            if args.keywords_only:
                filterKeywords = '&filter=original:.*(' + re.escape(FILTER_KEYWORDS).replace(',','|') + ').*'
                
            # Get the list again with filters and include timestamp
            linksFound = set()
            
            # Set mime content type filter
            filterMIME = '&filter=!mimetype:warc/revisit' 
            if FILTER_MIME.strip() != '':
                filterMIME = filterMIME + '|' + re.escape(FILTER_MIME).replace(',','|')
                
            # Set status code filter
            filterCode = ''
            if FILTER_CODE.strip() != '':
                filterCode = '&filter=!statuscode:' + re.escape(FILTER_CODE).replace(',','|')
            
            # Set the collapse parameter value in the archive.org URL. From the Wayback API docs:
            # "A new form of filtering is the option to 'collapse' results based on a field, or a substring of a field.
            # Collapsing is done on adjacent cdx lines where all captures after the first one that are duplicate are filtered out.
            # This is useful for filtering out captures that are 'too dense' or when looking for unique captures."
            if args.capture_interval == 'none': # get all
                collapse = ''
            elif args.capture_interval == 'h': # get at most 1 capture per hour
                collapse = 'timestamp:10'
            elif args.capture_interval == 'd': # get at most 1 capture per day
                collapse = 'timestamp:8'
            elif args.capture_interval == 'm': # get at most 1 capture per month
                collapse = 'timestamp:6'

            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(argsInput) + path).replace('{COLLAPSE}',collapse) + filterMIME + filterCode + filterLimit + filterFrom + filterTo + filterKeywords
                
            if verbose():
                write(colored('The archive URL requested to get responses: ','magenta')+colored(url+'\n','white'))
            
            write(colored('\rGetting list of response links (this can take a while for some domains)...\r','cyan'))
                
            # Build the list of links, concatenating timestamp and URL
            try:
                # Choose a random user agent string to use for any requests
                success = True
                userAgent = random.choice(USER_AGENT)
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER)
                session.mount('http://', HTTP_ADAPTER)
                resp = session.get(url, stream=True, headers={"User-Agent":userAgent}, timeout=args.timeout)  
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] archive.org connection error'), 'red'))
                resp = None
                success = False
                return 
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Couldn\'t get list of responses: ' + str(e)),'red'))
                resp = None
                success = False
                return
            finally:
                try:
                    if resp is not None:
                        # If the response from archive.org is empty, then no responses were found
                        if resp.text == '':
                            writerr(colored(getSPACER('No archived responses were found on archive.org for the given search parameters.'),'red'))
                            success = False
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose(): 
                                writerr(colored(getSPACER('[ '+str(resp.status_code)+' ] Error for '+url),'red'))
                            success = False
                    if not success:
                        if args.keywords_only:
                            writerr(colored(getSPACER('Failed to get links from archive.org - consider removing -ko / --keywords-only argument, or changing FILTER_KEYWORDS in config.yml'), 'red'))
                        else:    
                            if resp.text.lower().find('blocked site error') > 0:
                                writerr(colored(getSPACER('Failed to get links from archive.org - Blocked Site Error (they block the target site)'), 'red'))
                            else:
                                writerr(colored(getSPACER('Failed to get links from archive.org - check input domain and try again.'), 'red'))
                        return
                except:
                    pass
            
            # Go through the response to save the links found        
            for line in resp.iter_lines():
                try:
                    results = line.decode("utf-8") 
                    timestamp = results.split(' ')[0]
                    originalUrl = results.split(' ')[1]
                    linksFoundAdd(timestamp+'/'+originalUrl)
                except Exception as e:
                    writerr(colored(getSPACER('ERROR processResponses 3: Cannot to get link from line: '+str(line)), 'red'))
            
            # Remove any links that have URL exclusions
            linkRequests = []
            exclusionRegex = re.compile(r'('+re.escape(FILTER_URL).replace(',','|')+')',flags=re.IGNORECASE)
            for link in linksFound:
                # Only add the link if:
                # a) if the -ra --regex-after was passed that it matches that
                # b) it does not match the URL exclusions
                if (args.regex_after is None or re.search(args.regex_after, link, flags=re.IGNORECASE) is not None) and exclusionRegex.search(link) is None:
                    linkRequests.append(link)
                    
            # Write the links to a temp file
            with open(
                    waymorePath
                    / 'results'
                    / str(argsInput).replace('/','-')
                    / 'responses.tmp',
                    'wb',
                ) as f:
                pickle.dump(linkRequests, f)
                
        # Get the total number of responses we will try to get and set the current file count to the success count
        totalResponses = len(linkRequests)
        fileCount = successCount
        
        # If the limit has been set over the default, give a warning that this could take a long time!
        if totalResponses - successCount > DEFAULT_LIMIT:
            if successCount > 0:
                writerr(colored(getSPACER('WARNING: Downloading remaining ' + str(totalResponses - successCount) + ' responses may take a loooooooong time! Consider using arguments -l, -ci, -from and -to wisely!'),'yellow'))
            else:
                writerr(colored(getSPACER('WARNING: Downloading ' + str(totalResponses) + ' responses may take a loooooooong time! Consider using arguments -l, -ci, -from and -to wisely!'),'yellow'))
        
        # Open the index file if hash value is going to be used (not URL)
        if not args.url_filename:
            indexFile = open(
                waymorePath
                / 'results'
                / str(argsInput).replace('/','-')
                / 'index.txt',
                'a',
            )
        
        # Open the continue.tmp file to store what record we are upto
        continueRespFile = open(
                waymorePath
                / 'results'
                / str(argsInput).replace('/','-')
                / 'continueResp.tmp',
                'w+',
            )
        
        # Process the URLs from web archive   
        if stopProgram is None:
            p = mp.Pool(args.processes)
            p.map(processArchiveUrl, linkRequests[successCount:])
            p.close()
            p.join()
            
        # Delete the tmp files now it has run successfully
        if stopProgram is None:
            try:
                os.remove(waymorePath
                    / 'results'
                    / str(argsInput).replace('/','-')
                    / 'continueResp.tmp')
                os.remove(waymorePath
                    / 'results'
                    / str(argsInput).replace('/','-')
                    / 'responses.tmp')
            except:
                pass
        
        # Close the index file if hash value is going to be used (not URL)
        if not args.url_filename:
            indexFile.close()
            
        # Close the continueResp.tmp file
        continueRespFile.close()
        
    except Exception as e:
        writerr(colored(getSPACER('ERROR processResponses 1: ' + str(e)), 'red'))
    finally:
        linkRequests = None    

def createDirs():
    """
    Create a directory for the 'results' and the sub directory for the passed domain/URL
    """
    global waymorePath, argsInput
    # Create a directory for "results" if it doesn't already exist
    try:
        results_dir = Path(waymorePath / 'results')
        results_dir.mkdir(exist_ok=True)
    except:
        pass
    # Create a directory for the target domain
    try:
        domain_dir = Path(
            waymorePath / 'results' / str(argsInput).replace('/','-')
        )
        domain_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        pass     

# Get width of the progress bar based on the width of the terminal
def getProgressBarLength():
    global terminalWidth
    try:
        if verbose():
            offset = 90
        else:
            offset = 50
        progressBarLength = terminalWidth - offset
    except:
        progressBarLength = 20
    return progressBarLength

# Get the length of the space to add to a string to fill line up to width of terminal
def getSPACER(text):
    global terminalWidth
    lenSpacer = terminalWidth - len(text) -1
    SPACER = ' ' * lenSpacer
    return text + SPACER

# For validating -m / --memory-threshold argument
def argcheckPercent(value):
    ivalue = int(value)
    if ivalue > 99:
        raise argparse.ArgumentTypeError(
            "A valid integer percentage less than 100 must be entered."
        )
    return ivalue
    
# Run waymore
if __name__ == '__main__':

    # Tell Python to run the handler() function when SIGINT is received
    signal(SIGINT, handler)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='waymore - by @Xnl-h4ck3r: Find way more from the Wayback Machine'    
    )
    parser.add_argument(
        '-i',
        '--input',
        action='store',
        help='The target domain (or file of domains) to find links for. This can be a domain only, or a domain with a specific path. If it is a domain only to get everything for that domain, don\'t prefix with "www."',
        type=validateArgInput
    )
    parser.add_argument(
        '-n',
        '--no-subs',
        action='store_true',
        help='Don\'t include subdomains of the target domain (only used if input is not a domain with a specific path).',
    )
    parser.add_argument(
        '-mode',
        action='store',
        help='The mode to run: U (retrieve URLs only), R (download Responses only) or B (Both).',
        choices = ['U','R','B'],
        default='B'
    )
    parser.add_argument(
        '-f',
        '--filter-responses-only',
        action='store_true',
        help='The initial links from Wayback Machine will not be filtered (MIME Type and Response Code), only the responses that are downloaded, e.g. it maybe useful to still see all available paths from the links even if you don\'t want to check the content.',
    )
    parser.add_argument(
        '-l',
        '--limit',
        action='store',
        type=int,
        help='How many responses will be saved (if -mode is R or B). A positive value will get the first N results, a negative value will will get the last N results. A value of 0 will get ALL responses (default: '+str(DEFAULT_LIMIT)+')',
        default=DEFAULT_LIMIT,
        metavar='<signed integer>'
    )
    parser.add_argument(
        '-from',
        '--from-date',
        action='store',
        type=int,
        help='What date to get responses from. If not specified it will get from the earliest possible results. A partial value can be passed, e.g. 2016, 201805, etc.',
        metavar='<yyyyMMddhhmmss>'
    )
    parser.add_argument(
        '-to',
        '--to-date',
        action='store',
        type=int,
        help='What date to get responses to. If not specified it will get to the latest possible results. A partial value can be passed, e.g. 2016, 201805, etc.',
        metavar='<yyyyMMddhhmmss>'
    )
    parser.add_argument(
        '-ci',
        '--capture-interval',
        action='store',
        choices=['h', 'd', 'm', 'none'],
        help='Filters the search on archive.org to only get at most 1 capture per hour (h), day (d) or month (m). This filter is used for responses only. The default is \'d\' but can also be set to \'none\' to not filter anything and get all responses.',
        default='d'
    )
    parser.add_argument(
        '-ra',
        '--regex-after',
        help='RegEx for filtering purposes against links found from archive.org/commoncrawl.org AND responses downloaded. Only positive matches will be output.',
        action='store',
    )
    parser.add_argument(
        '-url-filename',
        action='store_true',
        help='Set the file name of downloaded responses to the URL that generated the response, otherwise it will be set to the hash value of the response. Using the hash value means multiple URLs that generated the same response will only result in one file being saved for that response.',
        default=False
    )
    parser.add_argument(
        '-xwm',
        action='store_true',
        help='Exclude checks for links from Wayback Machine (archive.org)',
        default=False
    )
    parser.add_argument(
        '-xcc',
        action='store_true',
        help='Exclude checks for links from commoncrawl.org',
        default=False
    )
    parser.add_argument(
        '-xav',
        action='store_true',
        help='Exclude checks for links from alienvault.com',
        default=False
    )
    parser.add_argument(
        '-xus',
        action='store_true',
        help='Exclude checks for links from urlscan.io',
        default=False
    )
    parser.add_argument(
        '-lcc',
        action='store',
        type=int,
        help='Limit the number of Common Crawl index collections searched, e.g. \'-lcc 10\' will just search the latest 10 collections. As of June 2022 there are currently 88 collections. Setting to 0 (default) will search ALL collections. If you don\'t want to search Common Crawl at all, use the -xcc option.',
        default=0
    )
    parser.add_argument(
        '-t',
        '--timeout',
        help='This is for archived responses only! How many seconds to wait for the server to send data before giving up (default: '+str(DEFAULT_TIMEOUT)+' seconds)',
        default=DEFAULT_TIMEOUT,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        '-p',
        '--processes',
        help='Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes (threads) used (default: 3)',
        action='store',
        type=validateArgProcesses,
        default=3,
        metavar="<integer>",
    )
    parser.add_argument(
        '-r',
        '--retries',
        action='store',
        type=int,
        help='The number of retries for requests that get connection error or rate limited (default: 1).',
        default=1
    )
    parser.add_argument(
        "-m",
        "--memory-threshold",
        action="store",
        help="The memory threshold percentage. If the machines memory goes above the threshold, the program will be stopped and ended gracefully before running out of memory (default: 95)",
        default=95,
        metavar="<integer>",
        type=argcheckPercent,
    )
    parser.add_argument(
        '-ko',
        '--keywords-only',
        action='store_true',
        help='Only return links and responses that contain keywords that you are interested in. This can reduce the time it takes to get results. Keywords are given in a comma separated list in the "config.yml" file with the "FILTER_KEYWORDS" key',
        default=False
    )
    parser.add_argument(
        '-lr',
        '--limit-requests',
        type=int,
        help='Limit the number of requests that will be made when getting links from a source (this doesn\'t apply to Common Crawl). Some targets can return a huge amount of requests needed that are just not feasible to get, so this can be used to manage that situation. This defaults to 0 (Zero) which means there is no limit.',
        default=0,
    )
    parser.add_argument(
        "-ow",
        "--output-overwrite",
        action="store_true",
        help="If the URL output file (waymore.txt) already exists, it will be overwritten instead of being appended to.",
    )
    parser.add_argument(
        "-nlf",
        "--new-links-file",
        action="store_true",
        help="If this argument is passed, a waymore.new file will also be written that will contain links for the latest run.",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        help="Path to the YML config file. If not passed, it looks for file 'config.yml' in the same directory as runtime file 'waymore.py'.",
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    parser.add_argument('--version', action='store_true', help="Show version number")
    args = parser.parse_args()

    # If --version was passed, display version and exit
    if args.version:
        write(colored('Waymore - v' + __import__('waymore').__version__,'cyan'))
        sys.exit()
        
    # If no input was given, raise an error
    if sys.stdin.isatty():
        if args.input is None:
            writerr(colored('You need to provide an input with -i argument or through <stdin>.', 'red'))
            sys.exit()
    else:
        validateArgInput('<stdin>')       
    
    # Get the current Process ID to use to get memory usage that is displayed with -vv option
    try:
        process = psutil.Process(os.getpid())
    except:
        pass
        
    showBanner()
             
    try:     

        # For each input (maybe multiple if a file was passed)
        for inpt in inputValues:
            
            argsInput = inpt.strip().rstrip('\n')
            
            # Reset global variables
            linksFound = set()
            linkMimes = set()
            successCount = 0
            failureCount = 0
            fileCount = 0
            totalResponses = 0
            totalPages = 0
            indexFile = None
            path = ''
            stopSource = False
            
            # Get the config settings from the config.yml file
            getConfig()

            if verbose():
                showOptions()
            
            # If the mode is U (URLs retrieved) or B (URLs retrieved AND Responses downloaded)
            if args.mode in ['U','B']:
                
                # If not requested to exclude, get URLs from the Wayback Machine (archive.org)
                if not args.xwm and stopProgram is None:
                    getWaybackUrls()
            
                # If not requested to exclude, get URLs from commoncrawl.org
                if not args.xcc and stopProgram is None:
                    getCommonCrawlUrls()
                    
                # If not requested to exclude, get URLs from alienvault.com
                if not args.xav and stopProgram is None:
                    getAlienVaultUrls()
                
                # If not requested to exclude, get URLs from urlscan.io
                if not args.xus and stopProgram is None:
                    getURLScanUrls()
                    
                # Output results of all searches
                processURLOutput()
            
                # Clean up 
                linkMimes = None
                
            # If we want to get actual archived responses from archive.org...
            if (args.mode in ['R','B'] or inputIsDomainANDPath) and stopProgram is None:
                processResponses()
                
                # Output details of the responses downloaded
                processResponsesOutput()
            
            # Output stats if -v option was selected
            if verbose():
                processStats()
            
            # If the program was stopped then alert the user
            if stopProgram is not None:
                if stopProgram == StopProgram.MEMORY_THRESHOLD:
                    writerr(
                        colored(
                            "YOUR MEMORY USAGE REACHED "
                            + str(maxMemoryPercent)
                            + "% SO THE PROGRAM WAS STOPPED. DATA IS LIKELY TO BE INCOMPLETE.\n",
                            "red",
                        )
                    )
                elif stopProgram == StopProgram.WEBARCHIVE_PROBLEM:
                    writerr(
                        colored(
                            "THE PROGRAM WAS STOPPED DUE TO PROBLEM GETTING DATA FROM WEBARCHIVE.ORG\n",
                            "red",
                        )
                    )
                else:
                    writerr(
                        colored(
                            "THE PROGRAM WAS STOPPED. DATA IS LIKELY TO BE INCOMPLETE.\n",
                            "red",
                        )
                    )
                
    except Exception as e:
        writerr(colored('ERROR main 1: ' + str(e), 'red'))

    finally:
        # Clean up
        linksFound = None
        linkMimes = None
        inputValues = None
