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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"


    }
    return_main_object =[]
    addressess =[]
    base_url= "https://stuckeys.com/wp-admin/admin-ajax.php"
    data = "action=get_all_stores&lat=&lng="
    loc = session.post(base_url,headers=headers,data=data).json()
    # soup= BeautifulSoup(r.text,"lxml")

    for i in loc.keys():
        tem_var =[]
    # print("=================================",q)

        tem_var.append("https://stuckeys.com/")
        tem_var.append(loc[i]['na'])
        tem_var.append(loc[i]['st'] if loc[i]['st']  else "<MISSING>")
        tem_var.append(loc[i]['ct'])
        tem_var.append(loc[i]['rg'])

        tem_var.append(loc[i]['zp'])
        tem_var.append("US")
        tem_var.append("<MISSING>")
        if "te" in loc[i]:
            tem_var.append(loc[i]['te'])
        else:
            tem_var.append("<MISSING>")

        tem_var.append("<MISSING>")
        tem_var.append(loc[i]['lat'] if loc[i]['lat'] else "<MISSING>")
        tem_var.append(loc[i]['lng'] if loc[i]['lng'] else  "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(loc[i]['gu'])
        #print(tem_var)
        if tem_var[2] in addressess:
            continue
        addressess.append(tem_var[2])
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


