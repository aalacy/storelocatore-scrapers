from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://planetbeach.com/spa-locator/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(url, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    store_url_list = base.find(id="textResults").find_all("li")
    for store in store_url_list:
        store_url = store.a['href']
        detail_request = session.get(store_url, headers = HEADERS)
        print(store_url)
        time.sleep(randint(1,2))
        try:
            item = BeautifulSoup(detail_request.text,"lxml")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        geoinfo = str(item.find_all(class_="hidden-md hidden-lg")[-1]).split('red%7C')[1].split("')")[0].split(',')
        hours = item.find(class_="map-hours").text.replace('\n', '').replace("pm","pm ").strip()
        if "     " in hours:
            hours = hours[:hours.find("     ")].strip()

        output = []
        output.append("planetbeach.com") # locator_domain
        output.append(store_url) # url
        output.append("Planet Beach Spray & Spa " + item.find(id='spaName').text) #location name
        output.append(item.find('span', attrs={'itemprop': 'streetAddress'}).text.strip()) #address
        output.append(item.find('span', attrs={'itemprop': 'addressLocality'}).text.strip()) #city
        output.append(item.find('span', attrs={'itemprop': 'addressRegion'}).text.strip()) #state
        output.append(item.find('span', attrs={'itemprop': 'postalCode'}).text.strip()) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(item.find('span', attrs={'itemprop': 'telephone'}).text.strip()) #phone
        output.append("<MISSING>") #location type
        output.append(geoinfo[0]) #latitude
        output.append(geoinfo[1]) #longitude
        output.append(hours) #opening hours
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
