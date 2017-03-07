#author:sujit Kumar Behera
#To scrape : https://dockets.justia.com/browse/noscat-10?page=2
#Purpose:Read the bottom table grid with case details and export it to excel/csv
from bs4 import BeautifulSoup
import re, urllib2, time, sys, xlsxwriter, os.path, logging, pandas, requests
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from logging_tree import printout  # pip install logging_tree
printout()

# logging.root.handlers = []
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO , filename='ex1.log')
# 
# # set up logging to console
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# # set a format which is simpler for console use
# formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
# console.setFormatter(formatter)
# logging.getLogger("").addHandler(console)
# logging.debug('debug')
# logging.info('info')
# logging.warning('warning')
# logging.error('error')
# logging.exception('exp')



def get_pages():
 # sujit-To do dynamic identification of pages
# hard coded as of now
    pages = [1,2]
    
  
    return pages

def work():
    pages = get_pages()
   
   
    for p in pages:
        try:
            get_cases(p)
        except Exception, e:
            print e
            if 'HTTP Error' in str(e) or 'timed out' in str(e):
                work()
            else:
                # write empty .xlsx and move on
                f = str(p) + '.txt'
                xbook = xlsxwriter.Workbook(f)
                xsheet = xbook.add_worksheet(str(p))
                xbook.close()

def get_cases(pageno):
    p = pageno
    details = []
    print 'getting cases for - ' + str(p)
    start = time.time()
#     page = 'https://dockets.justia.com/browse/noscat-10?page=' + str(p)
    page = 'https://dockets.justia.com/browse/state-arkansas/noscat-10?'
    # get cases URLs for all pages
    urls=get_pageurls(page)
#     profiles = get_profiles(page)
    
    print str(urls)
    
#     newprofiles = []
#     for l in profiles:
#         newprofiles.extend(l)
    # PARALLELIZATION - multi-threaded retrieval of agent info
#     pool = ThreadPool(processes = 16)
    for u in range(len(urls)):
        get_case_details(urls[u])
    details = get_case_details(urls)
#     details = pool.map(get_case_details, urls)
#     pool.close()
#     pool.join()
    # clean details of agent
    for item in details:
        if item == 0:
            details.remove(item)
    print 'appended all for ' + str(p)
    end = time.time()
    print 'time elapsed: ' + str(end-start) + ' seconds'
    # write xlsx file with all the deets
    f = str(p) + '.xlsx'
    xbook = xlsxwriter.Workbook(f)
    xsheet = xbook.add_worksheet(str(p))
    row_index = 0
    for i in range(len(details)):
        if details[i] != 0:
            xsheet.write_row(row_index, 0, details[i])
            row_index += 1
    xbook.close()
    return details

def get_pageurls(url):
    print 'url-' + url
    all_profiles = []
    url = url.replace('?', '?page=1')
    urls = []
    for i in range(10):
        newurl = url.replace('page=1', 'page=' + str(i + 1))
        urls.append(newurl)
    # multi-threaded retrieval of profiles
    
    return urls

def get_profiles_on_page(page):
    profiles = []
    req = urllib2.Request(page)
    req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36')
    soup = BeautifulSoup(urllib2.urlopen(req).read(), 'html.parser')
    # parse each URL and append the profile ones
    for link in soup.findAll('a'):
        try:
            if 'profile/' in link['href'] and '/Reviews' not in link['href']:
                profiles.append('https://dockets.justia.com/browse/state-arkansas/noscat-10' + str(link['href']))
        except: pass
    return list(set(profiles))

def get_profiles(url):
    print 'url-' + url
    all_profiles = []
    url = url.replace('?', '?page=1')
    urls = []
    for i in range(25):
        newurl = url.replace('page=1', 'page=' + str(i + 1))
        urls.append(newurl)
    # multi-threaded retrieval of profiles
    pool = ThreadPool(processes = 3)
    all_profiles = pool.map(get_profiles_on_page, urls)
    pool.close()
    pool.join()
    return all_profiles


def get_case_details(url):
    print 'in get_case_details -----------------------------' + url
   
#     f = open('justia-data.txt','w')
    filed = []
    parties = []
    court = []
    judge = []
    lawsuit = []
    cozaction = []
    deets = []
#     soup = BeautifulSoup(urllib2.urlopen(profile).read(), 'html.parser')
#     soup = BeautifulSoup(urllib2.urlopen(profile))
#     table = soup("tr", {'class' : '-zb table-padding-10 bg-alto' })
#     table1 = soup.find("table", border=1)
#     print table1
#     table2 = table1.find('tbody')
#     table3 = table2.find_all('tr')
    page = urllib2.urlopen(url)

    content = page.read()
    
    soup = BeautifulSoup(content)
    data = soup.findAll('div',attrs={'class':'has-padding-content-block-30 -zb'});
    for dat in data:
        print dat
        print '========================'
        col = dat.find_all('time')
        column_1 = col[0].string.strip()
        print column_1
        print '------------------------'
        col2 = dat.find_all('a')
        column_2 = col2[0].string.strip()
        print column_2
        print '---------------------------------'
        col3 = dat.find_all('strong')
        column_3 = col3[0].string.strip()
        print column_3
        print '-----------------------------------------'
#     table1 = soup.find("table", border=1)
#     table2 = table1.find('tbody')
#     table3 = table2.find_all('tr')
# Scrape the HTML at the url
#     r = requests.get(profile)

# Turn the HTML into a Beautiful Soup object
#     soup = BeautifulSoup(r.text, 'lxml')
    table = soup.findAll('table',attrs={'class':'zebra bordered-rows'});
   
    table2 = table.findAll('tbody')
#     table3 = table2.find_all('tr')
#     table = soup.find(class_='zebra bordered-rows')
    for row in table2.find_all('tr',attrs={'class':'-zb table-padding-10'})[1:]:
        # Create a variable of all the <td> tag pairs in each <tr> tag pair,
        col = row.find_all('td')
       
        # Create a variable of the string inside 1st <td> tag pair,
        column_1 = col[0].string.strip()
        # and append it to first_name variable
        filed.append(column_1)
    
        # Create a variable of the string inside 2nd <td> tag pair,
        column_2 = col[1].string.strip()
        # and append it to last_name variable
        court.append(column_2)
    
        # Create a variable of the string inside 3rd <td> tag pair,
        column_3 = col[2].string.strip()
        # and append it to age variable
        judge.append(column_3)
    
        # Create a variable of the string inside 4th <td> tag pair,
        column_4 = col[3].string.strip()
        # and append it to preTestScore variable
        lawsuit.append(column_4)
    
        # Create a variable of the string inside 5th <td> tag pair,
        column_5 = col[4].string.strip()
        # and append it to postTestScore variable
        cozaction.append(column_5)
        
        
    # Create a variable of the value of the columns
    columns = {'filed': filed, 'parties': parties, 'court': court, 'judge': judge, 'lawsuit': lawsuit}

# Create a dataframe from the columns variable
 
    df = pandas.DataFrame(columns)
    df 
#     rows = soup.find("table", border=1).find("tbody").find_all("tr")
#     print str(rows)
#     for row in rows:
#         print 'row---------' + row
#         cells = row.find_all("td")
#         filed = cells[0].get_text()
#         parties = cells[1].get_text()
#         court = cells[2].get_text()
#         judge = cells[3].get_text()
#         lawsuit = cells[4].get_text()
#         causeofaction = cells[5].get_text()
#         
#         print 'filed'+ filed + 'parties' + parties + 'court' + court

# 
if __name__ == '__main__':
    work()