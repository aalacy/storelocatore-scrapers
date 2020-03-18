

import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "http://www.mysalonsuite.com"
    r =  session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml") 
    
    for data in soup.find_all("ul", {"class":"wsite-menu"})[2].find_all("a"):
        state_link = base_url+data['href']
        city_r = session.get(state_link)
        city_soup = BeautifulSoup(city_r.text, "lxml")

        for link in city_soup.find("div",{"class":"paragraph"}).find_all("a"):
            if "http://" in link['href']:
                page_url = link['href']
            else:
                page_url = "http://www.mysalonsuite.com"+link['href']
            if "http://www.mysalonsuite.com/get-started.html" in page_url or "http://www.mysalonsuite.com/in-the-news" in page_url:
                continue
            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            location_name = location_soup.find("span",{"class":"wsite-text wsite-headline"}).text.strip()
            addr = list(location_soup.find("span",{"class":"wsite-text wsite-headline-paragraph"}).stripped_strings)
            if len(addr) == 3:
                street_address = addr[1].replace("Northlake Shopping Center","1858 North Causeway Blvd.").replace("The Terrace at Windy Hill","3000 Windy Hill Road SE").replace("\xa0","").strip()

                if len(addr[-2].split(",")) == 2:
                    city = addr[-2].split(",")[0].replace("1858 North Causeway Blvd. Mandeville","Mandeville").replace("\u200b","").strip()
                    state = addr[-2].split(",")[1].replace(" PA18976"," PA 18976").split(" ")[1].replace("\xa0","").strip()
                    try:
                        zipp = addr[-2].split(",")[1].replace(" PA18976"," PA 18976").split(" ")[2]
                    except:
                        zipp = "<MISSING>"
                else:
                    city = addr[-2].split(",")[1].strip()
                    state = addr[-2].split(",")[-1].split(" ")[1]
                    zipp = addr[-2].split(",")[-1].split(" ")[2]
                phone = addr[-1].replace("Leasing Phone Number:","").replace("\u200b","").strip()
            elif len(addr) == 5:
                if addr[-2] == "2":
                    del addr[-2]
                if addr[-1] == ".":
                    del addr[-1]
                if addr[-1] == ")":
                    del addr[-1]
                if addr[-2] == "\u200b":
                    del addr[-2]
                if len(addr) == 4:
                    street_address = addr[1]
                    city = addr[-2].split(",")[0].strip()
                    state = state = addr[-2].split(",")[-1].split(" ")[1]
                    zipp = addr[-2].split(",")[-1].split(" ")[2]
                    phone = addr[-1].replace("03-493-6977","203-493-6977")
                else:
                    street_address = addr[0]
                    city = addr[-2].split(",")[0].strip()
                    state = addr[-2].split(",")[-1].split(" ")[1]
                    zipp = addr[-2].split(",")[-1].split(" ")[2]
                    phone = addr[-1].replace("03-493-6977","203-493-6977")
            elif len(addr) == 6:
                if "23162" in addr[0]:
                    street_address = addr[0]
                    city = " ".join(addr[1:3])
                    state = addr[3].replace(",","").split(" ")[1]
                    zipp = addr[3].replace(",","").split(" ")[2].strip()
                    phone = addr[-2]
                    
                else:
                    street_address = addr[2]
                    city = addr[-3].split(",")[0].strip()
                    state = addr[-3].split(",")[-1].split(" ")[1]
                    zipp = addr[-3].split(",")[-1].split(" ")[2]
                    phone = addr[-1]
            elif len(addr)==2:
                street_address = " ".join(addr[0].replace("\xa0"," ").split(",")[0].split(" ")[:-1])
                city = addr[0].replace("\xa0"," ").split(",")[0].split(" ")[-1]
                state = addr[0].split(",")[1].split(" ")[1]
                zipp = addr[0].split(",")[1].split(" ")[2]
                phone = addr[-1]
            else:
                if "behind the Wells" in addr[-1]:
                    del addr[-1]
                if "Black Rock Turnpike" in addr[-1]:
                    del addr[-1]
                if addr[-2] == "(":
                    del addr[-2]
                if "Leasing Phone Number" in addr[-2]:
                    del addr[-2]
                if addr[-1] == ".":
                    del addr[-1]
                if addr[-2] == "2":
                    del addr[-2]
                if addr[-2] == "\u200b":
                    del addr[-2]
                if addr[1] == "Brookfield":
                    del addr[1]

                if len(addr)==2:
                    street_address = addr[0].split(",")[0]
                    city = addr[0].split(",")[1].split(" ")[1]
                    state = addr[0].split(",")[1].split(" ")[2]
                    zipp = "<MISSING>"
                else:
                    street_address = " ".join(addr[:-2]).replace("Across From Rosedale Mall","Across From Rosedale Mall 1721 County Road B2").replace("Located inside The Brookwood","Located inside The Brookwood 1820 Peachtree Road NE")
                    city = addr[-2].replace(", WI 53005","Brookfield, WI 53005").replace("\u200b","").replace("\xa0","").split(",")[0].replace("1820 Peachtree Road NE Atlanta","Atlanta").replace("1721 County Road B2 WestRoseville","West Roseville").strip()
                    state = addr[-2].split(",")[1].split(" ")[1]
                    zipp = addr[-2].split(",")[1].split(" ")[2]
                phone = addr[-1].replace("03-493-6977","203-493-6977").replace("949) 424-6770","(949) 424-6770").replace("2203","203")

            
            try:
                coord = location_soup.find("span",{"class":"wsite-text wsite-headline-paragraph"}).find("a")['href']
                latitude = coord.split("ll=")[1].split(",")[0]
                longitude = coord.split("ll=")[1].split(",")[1].split("&")[0]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            if street_address == "427 Stillson Road":
                zipp = "06825"

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp.replace("8918","89183"))
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data~~~~~~"+str(store))
            yield store


    ########## CANADA LOCATION
    r =  session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml") 
    
    for data in soup.find_all("div", {"class":"wsite-menu-wrap"})[-2].find_all("a"):
        page_url = base_url+data['href']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        location_name = soup1.find("span",{"class":"wsite-text wsite-headline"}).text.strip()
        addr = list(soup1.find("span",{"class":"wsite-text wsite-headline-paragraph"}).stripped_strings)
        street_address = addr[0]
        city = addr[1].replace("\u200b \xa0\u200b","").split(" ")[0]
        state = addr[1].replace("\u200b \xa0\u200b","").split(" ")[1]
        zipp = " ".join(addr[1].replace("\u200b \xa0\u200b","").split(" ")[2:])
        phone = addr[-1]
        coord = soup1.find("span",{"class":"wsite-text wsite-headline-paragraph"}).find("a")['href']
        latitude = coord.split("ll=")[1].split(",")[0]
        longitude = coord.split("ll=")[1].split(",")[1].split("&")[0]

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append("<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data~~~~~~"+str(store))
        yield store

        




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
