import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    locator_domain = "http://swamiscafe.com/"
    location_url  = 'http://swamiscafe.com/?hcs=locatoraid&hca=search%3Asearch%2F%2Fproduct%2F_PRODUCT_%2Flat%2F%2Flng%2F%2Flimit%2F100'
    r = session.get(location_url ,headers = header)
    soup= BeautifulSoup(r.text,"lxml")
    data_12 = (soup.find_all("script",{'type':"application/json"})[-2].text.split('{"__typename":"CustomForm","id":20586,"allowAttachments":false,"description":null,"displayGeneralFeedback":false,"emailCsv":null,"heading":null,"isPhoneRequired":false,"label":"Form","showLocationDropdown":false,"showDateField":false},"customVideoUploadedVideo":null,"galleryImages":[],"locations":')[1].split(',"menus":[],"rootSectionType":null,"sectionColumns":[],"selectedEventTags":[],"selectedLocations":[{"__typename":"CustomPageSelectedLocation","id":7368')[0])
    latitude = ''
    longitude = ''
    json_data12 = json.loads(data_12)
    for mp in json_data12:
        latitude = (mp['lat'])
        longitude = (mp['lng'])
        store_number = mp['restaurantId']
        street_address = mp['streetAddress']
        city = mp['city']
        state = mp['state']
        zipp =mp['postalCode']
        phone = mp['phone']
        location_type = "<MISSING>"
        location_name = mp['slug']
        hours_of_operation = str(mp['schemaHours']).replace("'","").replace("[","").replace("]","")
        page_url = "https://www.swamiscafe.com/"+str(location_name)
        country_code = mp['country']
        store=[]
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name.replace('Encinitas Inland 101',"Encinitas Inland") if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        yield store
def scrape():
    data = fetch_data()

    write_output(data)

scrape()
