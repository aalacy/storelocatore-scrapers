import csv
import re
from lxml import etree
import json
from sgrequests import SgRequests

base_url = 'http://kingtaco.com'

def validate(item):
    if type(item) == list:
        item = ' '.join(item)
    while True:
        if item[-1:] == ' ':
            item = item[:-1]
        else:
            break
    return item.strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    output_list = []
    url = "https://kingtaco.com/locations.html"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "authority": "kingtaco.com",
        "method": "GET",
        "path": "/locations.html",
        "scheme": "https"
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//article')[1:-5]
    for store in store_list:
        address = eliminate_space(store.xpath('.//div[@class="caption"]//text()'))
        geoinfo = validate(store.xpath('.//div[@class="caption"]//a/@href'))
        try:
            latitude = geoinfo.split('!3d')[1].split('!')[0]
            longitude = geoinfo.split('!2d')[1].split('!3d')[0]            
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        if len(address) <= 2:
            phone = "<MISSING>"
        else:
            phone = address[2].replace("Phones:","")
            phone = re.findall("[(\d)]{5} [\d]{3}-[\d]{4}", str(phone))[0]

        output = []
        output.append(base_url) # url
        output.append(base_url)
        output.append(validate(store.xpath(".//h3//text()"))) #location name
        output.append(address[0]) #address
        output.append(address[1].split(', ')[0]) #city
        output.append(address[1].split(', ')[1][:2].upper()) #state
        output.append(address[1].split(', ')[1][3:].strip()) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone.replace('Phone: ', '')) #phone
        output.append("<MISSING>") #location type
        output.append(latitude) #latitude
        output.append(longitude) #longitude
        output.append(get_value(address[3:]).encode("ascii", "replace").decode().replace("?","")) #opening hours
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
