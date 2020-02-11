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

    base_url = "https://www.greenmill.com/"
    r =  session.get("https://www.greenmill.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    links = soup.find("ul",{"class":"sub-menu"}).find_all("a")
    for link in links:
        page_url = link['href']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if soup1.find("div",{"itemprop":"streetAddress"}):
            street_address = soup1.find("div",{"itemprop":"streetAddress"}).text.strip()
            city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
            state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
            zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip()
            phone = soup1.find("span",{"itemprop":"telephone"}).text.strip()
            latitude = soup1.find_all("meta",{"itemprop":"latitude"})[0]['content']
            longitude = soup1.find_all("meta",{"itemprop":"latitude"})[1]['content']
            hours = (str(soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[0].text)+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[1].text+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[2].text+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[3].text).strip()
        else:
            addr = list(soup1.find("p",{"style":"font-size: 13px;"}).stripped_strings)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].split(" ")[1]
            zipp = addr[1].split(",")[1].split(" ")[2]
            latitude = soup1.find_all("iframe",{"class":"gmapsloc"})[-1]['src'].split("!3d")[1].split("!")[0]
            longitude = soup1.find_all("iframe",{"class":"gmapsloc"})[-1]['src'].split("!2d")[1].split("!")[0]
            hours = (soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[1].text)+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[2].text+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[3].text
        
        location_name = "Green Mill Restaurant Sports Bar & Grill in "+str(city)+","+str(state)
        if zipp in ["56301","67207"]:
            location_name = "Green Mill Restaurant Sports Bar & Grill in "+str(city)
        if zipp in ["54474"]:
            location_name = "Green Mill Restaurant Sports Bar & Grill in Wausau"
        if zipp in ["54016"]:
            location_name = "Green Mill Restaurant Sports Bar & Grill in "+str(city)+", MN"
        location_type = "Restaurant"
        # if "54016" in zipp:
        #     state = "MN"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone )
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print("data===="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
