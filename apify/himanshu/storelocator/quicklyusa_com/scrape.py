import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('quickly.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    return_main_object = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://quicklyusa.com"
    r = session.get("http://quicklyusa.com/quicklystores.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("table")[2].find_all("a")[:-1]:
        if location.text == "":
            continue
        # print(location.text)
        page_url = base_url + "/" + location["href"]
        # print(page_url)
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        iframe = location_soup.find("iframe")["src"]
        geo_request = session.get(iframe,headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"html5lib")
        script = geo_soup.find_all('script', text = re.compile('initEmbed'))[0]
        # print(script.text)
        if "initEmbed" in script.text:
            try:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
            except:
                geo_data = "<MISSING>"
                lat = "<MISSING>"
                lng = "<MISSING>"
        
        if geo_data == "<MISSING>":
            street_address = list(location_soup.find("font",{'face':"arial, helvetica"}).stripped_strings)[0].split("(")[0].strip()
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
        else:
            street_address = " ".join(geo_data.split(",")[0:-2]).strip()
            city = geo_data.split(",")[-2].strip()
            state = geo_data.split(",")[-1].split(" ")[1].strip()
            zipp = geo_data.split(",")[-1].split(" ")[-1].strip()
        street_address = street_address.replace("Stoneridge Mall Rd","1 Stoneridge Mall Rd").replace("  "," ")
        if location.text =="Rohnert Park":
            street_address = "1451 Southwest Boulevard"
        if location.text =="Milpitas":
            street_address = "1350 S. Park Victoria Drive, Suite 30"
        if location.text =="Daly City Serramonte":
            street_address = "Serramonte Center Food Court, Hwy 280 & Serramonte Blvd."
        # print(lat,lng)
        # print(street_address)
        # print(city)
        # print(state)
        # print(zipp)
        # print()
       

           
        store = []
        store.append("http://quicklyusa.com")
        store.append(location.text)
        store.append(street_address if street_address != "" else "<MISSING>")
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("quicklyusa")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        return_main_object.append(store)

    r = session.get("http://quicklyusa.com/otqulo.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("table")[2].find_all("a"):
        if location.text == "":
            continue
        page_url = base_url + "/" + location["href"]
        # print(page_url)
        if "http://quicklyusa.com/annarbormi.html" in page_url:
            continue
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        iframe = location_soup.find("iframe")["src"]
        geo_request = session.get(iframe,headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"html5lib")
        script = geo_soup.find_all('script', text = re.compile('initEmbed'))[0]
        # print(script.text)
        if "initEmbed" in script.text:
            try:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
            except:
                geo_data = "<MISSING>"
                lat = "<MISSING>"
                lng = "<MISSING>"
        
        if geo_data == "<MISSING>":
            street_address = list(location_soup.find("font",{'face':"arial, helvetica"}).stripped_strings)[0].split("(")[0].strip()
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
        else:
            street_address = " ".join(geo_data.split(",")[0:-2]).strip()
            city = geo_data.split(",")[-2].strip()
            state = geo_data.split(",")[-1].split(" ")[1].strip()
            zipp = geo_data.split(",")[-1].split(" ")[-1].strip()

        street_address = street_address.replace("Stoneridge Mall Rd","1 Stoneridge Mall Rd").replace("  "," ")
        if location.text =="Rohnert Park":
            street_address = "1451 Southwest Boulevard"
        if location.text =="Milpitas":
            street_address = "1350 S. Park Victoria Drive, Suite 30"
        if location.text =="East Lansing, MI":
            street_address = "Michigan State University"
            state = "MI"
            zipp = "<MISSING>"


        # print(lat,lng)
        # print(street_address)
        # print(city)
        # print(state)
        # print(zipp)
        # print()
       

           
        store = []
        store.append("http://quicklyusa.com")
        store.append(location.text)
        store.append(street_address if street_address != "" else "<MISSING>")
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("quicklyusa")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
