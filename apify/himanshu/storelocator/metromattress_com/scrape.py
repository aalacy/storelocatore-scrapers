import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
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
    }
    return_main_object =[]
    addressess =[]
    for q in range(11):
        base_url= "https://www.metromattress.com/locationsmain/"+str(q)+"/"
        r = session.get(base_url,headers=headers)
        soup= BeautifulSoup(r.text,"lxml")
        loc = (soup.find_all("h2",{"class":"wppl-h2"}))
        for i in loc:
            tem_var=[]
            r1 = session.get(i.a['href'],headers=headers)
            name = (i.a.text.split(")")[1].strip())
            soup1= BeautifulSoup(r1.text,"lxml")
            if "Metro Mattress Batavia" in name:
                addr = list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[0]
                address = addr.split("\n")[0]
                city = addr.split("\n")[1].split(",")[0]
                state = addr.split("\n")[1].split(",")[1].strip().split(" ")[0]
                zip1 = addr.split("\n")[1].split(",")[1].strip().split(" ")[1]
                phone = addr.split("\n")[1].split(",")[1].strip().split("  ")[1]
                hours = ( " ".join(list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[6:18]))
            else:
                address = list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[0]
                city = list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[1].split(',')[0]
                full_add = list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[1].split(',')[1]
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_add))
                if us_zip_list:
                    zip1 = us_zip_list[-1]
                else:
                    zip1 = ''
                state = (full_add.replace(zip1,""))
                phone = list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[2]
                hours = ( " ".join(list(soup1.find("div",{"class":"black-line-wrap clearfix"}).stripped_strings)[6:20]))
            lat = soup1.find_all("iframe")[2]['src'].split("!2d")[-1].split("!3d")[0]
            lng = soup1.find_all("iframe")[2]['src'].split("!2d")[-1].split("!3d")[1].split("!")[0]
            tem_var.append("https://www.metromattress.com/")
            tem_var.append(name.strip())
            tem_var.append(address.strip())
            tem_var.append(city.strip())
            tem_var.append(state.strip())
            tem_var.append(zip1.strip() if zip1 else "14150")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("Call ","").strip())
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lng)
            tem_var.append(hours.replace("HOURS","").strip())
            tem_var.append(i.a['href'])
            if tem_var[2] in addressess:
                continue
            addressess.append(tem_var[2])
            return_main_object.append(tem_var)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


