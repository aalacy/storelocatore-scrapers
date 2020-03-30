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
    base_url= "https://locations.pon-bon.com/locations.json"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k =json.loads(soup.text)
   
    for i in k['locations']:
        tem_var=[]
        if i['loc']['country']== "US" or i['loc']['country']== "CA":
            st = i['loc']['address1']
            state=(i['loc']['state'])
            city = i['loc']['city']
            latitude = i['loc']['latitude']
            longitude = i['loc']['longitude']
            phone= i['loc']['phone']
            postalCode = i['loc']['postalCode']
            name = i['loc']['name']
            hours = i['loc']['hours']['days']
            time = ''
            for hours1 in hours:
                time = time + ' ' + hours1['day'] + ' '+ str(hours1['intervals'])
            
            time1 = time.replace("[{'end': ","").replace("}]","").replace("'start':","")
            
            if time1:
                time2 = time1
            else:
                time2 = "<MISSING>"
            hourss = (time2.replace("MONDAY [] TUESDAY [] WEDNESDAY [] THURSDAY [] FRIDAY [] SATURDAY [] SUNDAY []","<MISSING>").replace("MONDAY []",""))
           
            tem_var.append("https://www.ponderosasteakhouses.com")
            tem_var.append(city)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(postalCode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("ponderosasteakhouses")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hourss)
            return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


