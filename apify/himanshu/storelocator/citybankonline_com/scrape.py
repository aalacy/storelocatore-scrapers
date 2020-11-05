import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('citybankonline_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    adressessess=[]
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.city.bank"
    r = session.get("https://www.city.bank/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for dt in str(soup.find_all("div",{"style":"float: left; width: 25%; min-width: 200px;"})[-2]).split("Additional ATM Locations")[-1].split("ATM"):
        soup1 = BeautifulSoup(dt,"html5lib")
        addr = list(soup1.stripped_strings)
        if "Lubbock" in addr:
            continue
        name = addr[0].replace("102 E. Main","Forney")
        if "Forney" in addr:
            del addr[-1]
        if "Levelland" in addr:
            del addr[-1]
        city = addr[-1].split(",")[0]
        state = addr[-1].split(",")[1].strip().split( )[0]
        zipp = addr[-1].split(",")[1].strip().split( )[1]
        address = addr[-2]
        store = []
        store.append("https://citybankonline.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("ATM")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store




    for location in soup.find("div",{'class':"sf_cols"}).find_all("a",{"href":re.compile("/locations/")}):
        # logger.info(base_url + location["href"])
        page1= base_url + location["href"]
       
        try:
            location_request = session.get(page1.replace("https://www.city.bankhttps://staging.city.bank/locations/mortgage-southlake",'https://www.city.bank/locations/mortgage-southlake'),headers=headers)
        except:
            continue
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{"class":"main-content"}).find('div',{'class':"sfContentBlock"}).stripped_strings)
        type_data = list(location_soup.find("div",{"class":"sf_colsOut col-right"}).stripped_strings)
        if 'ATM' in type_data:
            location_type = "Branch + ATM"
        elif 'mortgage' in page1:
            location_type = "Mortgage Service"
        else:
            location_type = "Branch Only"
            

        # location_name = location_details
        
        if location_details ==[]:
            continue
        
        if location_details[0]=="City Bank":
            del location_details[0]
        

        if location_details[-1]=="<":
            del location_details[-1]
            
        if location_details[-1]=="ATM":
            del location_details[-1]

  
        
        if "FAX:" in location_details[-1]:
            del location_details[-1]
        if "Fax:" in location_details[-1]:
            del location_details[-1]

        if "City Bank Mortgage"==location_details[0]:
            del location_details[0]

        
        phone = location_details[-1].replace("Phone:",'').replace("Phone:",'').strip().replace("PH:",'')

        
        
        
        ignore_data = ['214 S. Main','210 N. Oak','1501 W. University Blvd']
        if location_details[0] in ignore_data:
            
            address = location_details[0]
            city = location_details[1].split(",")[0]
            state = location_details[1].split(",")[1].strip().split(" ")[0]
            zipp = location_details[1].split(",")[1].strip().split(" ")[1]
        else:
            address = " ".join(location_details[:-2])
            city = location_details[-2].replace("PO Box 410","Monahans, TX 79756").replace("PO Drawer K",'Kermit, TX 79745').split(",")[0]
            state = location_details[-2].replace("PO Box 410","Monahans, TX 79756").replace("PO Drawer K",'Kermit, TX 79745').split(",")[-1].strip().split( )[0]
            zipp = location_details[-2].replace("PO Box 410","Monahans, TX 79756").replace("PO Drawer K",'Kermit, TX 79745').split(",")[-1].strip().split( )[-1]
        
        
        hours = " ".join(list(location_soup.find("div",{'class':"sf_colsOut col-left"}).stripped_strings))
        # logger.info(phone)
        geo_location = location_soup.find_all("iframe")[-1]["src"]
        store = []
        store.append("https://citybankonline.com")
        store.append(location_soup.find("h1",{"class":"hero"}).text.strip())
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type)
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(hours.replace("\t"," "))
        store.append(base_url + location["href"])
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in adressessess :
            continue
        adressessess.append(store[2])
        # logger.info(store)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
