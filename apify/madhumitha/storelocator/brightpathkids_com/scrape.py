import csv
import requests
from bs4 import BeautifulSoup

DOMAIN = 'https://brightpathkids.com'
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
    url = "https://brightpathkids.com/all-locations/"    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    for row in soup.findAll('a', href = True, text = 'Visit Location'):
        try:
            loc_url = row['href']
            res = requests.get(loc_url)
            loc = BeautifulSoup(res.content, "html.parser")
            title = loc.find('title').text
            try:
                if "Nothing found" in title:
                    continue
                elif "Opening Early" in loc.find('meta', attrs={'property':'og:title'})['content']:
                    continue
                else:
                    location_name = loc.find('meta', attrs={'property':'og:title'})['content'].strip()
                    if(location_name == '' or location_name == 0):
                        location_name = MISSING
            except:
                continue
            try:
                street_address = loc.find('span', attrs={'itemprop':'streetAddress'}).text.strip()
                if(street_address == '' or street_address == 0):
                    street_address = MISSING
            except:
                street_address = MISSING
            try:
                city = loc.find('span', attrs={'itemprop':'addressLocality'}).text.strip()
                if(city == '' or city == 0):
                    city = MISSING
            except:
                city = MISSING
            try:
                state = loc.find('span', attrs={'itemprop':'addressRegion'}).text.strip()
                if(state == '' or state == 0):
                    state = MISSING
            except:
                state = MISSING
            try:
                zipcode = loc.find('span', attrs={'itemprop':'postalCode'}).text.strip()
                if(zipcode == '' or zipcode == 0):
                    zipcode = MISSING
            except:
                zipcode = MISSING
            try:
                phone = loc.find('span', attrs={'itemprop':'telephone'}).text.strip()
                if(phone == '' or phone == 0):
                    phone = MISSING
            except:
                phone = MISSING
            location_type = store_number = MISSING
            hr_tag = loc.find('td')
            if "Hours:" in hr_tag.text:
                hours_of_operation = hr_tag.findNext('td').text.strip()
            if(hours_of_operation == '' or hours_of_operation == 0):
                hours_of_operation = MISSING
            lat = loc.find('div', attrs={'class':'marker'})['data-lat']
            if(lat == '' or lat == 0):
                lat = MISSING
            lon = loc.find('div', attrs={'class':'marker'})['data-lng']
            if(lon == '' or lon == 0):
                lon = MISSING
            data.append([DOMAIN, location_name, street_address, city, state, zipcode, 'CA', store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
