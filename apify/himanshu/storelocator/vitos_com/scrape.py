import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://vitos.com/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    box = soup.find_all("div",{"role":"gridcell"})
    for cell in box:
        loc = list(cell.stripped_strings)
        # print(loc)
        # print(len(loc))
        if len(loc)== 6:
            location_name = loc[0]
            street_address = loc[1]
            city = loc[2].split(",")[0].strip()
            state = loc[2].split(",")[1].strip()
            zipp = "<MISSING>"
            phone = loc[4]
            hours_of_operation = loc[3].replace("1030","10:30").replace("230","2:30").replace("830","8:30")
        else:
            location_name = loc[0]
            street_address = loc[1]
            city = loc[2].split(",")[0].strip()
            state = loc[2].split(",")[1].strip()
            zipp = "<MISSING>"
            phone =  loc[5]
            hours_of_operation = ", ".join(loc[3:5]).replace("1030","10:30").replace("230","2:30").replace("830","8:30")

        page_url = session.get(cell.find("a")['href'],headers=headers).url
        store_number = page_url.split("vitos")[1]
        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        map_url = soup1.find("ul",{"class":"dropdown-menu"}).find("li").find("a")['href']
        # print(map_url)
        try:
            coords = session.get(map_url).url
            if "/@" in coords:
                lat = coords.split("/@")[1].split(",")[0]
                lng = coords.split("/@")[1].split(",")[1]
            else:
                map_soup = BeautifulSoup(session.get(map_url).text, "lxml")
                file_name = open("data.txt","w",encoding="utf-8")
                file_name.write(str(map_soup))
                try:
                    map_href = map_soup.find("a",{"href":re.compile("https://maps.google.com/maps?")})['href']
                    lat = str(BeautifulSoup(session.get(map_href).text, "lxml")).split("/@")[1].split(",")[0]
                    lng = str(BeautifulSoup(session.get(map_href).text, "lxml")).split("/@")[1].split(",")[1]
                except:
                    lat = str(map_soup).split("/@")[1].split(",")[0]
                    lng = str(map_soup).split("/@")[1].split(",")[1]
        except:
            lat = "<MISSING>"
            lng = "<MISSING>"
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("Vito's Pizza & Subs")
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()


