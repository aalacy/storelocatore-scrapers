import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    data = []

    country_codes = ['US', 'CA']
    main_urls = ['https://www.solasalonstudios.com/locations', 'https://www.solasalonstudios.ca/locations']
    i = 0
    for main_url in main_urls:
        req = session.get(main_url, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        # Fetch store urls from location menu
        store_els = base.find(class_="container location-grid").find_all(class_="link")
        if country_codes[i] == "US":
            domain = "https://www.solasalonstudios.com"
        else:
            domain = "https://www.solasalonstudios.ca"
        store_urls = [domain + store_el.find_all('a')[-1]['href'] for store_el in store_els]

        # Fetch data for each store url
        for store_url in store_urls:
            # print(store_url)
            req = session.get(store_url, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")

            script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').replace('\r', '').replace('\t', '').strip()
            store = json.loads(script)

            location_name = store['name'].replace("amp;","").encode("ascii", "ignore").decode().strip()
            street_address = store['address']['streetAddress'].replace("Woodbury Lakes - ,","").replace("amp;","").split("(")[0].strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()
            city = store['address']['addressLocality'].strip()
            state = store['address']['addressRegion'].strip()
            zipcode = store['address']['postalCode'].strip()
            store_number = "<MISSING>"
            phone = store['telephone'].replace("(Leasing queries only)","").replace("HAIR (4247)","4247").replace("Option 3","").replace("Leasing","")\
            .replace("Leasing","").replace("- Call or Text!","").replace("call or text","").replace("or text","").split('ext')[0].strip()
            lat = store['geo']['latitude']
            lon = store['geo']['longitude']
            data.append([
                'https://www.solasalonstudios.com',
                store_url,
                location_name,
                street_address,
                city,
                state,
                zipcode,
                country_codes[i],
                store_number,
                phone,
                '<MISSING>',
                lat,
                lon,
                '<MISSING>'
            ])
        i = i + 1

    return data

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()
