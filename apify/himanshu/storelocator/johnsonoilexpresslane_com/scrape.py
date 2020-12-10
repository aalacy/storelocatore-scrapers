import csv
import requests
from bs4 import BeautifulSoup
from sgrequests import SgRequests

session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.johnsonoilexpresslane.com/"
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
    }

    ### iowa location IA
    r = session.get("https://www.johnsonoilexpresslane.com/iowa", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("div",{"class":"style-jmm2w03pinlineContent"})
    for i in range(0,54,3):
        
        location_name = "".join(list(data.find_all("div",{"class":"txtNew"})[i].stripped_strings)).replace("Open 24 Hrs","DAVENPORT").replace("1139 BRADY ST563-888-5760","DAVENPORT")
        info = list(data.find_all("div",{"class":"txtNew"})[i+1].stripped_strings)
        
        if len(list(data.find_all("div",{"class":"txtNew"})[i+1].stripped_strings)) == 2:
            street_address = info[0]
            phone = info[1]

        else:
            if i+1 == 34:
                street_address = "3636 HICKORY GROVE"
                phone = "563-391-6302"
            else:
                street_address = "1139 BRADY ST"
                phone = "563-888-5760"
        hours_of_operation = " ".join(list(data.find_all("div",{"class":"txtNew"})[i+2].stripped_strings)).replace("3636 HICKORY GROVE563-391-6302","Open 24 Hrs")

        page_url = "https://www.johnsonoilexpresslane.com/iowa"
    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append("<MISSING>")
        store.append("IA")
        store.append("<MISSING>")   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store





    ## illinois location IL
    r = session.get("https://www.johnsonoilexpresslane.com/illinois", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("div",{"id":"acmhyinlineContent-gridContainer"})
    h = []
    for i in data.find_all("div",{"class":"txtNew"}):
        h.append(list(i.stripped_strings))

    for i in range(len(h)):
        if "Trendar" in h[9]:
            del h[9]
            del h[141]
            del h[158]
            for i in range(0,len(h),3):
                if i==24 or i==48 or i==117 or i==141:
                    location_name = "".join(h[i+1])
                else:
                    location_name = "".join(h[i])
                if i+1==25 or i+1==49 or i+1==118 or i+1==142:
                    street_address = "".join(h[i][0])
                    phone = "".join(h[i][1:])
                else:
                    street_address = "".join(h[i+1][0])
                    phone = "".join(h[i+1][1:])
                
                hours_of_operation = " ".join(h[i+2])
                page_url = "https://www.johnsonoilexpresslane.com/illinois"
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append("<MISSING>")
                store.append("IL")
                store.append("<MISSING>")   
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
                store.append(hours_of_operation)
                store.append(page_url)
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
