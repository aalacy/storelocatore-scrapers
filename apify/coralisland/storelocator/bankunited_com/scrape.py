import csv
import re
from sgrequests import SgRequests
from lxml import etree

base_url = 'https://www.bankunited.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
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
    url = "https://www.bankunited.com/contact-us/find-a-branch-atm/GetLocations"
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        'Latitude': '34.0448583',
        'Longitude': '-118.4484367',
        'Radius': '3000',
        'ShowDisasterView': 'False'
    }
    request = session.post(url, data=data, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "row marker-row")]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append("https://www.bankunited.com/contact-us/find-a-branch-atm")
        output.append(get_value(store.xpath('.//span[@itemprop="name"]//text()'))) #location name
        address = get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))
        output.append(address) #address        
        output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()'))) #city
        if address == "5295 Town Center Road":
            output.append("FL") #state
        else:
            output.append(get_value(store.xpath('.//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
        loc_type = "".join(store.xpath('.//span[@class="blue-text"]//text()')).replace("\r\n","").strip()
        loc_type = (re.sub(' +', ' ', loc_type)).strip()
        output.append(loc_type) #location type
        output.append(get_value(store.xpath('.//div[@class="col-sm-10 col-9 branch-location"]/@data-lat'))) #latitude
        output.append(get_value(store.xpath('.//div[@class="col-sm-10 col-9 branch-location"]/@data-lng'))) #longitude
        hours = get_value(store.xpath('.//span[@itemprop="openingHours"]//text()'))
        if hours[:1] == "0":
            hours = "Mon-Fri: " + hours
        output.append(hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
