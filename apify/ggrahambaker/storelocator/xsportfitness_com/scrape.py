from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('xsportfitness_com')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.xsportfitness.com/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    base_link = 'https://www.xsportfitness.com/locations/data/locations3-lead.xml?formattedAddress=&boundsNorthEast=&boundsSouthWest='

    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    all_store_data = []

    locs = base.find_all("marker")
    link_list = []
    for l in locs:
        item = str(l)

        location_name = item.split('name="')[1].split('phone')[0].replace('"',"").strip()
        street_address = item.split('address="')[1].split('button')[0].replace('"',"").replace("address2=","").strip()
        city = item.split('city="')[1].split('display')[0].replace('"',"").strip()
        state = item.split('state="')[1].split('type')[0].replace('"',"").strip()
        zip_code = item.split('postal="')[1].split('state')[0].replace('"',"").strip()
        phone_number = item.split('phone="')[1].split('postal')[0].replace('"',"").strip()
        longit = item.split('lng="')[1].split('name')[0].replace('"',"").strip()
        lat = item.split('lat="')[1].split('lng')[0].replace('"',"").strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        page_url = "https://" + item.split('web="')[1].split('>')[0].replace('"',"").strip()
        logger.info(page_url)

        req = session.get(page_url, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        hours = " ".join(list(base.find(class_="callout large row").find(class_="large-3 columns").find_all("p")[2].stripped_strings)).replace("HOURS:","").replace("–","-").strip()

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
