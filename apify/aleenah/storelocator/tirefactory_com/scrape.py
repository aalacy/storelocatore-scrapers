import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tirefactory_com')



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

    res=session.get("https://www.tirefactory.com/Find-a-Location")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'class': 'sitemap_states_list'})

    for div in divs:
        sts=div.find_all('a')
        for st in sts:
            res = session.get("https://www.tirefactory.com"+st.get('href'))
            soup = BeautifulSoup(res.text, 'html.parser')
            ndivs = soup.find_all('div', {'class': 'sitemap_states_list'})
            for ndiv in ndivs:
                cities = ndiv.find_all('a')
                for city in cities:
                    res = session.get("https://www.tirefactory.com" + city.get('href'))
                    soup = BeautifulSoup(res.text, 'html.parser')
                    sdivs = soup.find_all('div', {'class': 'sitemap_states_list'})
                    for sdiv in sdivs:
                        stores=sdiv.find_all('a')
                        for store in stores:
                            if "factory" in store.text.lower() or "Dan's Tire Service" in store.text:
                                url="https://www.tirefactory.com" + store.get('href')
                                res = session.get(url)
                                soup = BeautifulSoup(res.text, 'html.parser')
                                data= soup.find('div', {'class': 'tooltiptext'}).find('div', {'class': 'storeInfoDetails'}).text.strip().replace('\r\n','').replace('\n\n','\n').split('\n')
                                loc = data[1].strip()
                                street=data[2].strip()
                                csz=data[3].strip().split(',')
                                logger.info(csz)
                                phone=data[4].strip()
                                tim= data[9].strip().replace('M','Monday').replace('F','Friday')+" "+data[10].strip().replace('SAT','Saturday')+" "+data[11].strip().replace('SUN','Sunday')
                                city=csz[0].strip()
                                csz=csz[1].strip().split(' ')
                                state = csz[0]
                                zip=csz[1]
                                try:
                                    lat,long=re.findall(r'lat:(-?[\d\.]+),lon:(-?[\d\.]+)',str(soup))[0]
                                except:
                                    lat=long="<MISSING>"

                                all.append([
                                    "https://www.tirefactory.com",
                                    loc,
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
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
