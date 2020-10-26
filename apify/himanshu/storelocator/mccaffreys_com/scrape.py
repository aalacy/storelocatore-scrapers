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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url= "https://mccaffreys.com/wp-admin/admin-ajax.php?action=store_search&lat=40.211498&lng=-74.78793999999999&max_results=100&search_radius=100&autoload=1"
    locations = session.get(base_url,headers=headers).json()
    
    return_main_object=[]
    for loc in locations:
        lat = loc['lat']
        lng = loc['lng']
        name = loc['store']
        phone =loc['phone']
        phone = loc['phone']
        address = loc['address'] + ' ' +loc['address2']
        state = loc['state']
        city = loc['city']
        zip1 = loc['zip']
        description = loc['description']
        soup= BeautifulSoup(description,"lxml")
        hours = (" ".join(list(soup.stripped_strings)[3:]).replace(": ","").strip().replace("* *Tapas menu available until one hour before close",""))

        tem_var =[]
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "US"
        # print(hours)
        tem_var.append("https://mccaffreys.com")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8217;","").replace("&#038;",""))
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(country)
        tem_var.append("<MISSING>")
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hours.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("https://mccaffreys.com/about-us/our-locations/")
        if "COMING SOON TO NEW HOPE" in tem_var:
            pass
        else:
            pass

            return_main_object.append(tem_var)
            # print(tem_var)
        

   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


