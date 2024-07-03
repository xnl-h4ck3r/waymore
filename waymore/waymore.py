#!/usr/bin/env python
# Python 3
# waymore - by @Xnl-h4ck3r: Find way more from the Wayback Machine (also get links from Common Crawl, AlienVault OTX, URLScan and VirusTotal)
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
from datetime import datetime, timedelta
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
import time
import tldextract
try:
    from . import __version__
except:
    pass

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
inputIsSubDomain = False
subs = '*.'
path = ''
waymorePath = ''
terminalWidth = 135
maxMemoryUsage = 0
currentMemUsage = 0
maxMemoryPercent = 0
currentMemPercent = 0
HTTP_ADAPTER = None
HTTP_ADAPTER_CC = None
checkWayback = 0
checkCommonCrawl = 0
checkAlienVault = 0
checkURLScan = 0
checkVirusTotal = 0
argsInputHostname = ''
responseOutputDirectory = ''

# Source Provider URLs
WAYBACK_URL = 'https://web.archive.org/cdx/search/cdx?url={DOMAIN}{COLLAPSE}&fl=timestamp,original,mimetype,statuscode,digest'
CCRAWL_INDEX_URL = 'https://index.commoncrawl.org/collinfo.json'
ALIENVAULT_URL = 'https://otx.alienvault.com/api/v1/indicators/{TYPE}/{DOMAIN}/url_list?limit=500'
URLSCAN_URL = 'https://urlscan.io/api/v1/search/?q=domain:{DOMAIN}&size=10000'
VIRUSTOTAL_URL = 'https://www.virustotal.com/vtapi/v2/domain/report?apikey={APIKEY}&domain={DOMAIN}'

# User Agents to use when making requests, chosen at random
USER_AGENT  = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
]

# The default maximum number of responses to download
DEFAULT_LIMIT = 5000

# The default timeout for archived responses to be retrieved in seconds
DEFAULT_TIMEOUT = 30

# Exclusions used to exclude responses we will try to get from web.archive.org
DEFAULT_FILTER_URL = '.css,.jpg,.jpeg,.png,.svg,.img,.gif,.mp4,.flv,.ogv,.webm,.webp,.mov,.mp3,.m4a,.m4p,.scss,.tif,.tiff,.ttf,.otf,.woff,.woff2,.bmp,.ico,.eot,.htc,.rtf,.swf,.image,/image,/img,/css,/wp-json,/wp-content,/wp-includes,/theme,/audio,/captcha,/font,node_modules,/jquery,/bootstrap'

# MIME Content-Type exclusions used to filter links and responses from web.archive.org through their API
DEFAULT_FILTER_MIME = 'text/css,image/jpeg,image/jpg,image/png,image/svg+xml,image/gif,image/tiff,image/webp,image/bmp,image/vnd,image/x-icon,image/vnd.microsoft.icon,font/ttf,font/woff,font/woff2,font/x-woff2,font/x-woff,font/otf,audio/mpeg,audio/wav,audio/webm,audio/aac,audio/ogg,audio/wav,audio/webm,video/mp4,video/mpeg,video/webm,video/ogg,video/mp2t,video/webm,video/x-msvideo,video/x-flv,application/font-woff,application/font-woff2,application/x-font-woff,application/x-font-woff2,application/vnd.ms-fontobject,application/font-sfnt,application/vnd.android.package-archive,binary/octet-stream,application/octet-stream,application/pdf,application/x-font-ttf,application/x-font-otf,video/webm,video/3gpp,application/font-ttf,audio/mp3,audio/x-wav,image/pjpeg,audio/basic,application/font-otf,application/x-ms-application,application/x-msdownload,video/x-ms-wmv,image/x-png,video/quicktime,image/x-ms-bmp,font/opentype,application/x-font-opentype,application/x-woff,audio/aiff'

# Response code exclusions we will use to filter links and responses from web.archive.org through their API
DEFAULT_FILTER_CODE = '404,301,302'

# Used to filter out downloaded responses that could be custom 404 pages
REGEX_404 = r'<title>[^\<]*(404|not found)[^\<]*</title>'

# Keywords 
DEFAULT_FILTER_KEYWORDS = 'admin,login,logon,signin,signup,register,registration,dash,portal,ftp,panel,.js,api,robots.txt,graph,gql,config,backup,debug,db,database,git,cgi-bin,swagger,zip,rar,tar.gz,internal,jira,jenkins,confluence,atlassian,okta,corp,upload,delete,email,sql,create,edit,test,temp,cache,wsdl,log,payment,setting,mail,file,redirect,chat,billing,doc,trace,cp,ftp,gateway,import,proxy,dev,stage,stg,uat'

# Yaml config values
FILTER_URL = ''
FILTER_MIME = ''
FILTER_CODE = ''
MATCH_CODE  = ''
FILTER_KEYWORDS = ''
URLSCAN_API_KEY = ''
CONTINUE_RESPONSES_IF_PIPED = True
WEBHOOK_DISCORD = ''
DEFAULT_OUTPUT_DIR = ''

API_KEY_SECRET = "aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ=="

# When -oijs is passed, and the downloaded responses are checked for scripts, files with these extensions will be ignored
INLINE_JS_EXCLUDE = ['.js', '.csv', '.xls', '.xlsx', '.doc', '.docx', '.pdf', '.msi', '.zip', '.gzip', '.gz', '.tar', '.rar', '.json']

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

def showVersion():
    try:
        try:
            resp = requests.get('https://raw.githubusercontent.com/xnl-h4ck3r/waymore/main/waymore/__init__.py',timeout=3)
        except:
            write('Current waymore version '+__version__+' (unable to check if latest)\n')
        if __version__ == resp.text.split('=')[1].replace('"',''):
            write('Current waymore version '+__version__+' ('+colored('latest','green')+')\n')
        else:
            write('Current waymore version '+__version__+' ('+colored('outdated','red')+')\n')
    except:
        pass
    
def showBanner():
    write()
    write(colored(" _ _ _       _   _ ","red")+"____                    ")
    write(colored("| | | |_____| | | ","red")+r"/    \  ___   ____ _____ ")
    write(colored("| | | (____ | | | ","red")+r"| | | |/ _ \ / ___) ___ |")
    write(colored("| | | / ___ | |_| ","red")+"| | | | |_| | |   | |_| |")
    write(colored(r" \___/\_____|\__  ","red")+r"|_|_|_|\___/| |   | ____/")
    write(colored("            (____/ ","red")+colored("  by Xnl-h4ck3r ","magenta")+r" \_____)")
    try:
        currentDate = datetime.now().date()
        if currentDate.month == 12 and currentDate.day in (24,25):
            write(colored("            *** 🎅 HAPPY CHRISTMAS! 🎅 ***","green",attrs=["blink"]))
        elif currentDate.month == 10 and currentDate.day == 31:
            write(colored("            *** 🎃 HAPPY HALLOWEEN! 🎃 ***","red",attrs=["blink"]))
        elif currentDate.month == 1 and currentDate.day in  (1,2,3,4,5):
            write(colored("            *** 🥳 HAPPY NEW YEAR!! 🥳 ***","yellow",attrs=["blink"]))
    except:
        pass
    write()
    showVersion()
    
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
            writerr(colored(getSPACER(r">>> Patience isn't your strong suit eh? ¯\_(ツ)_/¯"), 'red'))
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
            write(colored(inputArgDesc + argsInput, 'magenta')+colored(' The target URL to search for.','white'))
        else: # input is a domain
            write(colored(inputArgDesc + argsInput, 'magenta')+colored(' The target domain to search for.','white'))
        
        if args.mode == 'U':
            write(colored('-mode: ' + args.mode, 'magenta')+colored(' Only URLs will be retrieved for the input.','white'))
        elif args.mode == 'R':
            write(colored('-mode: ' + args.mode, 'magenta')+colored(' Only Responses will be downloaded for the input.','white'))
        elif args.mode == 'B':
            write(colored('-mode: ' + args.mode, 'magenta')+colored(' URLs will be retrieved AND Responses will be downloaded for the input.','white'))

        if args.config is not None:
            write(colored('-c: ' + args.config, 'magenta')+colored(' The path of the YML config file.','white'))
            
        if args.no_subs:
            write(colored('-n: ' +str(args.no_subs), 'magenta')+colored(' Sub domains are excluded in the search.','white'))
        else:
            write(colored('-n: ' +str(args.no_subs), 'magenta')+colored(' Sub domains are included in the search.','white'))
        
        write(colored('-xwm: ' +str(args.xwm), 'magenta')+colored(' Whether to exclude checks for links from Wayback Machine (archive.org)','white'))    
        write(colored('-xcc: ' +str(args.xcc), 'magenta')+colored(' Whether to exclude checks for links from commoncrawl.org','white'))
        if not args.xcc:
            if args.lcc ==0 and args.lcy == 0:
                write(colored('-lcc: ' +str(args.lcc), 'magenta')+colored(' Search ALL Common Crawl index collections.','white'))
            else:
                if args.lcy == 0:
                    write(colored('-lcc: ' +str(args.lcc), 'magenta')+colored(' The number of latest Common Crawl index collections to be searched.','white'))
                else:
                    if args.lcc != 0:
                        write(colored('-lcc: ' +str(args.lcc), 'magenta')+colored(' The number of latest Common Crawl index collections to be searched.','white'))
                    write(colored('-lcy: ' +str(args.lcy), 'magenta')+colored(' Search all Common Crawl index collections with data from year '+str(args.lcy)+' and after.','white'))
        write(colored('-xav: ' +str(args.xav), 'magenta')+colored(' Whether to exclude checks for links from alienvault.com','white'))
        write(colored('-xus: ' +str(args.xus), 'magenta')+colored(' Whether to exclude checks for links from urlscan.io','white'))
        if URLSCAN_API_KEY == '':
            write(colored('URLScan API Key:', 'magenta')+colored(' {none} - You can get a FREE or paid API Key at https://urlscan.io/user/signup which will let you get more back, and quicker.','white'))
        else:
            write(colored('URLScan API Key: ', 'magenta')+colored(URLSCAN_API_KEY))
        write(colored('-xvt: ' +str(args.xvt), 'magenta')+colored(' Whether to exclude checks for links from virustotal.com','white'))
        if VIRUSTOTAL_API_KEY == '':
            write(colored('VirusTotal API Key:', 'magenta')+colored(' {none} - You can get a FREE or paid API Key at https://www.virustotal.com/gui/join-us which will let you get some extra URLs.','white'))
        else:
            write(colored('VirusTotal API Key: ', 'magenta')+colored(VIRUSTOTAL_API_KEY))
        
        if args.mode in ['U','B']:
            if args.output_urls != '':
                write(colored('-oU: ' +str(args.output_urls), 'magenta')+colored(' The name of the output file for URL links.','white'))
            write(colored('-ow: ' +str(args.output_overwrite), 'magenta')+colored(' Whether the URL output file will be overwritten if it already exists. If False (default), it will be appended to, and duplicates removed.','white'))
            write(colored('-nlf: ' +str(args.new_links_file), 'magenta')+colored(' Whether the URL output file ".new" version will also be written. It will include only new links found for the same target on subsequent runs. This can be used for continuous monitoring of a target.','white'))
            
        if args.mode in ['R','B']:
            if args.output_responses != '':
                write(colored('-oR: ' +str(args.output_responses), 'magenta')+colored(' The directory to store archived responses and index file.','white'))
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
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' Get at most 1 archived response per hour from Wayback Machine (archive.org)','white'))
            elif args.capture_interval == 'd':
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' Get at most 1 archived response per day from Wayback Machine (archive.org)','white'))
            elif args.capture_interval == 'm':
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' Get at most 1 archived response per month from Wayback Machine (archive.org)','white'))
            elif args.capture_interval == 'none':
                write(colored('-ci: ' +args.capture_interval, 'magenta')+colored(' There will not be any filtering based on the capture interval.','white'))
                    
            if args.url_filename:
                write(colored('-url-filename: ' +str(args.url_filename), 'magenta')+colored(' The filenames of downloaded responses wil be set to the URL rather than the hash value of the response.','white'))

            write(colored('-oijs: '+str(args.output_inline_js), 'magenta')+colored(' Whether the combined JS of all responses will be written to one or more files.','white'))
                    
        write(colored('-f: ' +str(args.filter_responses_only), 'magenta')+colored(' If True, the initial links from wayback machine will not be filtered, only the responses that are downloaded will be filtered. It maybe useful to still see all available paths even if you don\'t want to check the file for content.','white'))
        if args.keywords_only is not None and args.keywords_only != '#CONFIG':
            write(colored('-ko: ' +str(args.keywords_only), 'magenta')+colored(' Only get results that match the given Regex.','white'))
        
        write(colored('-lr: ' +str(args.limit_requests), 'magenta')+colored(' The limit of requests made per source when getting links. A value of 0 (Zero) means no limit is applied.','white'))
        if args.mc:
            write(colored('-mc: ' +str(args.mc), 'magenta')+colored(' Only retrieve URLs and Responses that match these HTTP Status codes.','white'))
        else:
            if args.fc:
                write(colored('-fc: ' +str(args.mc), 'magenta')+colored(' Don\'t retrieve URLs and Responses that match these HTTP Status codes.','white'))
        write(colored('MIME Type exclusions: ', 'magenta')+colored(FILTER_MIME))
        if not args.mc and args.fc:
            write(colored('Response Code exclusions: ', 'magenta')+colored(FILTER_CODE))      
        write(colored('Response URL exclusions: ', 'magenta')+colored(FILTER_URL))  
        if args.keywords_only and args.keywords_only == '#CONFIG':
            if FILTER_KEYWORDS == '':
                write(colored('Keywords only: ', 'magenta')+colored('It looks like no keywords have been set in config.yml file.','red'))
            else: 
                write(colored('Keywords only: ', 'magenta')+colored(FILTER_KEYWORDS))

        if args.notify_discord:
            if WEBHOOK_DISCORD == '' or WEBHOOK_DISCORD == 'YOUR_WEBHOOK':
                write(colored('Discord Webhook: ', 'magenta')+colored('It looks like no Discord webhook has been set in config.yml file.','red'))
            else: 
                write(colored('Discord Webhook: ', 'magenta')+colored(WEBHOOK_DISCORD))
        
        write(colored('Default Output Directory: ', 'magenta')+colored(str(DEFAULT_OUTPUT_DIR)))
                
        if args.regex_after is not None:
            write(colored('-ra: ' + args.regex_after, 'magenta')+colored(' RegEx for filtering purposes against found links from all sources of URLs AND responses downloaded. Only positive matches will be output.','white'))
        if args.mode in ['R','B']:
            write(colored('-t: ' + str(args.timeout), 'magenta')+colored(' The number of seconds to wait for a an archived response.','white'))
        if args.mode in ['R','B'] or (args.mode == 'U' and not args.xcc):
            write(colored('-p: ' + str(args.processes), 'magenta')+colored(' The number of parallel requests made.','white'))
        write(colored('-r: ' + str(args.retries), 'magenta')+colored(' The number of retries for requests that get connection error or rate limited.','white'))
        
        if not args.xwm:
            write(colored('-wrlr: ' + str(args.wayback_rate_limit_retry), 'magenta')+colored(' The number of minutes to wait for a rate limit pause on Wayback Machine (archive.org) instead of stopping with a 429 error.','white'))
        if not args.xus:
            write(colored('-urlr: ' + str(args.urlscan_rate_limit_retry), 'magenta')+colored(' The number of minutes to wait for a rate limit pause on URLScan.io instead of stopping with a 429 error.','white'))
            
        write()

    except Exception as e:
        writerr(colored('ERROR showOptions: ' + str(e), 'red'))

