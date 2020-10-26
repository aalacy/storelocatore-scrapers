import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    street_address = addy[0]
    city = addy[1].strip()
    state_zip = addy[-1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return street_address, city, state, zip_code

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://ffohome.com/'
    ext = 'allshops'
    r = session.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    locs = soup.find_all(class_="store_website")

    all_store_data = []
    for raw_loc in locs:
        page_url = raw_loc.a['href']
        print(page_url)
        req = session.get(page_url, headers = HEADERS)
        loc = BeautifulSoup(req.content, 'html.parser')
        location_name = loc.h1.text.strip()
        raw_address = loc.find(class_="custom-field--value").text.strip().replace("\r\n",",").replace("KY,","KY").split(",")
        street_address, city, state, zip_code = addy_ext(raw_address)

        phone_number = loc.find_all(class_="custom-field--value")[1].text.strip()
        hours = loc.find_all(class_="custom-field--value")[2].text.replace("\r\n"," ").strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        try:
            map_link = loc.find("iframe")['src']
            lat_pos = map_link.rfind("q=")
            latitude = map_link[lat_pos+2:map_link.find(",",lat_pos+5)].strip()
            lng_pos = map_link.find(",",lat_pos+5)
            longitude = map_link[lng_pos+1:map_link.find("&",lng_pos+5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, latitude, longitude, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
