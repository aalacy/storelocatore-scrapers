import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    addresses = []
    location_name2 = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation1 = ""
    page_url = ""
    base_url = "https://flyhightrampolinepark.com/"
    locator_domain = base_url
    try :
        r = session.get(base_url, headers=headers)
    except:
        pass
    soup = BeautifulSoup(r.text, "lxml")
    a = soup.find_all('a',{'class', 'et_pb_button'})
    for i in a:
        page_url = (i['href'])
        try:
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            b = soup1.find_all('div',{'class','text-block'})
        except:
            continue
        for j in b:
            street_address = (list(j.stripped_strings)[1].replace("Fort Collins","218 Smokey Street"))
            location_name2 = (list(j.stripped_strings)[0])
            if "Fly High At Reno" in location_name2 :
                location_name2 = location_name2 
            elif "Fly High At Boise" in location_name2 :
                location_name2 = location_name2 
            elif "Fly High At Ogden" in location_name2 :
                location_name2 = location_name2 
            elif "Fly High At Farmington" in location_name2 :
                location_name2 = location_name2 
            elif "Fly High At Altadena" in location_name2 :
                location_name2 = location_name2
            else:
                location_name2 = "Fly High At Fort Collins"
            city = (list(j.stripped_strings)[2].replace("218 Smokey Street –","Fort Collins").split(",")[0])
            state = (list(j.stripped_strings)[2].split(",")[-1].strip().replace("218 Smokey Street –","CO").split(" ")[0])
            zipp = (list(j.stripped_strings)[2].split(",")[-1].strip().replace("218 Smokey Street –","80525").split(" ")[-1]) 
            phone = (list(j.stripped_strings)[3].replace("Fort Collins, CO 80525","(970) 305-5300"))
            q = location_name2.replace(" ","-")
            location_url = str(page_url)+'/'+str(q)+"/hours/"
            r2 = session.get(location_url, headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            z = soup2.find_all('div',{'class','col-xs-12 col-md-8'})
            hours_of_operation1 = ''
            for h in z:
                if h != []:
                    hours_of_operation1 = hours_of_operation1+ ' '+"".join(list(h.stripped_strings)).replace("Winter Break:We will be open at 10 am during Winter Break from Dec 20, 2019 through Jan 5, 2020. Whoa 2020!","") 
                else:
                    hours_of_operation1 ="<MISSING>"
            store = []
            store.append("https://flyhightrampolinepark.com")
            store.append(location_name2)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.replace("View Hours","<MISSING>"))
            store.append("Fly High Adventure Parks")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation1)
            store.append(page_url)
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
