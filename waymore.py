#!/usr/bin/env python
# Python 3
# waymore - by @Xnl-h4ck3r: Find way more from the Wayback Machine
# Full help here: https://github.com/xnl-h4ck3r/waymore/blob/main/README.md
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

from ast import Pass
from logging import NOTSET
import requests
from requests.exceptions import ConnectionError
from requests.utils import quote
import argparse
from signal import SIGINT, signal
import multiprocessing.dummy as mp
from termcolor import colored
from datetime import datetime
import yaml
import os
import json
import re
import random
import sys
import math

# Global variables
linksFound = set()
linkMimes = set()
stopProgram = False
stopSource = False
successCount = 0
failureCount = 0
fileCount = 0
totalResponses = 0
totalPages = 0
indexFile = None
inputIsDomainANDPath = False
subs = '*.'
path = ''
waymorePath = ''
SPACER = ' ' * 70

WAYBACK_URL = 'https://web.archive.org/cdx/search/cdx?url={DOMAIN}&collapse={COLLAPSE}&fl=timestamp,original,mimetype,statuscode,digest'
CCRAWL_INDEX_URL = 'https://index.commoncrawl.org/collinfo.json'
ALIENVAULT_URL = 'https://otx.alienvault.com/api/v1/indicators/domain/{DOMAIN}/url_list?limit=500'

USER_AGENT  = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
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
DEFAULT_FILTER_URL = '.css,.jpg,.jpeg,.png,.svg,.img,.gif,.mp4,.flv,.ogv,.webm,.webp,.mov,.mp3,.m4a,.m4p,.scss,.tif,.tiff,.ttf,.otf,.woff,.woff2,.bmp,.ico,.eot,.htc,.rtf,.swf,.image,/image,/img,/css,/wp-json,/wp-content,/wp-includes,/theme,/audio,/captcha,/font,node_modules'

# MIME Content-Type exclusions used to filter links and responses from web.archive.org through their API
DEFAULT_FILTER_MIME = 'text/css,image/jpeg,image/jpg,image/png,image/svg+xml,image/gif,image/tiff,image/webp,image/bmp,image/vnd,image/x-icon,image/vnd.microsoft.icon,font/ttf,font/woff,font/woff2,font/x-woff2,font/x-woff,font/otf,audio/mpeg,audio/wav,audio/webm,audio/aac,audio/ogg,audio/wav,audio/webm,video/mp4,video/mpeg,video/webm,video/ogg,video/mp2t,video/webm,video/x-msvideo,video/x-flv,application/font-woff,application/font-woff2,application/x-font-woff,application/x-font-woff2,application/vnd.ms-fontobject,application/font-sfnt,application/vnd.android.package-archive,binary/octet-stream,application/octet-stream,application/pdf,application/x-font-ttf,application/x-font-otf'

# Response code exclusions we will use to filter links and responses from web.archive.org through their API
DEFAULT_FILTER_CODE = '404,301,302'

# Yaml config values
FILTER_URL = ''
FILTER_MIME = ''
FILTER_CODE = ''

# Define colours
class tc:
    NORMAL = '\x1b[39m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'

def showBanner():
    print()
    print(tc.RED+" _ _ _       _   _ "+tc.NORMAL+"____                    ")
    print(tc.RED+"| | | |_____| | | "+tc.NORMAL+"/    \  ___   ____ _____ ")
    print(tc.RED+"| | | (____ | | | "+tc.NORMAL+"| | | |/ _ \ / ___) ___ |")
    print(tc.RED+"| | | / ___ | |_| "+tc.NORMAL+"| | | | |_| | |   | |_| |")
    print(tc.RED+" \___/\_____|\__  "+tc.NORMAL+"|_|_|_|\___/| |   | ____/")
    print(tc.RED+"            (____/ "+tc.MAGENTA+"  by Xnl-h4ck3r "+tc.NORMAL+" \_____)")
    print()

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
    global stopProgram
    stopProgram = True
    print(colored('>>> "Oh my God, they killed Kenny... and waymore!" - Kyle','red'),SPACER)
    sys.exit()

