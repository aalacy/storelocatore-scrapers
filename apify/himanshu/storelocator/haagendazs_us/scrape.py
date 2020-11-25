import urllib.parse
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import csv
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('haagendazs_us')






session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    ## FOR STORE    
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 300
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }
    while coord:
        result_coords = []
        lat = str(coord[0])
        lng = str(coord[1])

        base_url = 'https://www.haagendazs.us'
        locator_domain = "https://www.haagendazs.us"
        location_name = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        try:
            json_data = session.get("https://www.haagendazs.us/locator/ws/"+str(search.current_zip)+"/"+lat+"/"+lng+"/25/0/2452?lat="+lat+"&lon="+lng+"&radius="+str(MAX_DISTANCE)+"&zipcode="+str(search.current_zip)+"&BrandFlavorID=2452&targetsearch=3").json()
        except:
            pass
        current_results_len = len(json_data)
        for data in json_data:
            url = data['URL'].strip()
            if url:
                page_url ="https://www.haagendazs.us"+ url
                html = session.get(page_url)
                soup = BeautifulSoup(html.text,"html.parser")
                try:
                    hours_of_operation = " ".join(list(soup.find("div",attrs={"class":"office-hours"}).stripped_strings))
                except:
                    hours_of_operation = ""
            else:
                page_url="<MISSING>"
                hours_of_operation ="<MISSING>"
            result_coords.append((data['lat__c'], data['lon__c']))
            location_type = data['IsHDShop']
            if location_type == True:
                continue
            else:
                location_type='store'        
            store = [locator_domain, data['Name'], data['Shop_Street__c'], data['Shop_City__c'], data['Shop_State_Province__c'], data['Shop_Zip_Postal_Code__c'], country_code,
            store_number, data['phone'], location_type, data['lat__c'], data['lon__c'], hours_of_operation, page_url]
            store = [x if x else "<MISSING>" for x in store]
            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            #logger.info("~~~~~~~~~~~~~~~~~~~  ",store)
            yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

    ## FOR SHOP 
    r = session.get("https://www.haagendazs.us/all-shops")
    soup = BeautifulSoup(r.text, "lxml")
    links= soup.find("div",{"class":"view-content"}).find_all("a")
    for link in links:
        page_url = "https://www.haagendazs.us/"+link['href']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("h1",{"itemprop":"name"}).text.strip()
        street_address = soup1.find("p",{"itemprop":"streetAddress"}).text.strip()
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
        zipp = soup1.find("span",{"itemprop":"addressRegion"}).find_next("span").text.strip()
        latitude = soup1.find(lambda tag: (tag.name == "script") and "lat" in tag.text).text.split('lat:"')[1].split('",')[0]
        longitude = soup1.find(lambda tag: (tag.name == "script") and "lat" in tag.text).text.split('long:"')[1].split('",')[0]
        if soup1.find("div",{"class":"office-hours"}):
            hours = " ".join(list(soup1.find("div",{"class":"office-hours"}).stripped_strings))
        else:
            hours = "<MISSING>"

        store = []
        store.append("https://www.haagendazs.us")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("Shop")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        # logger.info("data ====="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        store = [x.strip() if type(x) == str else x for x in store]
        yield store
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
