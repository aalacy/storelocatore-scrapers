import csv
import time
import requests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    url="https://thehoxton.com/contact?hotel=holborn"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    time.sleep(5)
    address = soup.findAll("p", {"class": "address"})
    phones=soup.findAll("span", {"class": "value"})
    for n in range(0,len(phones)):
        if '+' in phones[n].get_text():
            phone.append(phones[n].get_text())
    for n in range(0,len(address)):
        a=address[n].get_text()
        if 'USA' in a:
            street_address.append(a.split(",")[0])
            city.append(a.split(",")[1].strip())
            state.append(a.split(",")[2].split()[0].strip())
            zipcode.append(a.split(",")[2].split()[1].strip())
    for n in range(0,len(street_address)): 
        data.append([
            'https://thehoxton.com/',
            'https://thehoxton.com/contact?hotel=holborn',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<INACCESSIBLE>',
            '<INACCESSIBLE>',
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
