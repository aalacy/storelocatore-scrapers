import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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
    addresses = []
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.independent-bank.com/"
    loacation_url = "https://www.independent-bank.com/our-story/general-contact/locations-hours.html"
    r = session.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    ck = soup.find('ul',{'id':'locList'}).find_all('div',{'class':'branchName'})
    for target_list in ck:
        # print('https://www.independent-bank.com'+target_list.find('a')['href'])
        page_url='https://www.independent-bank.com'+target_list.find('a')['href']
        store_number = page_url.split('=')[1].split('&')[0]
        # print(store_number)
        k = session.get('https://www.independent-bank.com'+target_list.find('a')['href'],headers = header)
        soup = BeautifulSoup(k.text,"lxml")
        locator_domain = base_url
        country_code = "US"
        ul = soup.find('ul',{'id':'locList'}).find('li')
        location_name = ul['data-title']
        street_address = ul['data-address1']+ " "+ul['data-address2']
        city = ul['data-city']
        state = ul['data-state']
        zipp = ul['data-zip']
        latitude= ul['data-latitude']
        longitude = ul['data-longitude']
        contact = ul.find('div',class_='contact')
        if contact != None:
            list_phone = list(contact.stripped_strings)
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(list_phone)))
            if phone_list:
                phone = phone_list[0]
            else:
                phone = "<MISSING>"
        else:
            phone = "<MISSING>"
        hours = ul.find('div',class_="hours")
        if hours != None:
            hours_of_operation =  " ".join(list(hours.stripped_strings))
        else:
            hours_of_operation = "<MISSING>"
        location_type = "Branch"
        # loc_type = ul.find('div',class_="hours").nextSibling
        # print(loc_type.prettify())
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
                
        
def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
