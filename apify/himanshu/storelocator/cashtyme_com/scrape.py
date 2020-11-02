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
    base_url = "http://cashtyme.com"
    r = session.get(base_url+"/side.htm")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('select',{'name':"state"}).find_all('option')
    hour=list(soup.find_all('font')[0].stripped_strings)
    del hour[0]
    hour=' '.join(hour)+' , '+' '.join(soup.find_all('font')[1].stripped_strings)
    del main[0]
    for dt in main:
        r1 = session.get(base_url+"/locations/"+dt['value']+".htm")
        soup1 = BeautifulSoup(r1.text,"lxml")
        main1 = soup1.find('table').find('table').find('table').find('table').find_all('tr')
        del main1[0]
        for val in main1:
            address=val.find_all('td')[0].text.strip()
            store=[]
            store.append("http://cashtyme.com")
            store.append("<MISSING>")
            store.append(re.sub(r'\s+', ' ',address))
            store.append(val.find_all('td')[1].text.strip())
            store.append(dt['value'])
            store.append(val.find_all('td')[2].text.strip())
            store.append('US')
            store.append("<MISSING>")
            store.append(val.find_all('td')[3].text.strip())
            store.append("cashtyme")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hour)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
