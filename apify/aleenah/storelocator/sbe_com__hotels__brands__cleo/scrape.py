import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sbe_com__hotels__brands__cleo')



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
    res=session.get("https://www.sbe.com/restaurants/brands/cleo")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find_all('a', {'class': 'ftr-itm-hrf item-click'})
    divs=soup.find_all('div', {'class': 'address abstop vert-center'})

    for url in urls:
        url=url.get('href')
        if url=="https://www.sbe.com/restaurants/locations/cleo-baha-mar/" or url == "https://www.sbe.com/restaurants/locations/cleo-kuwait/":
            continue
     #   logger.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            tim = soup.find('div', {'class': 'text-spaced-extra more_info'}).text.replace(
            'Order Food Delivery with DoorDash', '').replace('\n', ' ').strip()
        except:
            continue
        street = soup.find('span', {'class': 'address1'}).text
        city=soup.find('span', {'class': 'city'}).text.replace(',','')
        state=soup.find('span', {'class': 'state'}).text
        zip=soup.find('span', {'class': 'postal_code'}).text.strip()
        if zip=="":
            zip="<MISSING>"

        phone=soup.find('li', {'class': 'serif-face cols borderright'}).find('a').text
        lat=soup.find('div', {'id': 'map_canvas'}).get('data-latitude')
        long=soup.find('div', {'id': 'map_canvas'}).get('data-longitude')

        all.append([
            "https://www.sbe.com/restaurants/brands/cleo",
            city,
            street,
            city,
            state,
            zip,
            'US',
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])

    #logger.info(len(divs))
    for i in range(2,4): #south beach & las vegas

        divas=divs[i].find_all('div')
        street=divas[0].text.strip()
        addr=divas[1].text.strip().split(',')
        city=addr[0].replace(',','')
        state=addr[1].strip()
        zip=addr[2].strip()

        all.append([
            "https://www.sbe.com/restaurants/brands/cleo",
            city,
            street,
            city,
            state,
            zip,
            'US',
            "<MISSING>",  # store #
            "<MISSING>",  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "https://www.sbe.com/restaurants/brands/cleo"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