def showOptions():
    """
    Show the chosen options and config settings
    """
    global inputIsDomainANDPath
                
    try:
        print(colored('Selected config and settings:', 'cyan'))
        
        if inputIsDomainANDPath:
            print(colored('-i: ' + args.input, 'magenta'), 'The target URL to download responses for.')
        else: # input is a domain
            print(colored('-i: ' + args.input, 'magenta'), 'The target domain to find links for.')
        
        if args.mode == 'U':
            print(colored('-mode: ' + args.mode, 'magenta'), 'Only URLs will be retrieved for the input.')
        elif args.mode == 'R':
            print(colored('-mode: ' + args.mode, 'magenta'), 'Only Responses will be downloaded for the input.')
        elif args.mode == 'B':
            print(colored('-mode: ' + args.mode, 'magenta'), 'URLs will be retrieved AND Responses will be downloaded for the input.')
            
        if not inputIsDomainANDPath:
            if args.no_subs:
                print(colored('-n: ' +str(args.no_subs), 'magenta'), 'Sub domains are excluded in the search.')
            else:
                print(colored('-n: ' +str(args.no_subs), 'magenta'), 'Sub domains are included in the search.')
                
            print(colored('-xcc: ' +str(args.xcc), 'magenta'), 'Whether to exclude checks to commoncrawl.org. Searching all their index collections can take a while, and it may not return any extra URLs that weren\'t already found on archive.org')
            if not args.xcc:
                if args.lcc == 0:
                    print(colored('-lcc: ' +str(args.lcc), 'magenta'), 'Search ALL Common Crawl index collections.')
                else:
                    print(colored('-lcc: ' +str(args.lcc), 'magenta'), 'The number of latest Common Crawl index collections to be searched.')
            print(colored('-xav: ' +str(args.xav), 'magenta'), 'Whether to exclude checks to alienvault.com. Searching all their pages can take a while, and it may not return any extra URLs that weren\'t already found on archive.org')
            
        if args.mode in ['R','B']:
            if args.limit == 0:
                print(colored('-l: ' +str(args.limit), 'magenta'), 'Save ALL responses found.')
            else:
                if args.limit > 0:
                    print(colored('-l: ' +str(args.limit), 'magenta'), 'Only save the FIRST ' + str(args.limit) + ' responses found.')
                else:
                    print(colored('-l: ' +str(args.limit), 'magenta'), 'Only save the LAST ' + str(abs(args.limit)) + ' responses found.')
                    
            if args.from_date is not None:
                print(colored('-from: ' +str(args.from_date), 'magenta'), 'The date/time to get responses from.')
            if args.to_date is not None:
                print(colored('-to: ' +str(args.to_date), 'magenta'), 'The date/time to get responses up to.')
            
            if args.capture_interval == 'h': 
                print(colored('-ci: ' +args.capture_interval, 'magenta'), 'Get at most 1 archived response per hour from archive.org')
            elif args.capture_interval == 'd':
                print(colored('-ci: ' +args.capture_interval, 'magenta'), 'Get at most 1 archived response per day from archive.org')
            elif args.capture_interval == 'm':
                print(colored('-ci: ' +args.capture_interval, 'magenta'), 'Get at most 1 archived response per month from archive.org')
            elif args.capture_interval == 'none':
                print(colored('-ci: ' +args.capture_interval, 'magenta'), 'There will not be any filtering based on the capture interval.')
                    
            if args.url_filename:
                print(colored('-url-filename: ' +str(args.url_filename), 'magenta'), 'The filenames of downloaded responses wil be set to the URL rather than the hash value of the response.')
            
        print(colored('-f: ' +str(args.filter_responses_only), 'magenta'), 'If True, the initial links from wayback machine will not be filtered, only the responses that are downloaded will be filtered. It maybe useful to still see all available paths even if you don\'t want to check the file for content.')
        print(colored('MIME Type exclusions:', 'magenta'), FILTER_MIME)
        print(colored('Response Code exclusions:', 'magenta'), FILTER_CODE)      
        print(colored('Response URL exclusions:', 'magenta'), FILTER_URL)  
        
        if args.regex_after is not None:
            print(
                colored("-ra: " + args.regex_after, "magenta"),
                "RegEx for filtering purposes against found links from archive.org AND responses downloaded. Only positive matches will be output.",
            )
        if args.mode in ['R','B']:
            print(colored('-t: ' + str(args.timeout), 'magenta'),'The number of seconds to wait for a an archived response.')
        if args.mode in ['R','B'] or (args.mode == 'U' and not args.xcc):
            print(colored('-p: ' + str(args.processes), 'magenta'), 'The number of parallel requests made.')
        
        print()

    except Exception as e:
        print(colored('ERROR showOptions: ' + str(e), 'red'))

