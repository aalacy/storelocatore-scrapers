import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rubinoshoes_com')





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


    # logger.info("phone ==== " + getDecodedPhoneNo(_phone))
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url= "https://cdn.shopify.com/s/files/1/0078/2191/8285/t/46/assets/sca.storelocatordata.json?v=1600888879&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    loc = session.get(base_url,headers=headers).json()
    # soup= BeautifulSoup(r.text,"lxml")
    
    return_main_object=[]
    for i in loc:
        lat = i['lat']
        lng = i['lng']
        name = i['name']
        phone = i['phone']
        address = i['address']
        state = i['state']
        city = i['city']
        zip1 = i['postal']
        tem_var =[]
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "US"
        tem_var.append("https://rubinoshoes.com")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(country)
        tem_var.append(i['id'])
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append("<MISSING>")
        tem_var.append("https://rubinoshoes.com/pages/store-locator")
        # logger.info(tem_var)
        return_main_object.append(tem_var)
        

   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


