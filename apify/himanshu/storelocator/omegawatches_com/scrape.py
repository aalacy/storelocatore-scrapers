
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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            # print(row)
            writer.writerow(row)


def fetch_data():
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.omegawatches.com/"

    location_url = "https://www.omegawatches.com/store/"
    r = session.get(location_url, headers=headers)

    soup = BeautifulSoup(r.text, "html5lib")
    data = soup.find("script", text=re.compile("var stores =")).text.split(
        "var stores = ")[1].split("; var pm_countries")[0]
    json_data = json.loads(data)
    # # print(json_data)

    for i in json_data:
        # name = i["name"]
        if i['countryName'] == "Canada" or i['countryName'] == "United States":
            if i['countryName'] == "Canada":
                location_name = i['name']
                street_address = i['adrOnly'].replace('\n', ', ')
                city = i['cityName']
                if len(i['adr'].split("\r\n")[-2].split(" ")[-1]) == 2:
                    state = i['adr'].split("\r\n")[-2].split(" ")[-1]
                else:
                    state = "<MISSING>"
                zipp = i['zipcode'].replace("(828) 298-4024", "<MISSING>")
                store_number = i['id']
                country_code = i['countryCode']
                phone = i['contacts']['phone']
                if i['latitude'] == 0:
                    latitude = "<MISSING>"
                else:
                    latitude = i['latitude']
                if i['longitude'] == 0:
                    longitude = "<MISSING>"
                else:
                    longitude = i['longitude']
                href = "https://www.omegawatches.com/" + str(i['websiteUrl'])
                r1 = session.get(href, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                hours = soup1.find("ul", {"class": "pm-store-opening"})
                if hours != [] and hours != None:
                    hours_of_operation = ' '.join(list(hours.stripped_strings))
                else:
                    hours_of_operation = "<MISSING>"

            elif i['countryName'] == "United States":
                location_name = i['name']
                if len(i['adrOnly'].split('\n'))==1:
                    street_address = i['adrOnly']
                elif location_name == "Chong Hing":
                    street_address = i['adrOnly'].replace("\n",",")
                elif location_name == "Timeless Luxury Watches":
                    street_address = i['adrOnly'].replace("\n",",")
                else:
                    street_address = " ".join(i['adrOnly'].split('\n')[1:])
                city = i['cityName']
                state = i['stateCode']
                zipp = i['zipcode'].replace("(828) 298-4024", "<MISSING>")
                store_number = i['id']
                country_code = i['countryCode']
                phone = i['contacts']['phone']
                if i['latitude'] == 0:
                    latitude = "<MISSING>"
                else:
                    latitude = i['latitude']
                if i['longitude'] == 0:
                    longitude = "<MISSING>"
                else:
                    longitude = i['longitude']
                href = "https://www.omegawatches.com/" + str(i['websiteUrl'])
                r2 = session.get(href, headers=headers)
                soup2 = BeautifulSoup(r2.text, "lxml")
                hours = soup2.find("ul", {"class": "pm-store-opening"})
                if hours != [] and hours != None:
                    hours_of_operation = ' '.join(list(hours.stripped_strings))
                else:
                    hours_of_operation = "<MISSING>"

            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code)
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(href)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
            #print(store)


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
