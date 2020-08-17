
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all=[]

def fetch_data():
    # Your scraper here
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,ms;q=0.8,ur;q=0.7,lb;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.batterygiant.com',

        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}

    res=session.get("https://www.batterygiant.com/sitemap.htm",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
#    print(soup)
    sa = soup.find_all('td', {'class': 'storeLink'})
    tims=soup.find_all('td', {'width': '206'})
    print(len(sa))
    for a in sa:
        url = "https://www.batterygiant.com"+a.find('a').get('href')

        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #print(soup)
        #print(re.findall('Hour.*',str(soup))[0])


        loc=soup.find('div', {'class': 'grid_92'}).find('h1').text
        divs = soup.find_all('div', {'style': 'width:200px; float:left;'})
        print(len(divs))
        addr=divs[0].text.replace('Address:','').replace('\r','').strip().split('\n')
        csz=addr[-1]
        del addr[-1]
        street = ' '.join(addr)
        csz=csz.split(',')
        city=csz[0]
        zip=re.findall(r'[\d]{5}',csz[1])
        if zip==[]:
            state=csz[1].strip()
            zip="<MISSING>"
        else:
            zip=zip[0]
            state=csz[1].replace(zip,'').strip()

        phone=re.findall(r'Phone:([\d\-]+)',divs[1].text.replace('\n',''))
        if phone==[]:
            phone="<MISSING>"
        else:
            phone=phone[0]

        tim=soup.find('div', {'style': 'float:left; padding:8px; padding-top:0px;'}).prettify()
        #tim=tims[sa.index(a)]
        print("hours:")
        print(tim)


        """
        all.append([
            "https://grottopizza.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim.replace('Äì','').replace('¬†',''),  # timing
            a.get('href')])"""



    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
