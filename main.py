from html.parser import HTMLParser
import requests
from lxml import html
from threading import Thread, Lock
from db import new_conn
import time
crawled = []
linktree = []
to_be_crawled = []
lock = Lock()
workers = []
n = 0

class Parser(HTMLParser):
    global to_be_crawled
    global last_crawled
    last_crawled = ''
    def get_hrefs(self, page=None):
        while True:
            if len(to_be_crawled) == 0:
                if page != None:
                    print(page)
                    self.last_crawled = page
                    page_data = requests.get(page)
                    page_data = html.fromstring(page_data.content)
                    [self.crawled_url(d) for d in page_data.xpath('//a/@href')
                    if d != '#' and 'mailto' not in d and d[0:4] == 'http'
                    and d != '' and d not in to_be_crawled]
                    print(to_be_crawled)
                    return 'completed'
                else:
                    pass
            else:
                try:
                    lock.acquire()
                    acq_page = to_be_crawled[0]
                    to_be_crawled.pop(0)
                    crawled.append(acq_page)
                    lock.release()
                    self.last_crawled = acq_page
                    page_data = requests.get(acq_page)
                    page_data = html.fromstring(page_data.content)
                    lock.acquire()
                    [self.crawled_url(d) for d in page_data.xpath('//a/@href')
                     if d != '#' and 'mailto' not in d and d[0:4] == 'http'
                     and d != '' and d not in to_be_crawled and d not in crawled]
                    lock.release()
                    global n
                    print(len(to_be_crawled))
                    time.sleep(5)
                    if n >= 2000:
                        return 'finished'
                except Exception as e:
                    print(e, 'something went wrong')

    def crawled_url(self, url):
        global n
        n += 1
        conn, c = new_conn()
        c.execute('''INSERT INTO crawled(url, parent) values(%s, %s)''', (url, self.last_crawled))
        to_be_crawled.append(url)
        conn.commit()

p = Parser()
source = p.get_hrefs('https://ryanmakesrobots.com')

for x in range(8):
    worker_parser = Parser()
    worker = Thread(target=worker_parser.get_hrefs, args=())
    workers.append(worker)
    worker.start()