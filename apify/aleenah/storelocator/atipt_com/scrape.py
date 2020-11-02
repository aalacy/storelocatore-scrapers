import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('atipt_com')



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
    res= session.get("https://locations.atipt.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    states = soup.find('ul', {'class': 'list-unstyled'}).find_all('a') #states
    headers={'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
             'referer': 'https://locations.atipt.com//fort-wayne-in-lima-rd',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'}
    for state in states:
        res = session.get("https://locations.atipt.com/"+state.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        cities = soup.find('ul', {'class': 'list-unstyled'}).find_all('a')  #cities
        for city in cities:
            res = session.get("https://locations.atipt.com/" + city.get('href'))
            soup = BeautifulSoup(res.text, 'html.parser')
            stores = soup.find_all('a', {'class': 'name'})  #stores
            for store in stores:
                loc = store.find('h3').text
                url="https://locations.atipt.com/" + store.get('href')
                """if url != "https://locations.atipt.com//fort-wayne-in-lima-rd":
                    res = session.get(url,headers=headers)
                    soup = BeautifulSoup(res.text, 'html.parser')
                else:
                    driver.get("https://locations.atipt.com//fort-wayne-in-lima-rd")
                    soup = BeautifulSoup(driver.page_source, 'html.parser')"""
                res = session.get(url,headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                jso = soup.find('script', {'type': 'application/ld+json'}).text
                jso=json.loads(jso)

                addr=jso["address"]
                city=addr["addressLocality"]
                state=addr["addressRegion"]
                zip=addr["postalCode"]
                street=addr["streetAddress"]
                lat=jso["geo"]["latitude"]
                long=jso["geo"]["longitude"]
                type=jso["name"]
                phone=soup.find('p', {'class': 'btn businesscard__info-btn hidden-xs'}).text.replace("Call","").strip()
                days=soup.find_all('p', {'class': 'day'})

                hours=soup.find_all('div', {'class': 'hours'})

                tim=""
                logger.info(url)
                #logger.info(len(hours))
                if len(hours)!=0:
                    for i in range(7):
                        ps = hours[i].find_all('p')
                        tim+= days[i].text+ps[0].text+" - "+ps[1].text+" "

                    tim=tim.replace("  - Closed","Closed")
                else:
                    tim="<MISSING>"

                all.append([
                    "https://atipt.com/",
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
                    tim.strip(),  # timing
                    url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
