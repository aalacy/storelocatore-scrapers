import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from random import randint
import time
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
      
    base_link = "https://www.fusian.com/locations"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    time.sleep(randint(1,2))
    try:
      base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
      print ('[!] Error Occured. ')
      print ('[?] Check whether system is Online.')

    items = base.find_all(class_="intrinsic")
    locator_domain = "fusian.com"

    data=[]
    for item in items:
        link = "https://www.fusian.com" + item.a['href']

        req = session.get(link, headers=headers)
        time.sleep(randint(1,2))
        try:
          base = BeautifulSoup(req.text,"lxml")
        except (BaseException):
          print ('[!] Error Occured. ')
          print ('[?] Check whether system is Online.')

        location_name = base.h1.text[1:-1].title()
        print(location_name)

        all_scripts = base.find_all('script', attrs={'type': "application/ld+json"})
        for script in all_scripts:
          if "latitude" in str(script):
            script = script.text.replace('\n', '').strip()
            break

        script = base.find_all('script', attrs={'type': "application/ld+json"})[-2].text.replace('\n', '').strip()
        store_data = json.loads(script)

        street_address = store_data['address']['streetAddress']
        city = store_data['address']['addressLocality']
        state = store_data['address']['addressRegion']
        zip_code = store_data['address']['postalCode']
        country_code = "US"
        store_number = "<MISSING>"
        phone = store_data['telephone']
        latitude = store_data['geo']['latitude']
        longitude = store_data['geo']['longitude']

        hours_of_operation = base.find_all(class_="sqs-block-content")[3].p.text.strip()
        if hours_of_operation == "sun-thurs: 11a – 9p":
            hours_of_operation = hours_of_operation + " " + base.find_all(class_="sqs-block-content")[3].find_all('p')[1].text.strip()
        location_type = "<MISSING>"
    
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

