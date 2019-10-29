import csv
import requests
from bs4 import BeautifulSoup
import re

DOMAIN = 'https://caliburger.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data=[]
    url = "https://caliburger.com/locations"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    locations = soup.find('div', attrs={'class':'locations-block'})
    for tag in locations.div.next_siblings:
        try:
            loc = BeautifulSoup(str(tag), features="lxml")
            if loc is not None:
                country = 'US'
                if loc.find('div', attrs={'class':'cali-country'}) is not None:
                    if "Canada" in loc.find('div', attrs={'class':'cali-country'}).text:
                        country = 'CA'
                    else:
                        break
                if loc.find('div', attrs={'class':'cali-store-description'}) is not None:
                    if "COMING SOON!" not in loc.find('div', attrs={'class':'cali-store-description'}).text.strip():
                        if loc.find('td', attrs={'valign':'top'}) is not None:
                            try:
                                location_name = loc.find('td', attrs={'valign':'top'}).text.strip()
                                if(location_name == '' or location_name == 0):
                                    location_name = MISSING
                            except:
                                location_name = MISSING
                        if loc.find('div', attrs={'class':'cali-store-address'}) is not None:
                            ad = loc.findAll('div', attrs={'class':'cali-store-address'})[-1]
                            street = loc.findAll('div', attrs={'class':'cali-store-address'})[0]
                            try:
                                if (ad.text == '' or ad.text == 0):
                                    city = state = city = MISSING
                                else:
                                    ad_line = ad.text.strip()
                                    ad_list = re.split("[\s]+", ad_line)
                                    zipcode = ad_list[-1]
                                    state = ad_list[-2]
                                    city = ad_list[-3]
                            except:
                                zipcode = state = city = MISSING
                            try:
                                if(street == '' or street == 0):
                                    street_address = MISSING
                                street_address = street.text.strip()
                            except:
                                street_address = MISSING
                            store_number = phone = location_type = hours_of_operation = phone = MISSING
                            lat = lon = '<INACCESSIBLE>'
                            data.append([DOMAIN, location_name, street_address, city, state, zipcode, country, store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
