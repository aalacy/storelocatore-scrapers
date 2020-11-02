import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cinnaholic_com')





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

def convert(time):
    d = datetime.strptime(str(time), "%H%M")
    e=d.strftime("%I:%M %p")
    return e
    # logger.info(e)

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
    base_url= "https://momentfeed-prod.apigee.net/api/llp.json?auth_token=BSPFTAWDPPVBKVPC&page=1&pageSize=10000"
    locations = session.get(base_url,headers=headers).json()
    
    # soup= BeautifulSoup(r.text,"lxml")
    # logger.info(len(locations))
    for loc in locations:
        tem_var=[]
        name = loc['store_info']['name']
        address = loc['store_info']['address']+ ' '+ loc['store_info']['address_extended']
        city = loc['store_info']['locality']
        state = loc['store_info']['region']
        zip1 = loc['store_info']['postcode']
        latitude = loc['store_info']['latitude']
        longitude = loc['store_info']['longitude']
        country =  loc['store_info']['country']
        hours =  loc['store_info']['hours']
        phone = loc['store_info']['phone']
        page_url = loc['store_info']['website']
        # logger.info(address)
        hours_of_operation =''
        if hours:
            time = (hours.strip().split(";"))
            if "2,1000,2100" == time[0]:
                time.insert(0,"Close")
            for p in time:
                if p != "Close" :
                    tiem1 = p.replace("1,","Monday,").replace("2,","Tuesday,").replace("3,","Wednesday,").replace("4,","Thursday,").replace("5,","Friday,").replace("6,","Saturday,").replace("7,","Sunday,").split(",")
                    if len(tiem1) != 1:
                        p3 = convert(tiem1[1])
                        p4 = convert(tiem1[2])
                        hours_of_operation = hours_of_operation + ' '+ tiem1[0] + ' '  + p3 + ' '+p4
                else:
                    hours_of_operation = "Monday Close"

            hours_of_operation1 = hours_of_operation.strip()
 
        
        if len(zip1)== 6 or len(zip1)== 7:
            country = "CA"
        else:
            country = "US"

        tem_var.append("https://www.cinnaholic.com/")
        tem_var.append(name.encode('ascii', 'ignore').decode('ascii').strip().replace("&#8211;",""))
        tem_var.append(address.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        tem_var.append(state.strip().encode('ascii', 'ignore').decode('ascii') if state.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>" )
        tem_var.append(zip1.encode('ascii', 'ignore').decode('ascii').strip().replace("7090","07090") if zip1  else "<MISSING>" )
        tem_var.append(country)
        tem_var.append("<MISSING>")
        tem_var.append(phone.encode('ascii', 'ignore').decode('ascii').strip() if phone.encode('ascii', 'ignore').decode('ascii').strip() else "<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours_of_operation1 if hours_of_operation1 else "<MISSING>")
        tem_var.append(page_url)
        if "Cinnaholic - Coming Soon" in tem_var:
            pass
        else:
            return_main_object.append(tem_var)
        # logger.info(tem_var)
    

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


