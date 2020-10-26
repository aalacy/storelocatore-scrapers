import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('henny-penny_com')



driver = SgSelenium().chrome()

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
    page_url=[]
    driver.get("http://henny-penny.com/locations/")
    #res=session.get("http://henny-penny.com/locations/",headers={'sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'cross-site','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'})
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all('div', {'class': 'row'})
    #logger.info(len(rows))
    del rows[0]
    del rows[0]
    del rows[0]
    del rows[0]
    del rows[-1]
    del rows[-1]
    del rows[-1]
    for row in rows:
        #logger.info(row.find('h3').text)
        loc=row.find('h3').text
        addrs=row.find_all('p')
        iframes=row.find_all('iframe')

        for add in addrs:
            addr=add.text.split("\n")
            #logger.info(addr.find('strong').text)
            id=re.findall(r'(\d+)',addr[0].strip())[0]
            street=addr[1].strip()
            phone=addr[3].strip()
            tim=addr[4].strip()
            addr=addr[2].strip().split(",")
            city = addr[0]
            addr=addr[1].strip().split(" ")
            #logger.info(addr)
            if len(addr) !=1:

                state=addr[0]
                zip=addr[1]
            else:
                city=city.replace('CT',"").strip()
                state = 'CT'
                zip=addr[0]
            long,lat=re.findall(r'!2d(.*)!3d([\.\d\-]+)!',iframes[addrs.index(add)].get('src'))[0]

            all.append([
                "http://henny-penny.com",
                loc,
                street,
                city,
                state,
                zip,
                'US',
                id,  # store #
                phone,  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                "http://henny-penny.com/locations/"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
