import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('baileybanksandbiddle_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://baileybanksandbiddle.com"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= soup.find_all("li",{"class":"navPages-sub-item li-sub-mega"})[-3:]
    
    # base1 = "https://baileybanksandbiddle.com/pages/houston-jewelry-store-at-town-country-village"
    # r1 = session.get(base1)
    # soup2= BeautifulSoup(r1.text,"lxml")
    # script  = soup2.find("script",{"type":"application/ld+json"})
    # data = json.loads(script.text.replace("// ]]>","").replace("// <![CDATA[",""))
    # logger.info(data)
    
    # exit()

    for i in k:
        # logger.info(i.a['href'])
        tem_var =[]
        r = session.get("https://baileybanksandbiddle.com"+i.a['href'])
        soup1= BeautifulSoup(r.text,"lxml")




        
        script  = soup1.find("script",{"type":"application/ld+json"})
        # data = json.loads(script.text.replace("// ]]>","").replace("// <![CDATA[",""))
        jp = json.loads(script.text.replace("// ]]>","").replace("// <![CDATA[",""),strict=False)
        lat = jp["geo"]['latitude']
        lon = jp["geo"]['longitude']
        # logger.info(jp["geo"]['longitude'])

        st = list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[1]
        city = list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[2].split( )[0]
        state = list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[2].split( )[1].replace("75093","")
        zip1 = list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[2].split( )[-1].replace("Texas","")
        phone = list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[3]
        hours1 = list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[4:]
        if len(hours1) !=[]:
            hours = (" ".join(list(soup1.find_all("div",{"class":"col-sm-4"})[1].stripped_strings)[4:]).replace("Store Hours",""))
        else:
            hours = "<MISSING>"
 
        tem_var.append("https://baileybanksandbiddle.com")
        tem_var.append(i.a.text)
        tem_var.append(st)
        tem_var.append(city.replace(",",""))
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("baileybanksandbiddle")
        tem_var.append(lat)
        tem_var.append(lon)
        tem_var.append(hours if  hours else "<MISSING>")
        # logger.info(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


