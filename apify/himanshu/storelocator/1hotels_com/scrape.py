import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as BS
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.1hotels.com"
    soup = BS(session.get(base_url, headers=headers).text, "lxml")

    for link in soup.find_all("div",{"class":"col-12 col-md-4 col-dt-4 card p-0 pl-0 pr-md-3 card--card"}):
        page_url = link.a['href']

        store_soup = BS(session.get(page_url).text, "lxml")

        json_data = json.loads(store_soup.find(lambda tag:(tag.name == "script") and '"streetAddress"' in tag.text).text)['@graph'][0]
        
        location_name = json_data['name']
        
        street_address = json_data['contactPoint']['areaServed']['address']['streetAddress']
        city = json_data['contactPoint']['areaServed']['address']['addressLocality']
        state = json_data['contactPoint']['areaServed']['address']['addressRegion']
        zipp = json_data['contactPoint']['areaServed']['address']['postalCode']
        country_code = json_data['contactPoint']['areaServed']['address']['addressCountry']
        phone = json_data['telephone']
        location_type = json_data['@type']

        coord_request = BS(session.get(base_url + store_soup.find("a",text=re.compile("Contact Us"))["href"],headers=headers).text, "lxml")
        
        coord_json = json.loads(coord_request.find(lambda tag: (tag.name == "script") and '"currentPath"' in tag.text).text)
        store_number = coord_json['path']['currentPath'].replace("node/",'')
        lat = coord_json['verb_directions']['location']['lat']
        lng = coord_json['verb_directions']['location']['lng']

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
