import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip

session = SgRequests()

 
 
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    addressess123 = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["gb"])
    MAX_RESULTS = 25
    MAX_DISTANCE = 10
    current_results_len = 1
    zip_code = search.next_zip()
    base_url = "https://www.onestop.co.uk/"
    while zip_code:
        #print(zip_code)
        
        result_coords = []
        page_url = "https://www.onestop.co.uk/store/?store="+str(zip_code)
        r = session.get("https://www.onestop.co.uk/store/?store="+str(zip_code))
        soup = BeautifulSoup(r.text, "lxml")
        location_name = soup.find("div",{"class":"col col3"}).find("h3").text.strip()
        addr = list(soup.find("div",{"class":"col col3"}).find_all("p")[0].stripped_strings)

        street_address = " ".join(addr[:-2])
        city = addr[-2]
        state = "<MISSING>"
        zipp = addr[-1]
        store_number = "<MISSING>"
        phone1 = soup.find("div",{"class":"col col3"}).find_all("p")[1].text.strip()
        if phone1:
            phone = phone1
        else:
            phone = phone1
        location_type = "Store"
        country_code = "UK"
        latitude = soup.find("div",{"id":"store-map"})['data-lat']
        longitude = soup.find("div",{"id":"store-map"})['data-lng']
        hours = " ".join(list(soup.find("p",{"class":"opening-times"}).stripped_strings))
     

        # print(page_url)
        result_coords.append((latitude,longitude))
        store = [base_url, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, str(latitude), str(longitude), hours,page_url]
        
        if store[2]  in addressess123:
            continue
        addressess123.append(store[2])
        yield store
       # print(store)

        if current_results_len < MAX_RESULTS:
    
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()      

        
      

        
       
        #
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
