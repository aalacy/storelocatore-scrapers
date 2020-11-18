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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "API-Token": "1497efd6-453c-4113-8344-ec05246dc657"
    }
    base_url= "https://api.snapkitchen.com/v1/locations"
    r = session.get(base_url,headers=headers).json()
    # soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    
    for i in r['data']:
        time=''
        for j in i['hours']:
            # j['day']
            if "start" in j or "end" in j:
                # if j['start']=="None" and j['end']=="None":
                #     time = time +" "+ j['day'] +' '+ "closed" +' ' +"closed"
                # else:
                time = time +" "+ j['day'] +' '+ str(j['start']) +' ' + str(j['end'])
            
        hours = (time.replace("None None","closed"))
        tem_var =[]
       
        tem_var.append("https://www.snapkitchen.com")
        tem_var.append(i['name'].strip())
        tem_var.append(i['address']['street'].strip())
        tem_var.append(i['address']['city'].strip())
        tem_var.append(i['address']['state'].strip())
        tem_var.append(i['address']['zipcode'].strip())
        tem_var.append(i['address']['country'].replace("USA","US"))
        tem_var.append(i["id"])
        tem_var.append(i['phone'].strip())
        tem_var.append("<MISSING>")
        tem_var.append(i['address']['coord'][1])
        tem_var.append(i['address']['coord'][0])
        tem_var.append(hours.strip())
        tem_var.append("https://www.snapkitchen.com/locations/" + tem_var[1].replace(' ',"-").lower() + "/" + str(tem_var[7]))
        yield tem_var


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


