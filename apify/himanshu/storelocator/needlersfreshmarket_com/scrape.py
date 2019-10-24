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

def getDecodedPhoneNo(encoded_phone_no):
        _dict = {}
        _dict["2"] = "ABC"
        _dict["3"] = "DEF"
        _dict["4"] = "GHI"
        _dict["5"] = "JKL"
        _dict["6"] = "MNO"
        _dict["7"] = "PQRS"
        _dict["8"] = "TUV"
        _dict["9"] = "WXYZ"

        _real_phone = ""
        for _dg in encoded_phone_no:
            for key in _dict:
                if _dg in _dict[key]:
                    _dg = key
            _real_phone += _dg
        return _real_phone


    # print("phone ==== " + getDecodedPhoneNo(_phone))
def fetch_data():
    return_main_object =[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url= "https://api.freshop.com/1/stores?app_key=needle&has_address=true&limit=-1&token=295a9cc3d9b6e0f918a73dd88361b312"
    locations = requests.get(base_url,headers=headers).json()
    # print(locations)
    # soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    for loc in locations['items']:
        address = loc['address_1']
        latitude = loc['latitude']
        name =loc['name']
        longitude = loc['longitude']
        city = loc['city']
        phone1 = loc['phone']
        zip1 = loc['postal_code']
        state = loc['state']
        hours = loc['hours_md']
        phone = (phone1.replace("\n"," ").split("  ")[0])
        store = loc['store_number']
        tem_var =[]
        # print(phone)
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "US"
        tem_var.append("https://www.needlersfreshmarket.com")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(country)
        tem_var.append(store)
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours)
        tem_var.append(loc['url'])
        # print(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


