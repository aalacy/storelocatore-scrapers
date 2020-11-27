import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import html5lib
import unicodedata
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

    addressesess = []
    base_url = "https://www.nathansfamous.com"
    headers = {
        'accept':'*/*',
        'Cookie':'__cfduid=d89370e180312a50705023f5f19721bec1606384421',
        'x-requested-with':'XMLHttpRequest',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }
    coords = sgzip.coords_for_radius(200)
    ct = 1
    for coord in coords:
        ct = ct + 1


        url = "https://restaurants.nathansfamous.com/wp-admin/admin-ajax.php?action=store_search&lat="+coord[0]+"&lng="+coord[1]+"&max_results=100&search_radius=500"
        json_data = session.get(url,headers=headers).json()
        for val in json_data:
            if val['country']=='Canada' or val['country']=='United States':
                if val['country']=='United States':
                    country_code="US"
                else:
                    country_code="CA"
                location_name = val['store']
                street_address = val['address']
                city = val['city']
                state = val['state']
                zipp = val['zip']
                store_number = val['id']
                phone = val['phone']
                if phone=="":
                    phone = "<MISSING>"
                latitude = val['lat']
                longitude = val['lng']
                h_soup = BeautifulSoup(val['hours'],'html5lib').find_all('tr')
                hour = []
                for h in h_soup:
                    frame = h.find_all('td')[0].text +" "+h.find_all('td')[1].text
                    hour.append(frame)
                hours_of_operation = ", ".join(hour)
                store = []
                store.append("https://www.nathansfamous.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append(store_number)
                store.append(phone if phone else "<MISSING>")
                store.append("Nathan's Famous")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append("<MISSING>") 
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]   
                if store[2] in addressesess:
                    continue
                addressesess.append(store[2])
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
