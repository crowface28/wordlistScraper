from bs4 import BeautifulSoup
import requests, tldextract, string, re
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
from multiprocessing.dummy import Pool as ThreadPool
pool = ThreadPool(20)

def getLinks(url):
        allLinks = []
        if url not in linksDone:
            print('getlinks({})'.format(url))
            try:
                req = requests.get(url, headers=headers, verify=False, timeout=5)
                if req.status_code==200:
                    if 'video' not in req.headers['Content-Type'] and 'application' not in req.headers['Content-Type'] and 'audio' not in req.headers['Content-Type'] and 'image' not in req.headers['Content-Type']:
                        s = BeautifulSoup(req.text, 'html.parser')
                        links = s.find_all('a')
                        for link in links:
                            linkDest = link.get('href')
                            try:
                                if linkDest[0] != "#" and (linkDest[0]=='/' or (tld in linkDest)) and 'mailto' not in linkDest:
                                    if linkDest[0]=='/':
                                        linkDest = 'https://'+domain+linkDest
                                        linkDest = re.sub('([^:])//', r'\1/', linkDest)
                                    allLinks.append(linkDest)
                            except:
                                continue
            except Exception as e:
                print('getLinks() error on {}'.format(url))
                print(str(e))
                return []
            linksDone.append(url)
        return allLinks
    


def getWords(url):
    try:
        words = []
        req = requests.get(url, headers=headers, verify=False, timeout=5)
        if 'video' not in req.headers['Content-Type'] and 'application' not in req.headers['Content-Type'] and 'audio' not in req.headers['Content-Type'] and 'image' not in req.headers['Content-Type']:
            if req.status_code==200:
                s = BeautifulSoup(req.text, 'html.parser')
                page = s.get_text()
                wordsTemp = page.split()
                for word in wordsTemp:
                    wordStripped = word.translate(str.maketrans('', '', string.punctuation))
                    if wordStripped not in commonWords and wordStripped[0:4] != 'https':
                        words.append(wordStripped)
                templates = s.find_all('template')
                for temp in templates:
                    strs = temp.get_text()
                    wordsTemp = strs.split()
                    for word in wordsTemp:
                        wordStripped = word.translate(str.maketrans('', '', string.punctuation))
                        if wordStripped not in commonWords and wordStripped[0:4] != 'https':
                            words.append(wordStripped)
        return words
    except Exception as e:
        print('getWords() error on {}'.format(url))
        print(str(e))
        return []


with open('commonWords.txt') as f:
    commonWords = []
    for line in f:
        commonWords.append(f.readline().strip())
    
depth = 1
target = "<url target>"

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

ext = tldextract.extract(target)
tld = ext.domain+'.'+ext.suffix
domain = ext.subdomain+'.'+ext.domain+'.'+ext.suffix

linkDict = {}
linkDict2 = linkDict
linksDone = []

links = getLinks(target)
linkDict[target] = links

for run in range(depth):
    linkDict = dict(linkDict2)
    for k,v in linkDict.items():
        if v!=None:
            for link in v:
                links = getLinks(link)
                linkDict2[link] = links

linkDict = dict(linkDict2)

uniqueLinks = set()
for run in range(depth):
    for k,v in linkDict.items():
        for link in v:
            uniqueLinks.add(link)


wordsFinal = set()



results = pool.map(getWords, uniqueLinks)
for page in results:
    for word in page:
        wordsFinal.add(word)

'''
for link in uniqueLinks:
    print('requesting {}'.format(link))
    try:
        wordsTemp = getWords(link)
        for word in wordsTemp:
            wordsFinal.add(word)
    except Exception as e:
        print('main() error on {}'.format(link))
        print(str(e))
        continue
'''

wordsFinal = list(wordsFinal)

with open('output/{}_wordsOut.txt'.format(target.translate(str.maketrans('', '', string.punctuation))), 'w', encoding='utf8') as f:
    for word in wordsFinal:
        f.write(word+'\n')