import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

import re


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


    res = session.get("https://tcmarkets.com/store-finder/")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('a', {'itemprop': 'url'})

    del stores[0]
    for store in stores:
        url=store.get('href')
        print(url)
        if 'https://tcmarkets.com/store-finder/dixon-ace-hardware/' in url:
            continue
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data=re.findall(r'Store Address([a-zA-Z0-9,\.\(\)\- #&\']+)Store Hours:([a-zA-Z0-9\. \-:]+)',str(soup).replace('<strong>','').replace('</p>','').replace('<p>','').replace('\n','').replace('</strong>','').replace('<br>','').replace('<br/>','').replace('\xa0','').replace('&nbsp;','').replace('Services Offered:',''))[0]
        print(data)
    """
    print(len(stores))

    for store in stores:
        id,lat,long,url=re.findall(r'store_number: (.*),lat: (.*),lon: (.*),status:.*<a href="([^"]+)">',store)[0]
        #print(id, lat, long, url)

        url='https://www.ontherun.com/store-locator/'+url
        print(url)

        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        street,city,state,zip=re.findall(r'<h1>(.*)<br/>(.*), (.*), ([\d]+)</h1>',str(soup))[0]
        phone=re.findall(r'phone-number">([\(\)\d \-]+)</h4>',str(soup))
        if phone==[]:
            phone="<MISSING>"
        else:
            phone=phone[0]

        print(street,city,state,zip,phone)
        tim=soup.find('div',{'class':'weekdays columns small-20'}).text.strip().replace('\n\n',',').replace('\n',' ')

        print(tim)

        all.append([

            "https://www.ontherun.com",
            '<MISSING>',
            street.replace('amp;',''),
            city,
            state,
            zip,
            "US",
            id,  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])

    """

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()