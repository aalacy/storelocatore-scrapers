import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
 
def fetch_data():
       
     

        soup = bs(session.get("https://www.regency-pacific.com/our-communities").text, "lxml")

        for link in soup.find("div",{"class":"directory-table full"}).find_all("a",{"class":"u-url"}):

            page_url = link['href']
            location_soup = bs(session.get(page_url).text, "lxml")

            json_data = json.loads(location_soup.find(lambda tag:(tag.name == "script") and "PostalAddress" in tag.text).text)
        
            location_name = json_data['name']
            street_address = json_data['address']['streetAddress']
            city = json_data['address']['addressLocality']
            state = json_data['address']['addressRegion']
            zipp = json_data['address']['postalCode']
            latitude = json_data['geo']['latitude']
            longitude = json_data['geo']['longitude']
            phone = json_data['telephone']

            hours = ""
            for day in json_data['openingHoursSpecification']:

                hours += " " + day['dayOfWeek'][0] +" "+ datetime.strptime(day['opens'], "%H:%M").strftime("%I:%M %p") + " - " + datetime.strptime(day['closes'], "%H:%M").strftime("%I:%M %p") + " "
           
            store = []
            store.append("https://www.regency-pacific.com")
            store.append(location_name) 
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append( latitude )
            store.append( longitude)
            store.append(hours)
            store.append(page_url)
            yield store

def scrape():
 data = fetch_data()
 write_output(data)
scrape()

