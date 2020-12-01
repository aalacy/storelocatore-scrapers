import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('suzuki_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:

            writer.writerow(row)

def time_converter(number):
    number = number - 1
    temp_time = number/2
    is_am = "AM"
    if temp_time > 12:
        is_am = "PM"
        temp_time = temp_time - 12
    hour = ""
    if ".0" in str(temp_time):
        return str(int(temp_time)) + ":00" + is_am
    else:
        return str(int(temp_time)) + ":30" + is_am

def fetch_data():
    base_url ="http://suzuki.com"
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 4
    MAX_DISTANCE = 25.0
    zip = search.next_zip()
    while zip:
        result_coords = []
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #logger.info('Pulling Lat-Long %s...' % (str(zip)))
        try:
            r = session.get(base_url+'/DealerSearchHandler.ashx?zip='+str(zip)+'&hasCycles=true&hasAtvs=true&hasScooters=true&hasMarine=true&hasAuto=true&maxResults=4&country=en')
        except:
            continue
        soup=BeautifulSoup(r.text,'lxml')
        for loc in soup.find_all('dealerinfo'):
            name=loc.find('name').text.strip()
            address=loc.find('address').text.strip().lower()
            city=loc.find('city').text.strip()
            state=loc.find('state').text.strip()
            zip=loc.find('zip').text.strip()
            phone=loc.find('phone').text.strip()
            country=loc.find('country').text.strip()
            storeno=loc.find('dealerid').text.strip()
            lat=loc.find('esriy').text.strip()
            lng=loc.find('esrix').text.strip()
            result_coords.append((lat, lng))
            hour = loc.find('hoursdetails').text
            hours = ""
            if hour == "||||||||||||||":
                continue
            groups = hour.split('|')
            days_hour = []
            for i in range(0,len(groups)-1,2):
                days_hour.append("|".join(groups[i:i+2]))
            days_map = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
            for i in range(len(days_hour)):
                if days_hour[i] == "|":
                    hours = hours + " " + days_map[i] + ' Closed'
                else:
                    hours = hours + " " + days_map[i] + " " + time_converter(int(days_hour[i].split("|")[0])) + "-" + time_converter(int(days_hour[i].split("|")[1]))
            store=[]
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone.replace("/","-") if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hours if hours else "<MISSING>")
            if store[-1].count("close") > 12:
                continue
            store.append("<MISSING>")
            store = [x.replace("–","-") for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            yield store
        if len(soup.find_all('dealerinfo')) < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(soup.find_all('dealerinfo')) == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
