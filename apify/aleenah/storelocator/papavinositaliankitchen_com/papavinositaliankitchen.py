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

    res=session.get("https://www.papavinositaliankitchen.com/locations.html")
    soup = BeautifulSoup(res.text, 'html.parser')
    tds = soup.find_all('div', {'class': 'wsite-section-content'})[1].find('table').find_all('td')

    for td in tds:
        loc = td.find('h2').text
        data=td.find('strong')
        print(data)
        phone, street, csz= re.findall(r'</font><br/>([0-9\.]+)<br/>(.*)<br/>(.*[\d]{5})<br/><span>',str(data))[0]
        tim = data.text.replace(phone,'').replace(street,'').replace(csz,'').replace("Papa Vino's Italian Kitchen",'').replace('Hours','Hours: ').replace('pm','pm ').replace('day','day ').replace('  ',' ').strip()
        csz=csz.split(',')
        city=csz[0]
        csz=csz[1].strip().split(' ')
        state=csz[0]
        zip=csz[1]
        long,lat=re.findall(r'long=(.*)&lat=(.*)&domain',td.find('iframe').get('src'))[0]
        print(lat,long)
        all.append([
            "https://www.papavinositaliankitchen.com",
            loc.replace('\u200b',''),
            street.replace('\u200b',''),
            city.replace('\u200b',''),
            state.replace('\u200b',''),
            zip.replace('\u200b',''),
            'US',
            "<MISSING>",  # store #
            phone.replace('\u200b',''),  # phone
            "<MISSING>",  # type
            lat.replace('\u200b',''),  # lat
            long.replace('\u200b',''),  # long
            tim.replace('\u200b',''),  # timing
            "https://www.papavinositaliankitchen.com/locations.html"])
    return(all)

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

fetch_data()