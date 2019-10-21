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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url= "https://www.niftyafterfifty.com/"
    get_url = "https://www.niftyafterfifty.com/locations"
    r = requests.get(get_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.findAll('p', {'class', 'font_8'})
    for data in exists:
        flg = True
        if data.find('span'):
            if data.find('span').get('style') == "font-weight:bold;":
                if "____" in data.get_text() or "Hours:" in data.get_text() or "Nifty People" in data.get_text() or "AM" in data.get_text() or "PM" in data.get_text() or "your fitness" in data.get_text():
                    flg = False
                else:
                    flg = True
            elif data.find('span').find_next('span').find_next('span').find_next('span').get('style') == "font-weight:bold;":
                if "____" in data.get_text() or "Hours:" in data.get_text() or "Nifty People" in data.get_text() or "AM" in data.get_text() or "PM" in data.get_text()  or "your fitness" in data.get_text():
                    flg = False
                else:
                    flg = True
            else:
                flg = False
        else:
            flg = False
        if flg == True:
            location_name = data.get_text()
            city = location_name
            if "," in data.find_next('p').find_next('p').get_text().strip():
                street_address = data.find_next('p').get_text().strip() + ", " + data.find_next('p').find_next('p').get_text().strip().split(',')[0]
                state = data.find_next('p').find_next('p').get_text().strip().split(',')[1].strip().split(' ')[0].strip()
                zip = data.find_next('p').find_next('p').get_text().strip().split(',')[1].strip().split(' ')[1].strip()
            else:
                street_address = data.find_next('p').get_text() + ", " + ' '.join(data.find_next('p').find_next('p').get_text().strip().split(' ')[:-2])

                state = data.find_next('p').find_next('p').get_text().strip().split(' ')[-2]
                zip = data.find_next('p').find_next('p').get_text().strip().split(' ')[-1]
            phone = data.find_next('p').find_next('p').find_next('p').get_text().strip()[:15]
            if "fax" not in data.find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip():
                hours_of_operation = data.find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip()
            elif "_______" in data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip() or len(data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip()) < 10 or "Fitness Hours:" in data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip() or "Nifty People" in data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip() or "TUCSON" in data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip():
                hours = data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text()
                if "Hours" in hours:
                    if hours.split('\n')[0].split(',')[0] == "Fitness Hours:":
                        if data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p'):
                            if "am" in data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text():
                                hours_of_operation = data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().split('\n')[0].split(',')[0] + ", " + data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text()
                            else:
                                hours_of_operation = data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().split('\n')[0].split(',')[0]
                    else:
                        if "am" in data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text():
                            hours_of_operation = hours.split('\n')[0].split(',')[0] + ", " + data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text()
                        else:
                            hours_of_operation = hours.split('\n')[0].split(',')[0]
            else:
                hours_of_operation = data.find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip().replace("\n", ',').strip()
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
            store.append("Nifty After Fifty")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            store.append(get_url)
            return_main_object.append(store)
        else:
            pass
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
