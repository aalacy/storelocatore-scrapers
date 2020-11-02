import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.debeers.com"
    r = session.get("https://www.debeers.com/on/demandware.store/Sites-DeBeersInternationalNet-Site/en_US/Stores-GetStoresByAddress?responseType=html&address=US&noAllowPosition=true", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for i in soup.find_all("a",{"class":"store-name dbj-font-header3 pointer"}):
        store_number = i['href'].split("=")[1]
        page_url = "https://www.debeers.com/"+i['href']
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,'lxml')
        location_name = soup1.find("span",{"class":"store-name dbj-font-header3"}).text
        dl = list(soup1.find("div",{"class":"store-address-details dbj-font-body3-alt1 pt-3"}).stripped_strings)
        zipp = dl[-1]
        if len(zipp.split(" "))==2:
            country_code = "CA"
        else:
            country_code = "US"
        if len(dl)==4:
            if "New York Madison Avenue" in location_name:
                street_address = "".join(dl[:2]).strip(",")
                city = dl[2].split(",")[1]
                state = dl[2].split(",")[0].replace("\n","")
            else:
                street_address = dl[1].strip(",")
                city = dl[2].split(",")[1]
                state = dl[2].split(",")[0].replace("\n","")
        else:
            street_address = dl[0].strip(",")
            if len(dl[1].split(","))==2:
                city = dl[1].split(",")[1]
                state = dl[1].split(",")[0].replace("\n","")
            else:
                city = dl[1]
                state = "ON"
        phone = soup1.find('a',{'class':'dbj-font-body3-alt1'}).text.replace("+1","").strip().replace(" ","-")
        hours_of_operation = " ".join(list(soup1.find("table",{"class":"table-no-border w-100"}).stripped_strings))
        coord = json.loads(soup1.find("div",{"class":"data-locations-default d-none"}).text)[0]
        latitude = coord['latitude']
        longitude = coord['longitude']
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append("De Beers Jewellers")
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()