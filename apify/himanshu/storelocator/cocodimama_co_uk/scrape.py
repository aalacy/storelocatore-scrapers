import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url= "https://www.cocodimama.co.uk/locations/"
    r = session.get(base_url, headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    link = soup.find_all("div",{"class":"js-locations"})
    for i in link:
        r1 = session.get(base_url, headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        link1 = soup1.find_all("div",{"class":"c-location__inner"})
        for j in link1:
            k=(j.find("a")['href'])
            r2 = session.get(k,headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            link2 = soup2.find("address",{"class":"u-mb-20"})
            if "London" in list(link2.stripped_strings) or  "London," in list(link2.stripped_strings):
                zipp = list(link2.stripped_strings)[-1]
                city = "London"
                street_address = (" ".join(list(link2.stripped_strings)[:-2]).replace(",",""))
            else :
                zipp = list(link2.stripped_strings)[-1]
                city = "<MISSING>"
                street_address = " ".join(list(link2.stripped_strings))[:-2].replace(", W12 7","").replace(", W6 9","")
            link3 = soup2.find("span",{"class":"l-col"})
            hours_of_operation = (" ".join(list(link3.stripped_strings)).replace("Christmas Opening Hours",""))
            link4 = soup2.find("h3",{"class":"t-heading-delta"})
            location_name = ("".join(list(link4.stripped_strings)))
            try:
                k8 = soup2.find("iframe")
                longitude = (k8['src'].split("!2d")[1].split("!3d")[0])
            except:
                longitude  = "<MISSING>"
            try:
                k8 = soup2.find("iframe")
                latitude = (k8['src'].split("!3d")[1].split("!2m")[0].split("!3m2!1i")[0])
            except:
                latitude  = "<MISSING>" 
            try:
                link5 = soup2.find("h4",{"class":"t-heading-epsilon"}).find_next_siblings('span')[-1]
                phone = (link5.text.strip())
            except:
                phone = "<MISSING>"
            store = []
            store.append("https://www.cocodimama.co.uk/")
            store.append(location_name if location_name else "<MISSING>" )
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append("<MISSING>")
            store.append(zipp if zipp else "<MISSING>")   
            store.append("UK")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(k if k else "<MISSING>" )  
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
