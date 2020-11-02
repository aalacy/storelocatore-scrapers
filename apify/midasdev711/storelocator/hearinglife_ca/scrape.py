import csv
import re
from sgrequests import SgRequests
from lxml import etree
import json

base_url = 'https://www.hearinglife.ca'

def validate(items):
    rets = []
    for item in items:
        if item is '<MISSING>':
            continue
        if type(item) is str:
            item = item.strip()
        rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)
    return

def fetch_data():
    output_list = []
    url = "https://www.hearinglife.ca/webservices/centerlocator.svc/GetCenters/%7B6B8D4C17-298F-47DA-82F8-0628E2C8C6C9%7D/null/null/en-ca/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)['Centers']
    for store in store_list:
        output = []

        desc = re.findall(r'https://www\.hearinglife\.ca/book-a-consultation\?region=.+">', store["Description"])[0]
        link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', desc)[0].replace("&amp;","&").replace("%20","-")

        link = "https://www.hearinglife.ca/book-a-consultation?region=" + store["RegionFolder"] + "&centername=" + store["ItemName"]
        hours = store.get('OpeningDayHours')
        store_hours = ""
        if len(hours) > 0:
            for x in hours:
                store_hours += (x.get('Day') or ' ') + ' ' + (x.get('OpeningHours') or ' ') + ','
        store_hours = store_hours.replace("<!-- ","(").replace("<!-- ","(").replace(" -->",")").replace("  ,",",").strip()
        if store_hours[-1:] == ",":
            store_hours = store_hours[:-1].strip()
        output.append(base_url)
        output.append(link)
        output.append(store.get('Title'))
        street_address = store.get('Address').replace("Alpha Corporate Centre - ","")
        if "|" in street_address:
            street_address = street_address.split("|")[-1].strip()
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        output.append(street_address)
        output.append(store.get('City'))
        output.append(store.get('Region'))
        output.append(store.get('PostalCode'))
        output.append('CA')
        store_num = store.get('Id')
        if not store_num:
            store_num = '<MISSING>'
        output.append(store_num)
        output.append(store.get('Phonenumber'))
        output.append('<MISSING>')
        output.append(store.get('Latitude'))
        output.append(store.get('Longitude'))
        output.append(store_hours)
        output_list.append(validate(output))
    return output_list
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
