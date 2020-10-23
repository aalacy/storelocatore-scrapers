import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('seabrafoods_com')





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
    base_url= "https://www.powr.io/plugins/map/wix_view.json?cacheKiller=1571909457810&compId=comp-igjuritt&deviceType=desktop&height=660&instance=rcz7n1lIMmlfZ_wr1zJ6ADAlm_cOdZKFwO94_73Xy34.eyJpbnN0YW5jZUlkIjoiZWFkMzc4MTEtY2ExYy00MGEwLThjODQtMzAzMzg0MjM3ZmVhIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMTktMTAtMjRUMTE6MDE6NDEuNzAyWiIsInVpZCI6bnVsbCwiaXBBbmRQb3J0IjoiNDUuNTYuMTQ4Ljk1LzMyODI0IiwidmVuZG9yUHJvZHVjdElkIjoicHJlbWl1bSIsImRlbW9Nb2RlIjpmYWxzZSwiYWlkIjoiNjAzMDRiZmQtNDliMy00OGI4LTljNjQtMjAwZDJkMGM4ZjhlIiwic2l0ZU93bmVySWQiOiJjNjM1MWYzNC01MDBkLTRkYzktOTc0MS0xN2FjOWQxNmRkNDIifQ&locale=en&pageId=dmwpr&siteRevision=1069&viewMode=site&width=978"

    locations = session.get(base_url,headers=headers).json()
    # logger.info(locations['content']['locations'])
    # soup= BeautifulSoup(r.text,"lxml")
    # return_main_object=[]
    for loc in locations['content']['locations']:
        full_address = loc['address']
        # logger.info(loc['address'])
        tem_var =[]
        name = loc['name']
        soup1= BeautifulSoup(loc['name'],"lxml")
        name1 = soup1.text
        logger.info(soup1.text)
        
        soup= BeautifulSoup(loc['description'],"lxml")
        
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(soup.text))
        if phone_list:
            hours = soup.text.split(phone_list[-1])[-1].replace("/","").replace("Facebook","")
            phone =phone_list[-1]
        else:
            hours = soup.text.split("33067")[-1]
            phone = "<MISSING>"
            
        
        lat = loc['lat']
        lng = loc['lng']
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))[-1]
        state_list = re.findall(r' ([A-Z]{2}) ', str(full_address))[-1]
        address = loc['address'].replace(state_list,"").replace(us_zip_list,"").replace("USA","").split(',')[0]
        city = loc['address'].replace(state_list,"").replace(us_zip_list,"").replace("USA","").split(',')[1]
        
        tem_var.append("https://www.seabrafoods.com")
        tem_var.append(name1.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state_list.strip().encode('ascii', 'ignore').decode('ascii') if state_list.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(us_zip_list.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hours.replace('\r',''))
        tem_var.append("<MISSING>")
        # logger.info(tem_var)
        if "281 Ferry St" in tem_var:
            pass
        else:
            return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


