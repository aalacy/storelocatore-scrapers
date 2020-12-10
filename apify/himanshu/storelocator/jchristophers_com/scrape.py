import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jchristophers_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.jchristophers.com/find-a-j-christophers/"
    r = session.get(base_url, headers=headers, timeout=5)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div',{'class','post-content'})
    data_rem = exists.find_all("a")
    for i in data_rem :
        if "/maps/" in i['href'] :
            data = (i.parent)
            if "Flowery Branch" in data.text or "Peachtree City" in data.text or "Woodstock" in data.text :
                store = []
                store.append("http://www.jchristophers.com")
                store.append("J. Christopher's ("+ str(data.text) +")")
                store.append(data.findNext("p").text)
                store.append(data.findNext("p").findNext("p").text.split(",")[0])
                store.append(data.findNext("p").findNext("p").text.split(",")[1].strip().split(" ")[0])
                store.append(data.findNext("p").findNext("p").text.split(",")[1].strip().split(" ")[1])
                store.append("US")
                store.append("<MISSING>")
                store.append(data.findNext("p").findNext("p").findNext("p").text)
                store.append("resturant")
                lat = ''
                lng = ''
                if "Peachtree City" in data.text:
                    lat = "33.398584"
                    lng = "-84.5928759"
                if "Woodstock" in data.text:
                    lat = "34.0993808"
                    lng = "-84.5217057"
                store.append(lat  if  lat else "<MISSING>" )
                store.append(lng if  lng else "<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store = [x.strip() if type(x) == str else x for x in store]
                yield store
    if exists:
        for data in exists.find_all('a'):
            # logger.info(data)
            if 'ubereats' in data.get('href'):
                page_url = data.get('href')
                location_soup = BeautifulSoup(session.get(page_url).text, "lxml")
                json_data_1 = (location_soup.find("script",{"type":"application/ld+json"}))
                data_json = (str(json_data_1).split('type="application/ld+json">')[1].split('</script>')[0])
                json_data = json.loads(data_json)
                location_name = json_data['name']
                try:
                    street_address = json_data['address']['streetAddress']
                    city = json_data['address']['addressLocality']
                    state = json_data['address']['addressRegion']
                    zipp = json_data['address']['postalCode']
                    country = json_data['address']['addressCountry']
                except:
                    street_address = "220 Starcadia Cir"
                    city = "Macon"
                    state = "GA"
                    zipp = "31210"
                    country = "US"
                if "2430 Atlanta Rd. Ste 300" == street_address:
                    state = "GA"
                phone = json_data['telephone']
                lat = json_data['geo']['latitude']
                lng = json_data['geo']['longitude']
                location_type = json_data['@type']
                opens = datetime.strptime(json_data['openingHoursSpecification'][0]['opens'],"%H:%M").strftime("%I:%M %p")
                closes = datetime.strptime(json_data['openingHoursSpecification'][0]['closes'],"%H:%M").strftime("%I:%M %p") 
                hours = "Every Day " + opens + " - " + closes
                store = []
                store.append("http://www.jchristophers.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country)
                store.append("<MISSING>")
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                store = [x.strip() if type(x) == str else x for x in store]
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
