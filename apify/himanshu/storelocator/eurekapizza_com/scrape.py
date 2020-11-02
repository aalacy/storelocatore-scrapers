import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import io
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    base_url = "https://www.eurekapizza.com/order-now"
    address = []
    # h = session.get('https://orderonline.granburyrs.com/slice/account/initialize?account=335').json()
    # hh = []
    # for hours_list in  h['restaurants']:
    #     h1 = hours_list['hours']['Delivery']['ranges']
    #     hh1= "Monday " + h1['Monday']['startString'] +"-" + h1['Monday']['endString'] + ","+"Tuesday " + h1['Tuesday']['startString'] +"-" + h1['Tuesday']['endString'] + ","+"Wednesday " + h1['Wednesday']['startString'] +"-" + h1['Wednesday']['endString'] + ","+"Thursday " + h1['Thursday']['startString'] +"-" + h1['Thursday']['endString'] + " "+"Friday " + h1['Friday']['startString'] +"-" + h1['Friday']['endString'] + ","+"Saturday " + h1['Saturday']['startString'] +"-" + h1['Saturday']['endString'] + ","+"Sunday " + h1['Sunday']['startString'] +"-" + h1['Sunday']['endString']
    #     hh.append(hh1)
    soup = bs(session.get(base_url, headers=headers).text,"lxml")
    data = soup.find_all("span",{"class":"caption-inner"})
    for i in data:
        data1 = (i.find("a")['href'])
        link = "https://www.eurekapizza.com/"+str(data1)
        soup = bs(session.get(link, headers=headers).text, "lxml")
        data = soup.find("div",{"class":"dmRespCol large-4 medium-4 small-12 u_1291578465"}).div
        latitude = (data['lat'])
        longitude = (data['lon'])
        st_data = data['geocompleteaddress']
        street_address = (st_data.split(",")[0])
        city = (st_data.split(",")[1].strip())
        country_code = (st_data.split(",")[-1].strip())
        location_name = (data1.replace("/","").replace("-"," ").replace("---"," ").replace("   "," ").capitalize())
        phone = soup.find("div",{"class":"u_1763968975 dmNewParagraph hide-for-small"}).text.strip()
        zipp = soup.find("div",{"class":"u_1007316953 dmNewParagraph"}).text.strip().split(",")[1].strip().split(" ")[1]
        state = soup.find("div",{"class":"u_1007316953 dmNewParagraph"}).text.strip().split(",")[1].strip().split(" ")[0]
        if zipp =="72704":
            city = "Fayetteville"
            street_address = "2920 W Martin Luther King"
        if location_name == 'Springdale thompson st':
            city = "Springdale"
            street_address = "1503 S Thompson"
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("Eurekapizza")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(link if link else "<MISSING>")
        yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
