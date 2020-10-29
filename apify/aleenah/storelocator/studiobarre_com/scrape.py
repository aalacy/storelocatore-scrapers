import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('studiobarre_com')



driver = SgSelenium().chrome()

def get_value(item):
    if item == None or len(item) == 0:
        item = '<MISSING>'
    return item


def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '
    return {
        'street': get_value(street),
        'city': get_value(city),
        'state': get_value(state),
        'zipcode': get_value(zipcode)
    }


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


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []

    driver.get("https://studiobarre.com/find-your-studio/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    statel = soup.find_all('div', {'style': 'padding-top:50px; padding-bottom:0px; background-color:'})

    for sl in statel:
        h5s = sl.find_all("h5")

        for h in h5s:
            a = h.find_all("a")
            if a != []:
                locs.append(a[0].text)
                page_url.append(a[0].get('href'))
            else:
                locs.append(h.text)
                page_url.append("https://" + h.text.strip().lower() + ".studiobarre.com/")


    for url in page_url:
        logger.info(url)

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        addr=soup.find('ul',{'class':'elementor-icon-list-items'}).find_all('li')[0].text.strip().split('\n')[0]
        #logger.info(addr)
        parsed_address = parse_address(addr)

        cities.append(parsed_address['city'])
        states.append(parsed_address['state'])
        zips.append(parsed_address['zipcode'])
        street.append(parsed_address['street'])


        spans = soup.find_all('span', {'class': 'elementor-icon-list-text'})
        phones.append(re.sub(r'[\{\}a-z ]*', "", spans[1].text.strip()))
        try:
            tim=re.findall(r'Monday.*\d[ ]*pm',soup.text.replace('pm\n','pm, ').replace('am\n','am, '), re.DOTALL)[0]
            tim=re.sub(r'[\n]+',r' ',tim)
            tim=re.sub(r'[ ]+',' ',tim)
        except:
            try:
                tim = re.findall(r'Monday.*\d[ ]*am', soup.text.replace('pm\n', 'pm, ').replace('am\n', 'am, '), re.DOTALL)[0]
                tim = re.sub(r'[\n]+', r' ', tim)
                tim = re.sub(r'[ ]+', ' ', tim)
            except:
                tim="<MISSING>"

        tim=tim.split('Raising')[0]
        logger.info(tim)
        timing.append(tim.strip())

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://studiobarre.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
