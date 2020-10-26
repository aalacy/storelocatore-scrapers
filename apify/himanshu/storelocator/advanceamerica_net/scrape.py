import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.advanceamerica.net"
    data = {"postType":"location","postsPerPage":-1,"taxQuery":[{"taxonomy":"location_state","field":"slug","terms":"alabama"}]}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.advanceamerica.net',
        'Referer': 'https://www.advanceamerica.net/store-locations/alabama'
    }
    # print(base_url + "/api/posts/filter")
    # exit()
    r = session.post(base_url + "/api/posts/filter",data=data,headers=headers)
    data = r.json()['posts']
    return_main_object = []
    for i in range(len(data)):
        page_url =base_url+ (data[i]['url'])
        store_data = data[i]
        store = []
        store.append("https://www.advanceamerica.net")
        store.append(store_data['fields']['city'])
        store.append(store_data["fields"]["address"])
        store.append(store_data['fields']['city'])
        store.append(store_data['fields']['state'])
        store.append(store_data["fields"]["zip"])
        store.append("US")
        store.append(store_data['fields']['store_id'])
        if 'phone' in store_data['fields']:
            store.append(store_data['fields']['phone'])
        else:
            store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["fields"]['latitude'])
        store.append(store_data["fields"]['longitude'])
        store_hours = store_data["fields"]["hours"]
        hours = ""
        for k in range(len(store_hours)):
            if store_hours[k]['open_time']:
                hours = hours + store_hours[k]["day"] + " open_time " + store_hours[k]['open_time'] + " close_time " + store_hours[k]['close_time'] + " "
        if hours == "":
            hours = "<MISSING>"
        store.append(hours)
        store.append(page_url)

        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
