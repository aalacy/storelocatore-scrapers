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
    base_link = "https://oggis.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}


    req = requests.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
        print "Got today page"
    except (BaseException):
        print '[!] Error Occured. '
        print '[?] Check whether system is Online.'

    items = base.findAll('div', attrs={'class': 'post-entry post-entry-type-page post-entry-66'})
    items.pop(0)
    items.pop(0)
    
    data = []
    for item in items:
        no_zip = False
        locator_domain = "oggis.com"
        location_name = item.find('h3', attrs={'itemprop': 'headline'}).text.strip()
        raw_data = item.find('section', attrs={'class': 'av_textblock_section'}).text
        if raw_data[-1:] == "\n":
            raw_data = raw_data[:-1]
        raw_data = raw_data.split('\n')

        street_address = raw_data[0]
        bottom_line = raw_data[-1]
        city = bottom_line[:bottom_line.find(",")].strip()
        zip_code = bottom_line[bottom_line.rfind(" "):].strip()
        try:
            int(zip_code)
            state = bottom_line[bottom_line.find(",")+1:bottom_line.rfind(" ")].strip()
        except:
            zip_code = "<MISSING>"
            no_zip = True
            state = zip_code
                
        country_code = "US"
        link = item.find('a')['href']
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        links = item.find('div', attrs={'class': 'result_links'})
        link = links.findAll('a')[0]['href']

        if no_zip or location_name == "Del Mar":
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            directions = links.findAll('a')[1]['href']
            latitude = directions[directions.rfind("=")+1:directions.rfind(",")].strip()
            longitude = directions[directions.rfind(",")+1:directions.rfind("(")].strip()
            comma_point = directions.find(",")
            if latitude == "":
                latitude = directions[directions.find("@")+1:comma_point].strip()
                longitude = directions[directions.find(",")+1:directions.rfind(",",comma_point)].strip()
        
        phone = item.find('div', attrs={'class': 'result_address'})
        phone = phone.find('a').text

        req = requests.get(link, headers=headers)

        try:
            new_base = BeautifulSoup(req.text,"lxml")
            print "Got store details page"
        except (BaseException):
            print '[!] Error Occured. '
            print '[?] Check whether system is Online.'

        section = new_base.findAll('section', attrs={'class': 'av_textblock_section'})[1]
        hours_of_operation = section.find('div', attrs={'id': 'lbmb_hours'}).text.encode('utf-8').strip()

        data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
