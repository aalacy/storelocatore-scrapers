import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('changsmongoliangrill_com')





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
    base_url= "http://www.changsmongoliangrill.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    marker  = soup.find_all("div",{"class":"location-address"})
    for i in marker:
        tem_var =[]
        r = session.get(i.a['href'])
        soup1= BeautifulSoup(r.text,"lxml")
        v=(list(soup1.find("div",{'class':"col-md-4 location-left"}).stripped_strings))
        # exit()
        # if i['lobbyhours']:
    #         time = i['lobbyhours'].replace("<br/>",'').replace("\n"," ").replace("<br>"," ")+ ' ' +" ".join(i['driveuphours'].split("<br/>")).replace("\n","").replace("<br/>","")
    #     else:
    #         time = "<MISSING>"
        time = (" ".join(v[4:]))
        if "18925 SE McLoughlin Blvd, Milwaukie, OR 97267" in v:
            # logger.info("".join(v[3:]))
            
            tem_var.append("http://www.changsmongoliangrill.com")
            tem_var.append(soup1.find("h1",{"class":"page-title"}).text)
            tem_var.append(v[0].split(',')[0])
            tem_var.append(v[0].split(',')[1])
            tem_var.append(v[0].split(',')[2].split( )[0])
            tem_var.append(v[0].split(',')[2].split( )[1])
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(v[1])
            tem_var.append("changsmongoliangrill")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(" ".join(v[3:]))
            return_main_object.append(tem_var)
        else:
            tem_var.append("http://www.changsmongoliangrill.com")
            tem_var.append(soup1.find("h1",{"class":"page-title"}).text)
            tem_var.append(v[0])
            tem_var.append(v[1].split(',')[0])
            tem_var.append(v[1].split(',')[1].split( )[0])
            tem_var.append(v[1].split(',')[1].split( )[1].replace("OR","97267"))
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(v[2])
            tem_var.append("changsmongoliangrill")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(time)
            return_main_object.append(tem_var)
       

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


