import csv
import re
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kloecknermetals_com')



driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]

    driver.get('https://www.kloecknermetals.com/contact/kloeckner-branches/')
    #logger.info(r.html.render('return branches'))
    data=driver.execute_script("return branches")
    logger.info(len(data))
    for d in data:
        locs.append(d['branch_name'])
        street.append(d['branch_address'])
        cities.append(d['branch_city'])
        lat.append(d['branch_lat'])
        long.append(d['branch_lng'])
        p = d['branch_phone']
        if p=="":
            phones.append("<MISSING>")
        else:
            phones.append(p)
        zips.append(d['branch_postal'])
        states.append(d['branch_state'])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.kloecknermetals.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append("<MISSING>")  # timing
        row.append("https://www.kloecknermetals.com/contact/kloeckner-branches/")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
