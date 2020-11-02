import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('elmcroft_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():

    all=[]
    url="https://www.elmcroft.com/community-results/?cq=90001&lo=&am=&dist=8016096916B94309A828CDF99707584D"

    while(True):
        res= session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #logger.info(soup)
        stores = soup.find_all('div', {'class': 'col-md-12 results'})
        logger.info(url)
        for store in stores:
            adr=store.find('address')
            data = adr.text.replace("Get Directions","").replace("View Community","").strip().replace("\n\n","\n").split("\n")
            #logger.info(data)
            loc=data[0].strip()
            street=data[1].strip()
            city=data[2].replace(",","").strip()
            state = data[3].strip()
            zip=data[4].strip()
            phone=data[5].strip()

            coord=adr.find_all('a')[1].get('href').split('@')[-1].split(",")
            #logger.info(coord)
            lat=coord[0]
            long=coord[1]
            types=store.find('div', {'class': 'living-options-list'}).find_all('li')
            type=""
            for t in types:
                type+=t.text+", "
            type=type.strip(", ")

            all.append([
                "https://www.elmcroft.com",
                loc.replace('\u200b',''),
                street.replace('\u200b',''),
                city.replace('\u200b',''),
                state.replace('\u200b',''),
                zip.replace('\u200b',''),
                "US",
                "<MISSING>",  # store #
                phone.replace('\u200b',''),  # phone
                type.replace('\u200b',''),  # type
                lat.replace('\u200b',''),  # lat
                long.replace('\u200b',''),  # long
                "<MISSING>",  # timing
                url])

        try:
            url=soup.find('a', {'aria-label': 'Next'}).get('href')
        except:

            break
    logger.info(len(all))
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
