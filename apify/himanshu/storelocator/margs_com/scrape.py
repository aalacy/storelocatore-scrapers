import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.margs.com"
    r = requests.get("https://www.margs.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for link in soup.find_all("a",{"class":"ca1link"}):
        if base_url == link["href"]:
            continue
        state_request = requests.get(link["href"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,'lxml')
        geo_locations = []
        for geo in state_soup.find_all("a",{"href":re.compile("/@")}):
            geo_locations.append(geo["href"])
        for location in state_soup.find_all("div",{"data-width":"247"}):
            location_link = location.find("a")["href"]
            if "https://www.margs.com/ellsworth" == location_link:
                continue
           
            location_request = requests.get(location_link,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            try:
                phone = location_soup.find("a",{"data-type":"phone"})['data-content']
            except:
                phone = location_soup.find(lambda tag: (tag.name == "span") and "Phone:" in tag.text).text.replace("Phone:","").strip()

            if location_soup.find("span",text=re.compile("OPENING")):
                continue
            if location_soup.find("span",text=re.compile("Coming Soon")):
                continue
            location_details = []
            for details in location_soup.find_all("h2",{"class":"font_2"}):
                location_details.extend(list(details.stripped_strings))
            for i in range(len(location_details)):
                if location_details == "ONLINE ORDERING" or location_details[i] == "LOCATION DETAILS":
                    location_details = location_details[:i]
                    break
            location_details[3] = location_details[3].replace("\xa0"," ")
            if "We are\xa0open for" in location_details[2]:
                del location_details[2:4]
            store = []
            hour1 =" ".join(location_details[7:]).replace("\xa0"," ").replace("–","-").split("ONLINE ORDERING")[0].split("Kitchen hours")[0].split("ORDER TAKEOUT")[0].split("DELIVERY SERVICES")[0].strip()
            hour2 =hour1.replace(' for a siesta','').replace('We are open for dine-in! Margaritas is now offering online ordering for both curbside pickup and delivery and our outside patio is open!','').replace('Reservations are required by calling us at (732) 549-0444. ​','').replace('We are open for dine-in! Margaritas is now offering online ordering for both curbside pickup and delivery. ​','')
            hour3=hour2.replace('We are now open for outdoor dining! Reservations are required by calling us at (732) 505-1400. ​ ​','').replace(' We are open for dine-in & takeout! Hola Amigos!  We are open for dine-in and takeout! ​ For dine-in reservations are required.  Please call us at (603) 893-0110 to speak with a team member. ​ For takeout orders, please call us at (603) 893-0110. We will only be accepting credit card payments over the phone for the safety of our guests and staff. ​ View our current menu: ​ ​ ​ ​ Please review our dining policies to ensure the safety of our guests and staff: 1.  Party limit of 6. 2.  All guests must wear a mask when not seated at their table. 3.  If you have been exposed to COVID-19 recently or have symptoms of COVID-19 (fever, aches, cough, shortness of breath, difficulty breathing, headache, chills or loss of taste/smell), please help us keep everyone safe by staying home and planning to visit us when you are well.','')
            hour4 = hour3.replace('Hola Amigos!  We are open for dine-in and takeout! For dine-in, reservations are not required but we do accept reservations by calling us at (603) 647-7717 to speak with a team member. ​ For takeout orders, we will only be accepting credit card payments over the phone for the safety of our guests and staff. View our current menu:','').replace('FOLLOW US WRITE A REVIEW MONDAY INDUSTRY/RETAIL MONDAY HAPPY HOUR LATE NIGHT Promotions cannot be combined with any other offers or discounts.','')
            hour = hour4.replace('We are open for dine-in & takeout! ​ ','')
            store.append("https://www.margs.com")
            store.append(location_details[1])
            store.append(location_details[2])
            store.append(location_details[3].split(",")[0])
            store.append(" ".join(location_details[3].split(",")[1].split(" ")[1:-1]))
            store.append(location_details[3].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(geo_locations[0].split("/@")[1].split(",")[0])
            store.append(geo_locations[0].split("/@")[1].split(",")[1])
            del geo_locations[0]
            store.append(hour)
            if store[-1] == "":
                store[-1] = "<MISSING>"
            store.append(location_link)
            yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
