import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('talbots_com')



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
    res=session.get("https://www.talbots.com/on/demandware.store/Sites-talbotsus-Site/default/Stores-GetNearestStores?latitude=37.090240&longitude=-95.712891&maxdistance=5000")
    jso=res.json()["stores"]

    for id,js in jso.items():
        #logger.info(id)
        all.append([
            "https://www.talbots.com",
            js["name"],
            js["address2"],
            js["city"],
            js["stateCode"],
            js["postalCode"],
            js["countryCode"],
            id,  # store #
            js["phone"],  # phone
            "<MISSING>",  # type
            js["latitude"],  # lat
            js["longitude"],  # long
            js["storeHours"].replace("<br>",", "),  # timing
            "https://www.talbots.com/on/demandware.store/Sites-talbotsus-Site/default/Stores-GetNearestStores?latitude=37.090240&longitude=-95.712891&maxdistance=5000"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()