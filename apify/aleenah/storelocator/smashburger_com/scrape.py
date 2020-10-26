import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('smashburger_com')



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

    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

    res= session.get("https://smashburger.com/locations/",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    ca=soup.find('div', {'class': 'country country-CA'}).find_all('a', {'class': 'Teaser-titleLink'})
    us=soup.find('div', {'class': 'country country-US'}).find_all('a', {'class': 'Teaser-titleLink'})
    dic={'CA':ca,'US':us}
    for country in dic:
        stores=dic[country]
        for store in stores:
            url= store.get('href')
            logger.info(url)
            res = session.get(url,headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            jso = soup.find('script', {'type': 'application/ld+json'}).text
            jso = json.loads(jso)
            jso=jso[0]
            logger.info(jso)

            loc = jso['name']
            id=jso['branchCode']
            addr = jso['address']
            city = addr["addressLocality"]
            state = addr["addressRegion"]
            zip = addr["postalCode"].strip()
            if zip=="":
                zip="<MISSING>"
            street = addr["streetAddress"].replace(","," ").strip()
            lat = jso['location']["geo"]["latitude"]
            if str(lat) == "None":
                lat="<MISSING>"
            long = jso['location']["geo"]["longitude"]
            if str(long) == "None" or long =="":
                long="<MISSING>"
            type=jso['@type']
            phone = jso['telephone']
            if phone=="1":
                phone="<MISSING>"
            days = jso['openingHoursSpecification']
            tim=""
            for day in days:
                tim+=day['dayOfWeek']+": "+day['opens']+" - "+day['closes']+" "
            logger.info(tim)
            all.append([
                "https://smashburger.com",
                loc,
                street,
                city,
                state,
                zip,
                country,
                id,  # store #
                phone,  # phone
                type,  # type
                lat,  # lat
                long,  # long
                tim.strip(),  # timing
                url])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