def getConfig():
    """
    Try to get the values from the config file, otherwise use the defaults
    """
    global FILTER_CODE, FILTER_MIME, FILTER_URL, FILTER_KEYWORDS, URLSCAN_API_KEY, VIRUSTOTAL_API_KEY, CONTINUE_RESPONSES_IF_PIPED, subs, path, waymorePath, inputIsDomainANDPath, HTTP_ADAPTER, HTTP_ADAPTER_CC, argsInput, terminalWidth, MATCH_CODE, WEBHOOK_DISCORD, DEFAULT_OUTPUT_DIR
    try:
        
        # Set terminal width
        try:
            terminalWidth = os.get_terminal_size().columns
        except:
            terminalWidth = 135
        
        # If the input doesn't have a / then assume it is a domain rather than a domain AND path
        if str(argsInput).find('/') < 0:
            path = '/*'
            inputIsDomainANDPath = False
        else:
            # If there is only one / and is the last character, remove it
            if str(argsInput).count('/') == 1 and str(argsInput)[-1:] == '/':
                argsInput = argsInput.replace('/','')
                path = '/*'
                inputIsDomainANDPath = False
            else:
                path = '*'
                inputIsDomainANDPath = True

        # If the -no-subs argument was passed, don't include subs
        # Also, if a path is passed, the subs will not be used
        if args.no_subs or inputIsDomainANDPath:
            subs = ''
        
        # Set up an HTTPAdaptor for retry strategy when making requests
        try:
            retry= Retry(
                total=args.retries,
                backoff_factor=1.1,
                status_forcelist=[429, 500, 502, 503, 504],
                raise_on_status=False,
                respect_retry_after_header=False
            )
            HTTP_ADAPTER = HTTPAdapter(max_retries=retry)
        except Exception as e:
            writerr(colored('ERROR getConfig 2: ' + str(e), 'red'))
            
        # Set up an HTTPAdaptor for retry strategy for Common Crawl when making requests
        try:
            retry= Retry(
                total=args.retries+20,
                backoff_factor=1.1,
                status_forcelist=[503],
                raise_on_status=False,
                respect_retry_after_header=False
            )
            HTTP_ADAPTER_CC = HTTPAdapter(max_retries=retry)
        except Exception as e:
            writerr(colored('ERROR getConfig 3: ' + str(e), 'red'))
            
        # Try to get the config file values
        useDefaults = False
        try:
            # Get the path of the config file. If -c / --config argument is not passed, then it defaults to config.yml in the same directory as the run file      
            waymorePath = (
                Path(os.path.join(os.getenv('APPDATA', ''), 'waymore')) if os.name == 'nt'
                else Path(os.path.join(os.path.expanduser("~"), ".config", "waymore")) if os.name == 'posix'
                else Path(os.path.join(os.path.expanduser("~"), "Library", "Application Support", "waymore")) if os.name == 'darwin'
                else None
            )
            waymorePath.absolute
            if args.config is None:  
                if waymorePath == '':
                    configPath = 'config.yml'
                else:
                    configPath = Path(waymorePath / 'config.yml')
            else:
                configPath = Path(args.config)
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
            
            # If the argument -fc was passed, don't try to get from the config
            if args.fc:
                FILTER_CODE = args.fc
            else:
                try:
                    FILTER_CODE = str(config.get('FILTER_CODE'))
                    if str(FILTER_CODE) == 'None':
                        writerr(colored('No value for "FILTER_CODE" in config.yml - default set', 'yellow'))
                        FILTER_CODE = ''
                except Exception as e:
                    writerr(colored('Unable to read "FILTER_CODE" from config.yml - default set', 'red'))
                    FILTER_CODE = DEFAULT_FILTER_CODE
            
            # Set the match codes if they were passed
            if args.mc:
                MATCH_CODE = args.mc
            
            try:
                URLSCAN_API_KEY = config.get('URLSCAN_API_KEY')
                if str(URLSCAN_API_KEY) == 'None':
                    if not args.xus:
                        writerr(colored('No value for "URLSCAN_API_KEY" in config.yml - consider adding (you can get a FREE api key at urlscan.io)', 'yellow'))
                    URLSCAN_API_KEY = ''
            except Exception as e:
                writerr(colored('Unable to read "URLSCAN_API_KEY" from config.yml - consider adding (you can get a FREE api key at urlscan.io)', 'red'))
                URLSCAN_API_KEY = ''
                
            try:
                VIRUSTOTAL_API_KEY = config.get('VIRUSTOTAL_API_KEY')
                if str(VIRUSTOTAL_API_KEY) == 'None':
                    if not args.xvt:
                        writerr(colored('No value for "VIRUSTOTAL_API_KEY" in config.yml - consider adding (you can get a FREE api key at virustotal.com)', 'yellow'))
                    VIRUSTOTAL_API_KEY = ''
            except Exception as e:
                writerr(colored('Unable to read "VIRUSTOTAL_API_KEY" from config.yml - consider adding (you can get a FREE api key at virustotal.com)', 'red'))
                VIRUSTOTAL_API_KEY = ''
            
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
                writerr(colored('Unable to read "CONTINUE_RESPONSES_IF_PIPED" from config.yml - default set', 'red'))
                CONTINUE_RESPONSES_IF_PIPED = True
            
            if args.notify_discord:
                try:
                    WEBHOOK_DISCORD = config.get('WEBHOOK_DISCORD')
                    if str(WEBHOOK_DISCORD) == 'None' or str(WEBHOOK_DISCORD) == 'YOUR_WEBHOOK':
                        writerr(colored('No value for "WEBHOOK_DISCORD" in config.yml - default set', 'yellow'))
                        WEBHOOK_DISCORD = ''
                except Exception as e:
                    writerr(colored('Unable to read "WEBHOOK_DISCORD" from config.yml - default set', 'red'))
                    WEBHOOK_DISCORD = ''
            
            try:
                DEFAULT_OUTPUT_DIR = config.get('DEFAULT_OUTPUT_DIR')
                if str(DEFAULT_OUTPUT_DIR) == 'None' or str(DEFAULT_OUTPUT_DIR) == '':
                    DEFAULT_OUTPUT_DIR = os.path.expanduser(str(waymorePath))
                else:
                    # Test if DEFAULT_OUTPUT_DIR is a valid directory
                    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
                        writerr(colored('The "DEFAULT_OUTPUT_DIR" of "'+str(DEFAULT_OUTPUT_DIR)+'" is not a valid directory. Using "'+str(waymorePath)+'" instead.', 'yellow'))
                        DEFAULT_OUTPUT_DIR = os.path.expanduser(str(waymorePath))
                    else:
                        DEFAULT_OUTPUT_DIR = os.path.expanduser(DEFAULT_OUTPUT_DIR)
            except Exception as e:
                writerr(colored('Unable to read "DEFAULT_OUTPUT_DIR" from config.yml - default set', 'red'))
                DEFAULT_OUTPUT_DIR = waymorePath
                    
        except yaml.YAMLError as e: # A scan error occurred reading the file
            useDefaults = True
            if args.config is None:
                writerr(colored('WARNING: There seems to be a formatting error in "config.yml", so using default values', 'yellow'))
            else:
                writerr(colored('WARNING: There seems to be a formatting error in "' + args.config + '", so using default values', 'yellow'))
                
        except FileNotFoundError as e: # The config file wasn't found
            useDefaults = True
            if args.config is None:
                writerr(colored('WARNING: Cannot find file "config.yml", so using default values', 'yellow'))
            else:
                writerr(colored('WARNING: Cannot find file "' + args.config + '", so using default values', 'yellow'))
                
        except Exception as e: # Another error occurred
            useDefaults = True
            if args.config is None:
                writerr(colored('WARNING: Cannot read file "config.yml", so using default values. The following error occurred: ' + str(e), 'yellow'))
            else:
                writerr(colored('WARNING: Cannot read file "' + args.config + '", so using default values. The following error occurred: ' + str(e), 'yellow'))
            
        # Use defaults if required
        if useDefaults:
            FILTER_URL = DEFAULT_FILTER_URL
            FILTER_MIME = DEFAULT_FILTER_MIME
            FILTER_CODE = DEFAULT_FILTER_CODE
            URLSCAN_API_KEY = ''
            VIRUSTOTAL_API_KEY = ''
            FILTER_KEYWORDS = ''
            CONTINUE_RESPONSES_IF_PIPED = True
            WEBHOOK_DISCORD = ''
            DEFAULT_OUTPUT_DIR = os.path.expanduser('~/.config/waymore')
            outputInlineJSDir = DEFAULT_OUTPUT_DIR
            
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

# Add a link to the linksFound collection for archived responses (included timestamp preifx)
def linksFoundResponseAdd(link):
    global linksFound, argsInput, argsInputHostname
     
    try:
        if inputIsDomainANDPath:
            checkInput = argsInput
        else:
            checkInput = argsInputHostname
        
        # Remove the timestamp
        linkWithoutTimestamp = link.split('/', 1)[-1]
        
        # If the link specifies port 80 or 443, e.g. http://example.com:80, then remove the port
        parsed = urlparse(linkWithoutTimestamp.strip())
        if parsed.port in (80, 443):
            new_netloc = parsed.hostname
            parsed_url = parsed._replace(netloc=new_netloc).geturl()
        else:
            parsed_url = linkWithoutTimestamp

        # Don't write it if the link does not contain the requested domain (this can sometimes happen)
        if parsed_url.find(checkInput) >= 0:
            linksFound.add(link)
    except Exception as e:
        linksFound.add(link)
        
