import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://salonrepublic.com"
    r = session.get("http://salonrepublic.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    addresses = []
    script = soup.find_all(
        'script')[-2].text.strip().split('var mapdata = ')[1].split('};')[0] + "}"
    json_data = json.loads(script)
    for loc in json_data['pois']:
        body = BeautifulSoup(loc['body'], 'lxml')
        page_url = base_url + body.a['href']
        locator_domain = base_url
        address = list(body.find_all('p')[-1].stripped_strings)
        street_address = " ".join(address[:-2]).strip()
        city = address[-2].split(',')[0].strip()
        state = address[-2].split(',')[-1].split()[0].strip()
        zipp = address[-2].split(',')[-1].split()[-1].strip()
        latitude = loc['point']['lat']
        longitude = loc['point']['lng']
        location_name = loc['title']
        store_number = "<MISSING>"
        country_code = "US"
        location_type = "<MISSING>"
        # print(page_url)
        r_loc = session.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, 'lxml')
        try:
            try:
                phone = soup_loc.find(
                    'div', class_='loc_contact').find('a').text.strip()
                if phone == "":
                    phone = "<MISSING>"

                hours_of_operation = "<MISSING>"
            except:
                phone = list(soup_loc.find(
                    'p', class_='thelab_addr2').stripped_strings)[0]
                hours_of_operation = " ".join(list(soup_loc.find(
                    'div', class_='lab_hours_box').stripped_strings)).replace("The Lab Hours:", "")
        except:

            continue

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(
            hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        if store[1] + " " + store[2] in addresses:
            continue
        addresses.append(store[1] + " " + store[2])

        #print("data = " + str(store))
        #print(
            #'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
