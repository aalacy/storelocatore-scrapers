import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip
session = SgRequests()
import base64

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    
    addressess123 = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 5
    current_results_len = 0     
    zip_code = search.next_zip()
    while zip_code:
        #print(zip_code)
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        result_coords = []
        zip_bytes = zip_code.encode('ascii')
        base64_bytes = base64.b64encode(zip_bytes)
        base64_zip = base64_bytes.decode('ascii')
        # print(base64_zip)
        base_url = "https://www.onestop.co.uk/"
        data = {
            "action": "findstockists",
            "searchfor": str(base64_zip),
        }

        r = session.post("https://www.onestop.co.uk/wp-admin/admin-ajax.php",data=data)
        try:
            json_data = r.json()
        except Exception as e :
            # print(e)
            continue
        # current_results_len = len(json_data)  
        if "results" in json_data["message"]:
            for  loc in json_data["message"]["results"]:
                current_results_len = len(loc)
                try:
                    location_name = loc["location"]["name"]
                except:
                    location_name = "<MISSING>"
                try:
                    store_number = loc["location"]["altIds"]["oneStopStoreNumber"]
                except:
                    store_number = "<MISSING>"
                country_code = "UK"
                try:
                    state = loc["location"]["region"]["isoSubdivision"]
                except:
                    state = "<MISSING>"

                if len(loc["location"]["contact"]["address"]["lines"]) > 1:
                    street_address = loc["location"]["contact"]["address"]["lines"][0]["text"]+" "+loc["location"]["contact"]["address"]["lines"][1]["text"].strip()
                else:
                    street_address = loc["location"]["contact"]["address"]["lines"][0]["text"]
                try:
                    city = loc["location"]["contact"]["address"]["town"]
                except:
                    city = "<MISSING>"
                zipp=loc["location"]["contact"]["address"]["postcode"]
                try:
                    phone=loc["location"]["contact"]["phoneNumbers"][0]["number"]
                except:
                    phone = "<MISSING>"
                try:
                    latitude = loc["location"]["geo"]["coordinates"]["latitude"]
                    longitude = loc["location"]["geo"]["coordinates"]["longitude"]
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                try:
                    location_type = loc["location"]["classification"]["type"]
                except:
                    location_type = loc["location"]["classification"]["category"]
                try:
                    hours_of_operation = "Monday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["mo"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["mo"]["close"] +"   " +\
                                "Tuesday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["tu"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["tu"]["close"] +"   " +\
                                "Wednesday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["we"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["we"]["close"] +"   " +\
                                "Thurday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["th"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["th"]["close"] +"   " +\
                                "Friday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["fr"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["fr"]["close"] +"   " +\
                                "Saturday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["sa"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["sa"]["close"] +"   " +\
                                "Sunday: "+loc["location"]["openingHours"][0]["standardOpeningHours"]["su"]["open"] +" - "+ loc["location"]["openingHours"][0]["standardOpeningHours"]["su"]["close"] 
                except:
                    hours_of_operation = "<MISSING>"           
                page_url = "https://www.onestop.co.uk/store/?store="+str(zipp).lower().replace(" ","").strip()  
                # r = session.get(page_url)
                # soup = BeautifulSoup(r.text, "lxml")
                # hours = " ".join(list(soup.find("p",{"class":"opening-times"}).stripped_strings))
        
                result_coords.append((latitude,longitude))
                store = [base_url, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, str(latitude), str(longitude), hours_of_operation,page_url]
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in  store]
                if (str(store[2])+str(store[-3])+str(store[-1]))  in addressess123:
                    continue
                addressess123.append(str(store[2])+str(store[-3])+str(store[-1]))
                # print("data =="+str(store))
                yield store

        if current_results_len < MAX_RESULTS:
    
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        
       
        
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