def getConfig():
    """
    Try to get the values from the config file, otherwise use the defaults
    """
    global FILTER_CODE, FILTER_MIME, FILTER_URL, subs, path, waymorePath, inputIsDomainANDPath
    try:
        
        # If the input doesn't have a / then assume it is a domain rather than a domain AND path
        if str(args.input).find('/') < 0:
            path = '/*'
            inputIsDomainANDPath = False
        else:
            # If the input is a URL then -mode will have to be R (Responses only)
            inputIsDomainANDPath = True
            args.mode = 'R'
            
        # If the -no-subs argument was passed, OR the input is a path, don't include subs
        if args.no_subs or inputIsDomainANDPath:
            subs = ''
        
        # Try to get the config file values
        try:        
            waymorePath = os.path.dirname(os.path.realpath(__file__))
            if waymorePath == '':
                configPath = 'config.yml'
            else:
                configPath = waymorePath + '/config.yml' 
            config = yaml.safe_load(open(configPath))
        
            try:
                FILTER_URL = config.get('FILTER_URL')
                if str(FILTER_URL) == 'None':
                    FILTER_URL = ''
                else:
                    FILTER_URL = FILTER_URL.replace(',','|')
            except Exception as e:
                print(colored('Unable to read "FILTER_URL" from config.yml; defaults set', 'red'))
                FILTER_URL = DEFAULT_FILTER_URL

            try:
                FILTER_MIME = config.get('FILTER_MIME')
                if str(FILTER_MIME) == 'None':
                    FILTER_MIME = ''
                else:
                    FILTER_MIME = FILTER_MIME.replace(',','|')
            except Exception as e:
                print(colored('Unable to read "FILTER_MIME" from config.yml; defaults set', 'red'))
                FILTER_MIME = DEFAULT_FILTER_MIME
            
            try:
                FILTER_CODE = config.get('FILTER_CODE')
                if str(FILTER_CODE) == 'None':
                    FILTER_CODE = ''
                else:
                    FILTER_CODE = FILTER_CODE.replace(',','|')
            except Exception as e:
                print(colored('Unable to read "FILTER_CODE" from config.yml; defaults set', 'red'))
                FILTER_CODE = DEFAULT_FILTER_CODE
                
        except:
            print(colored('WARNING: Cannot find config.yml, so using default values\n', 'yellow'))
            FILTER_URL = DEFAULT_FILTER_URL
            FILTER_MIME = DEFAULT_FILTER_MIME
            FILTER_CODE = DEFAULT_FILTER_CODE
        
    except Exception as e:
        print(colored('ERROR getConfig: ' + str(e), 'red'))

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
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(colored(f"\r{prefix} |{bar}| {percent}% {suffix}", "green"), end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()
    except Exception as e:
        if verbose():
            print(colored("ERROR printProgressBar: " + str(e), "red"))

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
                
def processArchiveUrl(url):
    """
    Get the passed web archive response
    """
    global stopProgram, successCount, failureCount, fileCount, waymorePath, totalResponses, indexFile
    try:
        if not stopProgram:
            
            archiveUrl = 'https://web.archive.org/web/' + fixArchiveOrgUrl(url)
            hashValue = ''
        
            # Make a request to the web archive
            try:
                try:
                    # Choose a random user agent string to use for any requests
                    userAgent = random.choice(USER_AGENT)

                    resp = requests.get(url = archiveUrl, headers={"User-Agent":userAgent}, allow_redirects = False)
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
                        else:
                            hashValue = filehash(archiveHtml)
                            fileName = hashValue
                        filePath = waymorePath+'/results/'+str(args.input).replace('/','-')+'/'+fileName[0:250]+'.xnl'

                        # Write the file
                        try:
                            responseFile = open(filePath, 'w', encoding='utf8')
                            responseFile.write(archiveHtml)
                            responseFile.close()
                            fileCount = fileCount + 1
                        except Exception as e:
                            print(colored('[ ERR ] Failed to write file ' + filePath + ': '+ str(e), 'red'))
                            
                        # Write the hash value and URL to the index file
                        if not args.url_filename:
                            try:
                                timestamp = str(datetime.now())
                                indexFile.write(hashValue+','+archiveUrl+' ,'+timestamp+'\n')
                            
                            except Exception as e:
                                print(colored('[ ERR ] Failed to write to index.txt for "' + archiveUrl + '": '+ str(e), 'red'))

                        # FOR DEBUGGING PURPOSES
                        try:
                            if archiveHtml.find('archive.org') > 0 and os.environ.get('USER') == 'xnl':
                                print(colored('"' + hashValue + '.xnl" CONTAINS ARCHIVE.ORG - CHECK ITS A VALID REFERENCE', 'yellow'),SPACER)
                        except:
                            pass
                            
                    successCount = successCount + 1
                
                except WayBackException as wbe:
                    failureCount = failureCount + 1
                    if verbose():
                        print(colored('[ ERR ] archive.org returned a problem for "' + archiveUrl + '"', 'red'))
                except ConnectionError as ce:
                    failureCount = failureCount + 1
                    if verbose():
                        print(colored('[ ERR ] archive.org connection error for "' + archiveUrl + '"', 'red'))
                except Exception as e:
                    failureCount = failureCount + 1
                    if verbose():
                        try:
                            print(colored('[ ' + str(resp.status_code) +' ] Failed to get response for "' + archiveUrl + '"', 'red'))
                        except:
                            print(colored('[ ERR ] Failed to get response for "' + archiveUrl + '": '+ str(e), 'red'))
                
                # Show progress bar
                fillTest = (successCount + failureCount) % 2
                fillChar = "o"
                if fillTest == 0:
                    fillChar = "O"
                printProgressBar(
                    successCount + failureCount,
                    totalResponses,
                    prefix="Downloading " + str(totalResponses) + " responses: ",
                    suffix="Complete  ",
                    length=50,
                    fill=fillChar
                )
                    
            except Exception as e:
                if verbose():
                    print(colored('Error for "'+url+'": ' + str(e), 'red'))
        else:
            os.kill(os.getpid(),SIGINT)
            
    except Exception as e:
        print(colored('ERROR processArchiveUrl 1:  ' + str(e), 'red'))

def processURLOutput():
    """
    Show results of the URL output, i.e. getting URLs from archive.org and commoncrawl.org and write results to file
    """
    global linksFound, subs, path

    try:
            
        linkCount = len(linksFound)
        print(colored('Links found for ' + subs + args.input + ':', 'cyan'), str(linkCount) + ' 🤘'+SPACER+'\n')
        
        # Create 'results' and domain directory if needed
        createDirs()
        
        try:
            # Open the output file
            outFile = open(waymorePath+'/results/'+str(args.input).replace('/','-')+'/waymore.txt', "w")
        except Exception as e:
            if verbose():
                print(colored("ERROR processURLOutput 2: " + str(e), "red"))
                sys.exit()

        # Go through all links, and output what was found
        # If the -ra --regex-after was passed then only output if it matches
        outputCount = 0
        for link in linksFound:
            try:
                if args.regex_after is None or re.search(args.regex_after, link, flags=re.IGNORECASE):
                    # Don't write it if the link does not contain the requested domain (this can sometimes happen)
                    if link.find(args.input) >= 0:
                        outFile.write(link + "\n")
                        outputCount = outputCount + 1
            except Exception as e:
                if verbose():
                    print(colored("ERROR processURLOutput 3: " + str(e), "red"))

        # If there are less links output because of filters, show the new total
        if args.regex_after is not None and linkCount > 0 and outputCount < linkCount:
            print(colored('Links found after applying filter "' + args.regex_after + '":','cyan'), str(outputCount) + ' 🤘\n')
        
        # Close the output file
        try:
            outFile.close()
        except Exception as e:
            if verbose():
                print(colored("ERROR processURLOutput 4: " + str(e), "red"))

        if verbose():
            print(colored('Links successfully written to file', 'cyan'), waymorePath+'/results/'+str(args.input).replace('/','-')+'/waymore.txt' + '\n')

    except Exception as e:
        if verbose():
            print(colored("ERROR processURLOutput 1: " + str(e), "red"))

def processResponsesOutput():
    """
    Show results of the archive responses saved
    """
    global successCount, failureCount, subs, fileCount
    try:
        if failureCount > 0:
            print(colored('\nResponses saved for ' + subs + args.input + ':', 'cyan'), str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘', colored('(' + str(failureCount) + ' failed)\n','red'))
        else:
            print(colored('\nResponses saved for ' + subs + args.input + ':', 'cyan'), str(fileCount) +' (' +str(successCount-fileCount) + ' empty responses) 🤘\n')
    except Exception as e:
        if verbose():
            print(colored("ERROR processResponsesOutput 1: " + str(e), "red"))    

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
    # Check if input seems to be valid domain or URL
    match = re.search(r"^((?!-))(xn--)?([a-z0-9][a-z0-9\-\_]{0,61}[a-z0-9]{0,1}\.)+(xn--)?([a-z0-9\-]{1,61}|[a-z0-9\-]{1,30}\.[a-z]{2,})(/[^\n|?#]*)?$", x)
    if match is None:
        raise argparse.ArgumentTypeError('Pass a domain only (with no schema) to search for all links, or pass a domain and path (with no schema) to just get archived responses for that URL. Do not pass a query string or fragment.')
    return x

def processAlienVaultPage(url):
    """
    Get URLs from a specific page of otx.alienvault.org API for the input domain
    """
    global totalPages, linkMimes, linksFound, stopSource
    try:
        if not stopSource:
            try:             
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                page = url.split('page=')[1]
                resp = requests.get(url, headers={"User-Agent":userAgent})  
            except ConnectionError as ce:
                print(colored('[ ERR ] alienvault.org connection error for page ' + page, 'red'),SPACER)
                resp = None
                return
            except Exception as e:
                print(colored('[ ERR ] Error getting response for page' + page + ' - ' + str(e),'red'),SPACER)
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                        # If a status other of 429, then stop processing Alien Vault
                        if resp.status_code == 429:
                            print(colored('[ 429 ] Alien Vault rate limit reached, so stopping. Links that have already been retrieved will be saved.','red'))
                            stopSource = True
                            return
                        # If the response from archive.org is empty then skip
                        if resp.text == '' and totalPages == 0:
                            if verbose():
                                print(colored('[ ERR ] '+url+' gave an empty response.','red'))
                            return
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose():
                                print(colored('[ '+str(resp.status_code)+' ] Error for '+url,'red'))
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
                        linksFound.add(foundUrl)
                    else:
                        addLink = True
                        
                        # If the user requested -n / --no-subs then we don't want to add it if it has a sub domain (www. will not be classed as a sub domain)
                        if args.no_subs:
                            match = re.search(r'\:\/\/(www\.)?'+args.input.replace('.','\.'), foundUrl, flags=re.IGNORECASE)
                            if match is None:
                                addLink = False
                    
                        # If the user didn't requested -f / --filter-responses-only then check http code
                        # Note we can't check MIME filter because it is not returned by Alien Vault API
                        if addLink and not args.filter_responses_only: 
                            # Get the HTTP code
                            try:
                                httpCode = urlSection['httpcode']
                            except:
                                httpCode = ''
                            # If we have a HTTP Code, compare against the Code exclusions
                            if httpCode != '':
                                match = re.search(r'('+FILTER_CODE.replace('.','\.')+')', foundUrl, flags=re.IGNORECASE)
                                if match is not None:
                                    addLink = False
                            
                            # Check the URL exclusions
                            if addLink:
                                match = re.search(r'('+FILTER_URL.replace('.','\.')+')', foundUrl, flags=re.IGNORECASE)
                                if match is not None:
                                    addLink = False            
                                    
                        # Add link if it passed filters        
                        if addLink:
                            linksFound.add(foundUrl)
        else:
            pass                    
    except Exception as e:
        if verbose():
            print(colored("ERROR processLAlienVaultPage 1: " + str(e), "red"))
    
def getAlienVaultUrls():
    """
    Get URLs from the Alien Vault OTX, otx.alienvault.com
    """
    global linksFound, waymorePath, subs, path, stopProgram, totalPages, stopSource
    
    # Write the file of URL's for the passed domain/URL
    try:
        stopSource = False
        originalLinkCount = len(linksFound)
        
        url = ALIENVAULT_URL.replace('{DOMAIN}',quote(args.input))+'&page='
        
        # Get the number of pages (i.e. separate requests) that are going to be made to archive.org
        totalPages = 0
        try:
            print(colored('\rGetting the number of alienvault.com pages to search...','cyan'), end='\r')
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            resp = requests.get(url+'&showNumPages=True', headers={"User-Agent":userAgent}) 
        except Exception as e:
            print(colored('[ ERR ] unable to get links from alienvault.com: ' + str(e), 'red'),SPACER)
            return
        
        # If the rate limit was reached end now
        if resp.status_code == 429:
            print(colored('[ 429 ] Alien Vault rate limit reached so unable to get links.','red'))
            return
        
        if verbose():
            print(colored('The Alien Vault URL requested to get links:','magenta'), url+'\n')
        
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

                # if the page number was found then display it, but otherwise we will just try to increment until we have everything       
                print(colored('\rGetting links from ' + str(totalPages) + ' alienvault.com API requests (this can take a while for some domains)...','cyan'), end='\r')

                # Get a list of all the page URLs we need to visit
                pages = set()
                for page in range(1, totalPages):
                    pages.add(url+str(page))

                # Process the URLs from alien vault 
                if not stopProgram:
                    p = mp.Pool(args.processes)
                    p.map(processAlienVaultPage, pages)
                    p.close()
                    p.join()
        else:
            if verbose():
                print(colored('[ ERR ] An error was returned in the alienvault.com response.', 'red'),SPACER+'\n')
                
        linkCount = len(linksFound) - originalLinkCount
        print(colored('Extra links found on alienvault.com:', 'cyan'), str(linkCount) + SPACER+'\n')
        
    except Exception as e:
        print(colored('ERROR getAlienVaultUrls 1: ' + str(e), 'red'))
        
def processWayBackPage(url):
    """
    Get URLs from a specific page of archive.org CDX API for the input domain
    """
    global totalPages, linkMimes, linksFound, stopSource
    try:
        if not stopSource:
            try:             
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                page = url.split('page=')[1]
                resp = requests.get(url, headers={"User-Agent":userAgent})  
            except ConnectionError as ce:
                print(colored('[ ERR ] archive.org connection error for page ' + page, 'red'),SPACER)
                resp = None
                return
            except Exception as e:
                print(colored('[ ERR ] Error getting response for page' + page + ' - ' + str(e),'red'),SPACER)
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                         # If a status other of 429, then stop processing Alien Vault
                        if resp.status_code == 429:
                            print(colored('[ 429 ] Archive.org rate limit reached, so stopping. Links that have already been retrieved will be saved.','red'))
                            stopSource = True
                            return
                        # If the response from archive.org is empty then skip
                        if resp.text == '' and totalPages == 0:
                            if verbose():
                                print(colored('[ ERR ] '+url+' gave an empty response.','red'))
                            return
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose():
                                print(colored('[ '+str(resp.status_code)+' ] Error for '+url,'red'))
                            return
                except:
                    pass
            
            # Get the URLs and MIME types
            for line in resp.iter_lines():
                linkMimes.add(str(line).split(' ')[2])
                foundUrl = fixArchiveOrgUrl(str(line).split(' ')[1])
                linksFound.add(foundUrl)
        else:
            pass
    except Exception as e:
        if verbose():
            print(colored("ERROR processWayBackPage 1: " + str(e), "red"))
    
def getWaybackUrls():
    """
    Get URLs from the Wayback Machine, archive.org
    """
    global linksFound, linkMimes, waymorePath, subs, path, stopProgram, totalPages, stopSource
    
    # Write the file of URL's for the passed domain/URL
    try:
        stopSource = False
        filterMIME = '&filter=!mimetype:warc/revisit|' + FILTER_MIME 
        filterCode = '&filter=!statuscode:' + FILTER_CODE
        
        if args.filter_responses_only:
            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(args.input) + path).replace('{COLLAPSE}','')+'&page='
        else:
            url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(args.input) + path).replace('{COLLAPSE}','') + filterMIME + filterCode + '&page='
        
        # Get the number of pages (i.e. separate requests) that are going to be made to archive.org
        totalPages = 0
        try:
            print(colored('\rGetting the number of archive.org pages to search...','cyan'), end='\r')
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            resp = requests.get(url+'&showNumPages=True', headers={"User-Agent":userAgent}) 
            totalPages = int(resp.text.strip())
        except Exception as e:
            print(colored('[ ERR ] unable to get links from archive.org: ' + str(e), 'red'),SPACER)
            return
        
        # If the rate limit was reached end now
        if resp.status_code == 429:
            print(colored('[ 429 ] Archive.org rate limit reached so unable to get links.','red'))
            return
        
        if verbose():
            print(colored('The archive URL requested to get links:','magenta'), url+'\n')
         
        # if the page number was found then display it, but otherwise we will just try to increment until we have everything       
        print(colored('\rGetting links from ' + str(totalPages) + ' archive.org API requests (this can take a while for some domains)...','cyan'), end='\r')

        # Get a list of all the page URLs we need to visit
        pages = set()
        for page in range(0, totalPages):
            pages.add(url+str(page))

        # Process the URLs from web archive        
        if not stopProgram:
            p = mp.Pool(args.processes)
            p.map(processWayBackPage, pages)
            p.close()
            p.join()
               
        # Show the MIME types found (in case user wants to exclude more)
        if verbose() and len(linkMimes) > 0 :
            linkMimes.discard('warc/revisit')
            print(colored('MIME types found:','magenta'), str(linkMimes) + SPACER+'\n')
            linkMimes = None
        
        if not args.xcc or not args.xav:
            linkCount = len(linksFound)
            print(colored('Links found on archive.org:', 'cyan'), str(linkCount) + SPACER+'\n')
            
    except Exception as e:
        print(colored('ERROR getWaybackUrls 1: ' + str(e), 'red'))

