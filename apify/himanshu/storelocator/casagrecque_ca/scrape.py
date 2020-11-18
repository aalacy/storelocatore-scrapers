import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('casagrecque_ca')






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
    
    return_main_object =[]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url= "https://casagrecque.ca/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1571981616376"
    locations = session.get(base_url,headers=headers)
    
    soup= BeautifulSoup(locations.text,"lxml")
    item = soup.find_all("item")
    for i in item:
        tem_var =[]
        name  = i.find("location").text
        full_address = i.find("address").text
        zip1 = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))[-1]
        state = re.findall(r' ([A-Z]{2}) ', str(full_address))[-1]
        city = (full_address.replace(zip1,"").replace(state,"").replace("&#44;","").strip().lstrip().split('  ')[-1].replace(",",""))
        address = (full_address.replace(zip1,"").replace(state,"").replace("&#44;","").strip().lstrip().replace(city,"").replace("  ,",""))
        phone = i.find("telephone").text
        latitude = i.find("latitude").text
        longitude = i.find("longitude").text
        if i.find("storeId") !=None:
            storeId = i.find("storeId").text
        else:
            storeId = "<MISSING>"
        
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "CA"
        tem_var.append("https://casagrecque.ca")
        tem_var.append(name.strip().replace("&#8211;",""))
        tem_var.append(address.strip())
        tem_var.append(city.strip())
        tem_var.append(state.strip() if state.strip() else "<MISSING>" )
        tem_var.append(zip1.strip() if zip1  else "<MISSING>" )
        tem_var.append(country)
        tem_var.append(storeId)
        tem_var.append(phone.strip() if phone.strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        #logger.info(tem_var)
        return_main_object.append(tem_var)
    

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


