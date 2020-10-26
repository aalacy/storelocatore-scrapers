import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }

    base_url = "https://www.tranesupply.com"

    for zip_code in zips:
        while True:
            page_url="https://www.tranesupply.com/store-locator?q=" + str(zip_code)
            try:
                r = requests.get("https://www.tranesupply.com/store-locator?q=" + zip_code,
                                headers=headers)
            except:
                continue               
            soup = BeautifulSoup(r.text, "lxml")

            locator_domain = base_url
            location_name = ""
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = ""
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            raw_address = ""
            hours_of_operation = "<MISSING>"

            for script in soup.find_all("div", {'class': 'dealer listing hoverable z-depth-1 row pb20 pt20 mb10'}):
                location_name = script.find('h3', {'class': 'no-margin'}).text.strip()
                phone1 = script.find('a', {'class': 'storePhoneNumber dealer_phone'})#.text.strip()
                if phone1 !=None:
                    phone =  script.find('a', {'class': 'storePhoneNumber dealer_phone'}).text.strip()
                else:
                    phone =''    
                full_address = ",".join(list(script.find('p', {'class': 'address relative'}).stripped_strings))

                if not full_address.find('https://') >= 0:
                    if len(full_address.split(',')[-1].strip().split(' ')) > 1:
                        street_address = ','.join(full_address.split(',')[:-2])
                        city = full_address.split(',')[-2]
                        if len(street_address) == 0:
                            street_address = full_address.split(',')[0]
                            city = '<MISSING>'

                        state = full_address.split(',')[-1].strip().split(' ')[0]
                        zipp = full_address.split(',')[-1].strip().split(' ')[1][-5:]
                    else:
                        street_address = ','.join(full_address.split(',')[:-3])
                        city = full_address.split(',')[-3]
                        if str(full_address.split(',')[-1])[-5:].isdigit():
                            zipp = full_address.split(',')[-1][-5:]
                            state = full_address.split(',')[-2]
                        else:
                            zipp = full_address.split(',')[-2][-5:]
                            state = full_address.split(',')[-1]
                else:
                    street_address = "<MISSING>"
                    city = "<MISSING>"
                    zipp = "<MISSING>"
                    state = "<MISSING>"

                hours_of_operation = ", ".join(
                    list(script.find('ul', {'class': 'list-inline mt10 no-margin-bottom'}).stripped_strings))

                if script.find("a",{"class":"storeDirections"}) is not None:
                    location_url = script.find("a",{"class":"storeDirections"})['href']
                   
                    latitude = location_url.split('&daddr=')[1].split(',')[0]
                    longitude = location_url.split('&daddr=')[1].split(',')[1]                   

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

                if store[2]+store[-3] in addresses:
                    continue

                addresses.append(store[2]+store[-3])

                store = ["<MISSING>" if x == "" else x for x in store]
                yield store

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
            break

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