def processCommonCrawlCollection(cdxApiUrl):
    """
    Get URLs from a given Common Crawl index collection
    """
    global subs, path, linksFound, linkMimes, stopSource
    
    try:
        if not stopSource:
            # Set mime content type filter
            filterMIME = '&filter=!mimetype:warc/revisit' 
            if FILTER_MIME.strip() != '':
                filterMIME = filterMIME + '|' + FILTER_MIME
                
            # Set status code filter
            filterCode = ''
            if FILTER_CODE.strip() != '':
                filterCode = '&filter=!status:' + FILTER_CODE
                
            commonCrawlUrl = cdxApiUrl + '?output=json&fl=timestamp,url,mime,status,digest&url=' 
                        
            if args.filter_responses_only:
                url = commonCrawlUrl + subs + quote(args.input) + path
            else:
                url = commonCrawlUrl + subs + quote(args.input) + path + filterMIME + filterCode
            
            try:
                # Choose a random user agent string to use for any requests
                userAgent = random.choice(USER_AGENT)
                resp = requests.get(url, stream=True, headers={"User-Agent":userAgent})   
            except ConnectionError as ce:
                print(colored('[ ERR ] Common Crawl connection error', 'red'),SPACER)
                resp = None
                return
            except Exception as e:
                print(colored('[ ERR ] Error getting response - ' + str(e),'red'),SPACER)
                resp = None
                return
            finally:
                try:
                    if resp is not None:
                        # If a status other of 429, then stop processing Common Crawl
                        if resp.status_code == 429:
                            print(colored('[ 429 ] Common Crawl rate limit reached, so stopping. Links that have already been retrieved will be saved.','red'))
                            stopSource = True
                            return
                        # If the response from commoncrawl.org says nothing was found...
                        if resp.text.find('No Captures found') > 0:
                            # Don't output any messages, just exit function
                            return
                        # If the response from commoncrawl.org is empty, then stop
                        if resp.text == '':
                            if verbose():
                                print(colored('[ ERR ] '+url+' gave an empty response.','red'))
                            return
                        # If a status other than 200, then stop
                        if resp.status_code != 200:
                            if verbose(): 
                                print(colored('[ '+str(resp.status_code)+' ] Error for '+url,'red'))
                            return
                except:
                    pass
                
            # Get the URLs and MIME types
            for line in resp.iter_lines():
                data = json.loads(line)
                try:
                    linkMimes.add(data['mime'])
                except:
                    pass
                linksFound.add(data['url'])
        else:
            pass
    except Exception as e:
        print(colored('ERROR processCommonCrawlCollection 1: ' + str(e), 'red'))
            
