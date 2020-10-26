import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('newfoundlandgrocerystores_ca')





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
    base_url= "https://www.newfoundlandgrocerystores.ca/store-locator/v2/locations/all?_=1571920909554"
    locations = session.get(base_url,headers=headers).json()
    
    # soup= BeautifulSoup(r.text,"lxml")
    for loc in locations['searchResult']:
        tem_var=[]
        phone =''
        hours=''
        zip1 = ''
        address = loc['details']['streetAddress']
        city = loc['details']['city']
        zip1 = loc['details']['postalCode']
        locationType = loc['details']['locationType']
        store = loc['details']['storeID']
        name = loc['details']['storeName']
        state = loc["details"]['province']
        lat = loc["lat"]
        lng = loc['lng']
        
        # locations1 = session.get("https://www.newfoundlandgrocerystores.ca"+loc['details']['url'],headers=headers)
        locations1 = session.get("https://www.newfoundlandgrocerystores.ca"+loc['details']['url'],headers=headers)

        soup1= BeautifulSoup(locations1.text,"lxml")
        phone1 = soup1.find("div",{"class":"store-information__title-content"})
        hors1 = soup1.find("div",{"class":"hours-section__weekly-hours-group hours-section__weekly-hours-group--store"})
       
        if phone1 != None:
            phone = (list(phone1.stripped_strings)[-1])
       

        if hors1 != None:
            hours = (" ".join(list(hors1.stripped_strings)))
  
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "CA"
        tem_var.append("https://www.newfoundlandgrocerystores.ca")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip() if zip1  else "<MISSING>" )
        tem_var.append(country)
        tem_var.append(store)
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hours if hours else "<MISSING>")
        tem_var.append("https://www.newfoundlandgrocerystores.ca"+loc['details']['url'])
        # logger.info(tem_var)
        return_main_object.append(tem_var)
    

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


