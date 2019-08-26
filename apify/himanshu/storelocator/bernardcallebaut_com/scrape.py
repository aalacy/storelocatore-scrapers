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
    base_url = "http://bernardcallebaut.com/users/folder.asp?FolderID=4575"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('table', {'class', 'table-locations'})
    address = []
    for tr in exists.findAll('tr'):
        flg = True
        if tr.find('td'):
            if (tr.find('td')).has_attr('colspan'):
                state = tr.find('td').get_text().strip()
                flg = False
            else:
                if len(tr.find('td').get_text().strip().replace('\n', '').strip()) == 0:
                    flg = False
                else:
                    flg = True
        else:
            flg = False
        if flg == True:
            location_name = tr.find('td').get_text().strip().replace('\n', '').strip()
            city = location_name
            if tr.find('td').find_next('td').find('p').find_next('p').get_text().strip() == "Store Hours":
                street_address = tr.find('td').find_next('td').find('p').get_text().strip()
                if tr.find('td').find_next('td').find('p').find_next('p').find_next('p').find_next('p'):
                    hours_of_operation = tr.find('td').find_next('td').find('p').find_next('p').find_next('p').get_text().strip() + ", " + tr.find('td').find_next('td').find('p').find_next('p').find_next('p').find_next('p').get_text().strip()
                else:
                    hours_of_operation = tr.find('td').find_next('td').find('p').find_next('p').find_next('p').get_text().strip()
            else:
                street_address = tr.find('td').find_next('td').find('p').get_text().strip() + ", " + tr.find('td').find_next('td').find('p').find_next('p').get_text().strip()
                if tr.find('td').find_next('td').find('p').find_next('p').find_next('p').find_next('p').find_next('p'):
                    hours_of_operation = tr.find('td').find_next('td').find('p').find_next('p').find_next('p').find_next('p').get_text().strip() + ", " + tr.find('td').find_next('td').find('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text().strip()
                else:
                    hours_of_operation = tr.find('td').find_next('td').find('p').find_next('p').find_next('p').find_next('p').get_text().strip()
            phone = tr.find('td').find_next('td').find_next('td').get_text().strip().replace('\n', ", ").strip()

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append("<MISSING>")
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Cococo Chocolaterie Bernard Callebaut")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            return_main_object.append(store)
        else:
            pass
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
