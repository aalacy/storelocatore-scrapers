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
    base_url= "https://www.larosagrill.com/wp-admin/admin-ajax.php?action=store_search&lat=40.712775&lng=-74.00597299999998&max_results=25&search_radius=50&autoload=1"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k =json.loads(soup.text)

    for i in k:
        tem_var=[]
    
        if len(i["address"].split(','))==4:
            
            street_address = i["address"].split(',')[0]
            city = i["address"].split(',')[1]
            state = i["address"].split(',')[2].split( )[0]
            zipcode =  i["address"].split(',')[2].split( )[1]
            latitude = i["lat"]
            longitude  = i["lng"]

            store_name.append(i["store"])


            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("larosagrill")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)
            
        else:

            store_name.append(i["store"])
            # street_address = " ".join(i["address"].split(',')[:2])
            city = i["address"].split(',')[2]
            v1 =i["address"].split(',')
            if v1[-1]==" USA":
                del v1[-1]
            
            state = v1[-1].split( )[0]
            zip1 = v1[-1].split( )[1]
            city = v1[-2]
            st =(" ".join(v1[:-2]))

            # state =  i["address"].split(',')[3].split( )[0]
            # zipcode = i["address"].split(',')[3].split( )[1]
            latitude = i["lat"]
            longitude  = i["lng"]


            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zip1.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("larosagrill")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)
        
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.larosagrill.com/")
        store.append(store_name[i])
        store.extend(store_detail[i])

        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


