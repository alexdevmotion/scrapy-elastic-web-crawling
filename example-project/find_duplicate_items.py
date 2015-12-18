#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import redis
import sys
import time

start_time = time.time()

def main(id, no_processes):
    r = redis.Redis(host='54.201.225.114')
    no_items = r.llen("dmoz:items");
    main_interval = getMainInterval(no_items, no_processes, id)
    all_items = r.lrange("dmoz:items", 0, no_items - 1)
    main_items = all_items[main_interval[0]:main_interval[1]]
    seen_links = set()
    for main_item in main_items:
        main_item = json.loads(main_item)
        if main_item["link"] not in seen_links:
            seen_links.add(main_item["link"])
        else:
            r.lpush("dmoz:blacklist", main_item)
    secondary_intervals = getRemainingIntervals(no_items, no_processes, id)
    for secondary_interval in secondary_intervals:
        secondary_items = all_items[secondary_interval[0]:secondary_interval[1]]
        for secondary_item in secondary_items:
            secondary_item = json.loads(secondary_item)
            if secondary_item["link"] in seen_links:
                r.lpush("dmoz:blacklist", secondary_item)
    print("--- %i duplicates found in %s seconds ---" % ((r.llen("dmoz:blacklist")), (time.time() - start_time)))

def getMainInterval(len, no_processes, id):
    chunk_len = len / no_processes
    while (chunk_len * no_processes) < len:
        chunk_len = chunk_len + 1
    end = (id + 1) * chunk_len - 1
    if end > len - 1:
        end = len - 1
    return [id * chunk_len, end]

def getRemainingIntervals(len, no_processes, id):
    intervals = []
    for i in range(0, no_processes):
        if id != i:
            intervals.append(getMainInterval(len, no_processes, i))
    return intervals

if __name__ == '__main__':
    id = int(sys.argv[1])
    no_processes = int(sys.argv[2])
    main(id, no_processes)
