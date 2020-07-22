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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://cdn.shopify.com/s/files/1/2618/6674/t/2/assets/sca.storelocatordata.json?3243&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    address = []
    phone=[]
    k=json.loads(soup.text,strict=False)
    for index,i in enumerate(k):
        tem_var=[]
        country = i['country']
        lat = i['lat']
        log =i['lng']
        postal =i['postal']
        state =i['state']
        city =i['city']
        name =i['name']
        if "phone" in i:
            phone =i['phone']
        else:
            phone="<MISSING>"
        if 'schedule' in i:
            hours = (i['schedule'].replace("\\","").replace("/","").replace("\n","").replace("\r","").replace("\t",""))
        else:
            hours = "<MISSING>"
       
        if len(i['address'].split(','))==1:
            st = i['address']
        else: 
            st =(" ".join(i['address'].split(",")[1:]))
        tem_var.append("https://hartstores.com")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(st.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(postal.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(country.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("<MISSING>")
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("hartstores")
        tem_var.append(lat.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(log.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(hours.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("<MISSING>")
        if tem_var[2] in address :
            continue
        address.append(tem_var[2])
        yield tem_var
def scrape():
    data = fetch_data()
    write_output(data)
scrape()




