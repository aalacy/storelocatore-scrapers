import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import unicodedata
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    r = session.get("https://placesws.adidas-group.com/API/search?brand=adidas&geoengine=google&method=get&category=store&latlng=39.491751305282705%2C-471.94216860348604%2C15000&page=1&pagesize=50000&fields=name%2Cstreet1%2Cstreet2%2Caddressline%2Cbuildingname%2Cpostal_code%2Ccity%2Cstate%2Cstore_o+wner%2Ccountry%2Cstoretype%2Clongitude_google%2Clatitude_google%2Cstore_owner%2Cstate%2Cperformance%2Cbrand_store%2Cfactory_outlet%2Coriginals%2Cneo_label%2Cy3%2Cslvr%2Cchildren%2Cwoman%2Cfootwear%2Cfootball%2Cbasketball%2Coutdoor%2Cporsche_design%2Cmiadidas%2Cmiteam%2Cstella_mccartney%2Ceyewear%2Cmicoach%2Copening_ceremony%2Coperational_status%2Cfrom_date%2Cto_date%2Cdont_show_country&format=json&storetype=",headers=headers)
    soup = BeautifulSoup(r.text,'html5lib')
    location_data = json.loads(str(soup).split("<body>")[1].split("</body>")[0].replace("<br>","").replace("\n",""))['wsResponse']["result"]
    for store_data in location_data:
        if store_data["country"] == "US" or store_data["country"] == "CA":
            store = []
            store.append("https://www.adidas.com")
            store.append(store_data["name"])
            address = ""
            if "street1" in store_data:
                address = address + " " + store_data["street1"]
            if "street2" in store_data:
                address = address + " " + store_data['street2']
            if "addressline" in store_data:
                address = address + " " + store_data["addressline"] 
            store.append(address.replace("&amp;","&").replace(", San Antonio Tx, 78209","").replace("RICHFIELD, UTAH 84701","<MISSING>"))
            store.append(store_data["city"])
            st_list = ['British','Colombia','BRITISH','COLUMBIA','BRITISH COLUMBIA','British Colombia']
            try:
                state = store_data["state"]
            except:
                state = "<MISSING>"
            if state in st_list:
                state = "BC"
            store.append(state if state else "<MISSING>")
            if 'postal_code' in store_data:
                if 'US' in store_data["country"]:
                    try:
                        temp_zipp = store_data["postal_code"].split(",")[1].strip().replace("VA","")
                    except:
                        temp_zipp = store_data["postal_code"].split(" ")[-1].replace("VA","")
                    zipp = temp_zipp[:5].replace("TX 77","77056").replace("CA 90","90045").replace("CA 92","92626").replace("MI 48","48242").replace("NC 28","28204").replace("1224","98944")
                else:
                    zipp = store_data["postal_code"].upper().replace("BC ","")
            else:
                zipp = "<MISSING>"
            store.append(zipp if zipp else "<MISSING>")
            store.append(store_data["country"])
            store.append(store_data["id"])
            location_request = session.get("https://placesws.adidas-group.com/API/detail?brand=adidas&method=get&category=store&objectId=" + str(store_data["id"]) + "&format=json",headers=headers)
            soup1 = BeautifulSoup(location_request.text,'html5lib')
            location_data2 = json.loads(str(soup1).split("<body>")[1].split("</body>")[0].replace("<br>","").replace("\n",""))
            if location_data2["wsResponse"]["result"] == []:
                continue
            location_data = location_data2["wsResponse"]["result"][0]
            if 'phone' in location_data:
                phone = location_data["phone"].replace("001 (0)","").replace("+1","").replace("001 - ","").lstrip("1 ").replace("/ 8525","").replace("(0) ","").replace("001 - ","").replace("+ 1","").strip()
                phone = phone.replace("x6","").replace("x2","").replace("x1","").replace("x5","").replace("x4","").replace("x3","").replace("604-689-44","<MISSING>").replace(" / 9004","").replace("001- ","")
            else:
                phone = "<MISSING>"
            store.append(phone if phone else "<MISSING>")
            store.append(location_data['storetype'] if 'storetype' in location_data else "<MISSING>")
            try:
                try:
                    lat = location_data["latitude_bing"]
                    lng = location_data["longitude_bing"]
                except KeyError:
                    lat = location_data["latitude_google"]
                    lng = location_data["longitude_google"]
            except:
                lat = "<MISSING>"
                lng = "<MISSING>"
            if lat == "0":
                lat = "<MISSING>"
            if lng == "0":
                lng = "<MISSING>"
                
            if lat=="38":
                lat = "38.001954"
            store.append(lat)
            store.append(lng)
            hours = ""
            for key in location_data:
                if "openinghours" in key:
                    hours = hours + " " + key.split("_")[-1] + " " + location_data[key]
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<MISSING>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
