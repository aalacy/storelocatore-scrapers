import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url= "https://www.ramonatire.com/wp-admin/admin-ajax.php?action=store_search&lat=33.980601&lng=-117.375494&max_results=25&search_radius=50&autoload=1"
    r = requests.get(base_url,headers=headers).json()
    # soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

   
    

    for i in r:
        tem_var =[]
        r1 = requests.get(i['permalink'],headers=headers)
        soup= BeautifulSoup(r1.text,"lxml")
        hours = " ".join(list(soup.find("table",{"class":"table-borderless table-condensed table hours-list"}).stripped_strings))
        
        tem_var.append("https://www.ramonatire.com")
        tem_var.append(i['store'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i['address'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i['city'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i["state"].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i['zip'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("US")
        tem_var.append(i['id'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i['phone'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("<MISSING>")
        tem_var.append(i['lat'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i['lng'].encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(hours.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(i['permalink'])
        print(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


