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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://joevsmartshop.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('li',{'class':"menu-item-20726"}).find('ul').find_all('a')
    for dt in main:
        r1 = session.get(dt['href'], headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        main2=list(soup1.find('div',{"class":"vc_cta3-content"}).stripped_strings)
        location=main2[1].split(',')
        if len(location)==3:
            address=location[0].strip()
            city=location[1].strip()
            state=location[2].strip().split(' ')[0].strip()
            zip=location[2].strip().split(' ')[1].strip()
        else:
            rindex=location[0].strip().rindex(' ')
            address=location[0][0:rindex].strip()
            city=location[0][rindex:].strip()
            state=location[1].strip().split(' ')[0].strip()
            zip=location[1].strip().split(' ')[1].strip()
        store=[]
        store.append("https://joevsmartshop.com/")
        store.append(soup1.find('h1',{"class":"entry-title"}).text.strip())
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append('US')
        store.append("<MISSING>")
        store.append(main2[2])
        store.append("joevsmartshop")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(main2[3])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
