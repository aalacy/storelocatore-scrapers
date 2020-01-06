import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://daysinn.ca"
    r = requests.get(
        'https://www.wyndhamhotels.com/en-ca/days-inn/locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "property-list"}):
        for semi_parts in parts.find_all("li", {"class": "property"}):
            return_object = []
            try:
                # store_request = requests.get('https://www.wyndhamhotels.com/en-ca/hotels/99778')
                store_request = requests.get(
                    'https://www.wyndhamhotels.com' + semi_parts.find("a")['href'])
                # print(store_request)
            except Exception as e:
                # print('error =>' + str(e))
                if(str(e) == "Exceeded 30 redirects."):
                    continue
            # print('https://www.wyndhamhotels.com' + semi_parts.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            page_url = 'https://www.wyndhamhotels.com' + \
                semi_parts.find("a")['href']
            if store_soup.find('script', {'type': 'application/ld+json'}) is not None:
                script = store_soup.find(
                    'script', {'type': 'application/ld+json'})
                coords = json.loads(script.text)

                latitude = coords['geo']['latitude']
                longitude = coords['geo']['longitude']

                # print(latitude,longitude,page_url)
                # print('~~~~~~~~~~~~~~~~~~~~~')
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            if (store_soup.find("div", {"class": "property-info"})):
                locationDetails = store_soup.find(
                    "div", {"class": "property-info"})
                temp_storeaddresss = list(locationDetails.stripped_strings)
                # print(temp_storeaddresss[-2])
                if temp_storeaddresss[-2].strip() not in ["US", "CA"]:
                    continue
                # print(temp_storeaddresss[-2].strip())
                location_name = temp_storeaddresss[0]
                street_address = temp_storeaddresss[1]
                city = temp_storeaddresss[3]
                if(len(temp_storeaddresss) == 9):
                    state = temp_storeaddresss[5]
                    store_zip = temp_storeaddresss[6]
                    phone = temp_storeaddresss[8]
                elif(len(temp_storeaddresss) == 8):
                    store_zip = temp_storeaddresss[5]
                    state = temp_storeaddresss[6]
                    phone = temp_storeaddresss[7]
                else:
                    store_zip = '<MISSING>'
                    phone = temp_storeaddresss[6]
                    state = temp_storeaddresss[5]
                ca_zip_list = re.findall(
                    r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(store_zip))
                us_zip_list = re.findall(re.compile(
                    r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(store_zip))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country = "CA"
                elif us_zip_list:
                    zipp = us_zip_list[-1]
                    country = "US"

                else:
                    if "CA" == temp_storeaddresss[-2].strip():
                        zipp = temp_storeaddresss[-3].strip()
                        country = "CA"
                    else:
                        continue

                # print(zipp)

                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(zipp)
                return_object.append(country)
                return_object.append("<MISSING>")
                return_object.append(phone)
                return_object.append("<MISSING>")
                return_object.append(latitude)
                return_object.append(longitude)
                return_object.append("<MISSING>")
                return_object.append(page_url)
                # print("===="+str(return_object))
                # print('~~~~~~~~~~~~~~~~~~`')
                yield return_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
