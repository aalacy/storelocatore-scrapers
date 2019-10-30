import csv
import requests, re
from bs4 import BeautifulSoup
from lxml import html
import usaddress
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def fetch_data():
    url="https://zinburger.com/locations/"
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    r = requests.get(url)
    tree = html.fromstring(r.content)
    soup = BeautifulSoup(r.content, 'html.parser')
    script = soup.findAll("script")
    lat = re.findall(r'latitude.*?\":"[\d.*]*',str(script))
    lon = re.findall(r'longitude.*?\":"-[\d.*]*',str(script))
    for n in range(0,len(lat)):
        latitude.append(lat[n].split('":"')[1])
        longitude.append(lon[n].split('":"')[1])
    location = soup.findAll("h6", {"class": "title-heading-left"})
    for n in range(0,len(location)):
        if 'MAP IT' in location[n].get_text():
            location_name.append(location[n].get_text().strip())
    address = soup.findAll("div", {"class": "fusion-text"})
    hours = soup.findAll("div", {"class": "panel-body toggle-content fusion-clearfix"})
    hours_of_operation = [hours[n].get_text() for n in range(0,len(hours))]
    address = soup.findAll("div", {"class": "fusion-text"})
    address2 = [address[n].get_text().split("To Order")[0] for n in range(0,len(address))]
    for n in range(2,len(address2)):
        try:
            tagged = usaddress.tag(str(address2[n].split("\n")[0:3]))[0]
        except:
            tagged = usaddress.tag(str(address2[n].split("\n")[1:3]))[0]
        if re.findall(r'[\d].*',address2[n].split("\n")[0])!=[]:
            street_address.append(address2[n].split("\n")[0])
        else:
            street_address.append(address2[n].split("\n")[1])
        city.append(tagged['PlaceName'])
        state.append(tagged['StateName'])
        zipcode.append(tagged['ZipCode'])
        phones = address2[n].split("\n")
        for n in range(0,len(phones)):
            if '-' in phones[n]:
                phone.append(phones[n])
    for n in range(0,len(location_name)): 
        data.append([
            'https://zinburger.com/',
            'https://zinburger.com/locations/',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    return data
def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