def getCommonCrawlUrls():
    """
    Get all Common Crawl index collections to get all URLs from each one
    """
    global linksFound, linkMimes, waymorePath, subs, path, stopSource
    
    try:
        stopSource = False
        linkMimes = set()
        originalLinkCount = len(linksFound)
        
        # Set mime content type filter
        filterMIME = '&filter=~mime:^(?!warc/revisit' 
        if FILTER_MIME.strip() != '':
            filterMIME = filterMIME + FILTER_MIME
        filterMIME = filterMIME + ')'
        
        # Set status code filter
        filterCode = ''
        if FILTER_CODE.strip() != '':
            filterCode = '&filter=~status:^(?!' + FILTER_CODE + ')'
    
        if verbose():
            if args.filter_responses_only:
                url = '{CDX-API-URL}?output=json&fl=timestamp,url,mime,status,digest&url=' + subs + quote(args.input) + path
            else:
                url = '{CDX-API-URL}?output=json&fl=timestamp,url,mime,status,digest&url=' + subs + quote(args.input) + path + filterMIME + filterCode  
            print(colored('The commomcrawl index URL requested to get links (where {CDX-API-URL} is from ' + CCRAWL_INDEX_URL + '):','magenta'), url+'\n')
        
        print(colored('\rGetting commoncrawl.org index collections list...','cyan'), end='\r')
                  
        # Get all the Common Crawl index collections
        try:
            # Choose a random user agent string to use for any requests
            userAgent = random.choice(USER_AGENT)
            indexes = requests.get(CCRAWL_INDEX_URL, headers={"User-Agent":userAgent})
        except ConnectionError as ce:
            print(colored('[ ERR ] Common Crawl connection error', 'red'),SPACER)
            return
        except Exception as e:
            print(colored('[ ERR ] Error getting Commom Crawl index collection - ' + str(e),'red'),SPACER)
            return
        
        # If the rate limit was reached end now
        if indexes.status_code == 429:
            print(colored('[ 429 ] Common Crawl rate limit reached so unable to get links.','red'))
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
        
        print(colored('\rGetting links from the latest ' + str(len(cdxApiUrls)) + ' commoncrawl.org index collections (this can take a while for some domains)...','cyan'), end='\r')
             
        # Process the URLs from web archive        
        if not stopProgram:
            p = mp.Pool(args.processes)
            p.map(processCommonCrawlCollection, cdxApiUrls)
            p.close()
            p.join()
                           
        # Show the MIME types found (in case user wants to exclude more)
        if verbose() and len(linkMimes) > 0:
            linkMimes.discard('warc/revisit')
            print(colored('MIME types found:','magenta'), str(linkMimes) + SPACER +'\n')
        
        linkCount = len(linksFound) - originalLinkCount
        print(colored('Extra links found on commoncrawl.org:', 'cyan'), str(linkCount) + SPACER+'\n')
                    
    except Exception as e:
        print(colored('ERROR getCommonCrawlUrls 1: ' + str(e), 'red'))

