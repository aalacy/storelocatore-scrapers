import csv
import requests
from bs4 import BeautifulSoup
from lxml import html
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    url ='http://www.peakpt.com/contact.html'
    r = requests.get(url)
    tree = html.fromstring(r.content)
    soup = BeautifulSoup(r.content, 'html.parser')
    store = soup.findAll("a", href=lambda href: href and href.startswith("javascript:window.scrollTo(0,0)"))
    for n in range(0,len(store)):
        a=store[n].get_text()
        if ('Directions' not in a) and (a!="") and ('Top' not in a):
            street_address.append(store[n].get_text().strip().split(",")[0].split('   ')[0])
            tagged = usaddress.tag(store[n].get_text())[0]
            try:
                city.append(tagged['PlaceName'])
            except:
                city.append('<MISSING>')
    stores = soup.findAll("div", {"class": "address-full"})
    for n in range(0,len(stores)):
        state.append(stores[n].get_text().split(",")[1])
        zipcode.append(stores[n].get_text().split(",")[2])
    phones = soup.findAll("div", {"class": "address-line-idphone"})
    for n in range(0,len(phones)):
        phone.append(phones[n].get_text().split("Phone:")[1])
    hours = soup.findAll("div", {"class": "address-line-idhours"})
    for n in range(0,len(street_address)):
        try:
            hours_of_operation.append(hours[n].get_text().strip())
        except:
            hours_of_operation.append('<MISSING>')
    for n in range(0,len(street_address)): 
        data.append([
            'http://www.peakpt.com',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation[n]
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
