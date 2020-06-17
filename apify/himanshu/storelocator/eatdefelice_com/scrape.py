import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import requests



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
    addresses = []
    
    url = "https://www.google.com/maps/vt?pb=!1m4!1m3!1i9!2i140!3i192!1m4!1m3!1i9!2i140!3i193!1m4!1m3!1i9!2i141!3i192!1m4!1m3!1i9!2i141!3i193!1m4!1m3!1i9!2i140!3i194!1m4!1m3!1i9!2i141!3i194!1m4!1m3!1i9!2i142!3i192!1m4!1m3!1i9!2i142!3i193!1m4!1m3!1i9!2i143!3i192!1m4!1m3!1i9!2i143!3i193!1m4!1m3!1i9!2i142!3i194!1m4!1m3!1i9!2i143!3i194!2m3!1e0!2sm!3i516231764!2m43!1e2!2sspotlight!4m2!1sgid!2sgkigfbUHJKAzuvMRGjcwbA!5i1!8m36!11e11!12m19!3m1!3s0x0%3A0x2b91b0ef5aab2dbf!3m1!3s0x0%3A0x75b8d84fbd536d87!3m1!3s0x0%3A0x30491ea7ca95e375!3m1!3s0x0%3A0x714778b0ae298301!3m1!3s0x0%3A0x7bf24080c34f4f5!3m1!3s0x0%3A0xfaad827a4e11d859!3m1!3s0x0%3A0xe903608cfb2b91bb!3m1!3s0x0%3A0xb1303661a9326f96!10b0!11b1!20e3!13m12!2shh%2Chplexp%2Ca!14b1!18m5!5b0!6b0!9b1!12b1!16b0!22m3!6e2!7e3!8e2!19u14!19u29!3m12!2sen-US!3sUS!5e289!12m4!1e68!2m2!1sset!2sRoadmap!12m3!1e37!2m1!1ssmartmaps!4e3!12m1!5b1&client=google-maps-embed&token=32784"
    response = requests.request("GET", url).json()
    for i in response:
        if "features" in i:
            for d in i['features']:
                id1  = d["id"]
                name = json.loads(d['c'])['1']['title']
                url1 = "https://www.google.com/maps/api/js/ApplicationService.GetEntityDetails?"+"pb=!1m6!1m5!2s"+str(name)+"!3m2!1d40.37793612222415!2d-80.71929931640625!4s"+str(id1)+"!2m2!1sen_US!2sus!3shttp://eatdefelice.com/locations/!4sMgTiXrO9I_SHwbkPsrGo-A4!7m1!2i3!13m1!4b1"
                response1 = requests.request("GET", url1)
                kp = response1.text.replace(")]}'",'')
                location_name = json.loads(kp)[1][0][1].split(",")[0]
                street_address = json.loads(kp)[1][0][1].split(",")[1]
                city = json.loads(kp)[1][0][1].split(",")[2]
                state = json.loads(kp)[1][0][1].split(",")[3].strip().split( )[0]
                zipp = json.loads(kp)[1][0][1].split(",")[3].strip().split( )[1]
                latitude = json.loads(kp)[1][0][2][0]
                longitude = json.loads(kp)[1][0][2][1]
                phone = json.loads(kp)[1][7]
                hours_of_operation = "Sunday – Thursday 11am – 10pm Friday & Saturday 11am – 11pm"
                store=[]
                store.append("http://eatdefelice.com/")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append("http://eatdefelice.com/locations/")
                if store[2] in addresses :
                    continue
                addresses.append(store[2])
                if "21536" in zipp:
                    continue
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~",store)

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
