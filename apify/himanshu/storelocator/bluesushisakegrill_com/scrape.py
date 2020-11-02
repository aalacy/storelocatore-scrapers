import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bluesushisakegrill_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    base_url = "https://bluesushisakegrill.com/"
    get_url = "https://bluesushisakegrill.com/locations"
    r = session.get(get_url)
    soup = BeautifulSoup(r.text, "lxml")
    store_name = []
    store_detail = []
    return_main_object = []
    name1 = []
    main = soup.find_all("h3", {"class": "locations-item-title"})
    
    for i in main:
        addresss= i.find('locations-item-details-item')
        link =i.find('a').text
        if 'The Domain - Coming Soon!' in link:
            continue
      
        link =i.find('a')['href']
        r1 = session.get(link)
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1 = soup1.find("div", {"class": "location_details-address"})
        location_name = soup1.find('div',{'class':'page_header-container'}).text.strip()
        data= list(main1.stripped_strings)
        address= data[2]
        city = data[3].split(',')[0]
        state = data[3].split(',')[1].strip().split(' ')[0]
        zip = data[3].split(',')[1].strip().split(' ')[1]
        phone= soup1.find('p',{'class':'location_details-phone'}).text
        hour_tmp = soup1.find('div',{'class':'location_details-hours'})
        hour= ' '.join(list(hour_tmp.stripped_strings))
        cords = soup1.find('a',{'class':'location_details-address-directions button button--primary button--solid'})['href'].split('@')#[1].split(',')[0]
        if(len(cords)==2):

            lat = soup1.find('a',{'class':'location_details-address-directions button button--primary button--solid'})['href'].split('@')[1].split(',')[0]
            lng = soup1.find('a',{'class':'location_details-address-directions button button--primary button--solid'})['href'].split('@')[1].split(',')[1]
        elif(len(cords)==1):
            lat = soup1.find('a',{'class':'location_details-address-directions button button--primary button--solid'})['href'].split('=')[-1].split('+')[0]
            lng = soup1.find('a',{'class':'location_details-address-directions button button--primary button--solid'})['href'].split('=')[-1].split('+')[1]
            # logger.info(lat)


        store=list()
        store.append("https://bluesushisakegrill.com")
        store.append(location_name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        store.append(link)
        yield store
    
   # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
