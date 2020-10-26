import requests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    base_link = "http://newdixieoil.com/index.php?option=com_chronoconnectivity&connectionname=Stores"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    req = requests.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    content = base.find('div', attrs={'id': 'mainbody'})
    items = content.findAll('tr')
    items.pop(0)

    data = []
    for item in items:
        locator_domain = "newdixieoil.com"
        location_name = item.findAll('td')[0].text.strip()
        city = item.findAll('td')[1].text.strip()
        state = item.findAll('td')[2].text.strip()
        zip_code = item.findAll('td')[3].text.strip()
        country_code = "US"
        location_type = item.findAll('td')[4].text.strip()
        try:
            store_number = int(location_name[location_name.find('#')+1:location_name.find('#')+3])
        except:
            store_number = "<MISSING>"
        link = "http://newdixieoil.com" + item.find('a')['href']
    
        req = requests.get(link, headers=headers)

        try:
            new_base = BeautifulSoup(req.text,"lxml")
            print("Got store details page")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        page_details = new_base.find('div', attrs={'id': 'mainbody'})
        page_details = page_details[:-15]
        raw_str = page_details[page_details.rfind('div>')+7:page_details.rfind('<br/>')-4].replace("&amp;","&")
        street_address = raw_str[:raw_str.find('<br')-1].strip()
        if "Dixie Mart" in street_address:
            new_point = raw_str.find('<br')+5
            street_address = raw_str[new_point:raw_str.find('<br',new_point)]

        try:
            phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", raw_str)[0]
        except:
            phone = "<MISSING>"
            
        #street_address = raw_str[:raw_str.find('<br')].strip()

        start_point = page_details.find('GLatLng')
        end_point = page_details.find(')',start_point)
        raw_gps = page_details[start_point:end_point]

        latitude = raw_gps[raw_gps.find("(")+1:raw_gps.find(",")].strip()
        longitude = raw_gps[raw_gps.rfind(",")+1:].strip()
        hours_of_operation = "<MISSING>"

        data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()