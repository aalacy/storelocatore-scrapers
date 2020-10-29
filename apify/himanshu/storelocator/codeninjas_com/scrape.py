
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('codeninjas_com')


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
    json_data = session.get("https://services.codeninjas.com/api/locations/queryarea?latitude=37.09024&longitude=-95.712891&includeUnOpened=false&miles=5117.825778587137",headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).json()
    for data in json_data:
        if data['status'] != "OPEN":
            continue
        street_address = data["address1"] 

        if data['address2']:
          street_address += " " + data['address2'] 
           

        location_name = data["name"]
        city = data['city']
        zipp = data['postalCode']
        state = data['state']['code']
        if "GB" in data['countryCode']:
            continue
        longitude = data['longitude']
        latitude = data['latitude']
        page_url ="https://www.codeninjas.com/"+ data['cnSlug']
        
        countryCode = data['countryCode']
        
        soup1 = bs(session.get(page_url,headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).text,'lxml')
        
        phone = data['phone']
        hours = ""
        
        try:
            for index,data in enumerate(soup1.find("div",{"id":"centerHours"}).find_all("ul",{"class":"list mb-0"})):
                if index==0:
                    hours = "Center Hours " + " ".join(list(data.find("li").stripped_strings)).split(" (Summer Hours May Vary)")[0].split("; Birthday")[0].split("or by appointment")[0]
                else:
                    hours =hours + " Student Hours " + " ".join(list(data.find("li").stripped_strings)).split(" (Summer Hours May Vary)")[0].split("; Birthday")[0].split("or by appointment")[0]
        except:
            hours=""
     
        store_number = "<MISSING>"
        store = []
        store.append("https://www.codeninjas.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(countryCode)
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        hours = re.sub(r"\s+", " ", hours)
        if "https://www.codeninjas.com/ca-folsom" in page_url or "https://www.codeninjas.com/ca-rocklin" in page_url:
            hours ="<MISSING>"
        if "Center Hours Open By Appointment Only Student Hours Open By Appointment Only" in hours or "Center Hours Temporarily Shuttered due to COVID-19 Student Hours Temporarily Shuttered due to COVID-19" in hours or "Center Hours Stay safe! Currently offering Virtual sessions Student Hours Please check our Summer Camps schedule" in hours or "Center Hours Virtual Camps available. Tentative re-open in August Student Hours Virtual Camps available. Tentative re-open in August" in hours or "Center Hours By Appt Student Hours By Appt" in hours or "Center Hours Coming Real Soon ! Student Hours Coming Real Soon !" in hours or "Center Hours  (due to COVID-19) Student Hours  (due to COVID-19)" in hours or "Center Hours Temporarily Closed - Email for online options Student Hours Temporarily Closed - Email for online options" in hours or "Center Hours  (due to COVID-19) Student Hours  (due to COVID-19)" in hours or "Center Hours  due to COVID-19 Student Hours  due to COVID-19" in hours:
            hours ="<MISSING>"
        store.append(hours.replace("By Appointment Only",'').replace("Center Hours By appointment only Student",'Student').replace("Center Hours Monday-Friday (by appointment)",'').replace("Center Hours By appointments only.",'').replace("/",' ').replace(": Mon",'Mon').replace("To Schedule Tours https://calendly.com/mncodeninjas",'').replace("Center Hours By Appointment Student",'Student').replace("s only. Student",'Student').replace("by Appointment Student",'Student').replace("*See Camp Schedule for Camp hours ","Student").replace("|",' ').replace("Student Hours CREATE Appointments:",'Student Hours').replace("Appointments Only Student","Student").replace("(Note: Last check-in one hour before close)",'').replace("By-Appointment only for Drop-Ins (Due to Covid-19)",'').replace("Center Hours  Student Hours","Student Hours").replace("Center Hours By appointment Student",'Student').replace(")","").replace("(","").replace("Student Hours By Appointment",'').replace("Virtual",'').replace("Center Hours By Appointment only Student",'Student').replace(" To Schedule Tours https:  calendly.com mncodeninjas",'').replace("*See Camp Schedule for Camp hours",'').replace("Appointments Only",'').strip())
        store.append(page_url if page_url else "<MISSING>")     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",store)
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

