import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }
    locator_domain = 'https://www.elcompadrerestaurant.com/' 
    ext = 'locations'
    r = requests.get(locator_domain + ext, headers = HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find_all('div', {'id': 'ctl01_pSpanDesc'})
    locations = locs[0].find_all('td')
    hours = locs[1].text.strip()
    all_store_data = []
    for l in locations:
        location_name = l.find('h6').text
        addy_split = l.find('p', {'class': 'fp-el'}).prettify().split('\n')
        # print(addy_split)
        street_address = ((addy_split)[1].split(",")[0].strip())
        city = ((addy_split)[1].split(",")[1].strip())        
        state = ((addy_split)[1].split(",")[2].strip().split(" ")[0])
        # print(city)
        zipp = ((addy_split)[1].split(",")[2].strip().split(" ")[1])
        phone = (addy_split)[3].replace(" Phone. ","")
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = 'https://www.elcompadrerestaurant.com/locations'
        if "90046" in zipp :
            hours = hours.split("HollywoodHOURS")[0].replace("Echo ParkHOURS: ","")
        if "90026" in zipp :
            hours = hours.replace("Echo ParkHOURS: ","")
        store_data = [locator_domain, location_name, street_address,city,state, zipp, country_code, 
                    store_number, phone, location_type, lat, longit, hours.replace('(Covid-19 Temporary Hours)',''), page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
