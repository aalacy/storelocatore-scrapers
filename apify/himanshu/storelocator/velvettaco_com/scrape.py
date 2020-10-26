import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('velvettaco_com')





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
    base_url= "https://velvettaco.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object=[]

    k = soup.find("div",{"id":"location_drop"}).find_all("a")
    for i in k:
        tem_var =[]
        r = session.get(i['href'],headers=headers)
        soup= BeautifulSoup(r.text,"lxml")
        script = soup.find_all("script",{"type":"application/ld+json"})[1].text
        address = json.loads(script)['address']['streetAddress']
        contry = json.loads(script)['address']['addressCountry']
        city = json.loads(script)['address']['addressLocality']
        state = json.loads(script)['address']['addressRegion']
        zip1 = json.loads(script)['address']['postalCode']
        streetAddress = address.replace(city,"").replace(state,"").replace(zip1,"").replace(" ,","")
        phone = json.loads(script)['telephone']
        name = json.loads(script)['name']
        openingHours = " ".join(json.loads(script)['openingHours'])
        phone1 = getDecodedPhoneNo(phone)
        tem_var.append("https://velvettaco.com")
        tem_var.append(name)
        tem_var.append(streetAddress)
        tem_var.append(city)
        tem_var.append(state.strip() if state.strip() else "<MISSING>" )
        tem_var.append(zip1)
        tem_var.append(contry)
        tem_var.append("<MISSING>")
        tem_var.append(phone1)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(openingHours)
        tem_var.append(i['href'])
        # logger.info(tem_var)
        return_main_object.append(tem_var)
        

   
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


