import csv
from bs4 import BeautifulSoup
import re
import json
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('truevaluecompany_com')


session = SgRequests() 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://truevalue.com/"
    location_url = "https://stores.truevalue.com/"
    r = session.get(location_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = (soup.find_all("div",{"class":"itemlist"}))
    for i in data:
        link_1 = (i.find("a")['href'])
        r1 = session.get(link_1,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        data1 = (soup1.find_all("div",{"class":"itemlist"}))
        for i1 in data1:
            link_2 = (i1.find("a")['href'])
            r2 = session.get(link_2,headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            data2 = (soup2.find_all("script",{"type":"application/ld+json"})[-1]).text
            json_data = json.loads(data2)
            link_3 = (json_data['url'])
            # logger.info(link_3)
            r3 = session.get(link_3,headers=headers)
            soup3 = BeautifulSoup(r3.text,"lxml")
            try:
                data_3 = (soup3.find_all("script",{"type":"application/ld+json"})[-1]).text.replace(" //if applied, use the tmpl_var to retrieve the database value","").replace("  // starts services list","").replace(', ]',' ]')
                data3 = re.sub("\s+"," ", str(data_3))
                json_data1 = json.loads(data3)
                location_name = json_data1['name']
                street_address = (json_data1['address']['streetAddress'])
                city = (json_data1['address']['addressLocality'])
                state = (json_data1['address']['addressRegion'])
                zipp = (json_data1['address']['postalCode'])
                country_code = (json_data1['address']['addressCountry'])
                store_number = json_data1['@id']
                phone = json_data1['telephone']
                location_type = json_data1['@type']
                latitude = (json_data1['geo']['latitude'])
                longitude = (json_data1['geo']['longitude'])
                hours_of_operation = str(json_data1['openingHoursSpecification']).replace("'","").replace("{","").replace("}","").replace("[","").replace("]","").replace("opens","").replace("closes","").replace("OpeningHoursSpecification","").replace("dayOfWeek","").replace("@type","").replace(": , : ","").replace(", : - "," - ").replace(", :","").replace("Monday, , Tuesday, , Wednesday, , Thursday, , Friday, , Saturday, , Sunday, ","<MISSING>")
                page_url =json_data1['url']
            except:
                location_name = soup3.find("meta",{"property":"og:title"})['content']
                street_address = soup3.find("meta",{"property":"business:contact_data:street_address"})['content']
                city = soup3.find("meta",{"property":"business:contact_data:locality"})['content']
                state = soup3.find("meta",{"property":"business:contact_data:region"})['content']
                zipp = soup3.find("meta",{"property":"business:contact_data:postal_code"})['content']
                country_code = soup3.find("meta",{"property":"business:contact_data:country_name"})['content']
                phone = soup3.find("meta",{"property":"business:contact_data:phone_number"})['content']
                location_type = "HardwareStore"
                latitude = soup3.find("meta",{"property":"place:location:latitude"})['content']
                longitude = soup3.find("meta",{"property":"place:location:longitude"})['content']
                hours_of_operation = soup3.find("div",{"id":"all_hours"}).text.replace("\n","").replace("\r","").replace("\t","").replace("PM","PM, ").strip().lstrip().rstrip().replace("Sun","Sunday").replace("Sat","Saturday").replace("Fri","Friday").replace("Mon","Monday").replace("Tue","Tuesday").replace("Wed","Wednesday").replace("Thu","Thurseday")
                page_url =soup3.find("meta",{"property":"business:contact_data:website"})['content']
                store_number = page_url.split("/")[-1]
                # logger.info("---------------------done data---------------------------")

            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            store = [x.strip() if type(x) == str else x for x in store]
            yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
