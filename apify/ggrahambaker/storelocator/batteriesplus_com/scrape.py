from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re 

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.batteriesplus.com/'
    ext = 'store-locator'
    location_url = locator_domain + ext

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(location_url, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    main = base.find(class_='mobile-collapse')
    states = main.find_all('a')
    state_list = []
    for state in states:
        state_link = state['href']
        if state_link:
            state_list.append("https://www.batteriesplus.com" + state_link)

    city_list = []
    for state in state_list:
        req = session.get(state, headers = HEADERS)
        print(state)
        time.sleep(randint(1,2))
        try:
            base = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        
        cities = base.find_all(class_="map-list-item is-single")
        
        for c in cities:
            city_list.append("https://www.batteriesplus.com" + c.a['href'])

    all_store_data = []
    dup_tracker = []
    total_links = len(city_list)
    for i, link in enumerate(city_list):

        if link not in dup_tracker:
            dup_tracker.append(link)
        else:
            continue

        print("Link %s of %s" %(i+1,total_links))
        req = session.get(link, headers = HEADERS)
        time.sleep(randint(1,2))
        try:
            item = BeautifulSoup(req.text,"lxml")
            print(link)
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        items = item.find(class_="city-locator").find_all(class_="map-list-item-right")

        for item in items:
            raw_address = item.find(class_="address mt-10").find_all('div')
            street_address = raw_address[0].text.strip()

            city_line = raw_address[1].text.strip()
            city = city_line[:city_line.find(",")]
            state = city_line[city_line.find(",")+1:city_line.rfind(" ")].strip()
            zip_code = city_line[city_line.rfind(" "):].strip()
            
            store_number = item.find(class_="map-list-item-header").a['title'].split("#")[-1]
            
            try:
                raw_gps = item.find('a', attrs={'title': 'Directions'})['href']
                lat = raw_gps[raw_gps.rfind("=")+1:raw_gps.rfind(",")].strip()
                longit = raw_gps[raw_gps.rfind(",")+1:].strip()
            except:
                lat = '<MISSING>'
                longit = '<MISSING>'

            phone_number = item.find(class_="phone ga-link hover").text.strip()

            country_code = 'US'

            location_name = city + ', ' + state
            location_type = '<MISSING>'
            page_url = link
            
            try:
                hours_link = "https://www.batteriesplus.com" + item.find(class_="view-details ga-link btn btn-black ml-10")['href']
                req = session.get(hours_link, headers = HEADERS)
                time.sleep(randint(1,2))                
                hour_page = BeautifulSoup(req.text,"lxml")
                hours = hour_page.find(class_="hours").text.replace("\n"," ").replace("  "," ").strip()
                hours = re.sub(' +', ' ', hours)
            except (BaseException):
                hours = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                            store_number, phone_number, location_type, lat, longit, hours, page_url]
            
            all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
