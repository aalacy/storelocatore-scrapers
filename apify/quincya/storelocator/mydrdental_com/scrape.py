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
    # Your scraper here
    
    base_link = "https://www.mydrdental.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}


    req = requests.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')


    items = base.findAll('div', attrs={'class': 'address'})

    data = []
    for item in items:
        locator_domain = "mydrdental.com"
        location_name = item.find('h3').text.strip()
        raw_data = item.find('p').text.replace("<div>\r\n ","").split('\n')

        if len(raw_data) == 2:
            street_address = raw_data[0].strip()
            zip_code = raw_data[1][raw_data[1].rfind(" ")+1:].strip()
            state = raw_data[1][raw_data[1].rfind(" ")-2:raw_data[1].rfind(" ")].strip()
            city = raw_data[1][:raw_data[1].find(state)].replace(",","").strip()
        else:            
            street_address = base.find('span', attrs={'itemprop': 'streetAddress'}).text
            city = base.find('span', attrs={'itemprop': 'addressLocality'}).text
            state = base.find('span', attrs={'itemprop': 'addressRegion'}).text
            zip_code = base.find('span', attrs={'itemprop': 'postalCode'}).text

        country_code = "US"
        link = item.find('a')['href']
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        req = requests.get(link, headers=headers)

        try:
            new_base = BeautifulSoup(req.text,"lxml")
            print("Got store details page")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        phone = new_base.findAll('span', attrs={'class': 'mm-phone-number'})[1].text
        gps_link = new_base.find('a', attrs={'class': 'directions'})['href']
        latitude = gps_link[gps_link.find("=")+1:gps_link.find(",")].strip()
        longitude = gps_link[gps_link.find(",")+1:].strip()
        hours_of_operation = new_base.find('ul', attrs={'class': 'loc_hours'}).get_text(separator=' ').strip()

        data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data
    base.find('ul', attrs={'class': 'loc_hours'})
    
    return [["safegraph.com", "SafeGraph", "1543 Mission St.", "San Francisco", "CA", "94103", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
