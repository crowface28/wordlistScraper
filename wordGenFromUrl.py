from bs4 import BeautifulSoup
import requests, tldextract, string

def getLinks(url):
    try:
        req = requests.get(url)
        s = BeautifulSoup(req.text, 'html.parser')
        links = s.find_all('a')
        allLinks = []
        for link in links:
            linkDest = link.get('href')
            try:
                if linkDest[0] != "#" and (linkDest[0]=='/' or (tld in linkDest)) and 'mailto' not in linkDest:
                    if linkDest[0]=='/':
                        linkDest = url+linkDest
                    allLinks.append(linkDest)
            except:
                continue
        return allLinks
    except:
        return []


def getWords(url):
    try:
        req = requests.get(url)
        if 'video' not in req.headers['Content-Type'] and 'application' not in req.headers['Content-Type'] and 'audio' not in req.headers['Content-Type'] and 'image' not in req.headers['Content-Type']:
            s = BeautifulSoup(req.text, 'html.parser')
            page = s.get_text()
            wordsTemp = page.split()
            words = []
            for word in wordsTemp:
                wordStripped = word.translate(str.maketrans('', '', string.punctuation))
                if wordStripped not in commonWords:
                    words.append(wordStripped)
        return words
    except:
        return []


with open('commonWords.txt') as f:
    commonWords = []
    for line in f:
        commonWords.append(f.readline().strip())
    
depth = 2

target = "<target url>"
ext = tldextract.extract(target)
tld = ext.domain+'.'+ext.suffix

linkDict = {}
linkDict2 = linkDict

links = getLinks(target)
linkDict[target] = links

for run in range(depth):
    linkDict = dict(linkDict2)
    for k,v in linkDict.items():
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

for link in uniqueLinks:
    print('requesting {}'.format(link))
    try:
        req = requests.get(link)
        wordsTemp = getWords(link)
        for word in wordsTemp:
            wordsFinal.add(word)
    except Exception as e:
        print('error on {}'.format(link))
        print(str(e))
        continue

wordsFinal = list(wordsFinal)

with open('wordsOut.txt', 'w', encoding='utf8') as f:
    for word in wordsFinal:
        f.write(word+'\n')