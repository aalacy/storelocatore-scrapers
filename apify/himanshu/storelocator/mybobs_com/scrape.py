import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.mybobs.com/stores"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    a = soup.find_all("div",{"id":"locationType0"})
    for i in a:
        k = (i.find_all("a",{"class":"bobs-store-list__flist_result_ltype_pname_ename_esplace_atag"}))
        # print(k['href'])
        for j in k:
            link1 = ("https://www.mybobs.com"+str(j['href']))
            # print(link1)
            r1 = requests.get(link1)
            soup1 = BeautifulSoup(r1.text,"lxml")
            data = json.loads(soup1.find(lambda tag: (tag.name == "script") and "@context" in tag.text).text)[1]
            phone = (data['telephone'])
            street_address  = data['address']['streetAddress']+" "+ data['address']['addressLocality']
            state = data['address']['addressRegion']
            zipp = data['address']['postalCode']
            country_code =  data['address']['addressCountry'].upper()
            location_name = (data['name'])
            location_type = (data['@type'])
            city = location_name
            url = (data['url'].lower().split("/")[-1])
            m = state.lower().replace(" ","-")
            mp = "https://www.mybobs.com/stores/"+str(m)+"/"+str(url).replace(" ","-")
            r = requests.get(mp)
            soup= BeautifulSoup(r.text,"lxml")
            try:
                a = soup.find("ul",{"class":"bobs-store-additional-store-content_wrapper"}).find("iframe",{"class":"bobs-store-additional-store-content_wrapper-tourimg"})
                latitude = (a['src'].split("!1d")[1].split("!2d")[0])
                longitude =  (a['src'].split("!3f")[0].split("!2d")[1])
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            try:
                k  = data['openingHoursSpecification'][0]['opens']+" - "+data['openingHoursSpecification'][0]['closes']
                L  = data['openingHoursSpecification'][1]['opens']+" - "+data['openingHoursSpecification'][1]['closes']
                hours_of_operation = ("Mon-Sat"+' '+str(k)+","+"Sun"+" "+str(L))
            except:
                hours_of_operation = "<MISSING>"   
            store = []
            store.append("https://www.mybobs.com")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(mp if mp else "<MISSING>")
            yield store         
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
