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

    res= session.get("https://www.comfortkeepers.com/offices")
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
            if "MailDropOnly" in phone:
                phone="<MISSING>"
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
                type.strip(),  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

