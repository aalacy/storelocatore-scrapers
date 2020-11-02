# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hymiler_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url",  "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    # Your scraper here
    data = []
    p = 0
    url = 'https://hymiler.com/locations/hy-miler-2224-townsend-road'
    r = session.get(url, headers=headers, verify=False)
    time.sleep(3)    
    soup = BeautifulSoup(r.text,"html.parser")
    mainselect = soup.find('select')
    poption = mainselect.findAll('option')
    logger.info(len(poption))
    
    locs = []
    titles = []

    for n in range(1, len(poption)):
        link = poption[n]['value']
        link = "https://hymiler.com" + link
        locs.append(link)
        titles.append(poption[n].text)
    locs.append('https://hymiler.com/locations/hy-miler-2224-townsend-road')
    titles.append('Hy-Miler #2224, Townsend Road')

    
    cleanr = re.compile(r'<[^>]+>')
    for n in range(0, len(locs)):
        link = locs[n]
        title = titles[n]
        
          
        time.sleep(2)
        start = title.find("#") + 1
        end = title.find(",", start)
        store = title[start:end]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text,"html.parser")
        maindiv = soup.find('span',{'class':'locationaddress'})
        detail = cleanr.sub('\n', str(maindiv))
        
        detail = detail.splitlines()
        street = detail[1]
        city,state = detail[2].split(',', 1)
        pcode = detail[3]
        pcode = pcode.replace('United States ','')
        
        phone = detail[5]

        
        detail = str(soup)
        start = detail.find('"coordinates"')
        start = detail.find('[', start)+ 1
        end = detail.find(",", start)
        longt = detail[start:end]
        start = end + 1
        end = detail.find(']',start)
        lat = detail[start:end]               
        if detail.find("Open 24 hours") > -1:
            hours = "Open 24 hours"
        else:
            hours = "<MISSING>"
        lat = lat[0:8]
        longt = longt[0:8]
        title = title.replace(",", "")

       
        
        
        data.append([
            'https://hymiler.com',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            store,
            phone,
            "<MISSING>",
            lat,
            longt,
            hours
        ])
        #logger.info(p,data[p])
        p += 1
        
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
