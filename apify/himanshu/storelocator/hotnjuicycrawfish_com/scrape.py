from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    base_link = "http://hotnjuicycrawfish.com/locations"
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent': user_agent}
    req = session.get(base_link, headers=headers)
    try:
        base = BeautifulSoup(req.text, "lxml")
    except (BaseException):
        pass
    items = base.find('div',{"class":"w-layout-grid grid"})
    b = (items.find_all("a"))
    for i in b:
        page_link = "http://hotnjuicycrawfish.com" + i['href']
        req1 = session.get(page_link, headers=headers)
        base1 = BeautifulSoup(req1.text, "lxml")
        street_address1 = (base1.find('div',{"class":"sub-text updates info _2-lines"}).text)
        try:
            try:
                phone = (base1.find_all('div',{"class":"sub-text updates info"})[-1].text)
            except:
                phone = (base1.find('div',{"class":"sub-text updates info bottom"}).text)
        except:
            phone = "702-489-3220"
        hours_of_operation = (base1.find('div',{"class":"update pad-bottom"}).text.replace("\n","").replace("\r","").replace("\t","").replace("day","day ").replace("Hours","").replace("pm","pm ").strip().replace("HOURS",""))
        zipp = (street_address1.split(",")[-1].split(" ")[-1].replace("NY11354","11354").replace("NY10011","10011").replace("Nevada89109","89109"))
        state = (street_address1.split(",")[-1].strip().split(" ")[0].replace("NY11354","NY").replace("NY10011","NY").replace("Nevada89109","Nevada"))
        city = (base1.find('title').text.split("|")[0].split(",")[0].replace("Manhattan","New York").replace("Orange County ","Fountain Valley").replace("Washington DC","Washington").strip())
        location_name = (base1.find('h1',{"data-ix":"slide-in-inner-big-text-on-load"}).text.strip())
        location_type = "<MISSING>"
        street_address = street_address1.replace(state,"").replace(city,"").replace(zipp,"").replace(phone,"").replace(",","").strip().replace("Las Vegas","").replace(" Fountain Valley","").replace(" NW Washington","")
        try:
            latitude = (base1.find('div',{"class":"sub-text updates info _2-lines"}).find("a")["href"].split("Crawfish/@")[1].split(",")[0])
            longitude = (base1.find('div',{"class":"sub-text updates info _2-lines"}).find("a")["href"].split("Crawfish/@")[1].split(",")[1])
        except:
            longitude = base1.find("iframe")['src'].split("!2d")[1].split("!3d")[0]
            
            latitude = base1.find("iframe")['src'].split("!3d")[1].split("!2m")[0]
        if "11354" in zipp:
            phone = "718-358-2729"
        store = []
        store.append("http://hotnjuicycrawfish.com/")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_link if page_link else "<MISSING>")
        if store[2] in address :
            continue
        address.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
