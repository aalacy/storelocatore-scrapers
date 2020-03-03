import csv
import requests
from bs4 import BeautifulSoup
import re
import json
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.wyndhamhotels.com"
    r = requests.get("https://www.wyndhamhotels.com/en-uk/wyndham/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "wyndhamhotels"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    for val in soup.find_all('div', {'class': 'aem-rendered-content'}):
        location_name = val.find('div', class_="region").text.strip()
        country = val.find('h4', class_='country-name').text
        if country == 'United States':
            for address in val.find_all('div', class_='state-container'):
                add1 = address.text.strip()
                for li in address.find_all("ul"):
                    link = li.find('a')['href'].split('/')
                    location_name = (link[-2])
                    link[5] = 'local-area'
                    main_link = base_url + "/".join(link)
                    page_url = (main_link.replace("local-area","overview"))
                    r2 = requests.get(page_url, headers=headers)
                    soup_location1 = BeautifulSoup(r2.text, "lxml")
                    address1 = soup_location1.find('script',{'type':'application/ld+json'}).text
                    json_data = json.loads(address1)
                    street_address = (json_data['address']['streetAddress'])
                    city = (json_data['address']['addressLocality'])
                    if 'addressRegion' in json_data['address']:
                        state = (json_data['address']['addressRegion'])
                    else:
                        state = '<MISSING>'
                    zipp = (json_data['address']['postalCode']) 
                    country_code =  (json_data['address']['addressCountry'])
                    phone =  (json_data['telephone'])
                    latitude = (json_data['geo']['latitude'])
                    longitude  = (json_data['geo']['longitude'])
                    location_name =  (json_data['name']) 
                    page_url = (json_data['@id']) 
                    location_type = (json_data['@type'])
                    store = []
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    if "United States" in country_code :
                        yield store
    link8 = "https://www.wyndhamhotels.com/en-uk/wyndham/houston-texas/wyndham-houston-west-energy-corridor/overview"
    r2 = requests.get(link8, headers=headers)
    soup_location1 = BeautifulSoup(r2.text, "lxml")
    address1 = soup_location1.find('script',{'type':'application/ld+json'}).text
    json_data = json.loads(address1)
    street_address = (json_data['address']['streetAddress'])
    city = (json_data['address']['addressLocality'])
    if 'addressRegion' in json_data['address']:
        state = (json_data['address']['addressRegion'])
    else:
        state = '<MISSING>'
    zipp = (json_data['address']['postalCode']) 
    country_code =  (json_data['address']['addressCountry'])
    phone =  (json_data['telephone'])
    latitude = (json_data['geo']['latitude'])
    longitude  = (json_data['geo']['longitude'])
    location_name =  (json_data['name']) 
    page_url = (json_data['@id']) 
    location_type = (json_data['@type'])
    store = []
    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
    if "United States" in country_code :
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
