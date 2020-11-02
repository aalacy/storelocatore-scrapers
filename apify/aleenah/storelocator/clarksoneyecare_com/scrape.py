import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('clarksoneyecare_com')



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

    key_set=set([])
    coords = sgzip.coords_for_radius(50)
    for coord in coords:
        #logger.info(coord)
        url="https://www.clarksoneyecare.com/wp-json/352inc/v1/locations/coordinates?lat="+coord[0]+"&lng="+coord[1]
        res = session.get(url)
        try:
            jso=res.json()

        except:
            continue
        for js in jso:
            data=js["name"]+js["address1"]+" "+js["address2"]+" "+js["address3"].strip()+js["city"]+js["state"]
            if data in key_set:
                continue
            key_set.add(data)
            res = session.get(js['permalink'])
            soup = BeautifulSoup(res.text, 'html.parser')
            tim = soup.find('div', {'class': 'col-lg-4 times'}).text.replace("\n"," ").strip()
            logger.info(tim)
            name=js["name"].replace(";s ","; ").replace( u'\u200b','')
            if ";" in name:
                name=name.split(';')[-1]
            all.append([
                "https://www.clarksoneyecare.com",
                name,
                js["address1"]+" "+js["address2"]+" "+js["address3"].strip().replace( u'\u200b',''),
                js["city"].replace( u'\u200b',''),
                js["state"].replace( u'\u200b',''),
                js["zip_code"].replace( u'\u200b',''),
                "US",
                "<MISSING>",  # store #
                js["phone_number"].replace( u'\u200b',''),  # phone
                "<MISSING>",  # type
                js["lat"].replace( u'\u200b',''),  # lat
                js["lng"].replace( u'\u200b',''),  # long
                tim.replace( u'\u200b',''),  # timing
                url.replace( u'\u200b','')])

    return all

    # query the store locator using lat, lng

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
