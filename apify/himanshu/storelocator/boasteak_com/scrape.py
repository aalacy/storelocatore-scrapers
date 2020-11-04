import csv
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup

session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'content-type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.boasteak.com'
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    dropdown = soup.find("div",{"class":"dropdown w-dyn-list"}).find_all("a")
    for i in dropdown[:-1]:
        page_url = url+i['href']
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,'lxml')
        location_name = soup1.find("h1",{"class":"location-title lightest"}).text
        addr = soup1.find_all("h5",{"class":"location-detail"})[1].text.split(",")
        street_address = addr[0]
        city = addr[1].strip()
        state = addr[2].strip().split(" ")[0]
        zipp = addr[2].strip().split(" ")[1]
        temp_phone = soup1.find_all("h5",{"class":"location-detail"})[0].text.replace(".","")
        phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
        temp_coord = soup1.find("div",{"class":"location-map-image"}).find("a")['href'].split("@")[1].split(",")
        latitude = temp_coord[0]
        longitude = temp_coord[1]
        temp_hoo = soup1.find("div",{"class":"location-hours w-richtext"}).find_all("p")
        hour = []
        for h in temp_hoo[2:-2]:
            hour.append(h.text)
        hours_of_operation = ", ".join(hour)
    
    
        store = []
        store.append(url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        yield store
       
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
