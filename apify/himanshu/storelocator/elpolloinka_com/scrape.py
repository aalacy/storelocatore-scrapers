import csv
import requests
from bs4 import BeautifulSoup
import re
import io
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://elpolloinka.com/gardena/about-us/locations/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('div', {'class', 'entry-content'})
    if exists:
        i = 0
        for data in exists.findAll('p'):
            if data.find('span'):
                pass
            else:
                if "Other Locations" in data.text:
                    pass
                else:
                    if data.text.strip() == "":
                        pass
                    else:
                        if len(data.get_text().strip().replace('\n', ' ').split(",")) == 1:
                            pass
                        else:
                            all_data = data.get_text().strip().replace('\n', ' ').split(",")
                            location_name = all_data[0].strip()
                            street_address = all_data[1].strip()
                            city = location_name
                            state = all_data[2].strip().split(" ")[0]
                            zip = all_data[2].strip().split(" ")[1]
                            if i == 2:
                                phone_hours = data.get_text().strip().replace('\n', ' ').split("Tel: ")[-1]
                                phone = phone_hours[0:12]
                                hours_of_operation = "Monday thru Wednesday: 10:30 am to 9:30 pm Thursday: 10:30 to 12 am Friday: 10:30 am to 1 am Saturday: 11 am to 1 am Sunday: 11 am to 12 am"
                            else:
                                phone_hours = data.get_text().strip().replace('\n', ' ').split("Tel: ")[-1]
                                phone = phone_hours[0:12]
                                if "Fax" in phone_hours:
                                    hour_val = phone_hours.find("Fax")
                                    hours_of_val = hour_val + 18
                                    hours_of_operation = phone_hours[hours_of_val:]
                                else:
                                    hours_of_operation = ' '.join(phone_hours.split(' ')[1:]).strip().replace('\n', ' ')
                            print(i)
                            store = []
                            store.append(base_url)
                            store.append(location_name)
                            store.append(street_address)
                            store.append(city)
                            store.append(state)
                            store.append(zip)
                            store.append("US")
                            store.append("<MISSING>")
                            store.append(phone)
                            store.append("El Pollo Inka Gardena CA | Fine Peruvian Food | Gardena CA")
                            store.append("<MISSING>")
                            store.append("<MISSING>")
                            store.append(hours_of_operation)
                            return_main_object.append(store)
            i = i + 1
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