def processResponses():
    """
    Get archived responses from archive.org
    """
    global linksFound, subs, path, indexFile, totalResponses, stopProgram
    try:
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
        
        # Get the list again with filters and include timestamp
        linksFound = set()
        
        # Set mime content type filter
        filterMIME = '&filter=!mimetype:warc/revisit' 
        if FILTER_MIME.strip() != '':
            filterMIME = filterMIME + '|' + FILTER_MIME
            
        # Set status code filter
        filterCode = ''
        if FILTER_CODE.strip() != '':
            filterCode = '&filter=!statuscode:' + FILTER_CODE
        
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

        url = WAYBACK_URL.replace('{DOMAIN}',subs + quote(args.input) + path).replace('{COLLAPSE}',collapse) + filterMIME + filterCode + filterLimit + filterFrom + filterTo
            
        if verbose():
            print(colored('The archive URL requested to get responses:','magenta'), url+'\n')
        
        print(colored('\rGetting list of response links (this can take a while for some domains)...','cyan'), end='\r')
            
        # Build the list of links, concatenating timestamp and URL
        try:
            # Choose a random user agent string to use for any requests
            success = True
            userAgent = random.choice(USER_AGENT)
            resp = requests.get(url, stream=True, headers={"User-Agent":userAgent}, timeout=args.timeout)  
        except ConnectionError as ce:
            print(colored('[ ERR ] archive.org connection error', 'red'),SPACER)
            resp = None
            success = False
            return 
        except Exception as e:
            print(colored('[ ERR ] Couldn\'t get list of responses: ' + str(e),'red'),SPACER)
            resp = None
            success = False
            return
        finally:
            try:
                if resp is not None:
                    # If the response from archive.org is empty, then no responses were found
                    if resp.text == '':
                        print(colored('No archived responses were found on archive.org for the given search parameters.','red'),SPACER)
                        success = False
                    # If a status other than 200, then stop
                    if resp.status_code != 200:
                        if verbose(): 
                            print(colored('[ '+str(resp.status_code)+' ] Error for '+url,'red'),SPACER)
                        success = False
                if not success:
                    print(colored('Failed to get links from archive.org - check input domain and try again.', 'red'),SPACER+'\n')
                    stopProgram = True
                    return
            except:
                pass
        
        # Go through the response to save the links found        
        for line in resp.iter_lines():
            results = line.decode("utf-8") 
            timestamp = results.split(' ')[0]
            originalUrl = results.split(' ')[1]
            linksFound.add(timestamp+'/'+originalUrl)
        
        # Remove any links that have URL exclusions
        linkRequests = set()
        exclusionRegex = re.compile(r'('+FILTER_URL.replace('.','\.')+')',flags=re.IGNORECASE)
        for link in linksFound:
            # Only add the link if:
            # a) if the -ra --regex-after was passed that it matches that
            # b) it does not match the URL exclusions
            if (args.regex_after is None or re.search(args.regex_after, link, flags=re.IGNORECASE) is not None) and exclusionRegex.search(link) is None:
                linkRequests.add(link)
            
        # Get the total number of responses we will try to get
        totalResponses = len(linkRequests)
        
        # If the limit has been set over the default, give a warning that this could take a long time!
        if totalResponses > DEFAULT_LIMIT:
            print(colored('WARNING: Downloading ' + str(totalResponses) + ' responses may take a loooooooong time! Consider using arguments -l, -ci, -from and -to wisely!\n','yellow'),SPACER)

        # Create 'results' and domain directory if needed
        createDirs()
        
        # Open the index file if hash value is going to be used (not URL)
        if not args.url_filename:
            indexFile = open(waymorePath+'/results/'+str(args.input).replace('/','-')+'/index.txt', 'a')
        
        # Process the URLs from web archive        
        if not stopProgram:
            p = mp.Pool(args.processes)
            p.map(processArchiveUrl, linkRequests)
            p.close()
            p.join()
            
        # Close the index file if hash value is going to be used (not URL)
        if not args.url_filename:
            indexFile.close()
        
    except Exception as e:
        print(colored('ERROR processResponses 1: ' + str(e), 'red'),SPACER)
    finally:
        linkRequests = None    

