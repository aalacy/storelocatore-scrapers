import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url1="https://www.powr.io/plugins/map/wix_view.json?cacheKiller=1565172087400&compId=comp-jcccswek&deviceType=desktop&height=462&instance=yHGw_8WbCn7m6c6pR2XU186ZyTI_PDlSOhco9oNrjxk.eyJpbnN0YW5jZUlkIjoiN2IwNWYwOWYtMjE1NC00YTQxLTlmYmQtODc4Yzg5YTU4MWQ2IiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMTktMDgtMDdUMTA6NDE6NDAuNzQzWiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlwQW5kUG9ydCI6IjEyMy4yMDEuMjI2LjEyOC8zMzQ5NCIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI1N2Q5YjhmMS1jYmIzLTRmNGMtOWJmZC0zMTI3YTZkMGQ2ZWIiLCJzaXRlT3duZXJJZCI6IjkxOGU5NTAxLTQwMGMtNDcwNS1iM2VlLTc2ZDI5NWYxM2Y2ZiJ9&locale=en&pageId=e97g9&siteRevision=349&viewMode=site&width=733"
    soup = session.get(base_url1).json()

    base_url= "https://www.thesandwichspot.com/locations"
    r = session.get(base_url)
    soup1= BeautifulSoup(r.text,"lxml")
    data = soup1.find_all("div",{"class":"p2inlineContent","id":"e97g9inlineContent"})
    phone=[]
    for i in data:
        data = i.find_all("h2")

        for d in  data:
            if len(d.text.split("Phone:"))==2:
                phone.append(d.text.split("Phone:")[1].replace("\xa0","").strip())
       
   
    return_main_object =[]
    store_detail =[]
    store_name=[]
    latitude=[]
    longitude =[]
    for idx, val in enumerate(soup["content"]['locations']):
        tem_var=[]
        latitude.append(val["lat"])
        longitude.append(val['lng'])
        # store_name.append(json.loads(val['components'])[1]["long_name"])

        if len(val['address'].split(","))==5:
            street_address = " ".join(val['address'].split(",")[:2])
            city = val['address'].split(",")[2]
            state= val['address'].split(",")[3].split( )[0]
            zipcode = val['address'].split(",")[3].split( )[1]
        else:
            street_address =val['address'].split(",")[0]
            city = val['address'].split(",")[1]
            state= val['address'].split(",")[2].split( )[0]
            zipcode = val['address'].split(",")[2].split( )[1]

        tem_var.append(street_address)
        store_name.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        store_detail.append(tem_var) 


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.thesandwichspot.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("thesandwichspot")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append("<MISSING>")
        return_main_object.append(store)
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()