import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(' ')
    if len(address) == 4:
        city = address[0] + ' ' + address[1]
        state = address[2]
        zip_code = address[3]
    else:
        city = address[0]
        state = address[1]
        zip_code = address[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://submarina.com/'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}
    
    session = SgRequests()
    req = session.get(locator_domain, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    items = base.find_all(id="locations")[-1].find_all(class_="fusion-column-content")

    all_store_data = []
    for item in items:
        cont = item.find_all(class_="s1")           

        location_name = item.h4.text

        try:
        	street_address = cont[0].text.strip()
        except:
        	cont = item.find_all("span")
        	street_address = cont[0].text.strip()

        city, state, zip_code = addy_ext(cont[1].text)

        phone_number = cont[2].text
        hours = ''
        for h in cont[3:]:
            hours += h.text + ' '

        hours = hours.replace("\xa0","").replace("–","-").replace("\n"," ").replace("NOW OPEN!","").strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
