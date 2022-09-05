#!/usr/bin/python
import sys
import re
import requests
import urllib.parse
from os_docid import docid

rf=sys.argv[1]
wf=open(sys.argv[2], 'w', encoding='gb18030')

t = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = {}
for i in range(len(t)):
    tr[t[i]] = i
s = [11,10,3,8,4,6]
xor = 177451812
add = 8728348608

def docid_try(x):
    try:
        return docid(x)
    except:
        return 'nan'

def dec(x):
    r=0
    for i in range(6):
        r+=tr[x[s[i]]]*58**i
    return (r-add)^xor


def enc(x):
    x=(x^xor)+add
    r = ['B', 'V', '1', ' ', ' ', '4', ' ', '1', ' ', '7', ' ', ' ']
    for i in range(6):
        r[s[i]]=t[x//58**i%58]
    return ''.join(r)


def urlenc(x):
    start_pos = 0
    #ux = x.decode('u8', 'ignore')
    ux = x
    cpystr = ''
    flag = False
    for cc in re.finditer(u'[\u4e00-\u9fa5]+', ux):
        cpystr += ux[start_pos:cc.start()] + urllib.parse.quote(cc.group().encode('u8'))
        start_pos = cc.end()
        flag = True
    cpystr += ux[start_pos:]
    if flag:
        return cpystr
    else:
        return x


_PREFIX_SERV = 'http://portal.cm.sogou/cgi-bin/prefixlookup.pl?u=%s&n='
def get_baike_url(bkurl):
    urllist = []
    m = re.search(r'https?://baike\.sogou\.com/v(\d+)\.htm', bkurl)
    if not m:
        return urllist
    try:
        uu = 'http://baike.sogou.com/v%s.htm' % m.group(1)
        serv = _PREFIX_SERV % urllib.parse.quote(uu)
        r = requests.get(serv)
        if r.status_code == 200:
            for l in r.text.split('\n'):
                if l.startswith('http'):
                    urllist.append(l.strip().split('\t')[0])
    except:
        print >> sys.stderr, 'get baike url failed', uu
    return urllist


def general_transform(u):
     urllist = []
     if u.startswith('http://'):
        urllist.append(u.replace('http://', 'https://'))
     elif u.startswith('https://'):
        urllist.append(u.replace('https://', 'http://'))
     m = re.search('\\.(html|htm|shtml)$', u)
     if m:
        urllist.append(u[:m.start()])
     for url in urllist:
         m = re.search('\\.(html|htm|shtml)$', url)
         if m:
            urllist.append(url[:m.start()])

     return urllist


if __name__ == '__main__':
    handled = set()
    #for line in sys.stdin:
    for line in open(rf, encoding='utf8'):
        segs = line.strip().split('\t')
        if len(segs) != 3:
            continue
        query, rank, url = segs
        if url in handled:
            continue
        else:
            handled.add(url)
        did = str(docid_try(url))
        if did: wf.write('\t'.join([query, rank, url, url, did])+'\n')
        oriurl = urlenc(url)
        m = re.search(r'https?://www.bilibili.com/(read|video)/(av|bv|cv)(\w+)', oriurl, flags=re.I)
        if m:
            if m.group(2).lower() == 'av' and m.group(1) == 'video':
                uu = 'https://www.bilibili.com/video/%s/' % enc(int(m.group(3)))
            elif m.group(2).lower() == 'bv' and m.group(1) == 'video':
                uu = 'https://www.bilibili.com/video/BV%s/' % m.group(3)
            else:
                uu = 'https://www.bilibili.com/read/cv%s/' % m.group(3)
            did = str(docid(uu))
            if did: wf.write('\t'.join([query, rank, url, uu, did])+'\n')
            continue
        m = re.search(r'https?://(www\.)?sohu\.com/a/(\d+_\d+)', oriurl)
        if m:
            uu = 'https://www.sohu.com/a/%s' % m.group(2)
            did = str(docid_try(uu))
            if did: wf.write('\t'.join([query, rank, url, uu, did])+'\n')
            continue
        m = re.search(r'https?://zh\.(m\.)?wikipedia\.org/([\w-]+)/(\S+)', oriurl)
        if m:
            for p in ('zh-hans', 'zh-cn', 'wiki'):
                uu = 'https://zh.wikipedia.org/%s/%s' % (p, m.group(3))
                did = str(docid_try(uu))
                if did: wf.write('\t'.join([query, rank, url, uu, did])+'\n')
            continue
        if oriurl.startswith('https://wenwen.sogou.com/'):
            uu = oriurl.replace('https://', 'http://')
            did = str(docid_try(uu))
            if did: wf.write('\t'.join([query, rank, url, uu, did])+'\n')
            continue
        m = re.search(r'https?://baike\.sogou\.com/v(\d+)\.htm', oriurl)
        if m:
            uu = 'http://baike.sogou.com/v%s.htm' % m.group(1)
            urls = get_baike_url(uu)
            for u in urls:
                did = str(docid_try(u))
                if did: wf.write('\t'.join([query, rank, url, u, did])+'\n')
            continue
        elif url != oriurl:
            did = str(docid_try(oriurl))
            if did: wf.write('\t'.join([query, rank, url, oriurl, did])+'\n')
        for u in general_transform(oriurl):
            did = str(docid_try(u))
            if did: wf.write('\t'.join([query, rank, url, u, did])+'\n')

