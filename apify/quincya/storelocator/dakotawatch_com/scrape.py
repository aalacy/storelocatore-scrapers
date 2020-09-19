import requests
from bs4 import BeautifulSoup
import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_link = "https://www.dakotawatch.com/index.php/storelocator"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}


    req = requests.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')


    items = base.findAll('div', attrs={'class': 'store-ul'})

    data = []
    for item in items:
        locator_domain = "dakotawatch.com"
        location_name = item.find('span').text.strip()
        raw_data = item.find('div').replace("<div>\r\n ","").split('<br/>')
        street_address = raw_data[0].replace(",","").strip()
        city = raw_data[1].replace(",","").strip()
        state = raw_data[2].replace(",","").strip()
        zip_code = raw_data[3][raw_data[3].find(",")+1:].strip()
        country_code = raw_data[3][:raw_data[3].find(",")].strip()
        link = item.find('a')['href']
        store_number = link[link.rfind("id")+3:-1]
        phone = "<MISSING>"
        location_type = location_name[location_name.rfind(" ")+ 1:]
        if isinstance(location_type, int):
            location_type = location_name[:location_name.find(" ")]

        req = requests.get(link, headers=headers)

        try:
            new_base = BeautifulSoup(req.text,"lxml")
            print("Got store details page")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        full_page = str(new_base)
        start_point = full_page.find('myLatLng')
        end_point = full_page.find('}',start_point)
        raw_gps = full_page[start_point:end_point]

        latitude = raw_gps[raw_gps.find(":")+1:raw_gps.find(",")].strip()
        longitude = raw_gps[raw_gps.rfind(":")+1:].strip()
        hours_of_operation = "<MISSING>"

        data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
