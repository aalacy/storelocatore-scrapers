import time
import csv
import requests
from bs4 import BeautifulSoup
import re

DOMAIN = 'https://mastercuts.com'
MISSING = '<MISSING>'

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})


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
    url = "https://www.mastercuts.com/wpsl_stores-sitemap.xml"
    response = requests.get(url, headers = headers)

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.findAll('loc') 
    for row in table:
        try:
            loc_url = row.text
            time.sleep(4)
            res = requests.get(loc_url, headers = headers)
            loc_data = BeautifulSoup(res.content, "html.parser")
            loc_html = loc_data.find('div', attrs = {'class': 'tbg-column'})
            loc_soup = BeautifulSoup(str(loc_html), "lxml")
            location_name = loc_soup.find('h2').text.strip()
            loc_ad = loc_soup.find('address').text.strip()
            ad_list = re.split("\n", loc_ad)
            street_address = ad_list[0].strip()
            country = ad_list[2].strip()
            if(country == 'USA'):
                country = 'US'
            elif(country == 'PR'):
                continue
            hours_of_operation = loc_soup.find('table', attrs = {'class':'wpsl-opening-hours'}).text.strip()
            tel_data = loc_soup.findAll('a', href = True)
            for tel in tel_data:
                if "tel:" in str(tel['href']):
                    phone = tel.text.strip()
            gmap_url = loc_data.findAll('script', attrs = {'type':'text/javascript'})
            for map_data in gmap_url:
                if "var wpslSettings" in map_data.text:
                    lat_data = re.findall('\"lat\":\"[-+]?[0-9]*\.?[0-9]+', map_data.text)
                    lat = re.findall('[-+]?[0-9]*\.?[0-9]+', str(lat_data[0]))[0]
                    lat_data = re.findall('\"lng\":\"[-+]?[0-9]*\.?[0-9]+', map_data.text)
                    lon = re.findall('[-+]?[0-9]*\.?[0-9]+', str(lat_data[-1]))[0]
                    city_data = re.findall('(\"city\":\"[a-zA-Z0-9 ]+\")', map_data.text)
                    city_regex = re.split(':', str(city_data[0]))
                    city = re.sub('\"', '', city_regex[-1])
                    state_data = re.findall('(\"state\":\"[a-zA-Z0-9 ]+\")', map_data.text)
                    state_regex = re.split(':', str(state_data[0]))
                    state = re.sub('\"', '', state_regex[-1])
                    zip_data = re.findall('(\"zip\":\"[a-zA-Z0-9 ]+\")', map_data.text)
                    zip_regex = re.split(':', str(zip_data[0]))
                    zipcode = re.sub('\"', '', zip_regex[-1]).strip()
                    if(len(zipcode) <= 4):
                        zero = 5 - len(zipcode)
                        for z in str(zero):
                            zipcode = str(0) + zipcode
            store_number = location_type = MISSING
            data.append([DOMAIN, location_name, street_address, city, state, zipcode, country, store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
