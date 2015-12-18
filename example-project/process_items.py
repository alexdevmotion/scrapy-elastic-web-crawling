#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import redis
import csv
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

def main(id, no_processes):
    start_time = time.time()
    r = redis.Redis(host='54.201.225.114')
    writer = csv.writer(open("items.csv", 'a'), lineterminator='\n')
    no_items = r.llen("dmoz:items");
    interval = getInterval(no_items, no_processes, id)
    items = r.lrange("dmoz:items", interval[0], interval[1]) 
    for item in items:
        item = json.loads(item)
        try:
            writer.writerow([item[key] for key in item.keys()])
        except KeyError:
            print u"Error procesing: %r" % item
    print("--- %i items processed in %s seconds ---" % ((interval[1] - interval[0]), (time.time() - start_time)))

def getInterval(len, no_processes, id):
    chunk_len = len / no_processes
    while (chunk_len * no_processes) < len:
        chunk_len = chunk_len + 1
    end = (id + 1) * chunk_len - 1
    if end > len - 1:
        end = len - 1
    return [id * chunk_len, end]

if __name__ == '__main__':
    id = int(sys.argv[1])
    no_processes = int(sys.argv[2])
    main(id, no_processes)
