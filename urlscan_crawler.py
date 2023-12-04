from json import loads
import requests
from sys import argv
def urlsscan_urls( target ):
    uuids = ''
    with open(f"urls_{target}.txt", 'a')as f:
        req = loads(requests.get(f"https://urlscan.io/api/v1/search/?q=domain:{target}&size=10000").text)
        numb = int(req['total'])
        for url in req['results']:
            if target in url['task']['url']:
                print(url['task']['url'])
                f.write( url['task']['url'] + '\n')
            if target in url['page']['url']:
                print(url['page']['url'])
                f.write( url['page']['url'] + '\n')
            uuids = str(url["sort"][0])+"%2C"+str(url["sort"][1])
        numb2 = numb // 200
        for number in range(1, numb2 + 1 ):
            req2 = loads(requests.get(f"https://urlscan.io/api/v1/search/?q={target}&search_after={uuids}").text)
            for url2 in req2['results']:
                if target in url2['task']['url']:
                    print(url2['task']['url'])
                    f.write( url2['task']['url'] + '\n')
                if target in url2['page']['url']:
                    print(url2['page']['url'])
                    f.write( url2['page']['url'] + '\n')
                uuids = str(url2["sort"][0])+"%2C"+str(url2["sort"][1])
urlsscan_urls( argv[1] )