
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
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
    data = session.get("https://services.codeninjas.com/api/locations/queryarea?latitude=37.09024&longitude=-95.712891&includeUnOpened=false&miles=5117.825778587137",headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).json()
    for data in data:
        address2=''
        if data['address2']:
           address2= data['address2']
        street_address =data["address1"]+' '+address2
        location_name = data["name"]
        city = data['city']
        zipp = data['postalCode']
        state = data['state']['code']
        if "GB" in data['countryCode']:
            continue
        longitude =data['longitude']
        latitude =data['latitude']
        page_url ="https://www.codeninjas.com/"+ data['cnSlug']
        countryCode = data['countryCode']
        phone=''
        soup1 = bs(session.get(page_url,headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}).text,'lxml')
        phone = data['phone']
        hours=''
        try:
            hours=" ".join(list(soup1.find("div",{"id":"centerHours"}).find("ul",{"class":"list mb-0"}).stripped_strings)).replace("Program hours may vary. Contact us for details.",'')
        except:
            hours=''
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
        store.append(hours.replace("             ",' ').replace('     ','').replace("Monday-Friday (by appointment)","<MISSING>").replace(" by Appointment",'').replace("By Appointment",'<MISSING>').replace("   *See Camp Schedule for Camp hours",'').replace("(Note: Last check-in one hour before close)",'').replace("By Appt",'<MISSING>').replace("Coming Real Soon !","<MISSING>").replace("By Appointment Only (due to COVID-19)","<MISSING>").replace(" // ",'').replace("/",' ').replace(" | ",' ').replace(";           ",' ').replace("            ",' ').replace("     ",' ').replace("<MISSING> Only",'<MISSING>').replace("By appointment only","<MISSING>").replace("By appointments only.",'<MISSING>').replace("Regular Hours  ",'').replace("<MISSING> Only: ",'').replace("Stay safe! Currently offering Virtual sessions",'').replace("Virtual Camps available. Tentative re-open in August",'').replace(",           ",'').replace("<MISSING> Only (due to COVID-19)",'').replace("; Birthday parties on Saturday afternoons",'').replace("Summer Hours:  ",'').replace("<MISSING> (due to COVID-19)",'').replace("<MISSING>: ",'').replace(" (<MISSING>)",'').replace("To Schedule Tours https:  calendly.com mncodeninjas",'').replace("only",'').replace(" (Summer Hours May Vary)",'').replace("; Birthday parties on Saturday afternoons",'').replace("By appointment",'').replace("Open <MISSING>",'<MISSING>').replace("; Birthday Parties on Weekends",'').replace(" Appointments Only",'').replace("Virtual (",'').replace(")",'').replace("  or by appointment",'').replace("Saturday 10am-1pm <MISSING>",'Saturday 10am-1pm').replace(" on appointment basis",'').replace("; Birthday Parties on Weekends",'').replace(" - Email for online options",'').replace("; or by appointment",'').replace("Temporarily Shuttered due to COVID-19",'').split("or")[0].replace("Temp",''))
        store.append(page_url if page_url else "<MISSING>")     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
       # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ",store)
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
