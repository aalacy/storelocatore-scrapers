import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('greshampetroleum_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session=SgRequests()

def fetch_data():

    all=[]
    res= session.get('https://api.storepoint.co/v1/15f0da50058560/locations?rq')
    locs=res.json()['results']['locations']

    for loc in locs:

        addr=loc['streetaddress'].split(',')
        if len(addr)==3:
            city=addr[1]
        else:
            city = loc['name'].split('-')[-1].strip()
        logger.info(addr)
        logger.info(loc['name'])
        sz=addr[-1]
        del addr[-1]
        sz=sz.strip().split(' ')
        zip=sz[-1]
        del sz[-1]
        state=' '.join(sz)

        street=' '.join(addr).replace(city,'').replace('\xa0','')
        logger.info(street)
        logger.info(city)

        if loc['phone'] =='':
            phone='<MISSING>'
        else:
            phone=loc['phone']


        all.append([
            "http://greshampetroleum.com",
            loc['name'],
            street,
            city,
            state,
            zip,
            "US",
            loc['id'],  # store #
            phone,  # phone
            loc['tags'],  # type
            loc['loc_lat'],  # lat
            loc['loc_long'],  # long
            "<MISSING>",  # timing
            "https://api.storepoint.co/v1/15f0da50058560/locations?rq"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
