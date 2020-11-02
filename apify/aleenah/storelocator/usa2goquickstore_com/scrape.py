import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('usa2goquickstore_com')



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
    headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    res = session.get("https://usa2goquickstore.com/locations/",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('div', {'class': 'fusion-column-content'})

    for store in stores:
        loc= store.find('h2').text.strip()
        data=store.find_all('div', {'class': 'fusion-text'})[1].text.replace('click here for directions','').strip().split("\n")
        logger.info(data)

        street=data[0].strip()
        try:
            sz=data[1].strip().split(",")
            city = sz[0]
            sz = sz[1].strip().split(" ")
            state = sz[0]
            zip = sz[1]
        except:
            sz=data[1].strip().split(" ")
            zip=sz[-1]
            state=sz[-2]
            city=data[1].replace(zip,'').replace(state,'').strip()

        phone=data[2].replace('t:','').replace('\xa0','').strip()

        all.append([
            "https://usa2goquickstore.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "https://usa2goquickstore.com/locations/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()