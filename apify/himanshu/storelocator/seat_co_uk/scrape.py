
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('seat_co_uk')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['gb'])
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    current_results_len = 0
    zip_code = search.next_zip()
    base_url = "https://www.seat.co.uk"
    while zip_code:
        result_coords = []
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        soup = bs(session.get("https://dealersearch.seat.com/xml?app=seat-gbr&max_dist=0&city="+str(zip_code)+"&_=1591338622355").content, "lxml")
        current_results_len = len(soup.find_all("partner"))
        for data in soup.find_all("partner"):
            
            location_name = data.find_all("name")[1].text
            # logger.info(location_name)
            
            street_address = data.find("street").text
            city = data.find("city").text
            state =data.find("region_text").text
            zipp = data.find("zip_code").text
            phone = data.find("phone1").text
            if street_address == "367 Bath Road":
                phone = "01753 628300"
            latitude = data.find("latitude").text
            longitude = data.find("longitude").text
            page_url = "https://"+data.find("url").text.lower()
            if page_url == "https://www.seat.co.uk/dealer/coupers-seat.co.uk":
                page_url = "https://www.seat.co.uk/dealer/coupers-seat.html"
            if page_url == "https://www.seat.co.uk/dealer/dealer/capitol-seat-newport.html":
                page_url = "https://www.seat.co.uk/dealer/capitol-seat-newport.html"
            store_number = "<MISSING>"
            hours="<MISSING>"
            store = []
            try:
                
                soup1 = bs(session.get(page_url).content, "lxml")
                hours = " ".join(list(soup1.find(lambda tag: (tag.name == "p" or tag.name == "h2") and "Opening Hours" in tag.text.strip()).next_element.next_element.next_element.next_element.stripped_strings))
            except:
                hours="<MISSING>"
            if page_url.lower() == "https://www.seat-store.co.uk/seat-store-lakeside.html":

                page_url = "https://www.lakeside.seat-store.co.uk/"
                headers = {
                    'Origin': str(page_url),
                }
                # data = session.get("https://api.lakeside.seat-store.co.uk/api/v1/config", headers=headers).json()['content']['translations']['en_GB']['departments']['store']
                # **************************************************************************************************
                # 2020-06-18: When running in Docker, the host name api.lakeside.seat-store.co.uk doesn't resolve
                #   when getting it with requests or even wget. Strangely tools like dig and nslookup resolve it fine
                #   from inside the container. Perhaps the problem is related to it pointing to a wildcard subdomain 
                #   (*.seat-prod.motortrak.com).
                #   The solution was to change the API call to api.lakeside.seat-prod.motortrak.com. 
                #   Also the same goes for the below section that was accessing api.whitecity.seat-store.co.uk ... 
                #   Had to change that to api.whitecity.seat-prod.motortrak.com
                # **************************************************************************************************
                data = session.get("https://api.lakeside.seat-prod.motortrak.com/api/v1/config", verify=False, 
                                   headers=headers).json()['content']['translations']['en_GB']['departments']['store']
                hours = ''
                for key,value in data['opening'].items():
                    hours+= " "+key.capitalize() +" "+ value['open']+" - "+value['close']+" "
                

            if page_url.lower() == "https://www.seat-store.co.uk/seat-store-white-city.html":

                page_url = "https://www.whitecity.seat-store.co.uk/"
                headers = {
                    'Origin': str(page_url),
                }
                # data = session.get("https://api.whitecity.seat-store.co.uk/api/v1/config", headers=headers).json()['content']['translations']['en_GB']['departments']['store']
                data = session.get("https://api.whitecity.seat-prod.motortrak.com/api/v1/config", verify=False,
                                   headers=headers).json()['content']['translations']['en_GB']['departments']['store']
                hours = ''
                for key,value in data['opening'].items():
                    hours+= " "+key.capitalize() +" "+ value['open']+" - "+value['close']+" "


            result_coords.append((latitude,longitude))
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("UK")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours.strip())
            store.append(page_url if page_url else "<MISSING>")     
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # logger.info(store)
            yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()


"https://www.seat.co.uk/dealer/coupers-seat.html"
"https://seat.co.uk/dealer/coupers-seat.co.uk"