# Add a link to the linksFound collection
def linksFoundAdd(link):
    global linksFound, argsInput, argsInputHostname
    
    try:
        if inputIsDomainANDPath:
            checkInput = argsInput
        else:
            checkInput = argsInputHostname
        
        # If the link specifies port 80 or 443, e.g. http://example.com:80, then remove the port
        parsed = urlparse(link.strip())
        if parsed.port in (80, 443):
            new_netloc = parsed.hostname
            parsed_url = parsed._replace(netloc=new_netloc).geturl()
        else:
            parsed_url = link
        
        # Don't write it if the link does not contain the requested domain (this can sometimes happen)
        if parsed_url.find(checkInput) >= 0:
            linksFound.add(link)
    except Exception as e:
        linksFound.add(link)
    
def processArchiveUrl(url):
    """
    Get the passed web archive response
    """
    global stopProgram, successCount, failureCount, fileCount, DEFAULT_OUTPUT_DIR, totalResponses, indexFile, argsInput, continueRespFile, REGEX_404
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
                    resp = session.get(url = archiveUrl, headers={"User-Agent":userAgent}, allow_redirects = True)
                    archiveHtml = str(resp.text)
                    try:
                        contentType = resp.headers.get("Content-Type").split(';')[0].lower()
                    except:
                        contentType = ''
                    
                    # Only create a file if there is a response
                    if len(archiveHtml) != 0:
                        
                        # If the FILTER_CODE includes 404, and it only process if it doesn't seem to be a custom 404 page
                        if '404' in FILTER_CODE and not re.findall(REGEX_404, archiveHtml, re.DOTALL|re.IGNORECASE):
                        
                            # Add the URL as a comment at the start of the response
                            if args.url_filename:
                                archiveHtml = '/* Original URL: ' + archiveUrl + ' */\n' + archiveHtml
                            
                            # Remove all web archive references in the response
                            archiveHtml = re.sub(r'\<script type=\"text\/javascript" src=\"\/_static\/js\/bundle-playback\.js\?v=[A-Za-z0-9]*" charset="utf-8"><\/script>\n<script type="text\/javascript" src="\/_static\/js\/wombat\.js.*\<\!-- End Wayback Rewrite JS Include --\>','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'\<script src=\"\/\/archive\.org.*\<\!-- End Wayback Rewrite JS Include --\>','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'\<script\>window\.RufflePlayer[^\<]*\<\/script\>','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'\<\!-- BEGIN WAYBACK TOOLBAR INSERT --\>.*\<\!-- END WAYBACK TOOLBAR INSERT --\>','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'(}\n)?(\/\*|<!--\n)\s*FILE ARCHIVED ON.*108\(a\)\(3\)\)\.\n(\*\/|-->)','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'var\s_____WB\$wombat\$assign\$function.*WB\$wombat\$assign\$function_____\(\"opener\"\);','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'(\<\!--|\/\*)\nplayback timings.*(--\>|\*\/)','',archiveHtml,1,flags=re.DOTALL|re.IGNORECASE)
                            archiveHtml = re.sub(r'((https:)?\/\/web\.archive\.org)?\/web\/[0-9]{14}([A-Za-z]{2}\_)?\/','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'((https:)?\\\/\\\/web\.archive\.org)?\\\/web\\\/[0-9]{14}([A-Za-z]{2}\_)?\\\/','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'((https:)?%2F%2Fweb\.archive\.org)?%2Fweb%2F[0-9]{14}([A-Za-z]{2}\_)?%2F','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'((https:)?\\u002F\\u002Fweb\.archive\.org)?\\u002Fweb\\u002F[0-9]{14}([A-Za-z]{2}\_)?\\u002F','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'\<script type=\"text\/javascript\">\s*__wm\.init\(\"https:\/\/web\.archive\.org\/web\"\);[^\<]*\<\/script\>','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'\<script type=\"text\/javascript\" src="https:\/\/web-static\.archive\.org[^\<]*\<\/script\>','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'\<link rel=\"stylesheet\" type=\"text\/css\" href=\"https:\/\/web-static\.archive\.org[^\<]*\/\>','',archiveHtml,flags=re.IGNORECASE)
                            archiveHtml = re.sub(r'\<\!-- End Wayback Rewrite JS Include --\>','',archiveHtml,re.IGNORECASE)
                            
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
                                
                                # Determine extension of file from the content-type using the mimetypes library
                                extension = ''
                                try:
                                    # Get path extension
                                    targetUrl = 'https://' + url.split("://")[1]
                                    parsed = urlparse(targetUrl.strip())
                                    path = parsed.path
                                    extension = path[path.rindex('.')+1:]
                                except:
                                    pass
                                
                                # If the extension is blank, numeric, longer than 4 characters or not alphanumeric - then it's not a valid file type so check contentType
                                if extension == '' or extension.isnumeric() or not extension.isalnum() or len(extension) > 4:
                                    # Determine the extension from the content type
                                    try:
                                        if contentType != '':
                                            extension = contentType.split('/')[1].replace('x-','')
                                        if extension == '':
                                            extension = contentType.lower()
                                    except:
                                        pass
                                    if 'html' in extension:
                                        extension = 'html'
                                    elif 'javascript' in extension:
                                        extension = 'js'
                                    elif 'json' in extension:
                                        extension = 'json'
                                    elif 'css' in extension:
                                        extension = 'css'
                                    elif 'pdf' in extension:
                                        extension = 'pdf'
                                    elif 'plain' == extension:
                                        extension = 'txt'
                                    
                                    # If extension is still blank, set to html if the content ends with HTML tag, otherwise set to unknown
                                    if extension == '':
                                        if archiveHtml.lower().strip().endswith('</html>') or archiveHtml.lower().strip().startswith('<!doctype html') or archiveHtml.lower().strip().startswith('<html'):
                                            extension = 'html'
                                        else:
                                            extension = 'unknown'
    
                                fileName = fileName + '.' + extension
                            
                            # If -oR / --output-responses was passed then add the file to that directory, 
                            # else add to the default "results/{target.domain}" directory in the same path as the .py file
                            if args.output_responses != '':
                                filePath = args.output_responses + '/' + f'{fileName}'
                            else: 
                                filePath = (DEFAULT_OUTPUT_DIR + '/results/' + str(argsInput).replace('/','-') + '/' + f'{fileName}')
                                
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
                                if os.environ.get('USER') == 'xnl':
                                    debugText = ''
                                    if archiveHtml.lower().find('archive.org') > 0:
                                        debugText = 'ARCHIVE.ORG'
                                    elif archiveHtml.lower().find('internet archive') > 0:
                                        debugText = 'INTERNET ARCHIVE'
                                    elif archiveHtml.lower().find('wombat') > 0:
                                        debugText = 'WOMBAT (JS)'
                                    if debugText != '':
                                        writerr(colored(getSPACER('"' + fileName + '" CONTAINS ' + debugText + ' - CHECK ITS A VALID REFERENCE'), 'yellow'))
                            except:
                                pass
                                
                    successCount = successCount + 1
                
                except WayBackException as wbe:
                    failureCount = failureCount + 1
                    if verbose():
                        writerr(colored(getSPACER('[ ERR ] Wayback Machine (archive.org) returned a problem for "' + archiveUrl + '"'), 'red'))
                except ConnectionError as ce:
                    failureCount = failureCount + 1
                    if verbose():
                        writerr(colored(getSPACER('[ ERR ] Wayback Machine (archive.org) connection error for "' + archiveUrl + '"'), 'red'))
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
    global linksFound, subs, path, argsInput, checkWayback, checkCommonCrawl, checkAlienVault, checkURLScan, checkVirusTotal, DEFAULT_OUTPUT_DIR

    try:
        
        if args.check_only:
            totalRequests = checkWayback + checkCommonCrawl + checkAlienVault + checkURLScan + checkVirusTotal
            minutes = totalRequests*1 // 60
            hours = minutes // 60
            days = hours // 24
            if minutes < 5:
                write(colored('\n-> Getting URLs (e.g. at 1 req/sec) should be quite quick!','green'))
            elif hours < 2:
                write(colored('\n-> Getting URLs (e.g. at 1 req/sec) could take more than '+str(minutes)+' minutes.','green'))
            elif hours < 6:
                write(colored('\n-> Getting URLs (e.g. at 1 req/sec) could take more than '+str(hours)+' hours.','green'))
            elif hours < 24:
                write(colored('\n-> Getting URLs (e.g. at 1 req/sec) take more than '+str(hours)+' hours.','yellow'))
            elif days < 7:
                write(colored('\n-> Getting URLs (e.g. at 1 req/sec) could take more than '+str(days)+' days. Consider using arguments -lr, -ci, -from and -to wisely!','red'))
            else:
                write(colored('\n-> Getting URLs (e.g. at 1 req/sec) could take more than '+str(days)+' days!!! Consider using arguments -lr, -ci, -from and -to wisely!','red'))
            write('')
        else:
            linkCount = len(linksFound)
            write(getSPACER(colored('Links found for ' + subs + argsInput + ': ', 'cyan')+colored(str(linkCount) + ' 🤘','white'))+'\n')
            
            # If -oU / --output-urls was passed then use that file name, else use "waymore.txt" in the path of the .py file
            if args.output_urls == '':
                # Create 'results' and domain directory if needed
                createDirs()
            
                # If -oR / --output-responses was passed then set the path to that, otherwise it will be the "results/{target.domain}}" path
                if args.output_responses != '':
                    fullPath = args.output_responses + '/'
                else:
                    fullPath = str(DEFAULT_OUTPUT_DIR) + '/results/' + str(argsInput).replace('/','-') + '/'
                filename = fullPath + 'waymore.txt'
                filenameNew = fullPath + 'waymore.new'
                filenameOld = fullPath + 'waymore.old'
            else:
                filename = args.output_urls
                filenameNew = filename + '.new'
                filenameOld = filename + '.old'
                # If the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
                try:
                    if filename.find('/') > 0:
                        f = os.path.basename(filename)
                        p = filename[:-(len(f))-1]
                        if p != '' and not os.path.exists(p):
                            os.makedirs(p)
                except Exception as e:
                    if verbose():
                        writerr(colored('ERROR processURLOutput 6: ' + str(e), 'red'))
                    
            # If the -ow / --output_overwrite argument was passed and the file exists already, get the contents of the file to include
            appendedUrls = False
            if not args.output_overwrite:
                try:
                    with open(filename,'r') as existingLinks:
                        for link in existingLinks.readlines():
                            linksFound.add(link.strip())
                    appendedUrls = True
                except Exception as e:
                    pass
            
            # If the -nlf / --new-links-file argument is passed, rename the old links file if it exists
            try:
                if args.new_links_file: 
                    if os.path.exists(filename):
                        os.rename(filename, filenameOld)    
            except Exception as e:
                if verbose():
                    writerr(colored('ERROR processURLOutput 5: ' + str(e), 'red'))
                        
            try:
                # Open the output file
                outFile = open(filename,'w')
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
                    write(colored('No links were found so nothing written to file.', 'cyan'))
                else:   
                    if appendedUrls:
                        write(
                            colored('Links successfully appended to file ', 'cyan')+colored(filename,
                            'white')+colored(' and duplicates removed.','cyan'))
                    else:
                        write(
                            colored('Links successfully written to file ', 'cyan')+colored(filename,
                            'white'))

            try:
                # If the -nlf / --new-links-file argument is passes, create the .new file
                if args.new_links_file:
                    
                    # If the file and .old version exists then get the difference to write to .new file
                    if os.path.exists(filenameOld) and os.path.exists(filename):
                        
                        # Get all the old links
                        with open(filenameOld,'r') as oldFile:
                            oldLinks=set(oldFile.readlines())

                        # Get all the new links
                        with open(filename,'r') as newFile:
                            newLinks=set(newFile.readlines())

                        # Create a file with most recent new links
                        with open(filenameNew,'w') as newOnly:
                            for line in list(newLinks-oldLinks):
                                newOnly.write(line)

                        # Delete the old file
                        os.remove(filenameOld)
                    
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
    global successCount, failureCount, subs, fileCount, argsInput, DEFAULT_OUTPUT_DIR, responseOutputDirectory
    try:
            
        if failureCount > 0:
            if verbose():
                write(colored('\nResponses saved to ','cyan')+colored(responseOutputDirectory,'white') + colored(' for ' + subs + argsInput + ': ', 'cyan')+colored(str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘','white')+colored(' (' + str(failureCount) + ' failed)\n','red'))
            else:
                write(colored('\nResponses saved for ' + subs + argsInput + ': ', 'cyan')+colored(str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘','white')+colored(' (' + str(failureCount) + ' failed)\n','red'))
        else:
            if verbose():
                write(colored('\nResponses saved to ','cyan')+colored(responseOutputDirectory,'white') + colored(' for ' + subs + argsInput + ': ', 'cyan')+colored(str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘\n','white'))
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
        raise argparse.ArgumentTypeError('The number of processes must be between 1 and 5. Be kind to Wayback Machine (archive.org) and commoncrawl.org! :)')     
    return x

def stripUnwanted(url):
    """
    Strip the scheme, port number, query string and fragment form any input values if they have them
    """
    parsed = urlparse(url)
    # Strip scheme
    scheme = "%s://" % parsed.scheme
    strippedUrl = parsed.geturl().replace(scheme, '', 1)
    # Strip query string and fragment
    strippedUrl = strippedUrl.split('#')[0].split('?')[0]
    # Strip port number
    if re.search(r'^[^/]*:[0-9]+', strippedUrl):
        strippedUrl = re.sub(r':[0-9]+','', strippedUrl, 1)
    return strippedUrl

def validateArgInput(x):
    """
    Validate the -i / --input argument.
    Ensure it is a domain only, or a URL, but with no schema or query parameters or fragment
    """
    global inputValues, isInputFile
    # If the input was given through STDIN (piped from another program) then 
    if x == '<stdin>':
        stdinFile = sys.stdin.readlines()
        count = 0
        for line in stdinFile:
            # Remove newline characters, and also *. if the domain starts with this
            inputValues.add(stripUnwanted(line.rstrip('\n').lstrip('*.')))
            count = count + 1
        if count > 1:
            isInputFile = True
    else:
        # Determine if a single input was given, or a file
        if os.path.isfile(x):
            isInputFile = True
            # Open file and put all values in input list
            with open(x, 'r') as inputFile:
                lines = inputFile.readlines()          
            # Check if any lines start with a *. and replace without the *.
            for line in lines:
                inputValues.add(stripUnwanted(line.lstrip('*.')))
        else:
            # Just add the input value to the input list
            inputValues.add(stripUnwanted(x))
    return x

def validateArgStatusCodes(x):
    """
    Validate the -fc and -mc arguments
    Only allow 3 digit numbers separated by a comma
    """
    invalid = False
    codes = x.split(',')
    for code in codes:
        if len(code) != 3 or not code.isdigit():
            invalid = True
            break
    if invalid:
        raise argparse.ArgumentTypeError('Pass HTTP status codes separated by a comma')     
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
                                httpCode = 'UNKNOWN'
                            
                            # Compare the HTTP code gainst the Code exclusions and matches
                            if MATCH_CODE != '':
                                match = re.search(r'('+re.escape(MATCH_CODE).replace(',','|')+')', httpCode, flags=re.IGNORECASE)
                                if match is None:
                                    addLink = False
                            else:
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
                                if args.keywords_only == '#CONFIG':
                                    match = re.search(r'('+re.escape(FILTER_KEYWORDS).replace(',','|')+')', foundUrl, flags=re.IGNORECASE)
                                else:
                                    match = re.search(r'('+args.keywords_only+')', foundUrl, flags=re.IGNORECASE)
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
    global linksFound, waymorePath, subs, path, stopProgram, totalPages, stopSource, argsInput, checkAlienVault, inputIsSubDomain, argsInputHostname
    
    # Write the file of URL's for the passed domain/URL
    try:
        stopSource = False
        originalLinkCount = len(linksFound)
        
        # Set the Alien Vault API indicator types of domain or hostname (has subdomain)
        if inputIsSubDomain:
            indicatorType = 'hostname'
        else:
            indicatorType = 'domain'
        
        url = ALIENVAULT_URL.replace('{TYPE}',indicatorType).replace('{DOMAIN}',quote(argsInputHostname))+'&page='
        
        # Get the number of pages (i.e. separate requests) that are going to be made to alienvault.com
        totalPages = 0
        try:
            if not args.check_only:
                write(colored('\rGetting the number of alienvault.com pages to search...\r','cyan'))
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
            resp = session.get(url+'&showNumPages=True', headers={"User-Agent":userAgent}) 
        except Exception as e:
            writerr(colored(getSPACER('[ ERR ] Unable to get links from alienvault.com: ' + str(e)), 'red'))
            return
        
        # If the rate limit was reached end now
        if resp.status_code == 429:
            writerr(colored(getSPACER('[ 429 ] Alien Vault rate limit reached so unable to get links.'),'red'))
            return
        
        if verbose():
            write(getSPACER(colored('The Alien Vault URL requested to get links: ','magenta')+colored(url,'white'))+'\n')
        
        # Carry on if something was found
        if resp.text.lower().find('"error": "') < 0:

            try:
                # Get the JSON response
                jsonResp = json.loads(resp.text.strip())
                
                # Try to get the number of results
                totalUrls = int(jsonResp['full_size'])
            except:
                writerr(colored(getSPACER('[ ERR ] There was an unexpected response from the Alien Vault API'),'red'))
                totalUrls = 0
            
            # If there are results, carry on
            if totalUrls > 0 or args.check_only:
                
                # Get total pages 
                totalPages = math.ceil(totalUrls / 500)
                
                # If the argument to limit the requests was passed and the total pages is larger than that, set to the limit
                if args.limit_requests != 0 and totalPages > args.limit_requests:
                    totalPages = args.limit_requests

                if args.check_only:
                    if totalPages == 0:
                        checkAlienVault = 1
                    else:
                        checkAlienVault = totalPages
                    write(colored('Get URLs from Alien Vault: ','cyan')+colored(str(checkAlienVault)+' requests','white'))
                else:
                    # if the page number was found then display it, but otherwise we will just try to increment until we have everything       
                    write(colored('\rGetting links from ' + str(totalPages) + ' alienvault.com API requests (this can take a while for some domains)...\r','cyan'))

                    # Get a list of all the page URLs we need to visit
                    pages = []
                    for page in range(1, totalPages + 1):
                        pages.append(url+str(page))

                    # Process the URLs from alien vault 
                    if stopProgram is None:
                        p = mp.Pool(args.processes)
                        p.map(processAlienVaultPage, pages)
                        p.close()
                        p.join()
        else:
            if verbose():
                writerr(colored(getSPACER('[ ERR ] An error was returned in the alienvault.com response.')+'\n', 'red'))
        
        if not args.check_only:
            linkCount = len(linksFound) - originalLinkCount
            if args.xwm and args.xcc:
                write(getSPACER(colored('Links found on alienvault.com: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
            else:
                write(getSPACER(colored('Extra links found on alienvault.com: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
        
    except Exception as e:
        writerr(colored('ERROR getAlienVaultUrls 1: ' + str(e), 'red'))

def processURLScanUrl(url, httpCode, mimeType):
    """
    Process a specific URL from urlscan.io to determine whether to save the link
    """
    global argsInput, argsInputHostname
    
    addLink = True
    
    try:      
        # If filters are required then test them
        if not args.filter_responses_only:
            
            # If the user requested -n / --no-subs then we don't want to add it if it has a sub domain (www. will not be classed as a sub domain)
            if args.no_subs:
                match = re.search(r'^[A-za-z]*\:\/\/(www\.)?'+re.escape(argsInputHostname), url, flags=re.IGNORECASE)
                if match is None:
                    addLink = False
        
            # If the user didn't requested -f / --filter-responses-only then check http code
            # Note we can't check MIME filter because it is not returned by URLScan API
            if addLink and not args.filter_responses_only: 
                
                # Compare the HTTP code against the Code exclusions and matches
                if MATCH_CODE != '':
                    match = re.search(r'('+re.escape(MATCH_CODE).replace(',','|')+')', httpCode, flags=re.IGNORECASE)
                    if match is None:
                        addLink = False
                else:
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
                    if args.keywords_only == '#CONFIG':
                        match = re.search(r'('+re.escape(FILTER_KEYWORDS).replace(',','|')+')', url, flags=re.IGNORECASE)
                    else:
                        match = re.search(r'('+args.keywords_only+')', url, flags=re.IGNORECASE)
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
            # Just get the hostname of the url 
            tldExtract = tldextract.extract(url)
            subDomain = tldExtract.subdomain
            if subDomain != '':
                subDomain = subDomain+'.'
            domainOnly = subDomain+tldExtract.domain+'.'+tldExtract.suffix
            
            # URLScan might return URLs that aren't for the domain passed so we need to check for those and not process them
            # Check the URL
            match = re.search(r'(^|\.)'+re.escape(argsInputHostname)+'$', domainOnly, flags=re.IGNORECASE)
            if match is not None:
                linksFoundAdd(url)  
            
    except Exception as e:
        writerr(colored('ERROR processURLScanUrl 1: ' + str(e), 'red'))
        
def getURLScanUrls():
    """
    Get URLs from the URLSCan API, urlscan.io
    """
    global URLSCAN_API_KEY, linksFound, linkMimes, waymorePath, subs, stopProgram, stopSource, argsInput, checkURLScan, argsInputHostname
    
    # Write the file of URL's for the passed domain/URL
    try:
        requestsMade = 0
        stopSource = False
        linkMimes = set()
        originalLinkCount = len(linksFound)
        
        # Set the URL to just the hostname
        url = URLSCAN_URL.replace('{DOMAIN}',quote(argsInputHostname))

        if verbose():
            write(colored('The URLScan URL requested to get links: ','magenta')+colored(url+'\n','white'))
        
        if not args.check_only:           
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
            write(colored(getSPACER('[ ERR ] Unable to get links from urlscan.io: ' + str(e)), 'red'))
            return
        
        # If the rate limit was reached then determine if to wait and then try again
        if resp.status_code == 429:
            # Get the number of seconds the rate limit resets
            match = re.search(r'Reset in (\d+) seconds', resp.text, flags=re.IGNORECASE)
            if match is not None:
                seconds = int(match.group(1))
                if seconds <= args.urlscan_rate_limit_retry * 60:
                    writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached, so waiting for another '+str(seconds)+' seconds before continuing...'),'yellow'))
                    time.sleep(seconds+1)
                    try:
                        resp = session.get(url, headers={'User-Agent':userAgent, 'API-Key':URLSCAN_API_KEY})
                        requestsMade = requestsMade + 1
                    except Exception as e:
                        write(colored(getSPACER('[ ERR ] Unable to get links from urlscan.io: ' + str(e)), 'red'))
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
                    writerr(colored(getSPACER('[ ERR ] Unable to get links from urlscan.io: ' + str(e)), 'red'))
                    return
                
                # If the rate limit was reached end now
                if resp.status_code == 429:
                    writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached without API Key so unable to get links.'),'red'))
                    return
            else:
                writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached so unable to get links.'),'red'))
                return
        elif resp.status_code != 200:
            writerr(colored(getSPACER('[ ' + str(resp.status_code) + ' ] Unable to get links from urlscan.io'),'red'))
            return
        
        try:
            # Get the JSON response
            jsonResp = json.loads(resp.text.strip())

            # Get the number of results
            totalUrls = int(jsonResp['total'])
        except:
            writerr(colored(getSPACER('[ ERR ] There was an unexpected response from the URLScan API'),'red'))
            totalUrls = 0
        
        # Carry on if something was found
        if args.check_only:
            try:
                hasMore = jsonResp['has_more']
                if hasMore:
                    write(colored('Get URLs from URLScan: ','cyan')+colored('UNKNOWN requests','white'))
                else:
                    write(colored('Get URLs from URLScan: ','cyan')+colored('1 request','white'))
            except:
                pass
            checkURLScan = 1
            
        else:
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

                        # Also get the "task" url field
                        try:
                            taskUrl = urlSection['task']['url']
                            if not taskUrl.startswith('http'):
                                taskUrl = 'http://' + taskUrl
                        except:
                            taskUrl = ''
                        
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
                            httpCode = 'UNKNOWN'
                        
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
                            
                        # If a task url was found the process it
                        if taskUrl != '':    
                            processURLScanUrl(taskUrl, httpCode, mimeType)
                    
                    # If we have the field value to go to the next page...
                    if searchAfter != '':
                    
                        keepTrying = True
                        while not stopSource and keepTrying:
                            keepTrying = False
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
                                writerr(colored(getSPACER('[ ERR ] Unable to get links from urlscan.io: ' + str(e)), 'red'))
                                pass
                            
                            # If the rate limit was reached 
                            if resp.status_code == 429:
                                # Get the number of seconds the rate limit resets
                                match = re.search(r'Reset in (\d+) seconds', resp.text, flags=re.IGNORECASE)
                                if match is not None:
                                    seconds = int(match.group(1))
                                    if seconds <= args.urlscan_rate_limit_retry * 60:
                                        writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached, so waiting for another '+str(seconds)+' seconds before continuing...'),'yellow'))
                                        time.sleep(seconds+1)
                                        keepTrying = True
                                        continue
                                    else:
                                        writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached (waiting time of '+str(seconds)+'), so stopping. Links that have already been retrieved will be saved.'),'red'))
                                        stopSource = True
                                        pass
                                else:
                                    writerr(colored(getSPACER('[ 429 ] URLScan rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                                    stopSource = True
                                    pass
                            elif resp.status_code != 200:
                                writerr(colored(getSPACER('[ ' + str(resp.status_code) + ' ] Unable to get links from urlscan.io'),'red'))
                                stopSource = True
                                pass

                        if not stopSource:
                            # Get the JSON response
                            jsonResp = json.loads(resp.text.strip())
                            
                            # If there are no more results, or if the requests limit was specified and has been exceeded, then stop
                            if jsonResp['results'] is None or len(jsonResp['results']) == 0 or (args.limit_requests != 0 and requestsMade > args.limit_requests):
                                stopSource = True
        
            # Show the MIME types found (in case user wants to exclude more)
            if verbose() and len(linkMimes) > 0:
                linkMimes.discard('warc/revisit')
                write(getSPACER(colored('MIME types found: ','magenta')+colored(str(linkMimes),'white'))+'\n')
                        
            linkCount = len(linksFound) - originalLinkCount
            if args.xwm and args.xcc and args.xav:
                write(getSPACER(colored('Links found on urlscan.io: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
            else:
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
                resp = None
                userAgent = random.choice(USER_AGENT)
                page = url.split('page=')[1]
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER)
                session.mount('http://', HTTP_ADAPTER)
                resp = session.get(url, headers={"User-Agent":userAgent})  
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] Wayback Machine (archive.org) connection error for page ' + page), 'red'))
                resp = None
                return
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Error getting response for page ' + page + ' - ' + str(e)),'red'))
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                        # If a status other of 429, then stop processing Wayback Machine
                        if resp.status_code == 429:
                            if args.wayback_rate_limit_retry > 0:
                                seconds = args.wayback_rate_limit_retry * 60
                                if args.processes == 1:
                                    writerr(colored('\r[ 429 ] Wayback Machine (archive.org) rate limit reached on page '+str(page)+' of '+str(totalPages)+', so waiting for '+str(seconds)+' seconds before continuing...\r','yellow'))
                                else:
                                    writerr(colored('\r[ 429 ] Wayback Machine (archive.org) rate limit reached, so waiting for '+str(seconds)+' seconds before continuing...\r','yellow'))
                                time.sleep(seconds)
                                try:
                                    resp = session.get(url, headers={"User-Agent":userAgent})
                                except ConnectionError as ce:
                                    writerr(colored(getSPACER('[ ERR ] Wayback Machine (archive.org) connection error for page ' + page), 'red'))
                                    resp = None
                                    return
                                except Exception as e:
                                    writerr(colored(getSPACER('[ ERR ] Error getting response for page ' + page + ' - ' + str(e)),'red'))
                                    resp = None
                                    return
                                
                        if resp.status_code == 429:    
                            writerr(colored(getSPACER('[ 429 ] Wayback Machine (archive.org) rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                            stopSource = True
                            return
                        # If a status other of 503, then the site is unavailable
                        if resp.status_code == 503:
                            writerr(colored(getSPACER('[ 503 ] Wayback Machine (archive.org) is currently unavailable. It may be down for maintenance. You can check https://web.archive.org/cdx/ to verify.'),'red'))
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
                except ConnectionError as ce:
                    writerr(colored(getSPACER('[ ERR ] Wayback Machine (archive.org) connection error for page ' + page), 'red'))
                    resp = None
                    return
                except Exception as e:
                    writerr(colored(getSPACER('[ ERR ] Error getting response for page ' + page + ' - ' + str(e)),'red'))
                    resp = None
                    return
            
            # Get the URLs and MIME types. Each line is a separate JSON string
            try:
                for line in resp.iter_lines():
                    results = line.decode("utf-8")
                    foundUrl = fixArchiveOrgUrl(str(results).split(' ')[1])
                    
                    # If --filter-responses-only wasn't used, then check the URL exclusions
                    if args.filter_responses_only:
                        match = None
                    else:
                        match = re.search(r'('+re.escape(FILTER_URL).replace(',','|')+')', foundUrl, flags=re.IGNORECASE)
                    if match is None:
                        # Only get MIME Types if --verbose option was selected
                        if verbose():
                            try:
                                linkMimes.add(str(results).split(' ')[2])
                            except Exception as e:
                                if verbose():
                                    writerr(colored(getSPACER('ERROR processWayBackPage 2: Cannot get MIME type from line: ' + str(line)),'red'))
                                    write(resp.text)
                        try:
                            linksFoundAdd(foundUrl)
                        except Exception as e:
                            if verbose():
                                writerr(colored(getSPACER('ERROR processWayBackPage 3: Cannot get link from line: ' + str(line)),'red'))         
                                write(resp.text)       
            except Exception as e:
                if verbose():
                    writerr(colored(getSPACER('ERROR processWayBackPage 4: ' + str(line)),'red'))   
        else:
            pass
    except Exception as e:
        if verbose():
            writerr(colored("ERROR processWayBackPage 1: " + str(e), "red"))
    
def getWaybackUrls():
    """
    Get URLs from the Wayback Machine, archive.org
    """
    global linksFound, linkMimes, waymorePath, subs, path, stopProgram, totalPages, stopSource, argsInput, checkWayback
    
    # Write the file of URL's for the passed domain/URL
    try:
        stopSource = False
        # If there any + in the MIME types, e.g. image/svg+xml, then replace the + with a . otherwise the wayback API does not recognise it
        filterMIME = '&filter=!mimetype:warc/revisit|' + re.escape(FILTER_MIME).replace(',','|').replace('+','.') 
        if MATCH_CODE != '':
            filterCode = '&filter=statuscode:' + re.escape(MATCH_CODE).replace(',','|')
        else:
            filterCode = '&filter=!statuscode:' + re.escape(FILTER_CODE).replace(',','|')
        
        # Set keywords filter if -ko argument passed
        filterKeywords = ''
        if args.keywords_only:
            if args.keywords_only == '#CONFIG':
                filterKeywords = '&filter=original:.*(' + re.escape(FILTER_KEYWORDS).replace(',','|') + ').*'
            else:
                filterKeywords = '&filter=original:.*(' + args.keywords_only + ').*'
            
        if args.filter_responses_only:
            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(argsInput) + path).replace('{COLLAPSE}','') + '&page='
        else:
            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(argsInput) + path).replace('{COLLAPSE}','') + filterMIME + filterCode + filterKeywords + '&page='
        
        # Get the number of pages (i.e. separate requests) that are going to be made to archive.org
        totalPages = 0
        try:
            if not args.check_only:
                write(colored('\rGetting the number of Wayback Machine (archive.org) pages to search...\r','cyan'))
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
            resp = session.get(url+'&showNumPages=True', headers={"User-Agent":userAgent}) 
            # Try to get the total number of pages. If there is a problem, we'll return totalPages = 0 which means we'll get everything back in one request 
            try:
                totalPages = int(resp.text.strip())
                
                # If the argument to limit the requests was passed and the total pages is larger than that, set to the limit
                if args.limit_requests != 0 and totalPages > args.limit_requests:
                    totalPages = args.limit_requests
            except:
                totalPages = -1
        except Exception as e:
            try:
                # If the rate limit was reached end now
                if resp.status_code == 429:
                    writerr(colored(getSPACER('[ 429 ] Wayback Machine (Archive.org) rate limit reached so unable to get links.'),'red'))
                    return
                
                # If a status other of 503, then the site is unavailable
                if resp.status_code == 503:
                    writerr(colored(getSPACER('[ 503 ] Wayback Machine (Archive.org) is currently unavailable. It may be down for maintenance. You can check https://web.archive.org/cdx/ to verify.'),'red'))
                    return
        
                if resp.text.lower().find('blocked site error') > 0:
                    writerr(colored(getSPACER('[ ERR ] Unable to get links from Wayback Machine (archive.org): Blocked Site Error (they block the target site)'), 'red'))
                else:
                    writerr(colored(getSPACER('[ ERR ] Unable to get links from Wayback Machine (archive.org): ' + str(resp.text.strip())), 'red'))
            except:
                if str(e).lower().find('alert access denied'):
                    writerr(colored(getSPACER('[ ERR ] Unable to get links from Wayback Machine (archive.org): Access Denied. Are you able to manually visit https://web.archive.org/? Your ISP may be blocking you, e.g. your adult content filter is on (why it triggers that filter I don\'t know, but it has happened!)'), 'red'))
                elif str(e).lower().find('connection refused'):
                    writerr(colored(getSPACER('[ ERR ] Unable to get links from Wayback Machine (archive.org): Connection Refused. Are you able to manually visit https://web.archive.org/? Your ISP may be blocking your IP)'), 'red'))
                else:
                    writerr(colored(getSPACER('[ ERR ] Unable to get links from Wayback Machine (archive.org): ' + str(e)), 'red'))
            return
        
        if args.check_only:
            if totalPages < 0:
                write(colored('Due to a change in Wayback Machine API, all URLs will be retrieved in one request and it is not possible to determine how long it will take, so please ignore this.','cyan'))
            else:
                checkWayback = totalPages
                write(colored('Get URLs from Wayback Machine: ','cyan')+colored(str(checkWayback)+' requests','white'))
        else:
            if verbose():
                write(colored('The archive URL requested to get links: ','magenta')+colored(url+'\n','white'))
            
            if totalPages < 0:
                write(colored('\rGetting links from Wayback Machine (archive.org) with one request (this can take a while for some domains)...\r','cyan'))

                processWayBackPage(url)
            else:
                # if the page number was found then display it, but otherwise we will just try to increment until we have everything  
                write(colored('\rGetting links from ' + str(totalPages) + ' Wayback Machine (archive.org) API requests (this can take a while for some domains)...\r','cyan'))

                # Get a list of all the page URLs we need to visit
                pages = []
                if totalPages == 1:
                    pages.append(url)
                else:
                    for page in range(0, totalPages):
                        pages.append(url+str(page))
                
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
                write(getSPACER(colored('Links found on Wayback Machine (archive.org): ', 'cyan')+colored(str(linkCount),'white'))+'\n')
            
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
            filterMIME = '&filter=!~mime:(warc/revisit|' 
            if FILTER_MIME.strip() != '':
                filterMIME = filterMIME + re.escape(FILTER_MIME).replace(',','|')
            filterMIME = filterMIME + ')'
            
            # Set status code filter
            filterCode = ''
            if MATCH_CODE.strip() != '':
                filterCode = '&filter=~status:(' + re.escape(MATCH_CODE).replace(',','|') + ')'
            else:
                filterCode = '&filter=!~status:(' + re.escape(FILTER_CODE).replace(',','|') + ')'
            
            # Set keywords filter if -ko argument passed
            filterKeywords = ''
            if args.keywords_only:
                if args.keywords_only == '#CONFIG':
                    filterKeywords = '&filter=~url:.*(' + re.escape(FILTER_KEYWORDS).replace(',','|') + ').*'
                else:
                    filterKeywords = '&filter=~url:.*(' + args.keywords_only + ').*'
                
            commonCrawlUrl = cdxApiUrl + '?output=json&fl=timestamp,url,mime,status,digest&url=' 
               
            if args.filter_responses_only:
                url = commonCrawlUrl + subs + quote(argsInput) + path
            else:
                url = commonCrawlUrl + subs + quote(argsInput) + path + filterMIME + filterCode + filterKeywords
            
            try:
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER_CC)
                session.mount('http://', HTTP_ADAPTER_CC)
                resp = session.get(url, stream=True, headers={"User-Agent":userAgent})   
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] Common Crawl connection error for index '+cdxApiUrl), 'red'))
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
                                writerr(colored(getSPACER('[ '+str(resp.status_code)+' ] Error for '+cdxApiUrl),'red'))
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

def getCommonCrawlIndexes():
    """
    Requests the Common Crawl index file "collinfo.json" if it is not cached locally, or if the local file is older than a month.
    """
    try:
        # Check if a local copy of the index file exists
        createFile = False
        collinfoPath = str(Path(__file__).parent.resolve())+'/collinfo.json'
        if os.path.exists(collinfoPath):
            # Check if the file was created over a month ago
            monthAgo = datetime.now() - timedelta(days=30)
            fileModTime = datetime.fromtimestamp(os.path.getctime(collinfoPath))
            if fileModTime < monthAgo:
                createFile = True
                # Delete the current file
                try:
                    os.remove(collinfoPath)
                except Exception as e:
                    writerr(colored(getSPACER('[ ERR ] Couldn\'t delete local version of Common Crawl index file: ' + str(e)), 'red'))
        else:
            createFile = True

        # If the local file exists then read that instead of requesting the index file again
        if not createFile:
            # Read the indexes from the local file    
            try:
                with open(collinfoPath,'r') as file:
                    jsonResp = file.read()
                file.close()
            except Exception as e:
                createFile = True
                writerr(colored(getSPACER('[ ERR ] Couldn\'t read local version of Common Crawl index file: ' + str(e)),'red'))
                
        # If the local file needs creating again then make a new request
        if createFile:
            try:
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                session = requests.Session()
                session.mount('https://', HTTP_ADAPTER_CC)
                session.mount('http://', HTTP_ADAPTER_CC)
                indexes = session.get(CCRAWL_INDEX_URL, headers={"User-Agent":userAgent})
            except ConnectionError as ce:
                writerr(colored(getSPACER('[ ERR ] Common Crawl connection error getting Index file'), 'red'))
                return
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Error getting Common Crawl index collection - ' + str(e)),'red'))
                return
            
            # If the rate limit was reached end now
            if indexes.status_code == 429:
                writerr(colored(getSPACER('[ 429 ] Common Crawl rate limit reached so unable to get links.'),'red'))
                return
            # If the rate limit was reached end now
            elif indexes.status_code == 503:
                writerr(colored(getSPACER('[ 503 ] Common Crawl seems to be unavailable.'),'red'))
                return
            elif indexes.status_code != 200:
                writerr(colored(getSPACER('[ '+str(indexes.status_code)+' ] Common Crawl did not retrun the indexes file.'),'red'))
                return
            
            # Get the the returned JSON
            jsonResp = indexes.text

            # Write the contents of the response to a local file so we don't request in future. Overwrite it if it exists
            try:
                f = open(collinfoPath, 'w')
                f.write(jsonResp)
                f.close()
            except Exception as e:
                writerr(colored(getSPACER('[ ERR ] Couldn\'t create local version of Common Crawl index file: ' + str(e)),'red'))
        
        # Get the API URLs from the returned JSON
        cdxApiUrls = set()
        collection = 0
        for values in json.loads(jsonResp):
            for key in values:
                if key == 'cdx-api':
                    if args.lcy != 0:
                        try:
                            indexYear = values[key].split("CC-MAIN-")[1][:4]
                            if int(indexYear) >= args.lcy:
                                cdxApiUrls.add(values[key])
                        except Exception as e:
                            writerr(colored(getSPACER('[ ERR ] Failed to get the year from index name ' + values[key] + ' - ' + str(e)),'red'))
                    else:
                        cdxApiUrls.add(values[key])
            collection = collection + 1
            if collection == args.lcc: break
                    
        return cdxApiUrls
        
    except Exception as e:
        writerr(colored('ERROR getCommonCrawlIndexes 1: ' + str(e), 'red'))
        
def getCommonCrawlUrls():
    """
    Get all Common Crawl index collections to get all URLs from each one
    """
    global linksFound, linkMimes, waymorePath, subs, path, stopSource, argsInput, checkCommonCrawl
    
    try:
        stopSource = False
        linkMimes = set()
        originalLinkCount = len(linksFound)
        
        # Set mime content type filter
        filterMIME = '&filter=!~mime:(warc/revisit|' 
        if FILTER_MIME.strip() != '':
            filterMIME = filterMIME + re.escape(FILTER_MIME).replace(',','|')
        filterMIME = filterMIME + ')'
        
        # Set status code filter
        filterCode = ''
        if MATCH_CODE.strip() != '':
            filterCode = '&filter=~status:(' + re.escape(MATCH_CODE).replace(',','|') + ')'
        else:
            filterCode = '&filter=!~status:(' + re.escape(FILTER_CODE).replace(',','|') + ')'
    
        if verbose():
            if args.filter_responses_only:
                url = '{CDX-API-URL}?output=json&fl=timestamp,url,mime,status,digest&url=' + subs + quote(argsInput) + path
            else:
                url = '{CDX-API-URL}?output=json&fl=timestamp,url,mime,status,digest&url=' + subs + quote(argsInput) + path + filterMIME + filterCode  
            write(colored('The commoncrawl index URL requested to get links (where {CDX-API-URL} is from ' + CCRAWL_INDEX_URL + '): ','magenta')+colored(url+'\n','white'))
        
        if not args.check_only:
            write(colored('\rGetting commoncrawl.org index collections list...\r','cyan'))
                  
        # Get the Common Crawl index collections
        cdxApiUrls = getCommonCrawlIndexes()
        
        if args.check_only:
            if args.lcc < len(cdxApiUrls):
                checkCommonCrawl = args.lcc+1
            else:
                checkCommonCrawl = len(cdxApiUrls)+1
            write(colored('Get URLs from Common Crawl: ','cyan')+colored(str(checkCommonCrawl)+' requests','white'))
        else:
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
            if args.xwm:
                write(getSPACER(colored('Links found on commoncrawl.org: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
            else:
                write(getSPACER(colored('Extra links found on commoncrawl.org: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
                    
    except Exception as e:
        writerr(colored('ERROR getCommonCrawlUrls 1: ' + str(e), 'red'))

def processVirusTotalUrl(url):
    """
    Process a specific URL from virustotal.io to determine whether to save the link
    """
    global argsInput, argsInputHostname
    
    addLink = True
    
    # If the url passed doesn't have a scheme, prefix with http://
    match = re.search(r'^[A-za-z]*\:\/\/', url, flags=re.IGNORECASE)
    if match is None: 
        url = 'http://'+url
        
    try:      
        # If filters are required then test them
        if not args.filter_responses_only:
            
            # If the user requested -n / --no-subs then we don't want to add it if it has a sub domain (www. will not be classed as a sub domain)
            if args.no_subs:
                match = re.search(r'^[A-za-z]*\:\/\/(www\.)?'+re.escape(argsInputHostname), url, flags=re.IGNORECASE)
                if match is None:
                    addLink = False
        
            # If the user didn't requested -f / --filter-responses-only then check http code
            # Note we can't check MIME filter because it is not returned by VirusTotal API
            if addLink and not args.filter_responses_only: 
                
                # Check the URL exclusions
                if addLink:
                    match = re.search(r'('+re.escape(FILTER_URL).replace(',','|')+')', url, flags=re.IGNORECASE)
                    if match is not None:
                        addLink = False            
                
                # Set keywords filter if -ko argument passed
                if addLink and args.keywords_only:
                    if args.keywords_only == '#CONFIG':
                        match = re.search(r'('+re.escape(FILTER_KEYWORDS).replace(',','|')+')', url, flags=re.IGNORECASE)
                    else:
                        match = re.search(r'('+args.keywords_only+')', url, flags=re.IGNORECASE)
                    if match is None:
                        addLink = False     
                    
        # Add link if it passed filters        
        if addLink:
            # Just get the hostname of the urkl
            tldExtract = tldextract.extract(url)
            subDomain = tldExtract.subdomain
            if subDomain != '':
                subDomain = subDomain+'.'
            domainOnly = subDomain+tldExtract.domain+'.'+tldExtract.suffix

            # VirusTotal might return URLs that aren't for the domain passed so we need to check for those and not process them
            # Check the URL
            match = re.search(r'(^|\.)'+re.escape(argsInputHostname)+'$', domainOnly, flags=re.IGNORECASE)
            if match is not None:
                linksFoundAdd(url)  
                
    except Exception as e:
        writerr(colored('ERROR processVirusTotalUrl 1: ' + str(e), 'red'))
    
def getVirusTotalUrls():
    """
    Get URLs from the VirusTotal API v2
    """
    global VIRUSTOTAL_API_KEY, linksFound, linkMimes, waymorePath, subs, stopProgram, stopSource, argsInput, checkVirusTotal, argsInputHostname
    
    # Write the file of URL's for the passed domain/URL
    try:
        requestsMade = 0
        stopSource = False
        linkMimes = set()
        originalLinkCount = len(linksFound)
        
        # Just pass the hostname in the URL
        url = VIRUSTOTAL_URL.replace('{DOMAIN}',quote(argsInputHostname)).replace('{APIKEY}',VIRUSTOTAL_API_KEY)
        
        if verbose():
            write(colored('The VirusTotal URL requested to get links: ','magenta')+colored(url+'\n','white'))
        
        if not args.check_only:           
            write(colored('\rGetting links from virustotal.com API...\r','cyan'))
       
        # Get the domain report from virustotal
        try:
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            session.mount('http://', HTTP_ADAPTER)
            # Pass the API-Key header too. This can change the max endpoints per page, depending on URLScan subscription
            resp = session.get(url, headers={'User-Agent':userAgent})
            requestsMade = requestsMade + 1
        except Exception as e:
            write(colored(getSPACER('[ ERR ] Unable to get links from virustotal.io: ' + str(e)), 'red'))
            return
                        
        # Deal with any errors
        if resp.status_code == 429:
            writerr(colored(getSPACER('[ 429 ] VirusTotal rate limit reached so unable to get links.'),'red'))
            return
        elif resp.status_code == 403:
            writerr(colored(getSPACER('[ 403 ] VirusTotal: Permission denied. Check your API key is correct.'),'red'))
            return
        elif resp.status_code != 200:
            writerr(colored(getSPACER('[ ' + str(resp.status_code) + ' ] Unable to get links from virustotal.com'),'red'))
            return
        
        # Get the JSON response
        try:
            jsonResp = json.loads(resp.text.strip())
  
            # Get the different URLs
            if args.no_subs:
                subDomains = []
            else:
                try:
                    subDomains = jsonResp['subdomains']
                except Exception as e:
                    subDomains = []
            try:  
                detectedUrls = [entry['url'] for entry in jsonResp.get('detected_urls', [])]
            except Exception as e:
                detectedUrls = []
            try:
                undetectedUrls = [entry[0] for entry in jsonResp.get('undetected_urls', [])]
            except Exception as e:
                undetectedUrls = []
            try:
                totalUrls = set(subDomains + detectedUrls + undetectedUrls)
            except Exception as e:
                totalUrls = []
        except:
            writerr(colored(getSPACER('[ ERR ] There was an unexpected response from the VirusTotal API'),'red'))
            totalUrls = []
            
        if args.check_only:
            write(colored('Get URLs from VirusTotal: ','cyan')+colored('1 request','white'))
            checkVirusTotal = 1
        else:
            # Carry on if something was found
            for vturl in totalUrls:
                
                if stopSource:
                    break
                
                # Get memory in case it exceeds threshold
                getMemory()
                
                # Work out whether to include it
                processVirusTotalUrl(vturl)
                        
            linkCount = len(linksFound) - originalLinkCount
            if args.xwm and args.xcc and args.xav and args.xus:
                write(getSPACER(colored('Links found on virustotal.com: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
            else:
                write(getSPACER(colored('Extra links found on virustotal.com: ', 'cyan')+colored(str(linkCount),'white'))+'\n')
        
    except Exception as e:
        writerr(colored('ERROR getVirusTotalUrls 1: ' + str(e), 'red'))

def processResponses():
    """
    Get archived responses from Wayback Machine (archive.org)
    """
    global linksFound, subs, path, indexFile, totalResponses, stopProgram, argsInput, continueRespFile, successCount, fileCount, DEFAULT_OUTPUT_DIR, responseOutputDirectory
    try:
        if not args.check_only:
            # Create 'results' and domain directory if needed
            createDirs()
            
            # Get the path of the files, depending on whether -oR / --output_responses was passed
            try:
                continuePath = responseOutputDirectory + 'continueResp.tmp'
                responsesPath = responseOutputDirectory + 'responses.tmp'
                indexPath = responseOutputDirectory + 'index.txt'
            except Exception as e:
                if verbose():
                    writerr(colored('ERROR processResponses 4: ' + str(e), 'red'))
                
        # Check if a continueResp.tmp and responses.tmp files exists
        runPrevious = 'n'
        if not args.check_only and os.path.exists(continuePath) and os.path.exists(responsesPath):
            
            # Load the links into the set
            with open(responsesPath,'rb') as fl:
                linkRequests = pickle.load(fl)
            totalPrevResponses = len(linkRequests)        
            
            # Get the previous end position to start again at this point
            try:
                with open(continuePath,'r') as fc:
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
                if args.keywords_only == '#CONFIG':
                    filterKeywords = '&filter=original:.*(' + re.escape(FILTER_KEYWORDS).replace(',','|') + ').*'
                else:
                    filterKeywords = '&filter=original:.*(' + args.keywords_only + ').*'
                
            # Get the list again with filters and include timestamp
            linksFound = set()
            
            # Set mime content type filter
            filterMIME = '&filter=!mimetype:warc/revisit' 
            if FILTER_MIME.strip() != '':
                filterMIME = filterMIME + '|' + re.escape(FILTER_MIME).replace(',','|')
                
            # Set status code filter
            filterCode = ''
            if MATCH_CODE.strip() != '':
                filterCode = '&filter=statuscode:' + re.escape(MATCH_CODE).replace(',','|')
            else:
                filterCode = '&filter=!statuscode:' + re.escape(FILTER_CODE).replace(',','|')
            
            # Set the collapse parameter value in the archive.org URL. From the Wayback API docs:
            # "A new form of filtering is the option to 'collapse' results based on a field, or a substring of a field.
            # Collapsing is done on adjacent cdx lines where all captures after the first one that are duplicate are filtered out.
            # This is useful for filtering out captures that are 'too dense' or when looking for unique captures."
            if args.capture_interval == 'none': # get all
                collapse = ''
            elif args.capture_interval == 'h': # get at most 1 capture per URL per hour
                collapse = '&collapse=timestamp:10'
            elif args.capture_interval == 'd': # get at most 1 capture per URL per day
                collapse = '&collapse=timestamp:8'
            elif args.capture_interval == 'm': # get at most 1 capture per URL per month
                collapse = '&collapse=timestamp:6'

            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(argsInput) + path).replace('{COLLAPSE}',collapse) + filterMIME + filterCode + filterLimit + filterFrom + filterTo + filterKeywords
                
            if verbose():
                write(colored('The archive URL requested to get responses: ','magenta')+colored(url+'\n','white'))
            
            if args.check_only:
                write(colored('\rChecking archived response requests...\r','cyan'))
            else:
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
                writerr(colored(getSPACER('[ ERR ] Wayback Machine (archive.org) connection error'), 'red'))
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
                            writerr(colored(getSPACER('No archived responses were found on Wayback Machine (archive.org) for the given search parameters.'),'red'))
                            success = False
                        # If a status other of 429, then stop processing Alien Vault
                        if resp.status_code == 429:
                            writerr(colored(getSPACER('[ 429 ] Wayback Machine (archive.org) rate limit reached, so stopping. Links that have already been retrieved will be saved.'),'red'))
                            success = False
                        # If a status other of 503, then the site is unavailable
                        elif resp.status_code == 503:
                            writerr(colored(getSPACER('[ 503 ] Wayback Machine (archive.org) is currently unavailable. It may be down for maintenance. You can check https://web.archive.org/cdx/ to verify.'),'red'))
                            success = False
                        # If a status other than 200, then stop
                        elif resp.status_code != 200:
                            if verbose(): 
                                writerr(colored(getSPACER('[ '+str(resp.status_code)+' ] Error for '+url),'red'))
                            success = False
                    if not success:
                        if args.keywords_only:
                            if args.keywords_only == '#CONFIG':
                                writerr(colored(getSPACER('Failed to get links from Wayback Machine (archive.org) - consider removing -ko / --keywords-only argument, or changing FILTER_KEYWORDS in config.yml'), 'red'))
                            else:
                                writerr(colored(getSPACER('Failed to get links from Wayback Machine (archive.org) - consider removing -ko / --keywords-only argument, or changing the Regex value you passed'), 'red'))
                        else:    
                            if resp.text.lower().find('blocked site error') > 0:
                                writerr(colored(getSPACER('Failed to get links from Wayback Machine (archive.org) - Blocked Site Error (they block the target site)'), 'red'))
                            else:
                                writerr(colored(getSPACER('Failed to get links from Wayback Machine (archive.org) - check input domain and try again.'), 'red'))
                        return
                except:
                    pass
            
            # Go through the response to save the links found    
            for line in resp.iter_lines():
                try:
                    results = line.decode("utf-8") 
                    parts = results.split(' ', 2)
                    timestamp = parts[0]
                    originalUrl = parts[1]
                    linksFoundResponseAdd(timestamp+'/'+originalUrl)
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
            if not args.check_only:
                with open(responsesPath,'wb') as f:
                    pickle.dump(linkRequests, f)
                
        # Get the total number of responses we will try to get and set the current file count to the success count
        totalResponses = len(linkRequests)
        
        # If there are no reponses to download, diaplay an error and exit
        if totalResponses == 0:
            try:
                if originalUrl:
                    writerr(colored(getSPACER('Failed to get links from Wayback Machine (archive.org) - there were results (e.g. "'+originalUrl+'") but they didn\'t match the input you gave. Check input and try again.'), 'red'))
            except:
                writerr(colored(getSPACER('Failed to get links from Wayback Machine (archive.org) - check input and try again.'), 'red'))
            return
        
        fileCount = successCount
        
        if args.check_only:
            if args.limit == 5000 and totalResponses+1 == 5000:
                writerr(colored('Downloading archived responses: ','cyan')+colored(str(totalResponses+1)+' requests (the --limit argument defaults to '+str(DEFAULT_LIMIT)+')','cyan'))
            else:
                writerr(colored('Downloading archived responses: ','cyan')+colored(str(totalResponses+1)+' requests','white'))
            minutes = round(totalResponses*2.5 // 60)
            hours = minutes // 60
            days = hours // 24
            if minutes < 5:
                write(colored('\n-> Downloading the responses (depending on their size) should be quite quick!','green'))
            elif hours < 2:
                write(colored('\n-> Downloading the responses (depending on their size) could take more than '+str(minutes)+' minutes.','green'))
            elif hours < 6:
                write(colored('\n-> Downloading the responses (depending on their size) could take more than '+str(hours)+' hours.','green'))
            elif hours < 24:
                write(colored('\n-> Downloading the responses (depending on their size) could take more than '+str(hours)+' hours.','yellow'))
            elif days < 7:
                write(colored('\n-> Downloading the responses (depending on their size) could take more than '+str(days)+' days. Consider using arguments -ko, -l, -ci, -from and -to wisely! ','red'))
            else:
                write(colored('\n-> Downloading the responses (depending on their size) could take more than '+str(days)+' days!!! Consider using arguments -ko, -l, -ci, -from and -to wisely!','red'))
            write('')
        else:
            # If the limit has been set over the default, give a warning that this could take a long time!
            if totalResponses - successCount > DEFAULT_LIMIT:
                if successCount > 0:
                    writerr(colored(getSPACER('WARNING: Downloading remaining ' + str(totalResponses - successCount) + ' responses may take a loooooooong time! Consider using arguments -ko, -l, -ci, -from and -to wisely!'),'yellow'))
                else:
                    writerr(colored(getSPACER('WARNING: Downloading ' + str(totalResponses) + ' responses may take a loooooooong time! Consider using arguments -ko, -l, -ci, -from and -to wisely!'),'yellow'))
            
            # Open the index file if hash value is going to be used (not URL)
            if not args.url_filename:
                indexFile = open(indexPath,'a')
            
            # Open the continue.tmp file to store what record we are upto
            continueRespFile = open(continuePath,'w+')
            
            # Process the URLs from web archive   
            if stopProgram is None:
                p = mp.Pool(args.processes)
                p.map(processArchiveUrl, linkRequests[successCount:])
                p.close()
                p.join()
                
            # Delete the tmp files now it has run successfully
            if stopProgram is None:
                try:
                    os.remove(continuePath)
                    os.remove(responsesPath)
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
    Create a directory for the 'results' and the sub directory for the passed domain/URL, unless if
    -oR / --output-responses was passed, just create those directories
    """
    global DEFAULT_OUTPUT_DIR, argsInput
    try:
        if (args.mode in 'R,B' and args.output_responses == '') or (args.mode in 'U,B' and args.output_urls == ''):
            # Create a directory for "results" if it doesn't already exist
            try:
                results_dir = Path(DEFAULT_OUTPUT_DIR+'/results')
                results_dir.mkdir(exist_ok=True)
            except:
                pass
            # Create a directory for the target domain
            try:
                domain_dir = Path(DEFAULT_OUTPUT_DIR + '/results/' + str(argsInput).replace('/','-'))
                domain_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                pass     
        try:
            # Create specified directory for -oR if required
            if args.output_responses != '':
                responseDir = Path(args.output_responses)
                responseDir.mkdir(parents=True, exist_ok=True)
            # If -oU was passed and is prefixed with a directory, create it
            if args.output_urls != '' and '/' in args.output_urls:
                directoriesOnly = os.path.dirname(args.output_urls)
                responseDir = Path(directoriesOnly)
                responseDir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            pass
    except Exception as e:
        writerr(colored(getSPACER('ERROR createDirs 1: ' + str(e)), 'red'))
                
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
    lenSpacer = terminalWidth - len(text) +5
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

def notifyDiscord():
    global WEBHOOK_DISCORD, args
    try:
        data = {
            'content': 'waymore has finished for `-i ' + args.input + ' -mode ' + args.mode + '` ! 🤘',
            'username': 'waymore',
        }
        try:
            result = requests.post(WEBHOOK_DISCORD, json=data)
            if 300 <= result.status_code < 200:
                writerr(colored(getSPACER('WARNING: Failed to send notification to Discord - ' + result.json()), 'yellow'))
        except Exception as e:
            writerr(colored(getSPACER('WARNING: Failed to send notification to Discord - ' + str(e)), 'yellow'))
    except Exception as e:
        writerr(colored('ERROR notifyDiscord 1: ' + str(e), 'red'))

def checkScript(script):
    try:
        if script.replace('\n','').strip() != '':
            return True 
    except Exception as e:
        writerr(colored('ERROR extractScripts 1: ' + str(e), 'red'))
        
def extractScripts(filePath):
    try:
        with open(filePath, 'rb') as file:
            content = file.read().decode('utf-8', errors='ignore')
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            scripts = list(filter(checkScript, scripts))
            return scripts
    except Exception as e:
        writerr(colored('ERROR extractScripts 1: ' + str(e), 'red'))

def extractExternalScripts(filePath):
    try:
        with open(filePath, 'rb') as file:
            content = file.read().decode('utf-8', errors='ignore')
            scripts = re.findall(r'<script[^>]* src="(.*?)".*?>', content, re.DOTALL)
            scripts = list(filter(checkScript, scripts))
            return scripts
    except Exception as e:
        writerr(colored('ERROR extractExternalScripts 1: ' + str(e), 'red'))
        
def combineInlineJS():
    global responseOutputDirectory, INLINE_JS_EXCLUDE
    try:
        write(colored('Creating combined inline JS files...', 'cyan'))
        outputFileTemplate = "combinedInline{}.js"
        excludedNames = ['index.txt', 'continueResp.tmp', 'responses.tmp']
        fileList = [name for name in os.listdir(responseOutputDirectory) 
            if os.path.isfile(os.path.join(responseOutputDirectory, name)) 
            and not any(name.lower().endswith(ext) for ext in INLINE_JS_EXCLUDE) 
            and name not in excludedNames 
            and 'combinedInline' not in name]

        allScripts = {}  # To store all scripts from all files
        allExternalScripts = [] # To store all external script sources from all files
        
        fileCount = len(fileList)
        currentFile = 1
        for filename in fileList:
            filePath = os.path.join(responseOutputDirectory, filename)
            scripts = extractScripts(filePath)
            if scripts:
                allScripts[filename] = scripts
            allExternalScripts.extend(extractExternalScripts(filePath))
            
            # Show progress bar
            fillTest = currentFile % 2
            fillChar = "o"
            if fillTest == 0:
                fillChar = "O"
            suffix="Complete "
            printProgressBar(
                currentFile,
                fileCount,
                prefix="Checking "+str(fileCount)+" files:",
                suffix=suffix,
                length=getProgressBarLength(),
                fill=fillChar
            )
            currentFile += 1   

        # Write a file of external javascript files referenced in the inline scripts
        totalExternal = len(allExternalScripts)
        if totalExternal > 0:
            uniqueExternalScripts = set(allExternalScripts)
            outputFile = os.path.join(responseOutputDirectory, 'combinedInlineSrc.txt')
            inlineExternalFile = open(outputFile, 'w', encoding='utf-8')
            for script in uniqueExternalScripts:
                inlineExternalFile.write(script.strip() + '\n')
            write(colored('Created file ','cyan')+colored(responseOutputDirectory+'combinedInlineSrc.txt','white')+colored(' (src of external JS)','cyan'))
            
        # Write files for all combined inline JS
        uniqueScripts = set()
        for scriptsList in allScripts.values():
            uniqueScripts.update(scriptsList)
                
        totalSections = len(uniqueScripts)
        sectionCounter = 0  # Counter for inline JS sections
        currentOutputFile = os.path.join(responseOutputDirectory, outputFileTemplate.format(1))
        currentSectionsWritten = 0  # Counter for sections written in current file

        if totalSections > 0:
            fileNumber = 1
            with open(currentOutputFile, 'w', encoding='utf-8') as inlineJSFile:
                currentScript = 1
                for script in uniqueScripts:
                    # Show progress bar
                    fillTest = currentScript % 2
                    fillChar = "o"
                    if fillTest == 0:
                        fillChar = "O"
                    suffix="Complete "
                    printProgressBar(
                        currentScript,
                        totalSections,
                        prefix="Writing "+str(totalSections)+" unique scripts:",
                        suffix=suffix,
                        length=getProgressBarLength(),
                        fill=fillChar
                    )
                    sectionCounter += 1
                    currentSectionsWritten += 1
                    if currentSectionsWritten > 1000:
                        # If 1000 sections have been written, switch to the next output file
                        inlineJSFile.close()
                        fileNumber = sectionCounter // 1000 + 1
                        currentOutputFile = os.path.join(responseOutputDirectory, outputFileTemplate.format(fileNumber))
                        inlineJSFile = open(currentOutputFile, 'w', encoding='utf-8')
                        currentSectionsWritten = 1 
                        
                    # Insert comment line for the beginning of the section
                    inlineJSFile.write(f"//****** INLINE JS SECTION {sectionCounter} ******//\n\n")
                    
                    # Write comments indicating the files the script was found in
                    files = ''
                    for filename, scripts_list in allScripts.items():
                        if script in scripts_list:
                            files = files + filename + ', '

                    # Write the files the script appears in
                    inlineJSFile.write('// ' + files.rstrip(', ') + '\n')
                    
                    # Write the script content
                    inlineJSFile.write('\n' + script.strip() + '\n\n')
                    
                    currentScript += 1
                    
        if totalExternal == 0 and totalSections == 0:
            write(colored('No scripts found, so no combined JS files written.\n','cyan'))
        elif fileNumber == 1:
            write(colored('Created file ','cyan')+colored(responseOutputDirectory+'combinedInline1.js','white')+colored(' (contents of inline JS)\n','cyan'))
        else:
            write(colored('Created files ','cyan')+colored(responseOutputDirectory+'combinedInline{1-'+str(fileNumber)+'}.js','white')+colored(' (contents of inline JS)\n','cyan'))
                    
    except Exception as e:
        writerr(colored('ERROR combineInlineJS 1: ' + str(e), 'red'))
        
# Run waymore
def main():
    global args, DEFAULT_TIMEOUT, inputValues, argsInput, linksFound, linkMimes, successCount, failureCount, fileCount, totalResponses, totalPages, indexFile, path, stopSource, stopProgram, VIRUSTOTAL_API_KEY, inputIsSubDomain, argsInputHostname, WEBHOOK_DISCORD, responseOutputDirectory, fileCount

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
        '-oU',
        '--output-urls',
        action='store',
        help='The file to save the Links output to, including path if necessary. If the "-oR" argument is not passed, a "results" directory will be created in the path specified by the DEFAULT_OUTPUT_DIR key in config.yml file (typically defaults to "~/.config/waymore/"). Within that, a directory will be created with target domain (or domain with path) passed with "-i" (or for each line of a file passed with "-i").' ,
        default='',
    )
    parser.add_argument(
        '-oR',
        '--output-responses',
        action='store',
        help='The directory to save the response output files to, including path if necessary. If the argument is not passed, a "results" directory will be created in the path specified by the DEFAULT_OUTPUT_DIR key in config.yml file (typically defaults to "~/.config/waymore/"). Within that, a directory will be created with target domain (or domain with path) passed with "-i" (or for each line of a file passed with "-i").' ,
        default='',
    )
    parser.add_argument(
        '-f',
        '--filter-responses-only',
        action='store_true',
        help='The initial links from Wayback Machine will not be filtered (MIME Type and Response Code), only the responses that are downloaded, e.g. it maybe useful to still see all available paths from the links even if you don\'t want to check the content.',
    )
    parser.add_argument(
        '-fc',
        action='store',
        help='Filter HTTP status codes for retrieved URLs and responses. Comma separated list of codes (default: the FILTER_CODE values from config.yml). Passing this argument will override the value from config.yml',
        type=validateArgStatusCodes,
    )
    parser.add_argument(
        '-mc',
        action='store',
        help='Only Match HTTP status codes for retrieved URLs and responses. Comma separated list of codes. Passing this argument overrides the config FILTER_CODE and -fc.',
        type=validateArgStatusCodes,
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
        help='Filters the search on Wayback Machine (archive.org) to only get at most 1 capture per hour (h), day (d) or month (m). This filter is used for responses only. The default is \'d\' but can also be set to \'none\' to not filter anything and get all responses.',
        default='d'
    )
    parser.add_argument(
        '-ra',
        '--regex-after',
        help='RegEx for filtering purposes against links found all sources of URLs AND responses downloaded. Only positive matches will be output.',
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
        '-xvt',
        action='store_true',
        help='Exclude checks for links from virustotal.com',
        default=False
    )
    parser.add_argument(
        '-lcc',
        action='store',
        type=int,
        help='Limit the number of Common Crawl index collections searched, e.g. \'-lcc 10\' will just search the latest 10 collections (default: 3). As of July 2023 there are currently 95 collections. Setting to 0 (default) will search ALL collections. If you don\'t want to search Common Crawl at all, use the -xcc option.'
    )
    parser.add_argument(
        '-lcy',
        action='store',
        type=int,
        help='Limit the number of Common Crawl index collections searched by the year of the index data. The earliest index has data from 2008. Setting to 0 (default) will search collections or any year (but in conjuction with -lcc). For example, if you are only interested in data from 2015 and after, pass -lcy 2015. If you don\'t want to search Common Crawl at all, use the -xcc option.',
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
        help='Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes (threads) used (default: 1)',
        action='store',
        type=validateArgProcesses,
        default=1,
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
        action='store',
        help=r'Only return links and responses that contain keywords that you are interested in. This can reduce the time it takes to get results. If you provide the flag with no value, Keywords are taken from the comma separated list in the "config.yml" file with the "FILTER_KEYWORDS" key, otherwise you can pass an specific Regex value to use, e.g. -ko "admin" to only get links containing the word admin, or -ko "\.js(\?|$)" to only get JS files. The Regex check is NOT case sensitive.',
        nargs='?',
        const="#CONFIG"
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
        help="If the URL output file (default waymore.txt) already exists, it will be overwritten instead of being appended to.",
    )
    parser.add_argument(
        "-nlf",
        "--new-links-file",
        action="store_true",
        help="If this argument is passed, a .new file will also be written that will contain links for the latest run. This is only relevant for mode U.",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        help="Path to the YML config file. If not passed, it looks for file 'config.yml' in the same directory as runtime file 'waymore.py'.",
    )
    parser.add_argument(
        '-wrlr',
        '--wayback-rate-limit-retry',
        action='store',
        type=int,
        help='The number of minutes the user wants to wait for a rate limit pause on Watback Machine (archive.org) instead of stopping with a 429 error (default: 3).',
        default=3
    )
    parser.add_argument(
        '-urlr',
        '--urlscan-rate-limit-retry',
        action='store',
        type=int,
        help='The number of minutes the user wants to wait for a rate limit pause on URLScan.io instead of stopping with a 429 error (default: 1).',
        default=1
    )
    parser.add_argument(
        "-co",
        "--check-only",
        action="store_true",
        help="This will make a few minimal requests to show you how many requests, and roughly how long it could take, to get URLs from the sources and downloaded responses from Wayback Machine.",
    )
    parser.add_argument(
        "-nd",
        "--notify-discord",
        action="store_true",
        help="Whether to send a notification to Discord when waymore completes. It requires WEBHOOK_DISCORD to be provided in the config.yml file.",
    )
    parser.add_argument(
        '-oijs',
        '--output-inline-js',
        action="store_true",
        help='Whether to save combined inline javascript of all relevant files in the response directory when "-mode R" (or "-mode B") has been used. The files are saved with the name "combined_inline{}.js" where "{}" is the number of the file, saving 1000 unique scripts per file. '
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    parser.add_argument('--version', action='store_true', help="Show version number")
    args = parser.parse_args()

    # If --version was passed, display version and exit
    if args.version:
        write(colored('Waymore - v' + __version__,'cyan'))
        sys.exit()
    
    # If -lcc wasn't passed then set to the default of 3 if -lcy is 0. This will make them work together
    if args.lcc is None:
        if args.lcy == 0:
            args.lcc = 3
        else:
            args.lcc = 0
    
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
            
            argsInput = inpt.strip().rstrip('\n').strip('.').lower()
            
            # Get the input hostname
            tldExtract = tldextract.extract(argsInput)
            subDomain = tldExtract.subdomain
            inputIsSubDomain = False
            if subDomain != '':
                inputIsSubDomain = True
                subDomain = subDomain+'.'
            argsInputHostname = subDomain+tldExtract.domain+'.'+tldExtract.suffix
            
            # Warn user if a sub domains may have been passed
            if inputIsSubDomain:
                writerr(colored(getSPACER('IMPORTANT: It looks like you may be passing a subdomain. If you want ALL subs for a domain, then pass the domain only. It will be a LOT quicker, and you won\'t miss anything. NEVER pass a file of subdomains if you want everything, just the domains.\n'),'yellow'))
                
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
            
            if args.check_only:
                write(colored('*** Checking requests needed for ','cyan')+colored(argsInput,'white')+colored(' ***\n','cyan'))
                
            # If the mode is U (URLs retrieved) or B (URLs retrieved AND Responses downloaded)
            if args.mode in ['U','B']:
                
                # If not requested to exclude, get URLs from the Wayback Machine (archive.org)
                if not args.xwm and stopProgram is None:
                    getWaybackUrls()
            
                # If not requested to exclude, get URLs from commoncrawl.org
                if not args.xcc and stopProgram is None:
                    getCommonCrawlUrls()
                    
                # If not requested to exclude and a TLD wasn't passed, get URLs from alienvault.com
                if not args.xav and stopProgram is None and not inpt.startswith('.'):
                    getAlienVaultUrls()
                
                # If not requested to exclude, get URLs from urlscan.io
                if not args.xus and stopProgram is None:
                    getURLScanUrls()

                # If not requested to exclude, get URLs from virustotal.com if we have an API key
                if not args.xvt and VIRUSTOTAL_API_KEY != '' and stopProgram is None:
                    getVirusTotalUrls()
                    
                # Output results of all searches
                processURLOutput()
            
                # Clean up 
                linkMimes = None
                
            # If we want to get actual archived responses from archive.org...
            if (args.mode in ['R','B']) and stopProgram is None:
                
                # Get the output directory for responses
                if args.output_responses != '':
                    responseOutputDirectory = args.output_responses + '/'
                else:
                    responseOutputDirectory = str(DEFAULT_OUTPUT_DIR) + '/results/' + str(argsInput).replace('/','-') + '/'
            
                processResponses()
                
                # Output details of the responses downloaded
                if not args.check_only:
                    processResponsesOutput()
            
                    # If requested, generate the combined inline JS files
                    if stopProgram is None and fileCount > 0 and args.output_inline_js:
                        combineInlineJS()
                    
            if args.check_only:
                write(colored('NOTE: The time frames are a very rough guide and doesn\'t take into account additonal time for rate limiting.','magenta'))
                
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
                            "THE PROGRAM WAS STOPPED DUE TO PROBLEM GETTING DATA FROM WAYBACK MACHINE (ARCHIVE.ORG)\n",
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
        # Send a notification to discord if requested
        try:
            if args.notify_discord and WEBHOOK_DISCORD != '':
                notifyDiscord()
        except:
            pass
        try:
            if sys.stdout.isatty():
                writerr(colored('✅ Want to buy me a coffee? ☕ https://ko-fi.com/xnlh4ck3r 🤘', 'green'))
        except:
            pass
        # Clean up
        linksFound = None
        linkMimes = None
        inputValues = None

if __name__ == '__main__':
    main()