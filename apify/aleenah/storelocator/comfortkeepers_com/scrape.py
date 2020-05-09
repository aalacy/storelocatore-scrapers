import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup


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
    headers={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9',
'cache-control': 'max-age=0',
'if-none-match': 'W/"1b70fd-YIZuQ3temblmMrTefTuK6Cg4fH0"',
'referer': 'https://www.comfortkeepers.com/offices',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'same-origin',
'sec-fetch-user': '?1',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    res= session.get("https://www.comfortkeepers.com/offices",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    states = soup.find_all('a', {'class': 'btn btn-flat btn-block ember-view'})  #states
    print(len(states))
    for state in states:
        res = session.get("https://www.comfortkeepers.com/"+state.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        stores = soup.find_all('div', {'class': 'col s12 m6 l4'})  # store
        for store in stores:
            type=store.find('div', {'class': 'card-office-label'}).text
            url="https://www.comfortkeepers.com/" + store.find('a', {'title': 'View Website'}).get('href')
            print(url)
            res = session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            jso = json.loads(soup.find('script', {'type': 'application/ld+json'}).text)  # store

            addr=jso['address']
            city = addr["addressLocality"]
            state = addr["addressRegion"]
            zip = addr["postalCode"]
            street = addr["streetAddress"]
            lat = jso["geo"]["latitude"]
            long = jso["geo"]["longitude"]
            loc=jso['name']
            phone=jso['telephone']
            tim=jso['openingHours']

            all.append([
                "https://comfortkeepers.com/",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                type,  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