def createDirs():
    """
    Create a directory for the 'results' and the sub directory for the passed domain/URL
    """
    global waymorePath
    # Create a directory for "results" if it doesn't already exist
    try:
        os.mkdir(waymorePath+'/results')
    except:
        pass
    # Create a directory for the target domain
    try:
        os.mkdir(waymorePath+'/results/'+str(args.input).replace('/','-'))
    except Exception as e:
        pass     
    
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
        help='The target domain to find links for. This can be a domain only, or a domain with a specific path.',
        required=True,
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
        '-xcc',
        action='store_true',
        help='Exclude checks to commoncrawl.org. Searching all their index collections can take a while, and it may not return any extra URLs that weren\'t already found on archive.org',
        default=False
    )
    parser.add_argument(
        '-xav',
        action='store_true',
        help='Exclude checks to alienvault.com. Searching all their pages can take a while, and it may not return any extra URLs that weren\'t already found on archive.org',
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
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    args = parser.parse_args()

    showBanner()
             
    try:     

        # Get the config settings from the config.yml file
        getConfig()

        if verbose():
            showOptions()
        
        # If the mode is U (URLs retrieved) or B (URLs retrieved AND Responses downloaded)
        if args.mode in ['U','B']:
            
            # Get URLs from the Wayback Machine (archive.org)
            getWaybackUrls()
        
            # If not requested to exclude, get URLs from commoncrawl.org
            if not args.xcc and not stopProgram:
                getCommonCrawlUrls()
    
            # If not requested to exclude, get URLs from alienvault.com
            if not args.xav and not stopProgram:
                getAlienVaultUrls()
                
            # Output results of all searches
            if not stopProgram:
                processURLOutput()
        
        # If we want to get actual archived responses from archive.org...
        if (args.mode in ['R','B'] or inputIsDomainANDPath) and not stopProgram:
            processResponses()
            
            # Output details of the responses downloaded
            if not stopProgram:
                processResponsesOutput()
            
    except Exception as e:
        print(colored('ERROR main 1: ' + str(e), 'red'))

    finally:
        # Clean up
        linksFound = None  
        linkMimes = None