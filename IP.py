#!/usr/bin/env python

import re
from HTMLParser import HTMLParser

from bs4 import BeautifulSoup
import re, urllib2, time, sys, os.path
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

class Table(list):
    def append_row(self):
        self.append([])

    def append_cell(self, data):
        self[-1].append(data)

    # remove all HTML tags but keep the text between tags
    def flatten(self):
        for i, row in enumerate(self):
            self[i] = map(lambda cell: re.sub('<[^>]*>', '', cell).strip(), row)

class HTMLTableExtractor(HTMLParser):
    STATE_OUTTER        = 0
    STATE_IN_TABLE      = 1
    STATE_IN_ROW        = 2
    STATE_IN_CELL       = 3
    STATE_IN_CELL_TABLE = 4

    def handle_starttag(self, tag, attrs):
        if self.state == self.STATE_IN_CELL:
            self.cell_data += '<%s %s>' % (tag, 
                    ' '.join(['%s="%s"' % (str(name), str(value)) for name, value in attrs]))
            if tag == 'table':
                self.depth += 1
        elif tag == 'table':
            if self.state != self.STATE_OUTTER:
                raise Exception('Incorrectly nested table found')
            self.state = self.STATE_IN_TABLE
            self.tables.append(Table())
        elif tag == 'tr':
            if self.state != self.STATE_IN_TABLE:
                raise Exception('<tr> found outside a table')
            self.state = self.STATE_IN_ROW
            self.tables[-1].append_row()
        elif tag in ('td', 'th'):
            if self.state != self.STATE_IN_ROW:
                raise Exception('<%s> found outside a table' % tag)
            self.state = self.STATE_IN_CELL
            self.cell_data = ''

    def handle_endtag(self, tag):
        if self.state == self.STATE_IN_CELL:
            if tag in ('td', 'th') and self.depth == 0:
                self.state = self.STATE_IN_ROW
                self.tables[-1].append_cell(self.cell_data.strip())
            else:
                self.cell_data += '</%s>' % tag
                if tag == 'table':
                    self.depth -= 1
                    assert(self.depth >= 0)
        elif tag == 'table' and self.state == self.STATE_IN_TABLE:
            self.state = self.STATE_OUTTER
        elif tag == 'tr' and self.state == self.STATE_IN_ROW:
            self.state = self.STATE_IN_TABLE

    def handle_data(self, data):
        if self.state == self.STATE_IN_CELL:
            if data != data.lstrip():
                data = ' ' + data.lstrip()
            if data != data.rstrip():
                data = data.rstrip() + ' '
            self.cell_data += data

    def get_tables(self, html):
        self.state = self.STATE_OUTTER
        self.tables = []
        self.depth = 0
        self.cell_data = ''

        self.feed(html)
        return self.tables

    def get_tables_nested(self, html):
        self.all_tables = []

        def recur(self, html):
            tables = self.get_tables(html)
            self.all_tables += tables
            for table in tables:
                for row in table:
                    for cell in row:
                        recur(self, cell)

        recur(self, html)
        return self.all_tables

def print_tables(tables):
    for i, table in enumerate(tables):
        print 'Table %d/%d' % (i + 1, len(tables))
        print '-' * 78
        for row in table:
            print '|',
            for cell in row:
                print cell, '|',
            print
        print '-' * 78
        print

if __name__ == '__main__':
    print 'Nested tables sample'
    html = urllib2.urlopen('https://dockets.justia.com/browse/noscat-10').read()
    
    extractor = HTMLTableExtractor()
    tables = extractor.get_tables_nested(html)
    for i in range(len(tables)):
        tables[i].flatten()
    print_tables(tables)

    print 'Flattened table sample'
    html = urllib2.urlopen('https://dockets.justia.com/browse/noscat-10').read()
    extractor = HTMLTableExtractor()
    tables = extractor.get_tables(html)

    for i in range(len(tables)):
        tables[i].flatten()
    print_tables(tables)