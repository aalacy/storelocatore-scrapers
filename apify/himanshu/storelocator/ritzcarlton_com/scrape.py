import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import html5lib
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    addressess = []
    base_url = "https://ritzcarlton.com"
    r = session.get("https://www.ritzcarlton.com/en/hotels",headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    rm = ["https://www.ritzcarlton.com/en/hotels/arizona/paradise-valley",
    "https://www.ritzcarlton.com/en/hotels/california",
    "https://www.ritzcarlton.com/en/hotels/colorado",
    "https://www.ritzcarlton.com/en/hotels/florida",
    "https://www.ritzcarlton.com/en/hotels/georgia",
    "https://www.ritzcarlton.com/en/hotels/hawaii",
    "https://www.ritzcarlton.com/en/hotels/new-york",
    "https://www.ritzcarlton.com/en/hotels/washington-dc",
    "https://www.ritzcarlton.com/en/hotels/canada/toronto"]
    for i in soup.find("div",{"class":"region"}).find_all("a"):
        page_url = i['href']
        if page_url in rm:
            continue
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,'html5lib')
        jd = json.loads(soup1.find_all("script",{"type":"application/ld+json"})[1].text.replace('"City by the Bay"',''))
        location_name = jd['name']
        street_address = jd['address']['streetAddress']
        city = jd['address']['addressLocality'].strip(",")
        state = jd['address']['addressRegion']
        zipp = jd['address']['postalCode']
        temp_phone = jd['telephone'].replace("+1","")
        phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
        location_type = "Ritz-Carlton Hotels"
        try:
            coord = json.loads(soup1.find("div",{"id":"poimap-canvas"})['data-map-settings'])
            latitude = coord['mapCenter']['latitude']
            longitude = coord['mapCenter']['latitude']
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>')
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
    ca_r = session.get("https://www.ritzcarlton.com/en/hotels/canada",headers=headers)
    ca_soup = BeautifulSoup(ca_r.text, 'lxml')
    for i in ca_soup.find_all("div",{"class":"card-content"}):
        page_url = i.find("a")['href']
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,'html5lib')
        jd = json.loads(soup1.find_all("script",{"type":"application/ld+json"})[1].text.replace('"City by the Bay"',''))
        location_name = jd['name'].replace("Montréal","Montreal")
        street_address = jd['address']['streetAddress']
        city = jd['address']['addressLocality'].strip(",").replace("Montréal","Montreal")
        if city == "Toronto":
            state = "ON"
        else:
            state = "QC"
        zipp = jd['address']['postalCode'].replace("ON","").strip()
        temp_phone = jd['telephone'].replace("+1","")
        phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
        location_type = "Ritz-Carlton Hotels"
        try:
            coord = json.loads(soup1.find("div",{"id":"poimap-canvas"})['data-map-settings'])
            latitude = coord['mapCenter']['latitude']
            longitude = coord['mapCenter']['latitude']
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("CA")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>')
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()