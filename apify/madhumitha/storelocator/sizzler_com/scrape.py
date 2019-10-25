import csv
import requests
from bs4 import BeautifulSoup
import re
import time


DOMAIN = 'https://www.sizzler.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data=[]
    url = "https://www.sizzler.com/locations"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    loc_tag = soup.find('script', attrs = {'type':'text/javascript'})
    jsn = re.findall('store.*\n\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\}', loc_tag.text)
    try:
        for j in jsn:
            loc_url = re.findall('url:.*',j)
            loc_tag = re.findall("\'.*\'", loc_url[0])
            l = re.sub("\'", '',loc_tag[0])
            page_url = "https://www.sizzler.com/locations/"+ l +"#locations"
            res = requests.get(page_url)
            loc_data = BeautifulSoup(res.content, "html.parser")
            time.sleep(3)
            ad_html = loc_data.find('div', attrs={'class':'restaurant-info'})
            if ad_html is None:
                continue
            ad_data = ad_html.findAll('p')
            state = ad_data[2].text.split(' ')[0].strip()
            if state == 'PR':
                continue
            zipcode = ad_data[2].text.split(' ')[1].strip()
            if(len(zipcode) <= 4):
                zero = 5 - len(zipcode)
                for z in str(zero):
                    zipcode = str(0) + zipcode
            loc_detail = loc_data.find('script', attrs={'type':'text/javascript'})
            lat_data = re.findall('lat\:[-+]?[0-9]*.*\.?[0-9]+', loc_detail.text)
            lat = re.split(':', lat_data[0])[1].strip()
            lng_data = re.findall('lng\:[-+]?[0-9]*.*\.?[0-9]+', loc_detail.text)
            lon = re.split(':', lng_data[0])[1].strip()
            title_data = re.findall('title\:.*', loc_detail.text)
            if title_data == []:
                continue
            location_name = re.split(':', title_data[0])[1].replace('\'','').replace(',', '').strip()
            hrs_data = re.findall('hours\:.*', loc_detail.text)
            hours_of_operation = hrs_data[0].replace('hours:','').replace('<p>','').replace(',', '').replace('</p>',', ').replace('<br>', ',').replace('<br/>', ' ').replace('<font>', '').replace('</font>', '').replace('<b>', '').replace('</b>', '').replace('\'','').strip()
            if "Closed" in hours_of_operation:
                continue
            elif hours_of_operation == '':
                hours_of_operation = MISSING
            phone_data = re.findall('phone\:.*', loc_detail.text)
            phone = re.split(':', phone_data[0])[1].replace('\'','').replace(',', '').strip()
            if phone is '':
                phone = MISSING
            ad_details = re.findall('address\:.*', loc_detail.text)
            ad = re.split(':', ad_details[0])[1].replace('\'','').strip()
            city = re.split(',', ad)[-2].strip()
            street_address = re.split(',', ad)[0].strip()
            location_type = store_number = MISSING
            data.append([DOMAIN, page_url, location_name, street_address, city, state, zipcode, 'US', store_number, phone, location_type, lat, lon, hours_of_operation])
    except requests.exceptions.RequestException:
        pass
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
