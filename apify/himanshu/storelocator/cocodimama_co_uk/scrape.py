import csv
import requests
from bs4 import BeautifulSoup
import re
import json
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
    r = requests.get(base_url, headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    link = soup.find_all("div",{"class":"js-locations"})
    for i in link:
        r1 = requests.get(base_url, headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        link1 = soup1.find_all("div",{"class":"c-location__inner"})
        for j in link1:
            k=(j.find("a")['href'])
            r2 = requests.get(k,headers=headers)
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
            link5 = soup2.find("h4",{"class":"t-heading-epsilon"}).find_next_siblings('span')[-1]
            phone = (link5.text.strip())
            if soup2.find("iframe") != None:
                longitude = (soup2.find("iframe")["src"].split('!2d')[1].split('!3d')[0])
                latitude = (soup2.find("iframe")["src"].split('!3d')[1]).split('!2m3!')[0].replace("!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x487604ad58629689%3A0x3ba11f99a698ecc2!2sCoco+di+Mama+-+Italian+to+Go+-+Fleet+St!5e0!3m2!1sen!2suk!4v1544788455150","")
            else:
                longitude = ("<MISSING>")
                latitude = ("<MISSING>")
            store = []
            store.append("https://www.cocodimama.co.uk/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append("<MISSING>")
            store.append(zipp)   
            store.append("UK")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(k)  
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
