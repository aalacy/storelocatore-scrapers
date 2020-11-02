import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thebarrecode_com')



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

    driver.get("https://www.thebarrecode.com/studios/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    divs = soup.find_all('div', {'class': 'studio-box studio-box-toprow studio-column'})
    divs+= soup.find_all('div', {'class': 'studio-box studio-column'})
    logger.info(len(divs))
    sa = soup.find_all('a',{'class':'hoveranchor'})
    logger.info(len(sa))
    for a in sa:
        url="https://www.thebarrecode.com/studios/"+a.get("href")
        page_url.append(url)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            div = soup.find('div', {'class': 'studio-column-66'}).find_all('div')[1]
            data= div.get("data-mapdata")
            lat.append( re.findall(r'.*"coordinates":\[-?[\d\.]*,(-?[\d\.]*)', data)[0])
            long.append(re.findall(r'.*"coordinates":\[(-?[\d\.]*),', data)[0])
        except:
            lat.append("<MISSING>")
            long.append("<MISSING>")

    for div in divs:
        tex = div.text.strip().split("\n")

        try:
            del tex[tex.index("")]
        except:
            k=9
        if len(tex)<6:
            logger.info(tex)
        ids.append(tex[0].strip())
        locs.append(tex[2].strip())
        street.append(tex[3].strip())
        addr=tex[4].strip().split(",")
        logger.info(addr)
        cities.append(addr[0])
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])
        try:
            p=re.findall(r'([0-9 \(\)\-]+)',tex[5].strip() )
            if p ==[]:
                phones.append("<MISSING>")
            else:
                phones.append(p[0])
        except:
            phones.append("<MISSING>")
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.thebarrecode.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append("<MISSING>")  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
