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
    base_url = "https://sugarfishsushi.com/"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    exists = soup.find('li', {'class', 'menu-item-93'}).find_next('ul')
    if soup.find('li', {'class', 'menu-item-93'}):
        for val in exists.findAll('a'):
            if "sugarfish-new-york-locations" in val.get('href') or "sugarfish-los-angeles-locations" in val.get('href') or "santa-monica-farmers-market" in val.get('href'):
                pass
            else:
                print(val.get('href'))
                detail_url = requests.get(val.get('href'), headers=headers)
                detail_soup = BeautifulSoup(detail_url.text, "lxml")
                address = detail_soup.find('h6').get_text().strip().replace('\n', ':').split(':')
                if len(address) > 1:
                    if len(address) > 5:
                        location_name = address[0].strip()
                        street_address = address[1].strip()
                        city = address[3].strip().split(',')[0]
                        state = address[3].strip().split(',')[1].strip().split(' ')[0]
                        zip = address[3].strip().split(',')[1].strip().split(' ')[1]
                        phone = address[5].strip()
                        hours_val = detail_soup.find('h6').find_next('h6').get_text().strip().replace('\n', '').strip()
                        hours = hours_val.rfind('pm')
                        hours_of_operation = hours_val[:hours+2]
                    else:
                        location_name = address[0].strip()
                        street_address = address[1].strip()
                        city = address[2].strip().split(',')[0]
                        if len(address[2].strip().split(',')[1].strip().split(' ')) == 1:
                            state = address[2].strip().split(',')[1].strip()[0:2]
                            zip = str(0) + address[2].strip().split(',')[1].strip()[3:]
                        else:
                            state = address[2].strip().split(',')[1].strip().split(' ')[0]
                            zip = address[2].strip().split(',')[1].strip().split(' ')[1]
                        phone = address[4].strip()
                        hours_val = detail_soup.find('h6').find_next('h6').get_text().strip().replace('\n', '').strip()
                        hours = hours_val.rfind('pm')
                        hours_of_operation = hours_val[:hours + 2]
                else:
                    check_val = detail_soup.find('h6').find_next('h6').find_next('h6').get_text().strip()
                    if "Monday" in check_val or "pm" in check_val:
                        address = detail_soup.find('h6').find_next('h6').get_text().strip().replace('\n', ':').split(':')
                        location_name = address[0].strip()
                        street_address = address[1].strip()
                        city = address[2].strip().split(',')[0]
                        state = address[2].strip().split(',')[1].strip().split(' ')[0]
                        zip = address[2].strip().split(',')[1].strip().split(' ')[1]
                        phone = address[4].strip()
                        hours_val = detail_soup.find('h6').find_next('h6').find_next('h6').get_text().replace('\n', '').strip()
                        hours = hours_val.rfind('pm')
                        hours_of_operation = hours_val[:hours + 2]
                    else:
                        address = detail_soup.find('h6').find_next('h6').find_next('h6').get_text().strip().replace('\n', ':').split(':')
                        location_name = address[0].strip()
                        street_address = address[1].strip()
                        city = address[2].strip().split(',')[0]
                        state = address[2].strip().split(',')[1].strip().split(' ')[0]
                        zip = address[2].strip().split(',')[1].strip().split(' ')[1]
                        phone = address[4].strip()
                        hours_val = detail_soup.find('h6').find_next('h6').find_next('h6').find_next('h6').find_next('h6').get_text().replace('\n', '').strip()
                        hours = hours_val.rfind('pm')
                        hours_of_operation = hours_val[:hours + 2]
                store = []
                store.append(val.get('href'))
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("Sugar Fish By Sushi Nozawa")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation)
                return_main_object.append(store)
        return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
