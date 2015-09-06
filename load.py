#!/usr/bin/env python


import argparse
import sys
import csv
import sqlite3
import time
import logging
import re
import os


# config
integer_keys = ('count', 'tradelistcount', 'cardnumber')
real_keys = ('myprice', 'price')


# check version
version = sys.hexversion
if version < 0x02070000:
    sys.stderr.write('python 2.7 or higher required\n')
    sys.exit(-1)


# parse args
parser = argparse.ArgumentParser(description = 'Create an SQLite database from a Deckbox export.', formatter_class = argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-f', '--input-file', required = True, help = 'CSV file containing an export from Deckbox')
parser.add_argument('-d', '--database-file', default = 'database.sqlite3', help = 'SQLite databse file.')
parser.add_argument('--log-level', default = 'INFO', help = 'set the log level to increase or decrease verbosity')

args = parser.parse_args()

in_file = args.input_file
db_file = args.database_file
log_level = args.log_level

# setup logging
logging.basicConfig(format = '%(asctime)s %(levelname)s: %(message)s', level = getattr(logging, log_level.upper()), datefmt = '%Y/%m/%d %H:%M:%S')


# check args
if not os.path.isfile(in_file):
    logging.critical('input file does not exist')
    sys.exit(-1)

if os.path.isfile(db_file):
    logging.critical('database file already exists')
    sys.exit(-1)


# read the file to get the column headers
logging.info('reading column headers from the first line of the file...')
headers = []
with open(in_file, 'r') as ifp:
    reader = csv.reader(ifp)

    headers = reader.next()

logging.debug('headers: ' + ', '.join(headers))


# get keys and set their types
logging.info('converting columng headers to keys...')
keys = []
types = {}
for h in headers:
    k = h.replace(' ', '').lower()
    keys.append(k)
    types[k] = 'text'

for key in integer_keys:
    types[key] = 'int'

for key in real_keys:
    types[key] = 'real'

logging.debug('keys: ' + ','.join(keys))


# get the contents using the keys
logging.info('reading contents of the file...')
contents = []
with open(in_file, 'r') as ifp:
    reader = csv.DictReader(ifp, keys)

    skip_headers = reader.next()
    logging.debug('skipping headers: ' + ','.join(skip_headers))

    for row in reader:
        if row:
            # transforms
            for integer_key in integer_keys:
                s = row[integer_key]
                v = re.sub('[^0-9\.]', '', s)
                row[integer_key] = v

            for real_key in real_keys:
                s = row[real_key]
                v = re.sub('[^0-9\.]', '', s)
                row[real_key] = v

            logging.debug('row: ' + ','.join(row.values()))
            contents.append(row)


# build the create and insert statements
create = 'CREATE TABLE IF NOT EXISTS cards ('
insert = 'INSERT INTO cards VALUES ('
for key in keys:
    create = create + key + ' ' + types[key] + ', ' 
    insert = insert + '?,'
create = create + ' created_at int, updated_at int)'
insert = insert + '?,?)'

logging.debug('create statement: ' + create)
logging.debug('insert statement: ' + insert)


# load the data
logging.info('loading cards...')

conn = sqlite3.connect(db_file)
conn.execute(create)

t = str(int(time.time()))

for row in contents:
    data = []
    for key in keys:
        data.append(row[key])
    data.append(t)
    data.append(t)

    logging.debug('loading data: ' + ','.join(data))

    with conn:
        conn.execute(insert, data)






