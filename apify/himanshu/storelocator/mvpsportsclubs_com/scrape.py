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
    base_url= "https://mvpsportsclubs.com/wp-admin/admin-ajax.php?action=store_search&lat=42.956273&lng=-85.80017270000002&autoload=1"
    locations = session.get(base_url,headers=headers).json()
    # soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    for loc in locations:
        tem_var =[]
        city = loc['address'].split("<br />")[-1].replace("\n","").replace("\r","").split(",")[0]
        state = loc['address'].split("<br />")[-1].replace("\n","").replace("\r","").split(",")[1].split( )[0]
        zip1 = loc['address'].split("<br />")[-1].replace("\n","").replace("\r","").split(",")[1].split( )[1]
        address = loc['address'].split("<br />")[0]
        phone = loc["phone_number"]
        lat = loc["latitude"]
        lng = loc["longitude"]
        name = loc['store']
        hours1 = session.get(loc['permalink'],headers=headers)
        soup1= BeautifulSoup(hours1.text,"lxml")


        hours1 = soup1.find_all("div",{"class":"topbar-dropdown"})
        if hours1 !=[]:
            hours = " ".join(list(hours1[-1].stripped_strings)[1:])
            
        else:
            # print(loc['permalink'])
            hours = "<INACCESSIBLE>"
        
        
        tem_var =[]
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "US"
        tem_var.append("https://mvpsportsclubs.com")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(country)
        tem_var.append("<MISSING>")
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hours)
        tem_var.append(loc['permalink'])
        # print(tem_var)
        return_main_object.append(tem_var)
        

   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


