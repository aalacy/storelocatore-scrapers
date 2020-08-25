import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addressess = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.empirecinemas.co.uk/"
    location_url = "https://www.empirecinemas.co.uk/select_cinema_first/ci/"
    r = session.get(location_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    link = soup.find("div",{"class":"select-cinema-block"}).find_all("a")

    for links in link:
        city_link = "https://www.empirecinemas.co.uk" + links['href']
        if city_link in ['https://www.empirecinemas.co.uk/cinema_info/empire_sutton_surrey/t36/','https://www.empirecinemas.co.uk/cinema_info/empire_ipswich/t44/']:
            continue
        else:
            r1 = session.get(city_link)
            soup1 = BeautifulSoup(r1.text,"lxml")
            location_name = soup1.find("section",{"id":"content"}).find("h1").text
            raw_add = soup1.find("section",{"id":"content"}).find_all("p")

            if raw_add[0].text == "Contact Information":
                add = raw_add[1].text.strip()
            elif location_name == "EMPIRE CATTERICK GARRISON":
                add = raw_add[1].text.replace("General Manager: Anish Patel","").strip()
            elif location_name == "EMPIRE WALTHAMSTOW":
                add = raw_add[4].text.strip()
            else:
                add = raw_add[0].text.replace("If using satellite navigation please use B45 9FP.","").strip()

            temp = add.split("\n")
            if location_name == "EMPIRE BIRMINGHAM GREAT PARK":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[3]
                state = "<MISSING>"
                zipp = temp[-1]
                location_type = "EMPIRE CINEMAS(IMAX)"

            elif location_name == "EMPIRE SUTTON COLDFIELD":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[3]
                state = temp[4]
                zipp = temp[-1]
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE BISHOP'S STORTFORD":
                street_address = temp[1]
                city = temp[2]
                state = temp[3].split(" ")[0]
                zipp = " ".join(temp[3].split(" ")[1:])
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE CATTERICK GARRISON":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[3]
                state = temp[4]
                zipp = temp[5]
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE CLYDEBANK":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[-1].split(" ")[0]
                state = "<MISSING>"
                zipp = " ".join(temp[-1].split(" ")[1:])
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE HIGH WYCOMBE":
                street_address = temp[1]
                city = temp[2]
                state = "<MISSING>"
                zipp = temp[3]
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE LONDON HAYMARKET":
            
                st1 = temp[1].replace("\r","")
                st2 = temp[2].split(",")
                street_address = st1 + " " + st2[0]
                city = st2[1].strip().split(" ")[0]
                state = "<MISSING>"
                zipp = "".join(st2[1].strip().split(" ")[1:])
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE SLOUGH":
                street_address = temp[1].replace(",","")
                city = temp[2].replace(",","")
                state = temp[3]
                zipp = temp[4]
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE SUNDERLAND":
                street_address = " ".join(temp[1:4]).replace("\r","")
                city = temp[4]
                state = "<MISSING>"
                zipp = temp[5]
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE SWINDON (GREENBRIDGE)":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[3].split(",")[0]
                state = temp[3].split(",")[1]
                zipp = temp[4]
                location_type = "EMPIRE CINEMAS(IMAX)"
            elif location_name == "EMPIRE WALTHAMSTOW":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[3]
                state = "<MISSING>"
                zipp = temp[4]
                location_type = "EMPIRE CINEMAS"
            elif location_name == "EMPIRE WIGAN":
                street_address = " ".join(temp[1:3]).replace("\r","")
                city = temp[3]
                state = "<MISSING>"
                zipp = temp[4]
                location_type = "EMPIRE CINEMAS"
            else:
                continue
            store_number = city_link.split("/")[-2].replace("t","")
           
            try:
                latlng = str(soup1).split("cinemaLatLng = new google.maps.LatLng")[1].split("myOptions = {")[0].replace(");","").replace("(","").split(",")
                lat = latlng[0]
                lng = latlng[1]
            except IndexError:
                lat = "<MISSING>"
                lng = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("UK")
            store.append(store_number)
            store.append("<MISSING>")
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(city_link)     
            if store[2] in addressess:
                continue
            addressess.append(store[2]) 
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
            
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
