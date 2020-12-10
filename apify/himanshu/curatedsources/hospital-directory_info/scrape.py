import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["location_name", "raw_address", "phone", "page_url" , "website"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_url= "https://www.hospital-directory.info"
    state_r = session.get(base_url)
    state_soup = BeautifulSoup(state_r.text, "lxml")

    ## Usa location
    for link in state_soup.find("div",{"class":"content"}).find_all("table")[1].find_all("a"):
        href = base_url+link['href']
        r = session.get(href)
        soup = BeautifulSoup(r.text, "lxml")
        total = int(soup.find("div",{"class":"content"}).find_all("div")[1].text.split("of")[1].split("Next")[0].strip())
        page = 0
        while page < total:
            page_url = href+"/"+str(page)
            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            for info in location_soup.find("div",{"class":"content"}).find("table").find_all("tr"):
                data = list(info.stripped_strings)
                if len(data) > 1:
                    location_name = data[0].strip()
                    raw_address = data[1].strip()
                    phone = data[2].replace("tel:","").strip()
                    if info.find("a"):

                        if info.find("a").text == "website":
                            website = info.find("a")['href']
                        else:
                            website = "<MISSING>"

                    else:
                        website = "<MISSING>"
                    store = []
                    store.append(location_name)
                    store.append(raw_address)
                    store.append(phone)
                    store.append(page_url)
                    store.append(website)
                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    yield store
                else:
                    continue
            page+= 25
        

    ### Canada location
    for link in state_soup.find("div",{"class":"content"}).find_all("table")[2].find_all("a"):
        href = base_url+link['href']
        r = session.get(href)
        soup = BeautifulSoup(r.text, "lxml")
        total = int(soup.find("div",{"class":"content"}).find_all("div")[1].text.split("of")[1].split("Next")[0].strip())
        page = 0
        while page < total:
            page_url = href+"/"+str(page)
            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            for info in location_soup.find("div",{"class":"content"}).find("table").find_all("tr"):
                data = list(info.stripped_strings)
                if len(data) > 1:
                    location_name = data[0].strip()
                    raw_address = data[1].strip()
                    phone = data[2].replace("tel:","").strip()
                    if info.find("a"):

                        if info.find("a").text == "website":
                            website = info.find("a")['href']
                        else:
                            website = "<MISSING>"

                    else:
                        website = "<MISSING>"
                    store = []
                    store.append(location_name)
                    store.append(raw_address)
                    store.append(phone)
                    store.append(page_url)
                    store.append(website)
                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    yield store
                else:
                    continue
            page+= 25


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
