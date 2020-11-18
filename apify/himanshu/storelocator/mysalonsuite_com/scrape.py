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
    adressess = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    }

    base_url = "https://www.mysalonsuite.com"
    json_data = session.get("https://easylocator.net/ajax/search_by_lat_lon/Weebly%20Hearts/33.5973469/-112.1072528/null/null").json()['physical']
    for data in json_data:
        location_name = data['name'].replace("MY SALON Suite of Whitney Ranch","Whitney Ranch")
        street_address = (str(data['street_address']) +" "+ str(data['street_address_line2']) +" "+ str(data['street_address_line3'])).replace("(at 4th Avenue North)","").replace("Now Open!","").replace("(Next to Regal Cinema)","").strip()
        
        if "1943 E Brandon Blvd" in street_address:
            continue
        city = data['city']
        state = data['state_province']
        zipp = data['zip_postal_code'].replace("6825","06824")
        if street_address == "1559 CA-1, Hermosa Beach, CA 90254":
            city = "Hermosa Beach"
            state = "CA"
            zipp = "90254"
        street_address = street_address.replace("1559 CA-1, Hermosa Beach, CA 90254","1559 CA-1").replace("The Marks Retail Center 1610 East Girard Place","16010 East Girard Place")
        country_code = data['country'].replace("Canada","CA")
        if len(zipp) == 5 or len(zipp) == 0:
            country_code = "US"
        temp_phone = data['phone'].replace("MSS","").replace("MYSS","").replace("-","").replace(".","").replace(" ","").replace(")","").replace("(","").encode('ascii', 'ignore').decode("utf-8").strip()
        phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
        latitude = data['lat']
        longitude = data['lon']
        store_number = data['location_number']
        if data['website_url']:
            if 'http:' in data['website_url']:
                page_url = data['website_url']
            else:
                page_url = "https://"+data['website_url']
        else:
            page_url = "https://www.mysalonsuite.com/"+str(location_name.replace(" ","-").lower())
        if street_address:
            street_address = street_address
        else:
            r1 = session.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            street_address1 = list(soup1.find("div",{"class":"intro__content"}).find("p").stripped_strings)
            street_address =street_address1[0].replace("The Marks Retail Center","")
        if zipp:
            zipp = zipp
        else:
            r1 = session.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            try:
                zipp1 = list(soup1.find("div",{"class":"intro__content"}).stripped_strings)
                zipp = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp1))[0]
            except:
                zipp = "<MISSING>"
        
        if temp_phone:
            temp_phone = temp_phone
            phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
        else:
            r1 = session.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            try:
                number = list(soup1.find("div",{"class":"intro__content"}).find("p").stripped_strings)
                if number[-1] == ".":
                    del number[-1]
                temp_phone = number[-1].replace("-","").replace(".","").replace(" ","").replace(")","").replace("(","").encode('ascii', 'ignore').decode("utf-8")
                phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
            except:
                phone = "<MISSING>"

       
        filter_data= session.get(page_url,headers=headers)
        soup_filter = BeautifulSoup(filter_data.text, "lxml")
        try:
            title = soup_filter.find("div",{"class":"intro__content"}).find("h1").text.split("–")[-1]
        except:
            continue
        if " Coming soon" in title:
            continue
        else:
            std = street_address.replace("Coming Soon!","").strip()
            if location_name == "Bel Air":
                std = "564 Baltimore Pike"
                city = "Bel Air"
                state = "MD"
            if location_name == "Atlanta" or location_name == "Pittsburgh":
                continue
            else:
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(std if std else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append(store_number) 
                store.append(phone.replace("813.602.1 (677)","813.602.1677") if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append("<MISSING>")
                store.append(page_url)
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if store[2] in adressess:
                    continue
                adressess.append(store[2])
                yield store
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
