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
        
        base_link = "https://www.hsoil.com/locations.html"

        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        headers = {'User-Agent' : user_agent}

        req = requests.get(base_link, headers=headers)

        base = BeautifulSoup(req.text,"lxml")

        sections = base.findAll('section')
        sections.pop(0)

        data = []
        for section in sections:
                locator_domain = "hsoil.com"
                location_name = section.find('h4').text.strip()
                raw_data = str(section.findAll('div', attrs={'class': 'columns small-12 medium-6'})[0].p).strip().replace('<p>',"").replace('</p>',"").split('<br/>')

                if len(raw_data) == 3:
                        street_address = raw_data[0] + " " + raw_data[1]
                        last_line = 2
                else:
                        street_address = raw_data[0]
                        last_line = 1
                                        
                city = raw_data[last_line][:raw_data[last_line].find(',')].strip()
                state = raw_data[last_line][raw_data[last_line].find(',')+1:raw_data[last_line].rfind(' ')].strip()
                zip_code = raw_data[last_line][raw_data[last_line].rfind(' ')+1:].strip()
                country_code = "US"
                store_number = "<MISSING>"
                phone = section.findAll('div', attrs={'class': 'columns small-12 medium-6'})[1].a.text.strip()
                location_type = location_name[location_name.rfind(' ')+ 1:].strip()
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"

                data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

        return data

def scrape():
        data = fetch_data()
        write_output(data)

scrape()
